#new celery_app.py
import time
import os
import sys

import django
import datetime
from django.conf import settings
from celery import Celery
from celery.utils.log import get_task_logger
from cloudscheduler.lib.db_config_na import Config
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
    PULL_REQ = "csv2_image_pull_requests"
    IMG_CACHE = "csv2_image_cache"
    CLOUD = "csv2_clouds"
    config.db_open()
    # get tx row from database
    tx_row = _get_tx_row(PULL_REQ, tx_id, config)
    # check if the image is in the cache, if so return complete
    if _check_get_img_cache(IMG_CACHE, tx_row["image_name"], tx_row["checksum"], config) is not None:
        # Image is already downloaded, we can delete this transaction
        logger.error("Image %s-%s already in cache, removing transaction." % (tx_row["image_name"], tx_row["checksum"]))
        try:
            config.db_delete(PULL_REQ, tx_row)
            config.db_commit()
            config.db_close()
            return True
        except Exception as exc:
            logger.error("Unable to delete transaction %s-%s due to:" % (tx_row["image_name"], tx_row["checksum"]))
            logger.error(exc)
            config.db_close()
            return False

    # else get the cloud row for the source and create a glance client and call download function
    else:
        cloud_row = _get_cloud(CLOUD, tx_row["target_group_name"], tx_row["target_cloud_name"], config)
        os_session = glint_utils.get_openstack_session(cloud_row)
        glance = glint_utils.get_glance_client(os_session, cloud_row["region"])
        result_tuple = glint_utils.download_image(glance, tx_row["image_name"], tx_row["image_id"], tx_row["checksum"], config.categories["glintPoller.py"]["image_cache_dir"])
        if result_tuple[0]:
            # successful download, update the cache and remove transaction
            cache_dict = {
                "image_name": tx_row["image_name"],
                "checksum": tx_row["checksum"],
                "container_format": result_tuple[3],
                "disk_format": result_tuple[2]
            }
            config.db_merge(IMG_CACHE, cache_dict)

            logger.error("Download complete, removing transaction")
            config.db_delete(PULL_REQ, tx_row)
            config.db_commit()
            config.db_close()
            return True
        else:
            # failed download, report error and update tx status
            tx_row["message"] = result_tuple[1]
            tx_row["status"] = "Failed"
            config.db_merge(PULL_REQ, tx_row)
            config.db_commit()
            config.db_close()
            return False


    return None


# type 2, transaction requests (transfers)

@app.task(bind=True)
def tx_request(self, tx_id):
    db_category_list = ["glintv2", "general", "glintPoller.py"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3)
    IMG_TX = "csv2_image_transactions"
    IMG_CACHE = "csv2_image_cache"
    CLOUD = "csv2_clouds"
    IMAGE = "cloud_images"
    config.db_open()
    # get tx row from database
    tx_row = _get_tx_row(IMG_TX, tx_id, config)
    logger.info("Processing transaction: %s: Move image %s to target group-cloud %s-%s" % (tx_row["tx_id"], tx_row["image_name"], tx_row["target_group_name"], tx_row["target_cloud_name"]))
    print("Processing transaction: %s" % tx_row["tx_id"])
    # triple check target image doesn't exist
    if _check_image(tx_row["target_group_name"], tx_row["target_group_name"], tx_row["image_name"], tx_row["checksum"], config):
        #image already exists, we are done here
        logger.info("Image already exists, skipping transfer.")
        print("Image already exists, skipping transfer.")
        config.db_delete(IMG_TX, tx_row)
        config.db_commit()
        config.db_close()
        return True
    # if not, check cache for source image, if it's not there check that a pull request is queue'd
    logger.info("Finding source image...")
    print("Finding source image...")
    image = glint_utils.check_cache(config, tx_row["image_name"], tx_row["checksum"], tx_row["target_group_name"], tx_row["requester"], return_image=True) 

    if image is None:
        sleep_itterations = 0
        # try every 15s for 10 mins to get the image from the cache
        while image is None:
            time.sleep(15)
            image = glint_utils.check_cache(config, tx_row["image_name"], tx_row["checksum"], tx_row["target_group_name"], tx_row["requester"], return_image=True) 
            sleep_itterations = sleep_itterations + 1
            if sleep_itterations > 40:
                # we've waited 10 minutes for the download, put this transaction into error state and move on
                logger.error("Wait time exceeded waiting for pull request on image: %s---%s" % (tx_row["image_name"], tx_row["checksum"]))
                print("Wait time exceeded waiting for pull request on image: %s---%s" % (tx_row["image_name"], tx_row["checksum"]))
                tx_row["status"] = "error"
                tx_row["message"] = "Timed out waiting for pull request..."
                config.db_merge(IMG_TX, tx_row)
                config.db_commit()
                config.db_close()
                return False
    # we have the image, lets go ahead with the transfer
    try:
        logger.info("Source image found in cache, beginning upload..")
        print("Source image found in cache, beginning upload..")
        cloud = _get_cloud(CLOUD, tx_row["target_group_name"], tx_row["target_cloud_name"], config)
        os_session = glint_utils.get_openstack_session(cloud)
        glance = glint_utils.get_glance_client(os_session, cloud["region"])
        image_id = glint_utils.create_placeholder_image(glance, image["image_name"], image["disk_format"], image["container_format"])
        uploaded_image = glint_utils.upload_image(glance, image_id, image["image_name"], config.categories["glintPoller.py"]["image_cache_dir"], tx_row["checksum"], image["disk_format"], image["container_format"])  
    except Exception as exc:
        logger.error("Upload failed:")
        print("Upload failed:")
        logger.exception(exc)
        print(exc)
        tx_row["status"] = "error"
        tx_row["message"] = exc
        config.db_merge(IMG_TX, tx_row)
        config.db_commit()
        config.db_close()
        return False
    logger.info("Image upload complete")
    print("Image upload complete")
    # add new image row
    if uploaded_image.size == "":
        size = 0
    else:
        size = uploaded_image.size

    created_datetime = datetime.datetime.strptime(uploaded_image.created_at, "%Y-%m-%dT%H:%M:%SZ")
    created_datetime.strftime("%Y-%m-%d %H:%M:%S")
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
        'created_at': created_datetime,
        'last_updated': time.time()
    }
    config.db_merge(IMAGE, img_dict)
    config.db_delete(IMG_TX, tx_row)
    config.db_commit()
    config.db_close()
    return True 


@app.task(bind=True)
def debug_task(self):
    logger.debug('Request: {0!r}'.format(self.request))




#
# Helper functions
#

def _get_tx_row(table, tx_id, config):
    where_clause = "tx_id='%s'" % tx_id
    rc, msg, tx_row_list = config.db_query(table, where=where_clause)
    tx_row = tx_row_list[0]
    tx_row["status"] = "claimed"
    config.db_merge(table, tx_row)
    config.db_commit()
    return tx_row


# returns row of cached image or None if not in cache
def _check_get_img_cache(cache_table, image_name, image_checksum, config):
    where_clause = "image_name='%s' and image_checksum='%s'" % (image_name, image_checksum)
    rc, msg, rows = config.db_query(cache_table, where=where_clause)
    if len(rows) > 0:
        return rows[0]
    else:
        return None


def _get_cloud(table, group_name, cloud_name, config):
    where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, cloud_name)
    rc, msg, rows = config.db_query(table, where=where_clause)
    return rows[0]


# returns true if image exists, false if it doesn't
def _check_image(group_name, cloud_name, image_name, checksum, config):
    IMAGE = "cloud_images"
    where_clause = "name='%s' and checksum='%s' and cloud_name='%s' and group_name='%s'" % (image_name, checksum, cloud_name, group_name)
    rc, msg, image = config.db_query(IMAGE, where=where_clause)
    if len(image) > 0:
        return True
    else:
        return False

