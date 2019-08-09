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

app = Celery('glintv2', broker=config.celery_url, backend=config.celery_backend)
app.config_from_object('django.conf:settings')


#instead of having a task type for each transaction we will split it up into 2 worker types
# for now i think having 2 of each should be sufficient
#1)pull requests
#2)transfer requests

#logic will be similar for both both work off different database tables



# type 1, pull requests
@app.task(bind=True)
def pull_request(self, tx_id):
    db_category_list = ["glintv2", "general"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3)
    PULL_REQ = config.db_map.classes.csv2_image_pull_requests
    IMG_CACHE = config.db_map.classes.csv2_image_cache
    CLOUD = config.db_map.classes.csv2_clouds
    config.db_open()
    # get tx row from database
    tx_row = _get_tx_row(PULL_REQ, tx_id, config)
    # check if the image is in the cache, if so return complete
    if _check_get_img_cache(IMG_CACHE, tx_row.image_name, tx_row.checksum, config) is None:
        # Image is already downloaded, we can delete this transaction
        logger.info("Image %s-%s already in cache, removing transaction." % (tx_row.image_name, tx_row.checksum))
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
        result_tuple = glint_utils.download_image(glance, tx_row.image_name, tx_row.image_id, config.image_cache_dir)
        if result_tuple[0]:
            # successful download, update the cache and remove transaction
            cache_dict = {
                "image_name": tx_row.image_name,
                "checksum": tx_row.checksum,
                "container_format": result_tuple[2]
            }
            new_cache_item = IMG_CACHE(**cache_dict)
            config.db_session.merge(new_cache_item)

            logger.info("Download complete, removing transaction")
            config.db_session.delete(tx_row)
            config.db_session.commit()
            config.db_close()
            return True
        else:
            # failed download, report error and update tx status
            tx_row.message = result_typle[1]
            tx_row.status = "Failed"
            config.db_session.merge(tx_row)
            config.db_session.commit()
            config.db_close()
            return False


    return None


# type 2, transaction requests (transfers)

@app.task(bind=True)
def tx_request(self, tx_id):
    db_category_list = ["glintv2", "general"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3)
    IMG_TX = config.db_map.classes.csv2_image_transactions
    IMG_CACHE = db_config.db_map.classes.csv2_image_cache
    config.db_open()
    tx_row = _get_tx_row(IMG_TX, tx_id, config)
    # get tx row from database
    # triple check target image doesn't exist
    # if not, check cache for source image, if it's not there check that a pull request is queue'd
    # if none are queued queue one and wait for it to appear in cache
    # once image is in cache get the cloud row for the target and call the upload function,
    # maybe upload cloud image table and return complete

    return None


@app.task(bind=True)
def debug_task(self):
    logger.debug('Request: {0!r}'.format(self.request))




#
# Helper functions
#

def _get_tx_row(table, tx_id, config):
    return config.db_session.query(table).get(tx_id)

# returns row of cached image or None if not in cache
def _check_get_img_cache(cache_tabe, image_name, image_checksum, config):
    return config.db_session.query(cache_tabe).get(image_name, image_checksum)


def _get_cloud(table, group_name, cloud_name, config):
    return config.db_session.query(table).get(group_name, cloud_name)
