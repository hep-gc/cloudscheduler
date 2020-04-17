#new celery_app.py
import time
import os
import sys

import django
from django.conf import settings
from celery import Celery
from celery.utils.log import get_task_logger
from cloudscheduler.lib.db_config import Config
# this should be more specific as we don't need to import private functions, it will likely boil down to trasfer/delete/upload/glance client
from . import glint_utils


logger = get_task_logger(__name__)

db_category_list = ["general", "glintPoller.py"]
config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=4)

# Indicate Celery to use the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudscheduler_web.settings')

app = Celery('glintv2', broker=config.categories["glintPoller.py"]["celery_url"], backend=config.categories["glintPoller.py"]["celery_backend"])
app.config_from_object('django.conf:settings')


#instead of having a task type for each transaction we will split it up into 2 worker types
# for now i think having 2 of each should be sufficient
#1)pull requests
#2)transfer requests

#logic will be similar for both both work off different database tables



# type 1, pull requests
@app.task(bind=True)
def pull_request(self, tx_id):
    db_category_list = ["glintv2", "general", "glintPoller.py"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3)
    PULL_REQ = config.db_map.classes.csv2_image_pull_requests
    IMG_CACHE = config.db_map.classes.csv2_image_cache
    CLOUD = config.db_map.classes.csv2_clouds
    config.db_open()
    # get tx row from database
    tx_row = _get_tx_row(PULL_REQ, tx_id, config)
    # check if the image is in the cache, if so return complete
    if _check_get_img_cache(IMG_CACHE, tx_row.image_name, tx_row.checksum, config) is not None:
        # Image is already downloaded, we can delete this transaction
        logger.error("Image %s-%s already in cache, removing transaction." % (tx_row.image_name, tx_row.checksum))
        try:
            config.db_session.delete(tx_row)
            config.db_session.commit()
            config.db_close()
            return True
        except Exception as exc:
            logger.error("Unable to delete transaction %s-%s due to:" % (tx_row.image_name, tx_row.checksum))
            logger.error(exc)
            config.db_close()
            return False

    # else get the cloud row for the source and create a glance client and call download function
    else:
        cloud_row = _get_cloud(CLOUD, tx_row.target_group_name, tx_row.target_cloud_name, config)
        os_session = glint_utils.get_openstack_session(cloud_row)
        glance = glint_utils.get_glance_client(os_session, cloud_row.region)
        result_tuple = glint_utils.download_image(glance, tx_row.image_name, tx_row.image_id, tx_row.checksum, config.categories["glintPoller.py"]["image_cache_dir"])
        if result_tuple[0]:
            # successful download, update the cache and remove transaction
            cache_dict = {
                "image_name": tx_row.image_name,
                "checksum": tx_row.checksum,
                "container_format": result_tuple[3],
                "disk_format": result_tuple[2]
            }
            new_cache_item = IMG_CACHE(**cache_dict)
            config.db_session.merge(new_cache_item)

            logger.error("Download complete, removing transaction")
            config.db_session.delete(tx_row)
            config.db_session.commit()
            config.db_close()
            return True
        else:
            # failed download, report error and update tx status
            tx_row.message = result_tuple[1]
            tx_row.status = "Failed"
            config.db_session.merge(tx_row)
            config.db_session.commit()
            config.db_close()
            return False


    return None


# type 2, transaction requests (transfers)

@app.task(bind=True)
def tx_request(self, tx_id):
    db_category_list = ["glintv2", "general", "glintPoller.py"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3)
    IMG_TX = config.db_map.classes.csv2_image_transactions
    IMG_CACHE = config.db_map.classes.csv2_image_cache
    CLOUD = config.db_map.classes.csv2_clouds
    IMAGE = config.db_map.classes.cloud_images
    config.db_open()
    # get tx row from database
    tx_row = _get_tx_row(IMG_TX, tx_id, config)
    logger.info("Processing transaction: %s: Move image %s to target group-cloud %s-%s" % (tx_row.tx_id, tx_row.image_name, tx_row.target_group_name, tx_row.target_cloud_name))
    print("Processing transaction: %s" % tx_row.tx_id)
    # triple check target image doesn't exist
    if _check_image(tx_row.target_group_name, tx_row.target_group_name, tx_row.image_name, tx_row.checksum, config):
        #image already exists, we are done here
        logger.info("Image already exists, skipping transfer.")
        print("Image already exists, skipping transfer.")
        config.db_session.delete(tx_row)
        config.db_session.commit()
        config.db_close()
        return True
    # if not, check cache for source image, if it's not there check that a pull request is queue'd
    logger.info("Finding source image...")
    print("Finding source image...")
    image = _check_cache(tx_row.image_name, tx_row.checksum, tx_row.target_group_name, config) 
    if image is None:
        sleep_itterations = 0
        # try every 15s for 10 mins to get the image from the cache
        while image is None:
            time.sleep(15)
            image = _check_cache(tx_row.image_name, tx_row.checksum, tx_row.target_group_name, config)
            sleep_itterations = sleep_itterations + 1
            if sleep_itterations > 40:
                # we've waited 10 minutes for the download, put this transaction into error state and move on
                logger.error("Wait time exceeded waiting for pull request on image: %s---%s" % (tx_row.image_name, tx_row.checksum))
                print("Wait time exceeded waiting for pull request on image: %s---%s" % (tx_row.image_name, tx_row.checksum))
                tx_row.status = "error"
                tx_row.message = "Timed out waiting for pull request..."
                config.db_session.merge(tx_row)
                config.db_session.commit()
                config.db_close()
                return False
    # we have the image, lets go ahead with the transfer
    try:
        logger.info("Source image found in cache, beginning upload..")
        print("Source image found in cache, beginning upload..")
        cloud = _get_cloud(CLOUD, tx_row.target_group_name, tx_row.target_cloud_name, config)
        os_session = glint_utils.get_openstack_session(cloud)
        glance = glint_utils.get_glance_client(os_session, cloud.region)
        image_id = glint_utils.create_placeholder_image(glance, image.image_name, image.disk_format, image.container_format)
        uploaded_image = glint_utils.upload_image(glance, image_id, image.image_name, config.categories["glintPoller.py"]["image_cache_dir"], tx_row.checksum, image.disk_format, image.container_format)  
    except Exception as exc:
        logger.error("Upload failed:")
        print("Upload failed:")
        logger.error(exc)
        print(exc)
        tx_row.status = "error"
        tx_row.message = exc
        config.db_session.merge(tx_row)
        config.db_session.commit()
        config.db_close()
        return False
    logger.info("Image upload complete")
    print("Image upload complete")
    # add new image row
    if uploaded_image.size == "":
        size = 0
    else:
        size = uploaded_image.size
    img_dict = {
        'group_name': tx_row.target_group_name,
        'cloud_name': tx_row.target_cloud_name,
        'id': uploaded_image.id,
        'cloud_type': "openstack",
        'container_format': uploaded_image.container_format,
        'disk_format': uploaded_image.disk_format,
        'name': uploaded_image.name,
        'size': size,
        'visibility': uploaded_image.visibility,
        'min_disk': uploaded_image.min_disk,
        'min_ram': uploaded_image.min_ram,
        'checksum': uploaded_image.checksum,
        'last_updated': time.time()
    }
    new_image = IMAGE(**img_dict)
    config.db_session.merge(new_image)
    config.db_session.delete(tx_row)
    config.db_session.commit()
    config.db_close()
    return True 


@app.task(bind=True)
def debug_task(self):
    logger.debug('Request: {0!r}'.format(self.request))




#
# Helper functions
#

def _get_tx_row(table, tx_id, config):
    tx_row = config.db_session.query(table).get(tx_id)
    tx_row.status = "claimed"
    config.db_session.merge(tx_row)
    config.db_session.commit()
    return tx_row


# returns row of cached image or None if not in cache
def _check_get_img_cache(cache_tabe, image_name, image_checksum, config):
    return config.db_session.query(cache_tabe).get((image_name, image_checksum))


def _get_cloud(table, group_name, cloud_name, config):
    return config.db_session.query(table).get((group_name, cloud_name))


# returns true if image exists, false if it doesn't
def _check_image(group_name, cloud_name, image_name, checksum, config):
    IMAGE = config.db_map.classes.cloud_images
    image = config.db_session.query(IMAGE).filter(IMAGE.name == image_name, IMAGE.checksum == checksum, IMAGE.cloud_name == cloud_name, IMAGE.group_name == group_name)
    if image.count() > 0:
        return True
    else:
        return False


def _check_cache(image_name, checksum, group_name, config):
    CACHE = config.db_map.classes.csv2_image_cache 
    image = config.db_session.query(CACHE).get((image_name, checksum))
    if image is not None:
        return image
    else:
        PULL_REQ = config.db_map.classes.csv2_image_pull_requests
        #check if there is a pull request not in fail state for this image
        req = config.db_session.query(PULL_REQ).filter(PULL_REQ.image_name == image_name, PULL_REQ.checksum == checksum)
        #if there isn't queue a pull request and return None

        #if there IS then just return none

