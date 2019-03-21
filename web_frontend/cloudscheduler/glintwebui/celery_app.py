from __future__ import absolute_import, unicode_literals
import os
import time
import subprocess
import django
from django.conf import settings

from celery import Celery
from celery.utils.log import get_task_logger
#import glintwebui.config as config
from cloudscheduler.lib.db_config import Config
config = Config('/etc/cloudscheduler/cloudscheduler.yaml', 'web_frontend', pool_size=2, max_overflow=10)

from glintwebui.glint_api import repo_connector
from .utils import  jsonify_image_list, update_pending_transactions, get_images_for_group,\
set_images_for_group, process_pending_transactions, process_state_changes, queue_state_change,\
find_image_by_name, check_delete_restrictions, decrement_transactions, get_num_transactions,\
repo_proccesed, check_for_repo_changes, set_collection_task, check_for_image_conflicts,\
set_conflicts_for_group, check_cached_images, add_cached_image, do_cache_cleanup

logger = get_task_logger(__name__)


# Indicate Celery to use the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudscheduler_web.settings')

#django.setup()

app = Celery('glintv2', broker=config.celery_url, backend=config.celery_backend)
app.config_from_object('django.conf:settings')


@app.task(bind=True)
def debug_task(self):
    logger.debug('Request: {0!r}'.format(self.request))


# Must find and download the appropriate image (by name) and then upload it
# to the given image ID
@app.task(bind=True)
def transfer_image(self, image_name, image_id, group_name, auth_url, project_tenant, username, password, requesting_user, cloud_name, project_domain_name="Default", user_domain_name="Default", region=None):
    logger.info("User %s attempting to transfer %s - %s to repo '%s'", \
        requesting_user, image_name, image_id, project_tenant)

    # Find image by name in another repo where the state=present
    # returns tuple: (auth_url, tenant, username, password, img_id, checksum)
    src_img_info = find_image_by_name(group_name=group_name, image_name=image_name)

    if src_img_info is False:
        logger.error("Could not find suitable source image for transfer, cancelling transfer")
        decrement_transactions()
        return False

    #check if this image is cached locally
    image_path = check_cached_images(image_name, src_img_info[5])

    if image_path is not None:
        logger.info("Found cached copy at: %s uploading image", image_path)
        #upload cached image
        image_path = image_path.rsplit('/', 1)[0]+ "/"
        logger.info("Uploading Image to %s", project_tenant)
        dest_rcon = repo_connector(
            auth_url=auth_url,
            project=project_tenant,
            username=username,
            password=password,
            project_domain_name=project_domain_name,
            user_domain_name=user_domain_name,
            alias=cloud_name,
            region=region)
        dest_rcon.upload_image(image_id=image_id, image_name=image_name, scratch_dir=image_path)

        queue_state_change(
            group_name=group_name,
            cloud_name=cloud_name,
            img_id=image_id,
            state='Present',
            hidden=None)
        logger.info("Image transfer finished")
        decrement_transactions()
        return True

    else:
        logger.info("No cached copy found, downloading image")
        # Download img to the cache folder

        # First check if a file by this name exists in the cache folder
        image_path = "/var/www/glintv2/scratch/" + image_name

        if os.path.exists(image_path):
            # Filename exists locally, we need to use a temp folder
            for x in range(0, 10):
                #first check if the temp folder exists
                image_path = "/var/www/glintv2/scratch/" + str(x)
                if not os.path.exists(image_path):
                    #create temp folder and break since it is definitly empty
                    os.makedirs(image_path)
                    image_path = "/var/www/glintv2/scratch/" + str(x) + "/" + image_name
                    break

                #then check if the file is in that folder
                image_path = "/var/www/glintv2/scratch/" + str(x) + "/" + image_name
                if not os.path.exists(image_path):
                    break

        # remove file name from path
        image_path = image_path.rsplit('/', 1)[0]
        image_path = image_path + "/"

        print("Downloading Image from %s" % src_img_info[1])
        src_rcon = repo_connector(
            auth_url=src_img_info[0],
            project=src_img_info[1],
            username=src_img_info[2],
            password=src_img_info[3],
            user_domain_name=src_img_info[6],
            project_domain_name=src_img_info[7],
            region=src_img_info[8])
        download_result = src_rcon.download_image(
            image_name=image_name,
            image_id=src_img_info[4],
            scratch_dir=image_path)
        logger.info("Image download finished")
        logger.info("Download result: %s" % download_result)

        # Upload said image to the new repo
        logger.info("Uploading Image to %s", project_tenant)
        dest_rcon = repo_connector(
            auth_url=auth_url,
            project=project_tenant,
            username=username,
            password=password,
            project_domain_name=project_domain_name,
            user_domain_name=user_domain_name,
            region=region)
        dest_rcon.upload_image(image_id=image_id, image_name=image_name, scratch_dir=image_path)

        queue_state_change(
            group_name=group_name,
            cloud_name=cloud_name,
            img_id=image_id,
            state='Present',
            hidden=None)
        image_path = image_path + image_name
        add_cached_image(image_name, src_img_info[5], image_path)
        decrement_transactions()
        return True

# Accepts Image info (name, local path, and format), project name, repo object info, and the
# requesting user. Uploads the given image to the target cloud (repo object)
#
@app.task(bind=True)

def upload_image(self, image_name, image_path, auth_url, project_tenant, username, password, requesting_user, disk_format, container_format, project_domain_name="Default", user_domain_name="Default", region=None):
    # Upload said image to the new repo
    logger.info("Attempting to upload Image to %s for user:%s", project_tenant, requesting_user)
    dest_rcon = repo_connector(
        auth_url=auth_url,
        project=project_tenant,
        username=username,
        password=password,
        project_domain_name=project_domain_name,
        user_domain_name=user_domain_name,
        region=region)
    image_id = dest_rcon.upload_image(
        image_id=None,
        image_name=image_name,
        scratch_dir=image_path,
        disk_format=disk_format,
        container_format=container_format)
    img_checksum = dest_rcon.get_checksum(image_id)

    if check_cached_images(image_name, img_checksum) is None:
        #image isn't in cache and it's unique add it to the cache list
        add_cached_image(image_name, img_checksum, image_path)


    logger.info("Image upload finished")
    decrement_transactions()
    return True

# Accepts image id, project name, and repo object to delete image ID from.
@app.task(bind=True)
def delete_image(self, image_id, image_name, group_name, auth_url, project_tenant, username, password, requesting_user, cloud_name, project_domain_name="Default", user_domain_name="Default", region=None):
    logger.info("User %s attempting to delete %s - %s from cloud '%s'",\
        requesting_user, image_name, image_id, project_tenant)
    if check_delete_restrictions(image_id=image_id, group_name=group_name, cloud_name=cloud_name):
        rcon = repo_connector(
            auth_url=auth_url,
            project=project_tenant,
            username=username,
            password=password,
            project_domain_name=project_domain_name,
            user_domain_name=user_domain_name,
            region=region)
        result = rcon.delete_image(image_id)
        if result:
            queue_state_change(
                group_name=group_name,
                cloud_name=cloud_name,
                img_id=image_id,
                state='deleted',
                hidden=None)
            logger.info("Image Delete finished")
            decrement_transactions()
            return True
        logger.error("Unknown error deleting %s  (result = %s)", image_id, result)
        decrement_transactions()
        return False
    else:
        logger.error(("Delete request violates delete rules,"
                      "image either shared or the last copy."))
        queue_state_change(
            group_name=group_name,
            cloud_name=cloud_name,
            img_id=image_id,
            state='present',
            hidden=None)
        decrement_transactions()
        return False
