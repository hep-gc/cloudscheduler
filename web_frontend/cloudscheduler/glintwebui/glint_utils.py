# glint utils

import logging
import os
import string
import random

from cloudscheduler.lib.openstack_functions import get_openstack_sess, get_glance_connection

from cloudscheduler.lib.db_config import Config
config = Config('/etc/cloudscheduler/cloudscheduler.yaml', ['general', 'openstackPoller.py', 'web_frontend'], pool_size=2, max_overflow=10)
ALPHABET = string.ascii_letters + string.digits + string.punctuation
ALPHABET = ALPHABET.replace("'", "")
ALPHABET = ALPHABET.replace('"', "")

# new glint api, maybe make this part of glint utils?

"""
def create_placeholder_image(glance, image_name, disk_format, container_format):
    image = glance.images.create(
    #image = glance.create_image(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format)
    return image.id
"""

# Upload an image to repo, returns image id if successful
# if there is no image_id it is a direct upload and no placeholder exists
def upload_image(cloud, image_id, image_name, scratch_dir, image_checksum=None, disk_format=None, container_format="bare"):
    try:
        sess = get_openstack_sess(cloud, config.categories["openstackPoller.py"]["cacerts"])
        if sess is False:
            logging.error("Failed to get openstack session")
            return False
        glance = get_glance_connection(sess, cloud["region"])
        if glance is False:
            logging.error("Failed to get openstack glance connection")
            return False
 
        file_path = scratch_dir
        if image_checksum:
            file_path = scratch_dir + image_name + "---" + image_checksum
        image = glance.upload_image(name=image_name, disk_format=disk_format, container_format=container_format, data=open(file_path, 'rb'))
        logging.info("Image upload complete")
        return glance.get_image(image.id)
    except Exception as exc:
        logging.error("Image upload failed: %s" % exc)
        return False

# Download an image from the repo, returns True if successful or False if not
def download_image(cloud, image_name, image_id, image_checksum, scratch_dir):
    #open file then write to it
    try:
        sess = get_openstack_sess(cloud, config.categories["openstackPoller.py"]["cacerts"])
        if sess is False:
            return (False, "Failed to get openstack session", "", "")
        glance = get_glance_connection(sess, cloud["region"])
        if glance is False:
            return (False, "Failed to get openstack glance connection", "", "")
        
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
        file_path = scratch_dir + image_name + "---" + image_checksum
        
        glance.download_image(image_id, output=file_path)
        img = glance.get_image(image_id)
 
        return (True, "Success", img.disk_format, img.container_format)
    except Exception as exc:
        return (False, exc, "", "")

#def delete_image(glance, image_id):
def delete_image(cloud, image_id):
    try:
        sess = get_openstack_sess(cloud, config.categories["openstackPoller.py"]["cacerts"])
        if sess is False:
            return (1, "Failed to get openstack session")
        glance = get_glance_connection(sess, cloud["region"])
        if glance is False:
            return (1, "Failed to get openstack glance connection")

        glance.delete_image(image_id)
    except Exception as exc:
        logging.error("Unknown error, unable to delete image")
        logging.error(exc)
        return (1, exc)
    return (0,)


"""
def update_image_name(glance, image_id, image_name):
    #glance.images.update(image_id, name=image_name)
    glance.update_image(image_id, name=image_name)


def get_checksum(glance, image_id):
    #image = glance.images.get(image_id)
    image = glance.get_images(image_id)
    return image['checksum']
"""

#
# Check image cache and queue up a pull request if target image is not present
#
def check_cache(config, image_name, image_checksum, group_name, user, target_image=None, return_image=False):
    IMAGE_CACHE = "csv2_image_cache"
    if isinstance(user, str):
        username = user
    else:
        username = user.username

    if image_checksum is not None:
        where_clause = "image_name='%s' and checksum='%s'" % (image_name, image_checksum)
        rc, qmsg, image = config.db_query(IMAGE_CACHE, where=where_clause)
    else:
        where_clause = "image_name='%s' and checksum='%s'" % (image_name, image_checksum)
        rc, qmsg, image = config.db_query(IMAGE_CACHE, where=where_clause)

    if len(image) > 0:
        # we found something in the cache we can skip queueing a pull request
        if return_image:
            return image[0]
        return True
    else:
        from .celery_app import pull_request
        logging.info("No image n cache, getting target image for pull request")
        # nothing in the cache lets queue up a pull request
        if target_image is None:
            target_image = get_image(config, image_name, image_checksum, group_name)
            if target_image is False:
                # unable to find target image
                logging.info("Unable to find target image")
                if return_image:
                    return None
                return False #maybe raise an error here
            tx_id =  generate_tx_id()
            preq = {
                "tx_id": tx_id,
                "target_group_name": target_image["group_name"],
                "target_cloud_name": target_image["cloud_name"],
                "image_name": image_name,
                "image_id": target_image["id"],
                "checksum": target_image["checksum"],
                "status": "pending",
                "requester": username,
            }
        else:
            tx_id =  generate_tx_id()
            preq = {
                "tx_id": tx_id,
                "target_group_name": target_image["group_name"],
                "target_cloud_name": target_image["cloud_name"],
                "image_name": image_name,
                "image_id": target_image["id"],
                "checksum": target_image["checksum"],
                "status": "pending",
                "requester": username,
            }

        PULL_REQ = "csv2_image_pull_requests"
        # check if a pull request already exists for this image? or just let the workers sort it out?
        config.db_merge(PULL_REQ, preq)
        config.db_commit()
        #pull_request.delay(tx_id = tx_id)
        pull_request.apply_async((tx_id,), queue='pull_requests')

        if return_image:
            return None
        return True


#
def get_image(config, image_name, image_checksum, group_name, cloud_name=None):
    IMAGES = "cloud_images"
    if cloud_name is None:
        #getting a source image
        logging.info("Looking for image %s, checksum: %s in group %s" % (image_name, image_checksum, group_name))
        if image_checksum is not None:
            where_clause = "group_name='%s' and name='%s' and checksum='%s'" % (group_name, image_name, image_checksum)
            rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
        else:
            where_clause = "group_name='%s' and name='%s'" % (group_name, image_name)
            rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
        if len(image_candidates) > 0:
            return image_candidates[0]
        else:
            #No image that fits specs
            return False
    else:
        #getting a specific image
        logging.debug("Retrieving image %s" % image_name)
        where_clause = "group_name='%s' and cloud_name='%s' and name='%s' and checksum='%s'" % (group_name, cloud_name, image_name, image_checksum)
        rc, msg, image_candidates = config.db_query(IMAGES, where=where_clause)
        if len(image_candidates) > 0:
            return image_candidates[0]
        else:
            #No image that fits specs
            return False


# at a length of 16 with a 92 symbol alphabet we have a N/16^92 chance of a collision, pretty darn unlikely
def generate_tx_id(length=16):
    return ''.join(random.choice(ALPHABET) for i in range(length)) 

