# glint utils

import logging
import os
import string
import random

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
import glanceclient



from cloudscheduler.lib.db_config_na import Config
config = Config('/etc/cloudscheduler/cloudscheduler.yaml', ['general', 'openstackPoller.py', 'web_frontend'], pool_size=2, max_overflow=10)
ALPHABET = string.ascii_letters + string.digits + string.punctuation

def get_nova_client(session, region=None):
    nova = novaclient.Client("2", session=session, region_name=region, timeout=10)
    return nova

def get_glance_client(session, region=None):
    glance = glanceclient.Client("2", session=session, region_name=region)
    return glance

def get_openstack_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.debug("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
    if version == 2:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project)
    else:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project,
            user_domain=cloud.user_domain_name,
            project_domain_name=cloud.project_domain_name,
            project_domain_id=cloud.project_domain_id,)
    if session is False:
        logging.error("Failed to setup session, skipping %s", cloud.cloud_name)
        if version == 2:
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s",
                          (cloud.authurl, cloud.username, cloud.project))
        else:
            logging.error(
                "Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s",
                (cloud.authurl, cloud.username, cloud.project, cloud.user_domain, cloud.project_domain_name))
    return session

def _get_openstack_session_v1_v2(auth_url, username, password, project, user_domain="Default", project_domain_name="Default",
                                 project_domain_id=None):
    authsplit = auth_url.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.debug("Bad openstack URL: %s, could not determine version, aborting session", auth_url)
        return False
    if version == 2:
        try:
            auth = v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project)
            sess = session.Session(auth=auth, verify=config.categories["openstackPoller.py"]["cacerts"])
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s::%s" % (auth_url, exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
            return False
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project,
                user_domain_name=user_domain,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,)
            sess = session.Session(auth=auth, verify=config.categories["openstackPoller.py"]["cacerts"])
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess




# new glint api, maybe make this part of glint utils?

def create_placeholder_image(glance, image_name, disk_format, container_format):
    image = glance.images.create(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format)
    return image.id


# Upload an image to repo, returns image id if successful
# if there is no image_id it is a direct upload and no placeholder exists
def upload_image(glance, image_id, image_name, scratch_dir, image_checksum=None, disk_format=None, container_format="bare"):
    if image_id is not None:
        #this is the 2nd part of a transfer not a direct upload
        file_path = scratch_dir + image_name + "---" + image_checksum
        glance.images.upload(image_id, open(file_path, 'rb'))
        return glance.images.get(image_id)

    else:
        #this is a straight upload not part of a transfer
        image = glance.images.create(
            name=image_name,
            disk_format=disk_format,
            container_format=container_format)
        glance.images.upload(image.id, open(scratch_dir, 'rb'))
        logging.info("Upload complete")
        return glance.images.get(image.id) 


# Download an image from the repo, returns True if successful or False if not
def download_image(glance, image_name, image_id, image_checksum, scratch_dir):
    #open file then write to it
    try:
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
        file_path = scratch_dir + image_name + "---" + image_checksum
        image_file = open(file_path, 'wb')
        for chunk in glance.images.data(image_id):
            image_file.write(bytes(chunk))
        img = glance.images.get(image_id)

        return (True, "Success", img.disk_format, img.container_format)
    except Exception as exc:
        return (False, exc, "", "")

def delete_image(glance, image_id):
    try:
        glance.images.delete(image_id)
    except Exception as exc:
        logging.error("Unknown error, unable to delete image")
        logging.error(exc)
        return (1, exc)
    return (0,)


def update_image_name(glance, image_id, image_name):
    glance.images.update(image_id, name=image_name)


def get_checksum(glance, image_id):
    image = glance.images.get(image_id)
    return image['checksum']

#
# Check image cache and queue up a pull request if target image is not present
#
def check_cache(config, image_name, image_checksum, group_name, user, target_image=None):
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

    if image.count() > 0:
        # we found something in the cache we can skip queueing a pull request
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

        return True


#
#
#
def get_image(config, image_name, image_checksum, group_name, cloud_name=None):
    IMAGES = "cloud_images"
    if cloud_name is None:
        #getting a source image
        logging.info("Looking for image %s, checksum: %s in group %s" % (image_name, image_checksum, group_name))
        if image_checksum is not None:
            where_clause = "group_name='%s' and image_name='%s' and checksum='%s'" % (group_name, image_name, image_checksum)
            rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
        else:
            where_clause = "group_name='%s' and image_name='%s'" % (group_name, image_name)
            rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
        if image_candidates.count() > 0:
            return image_candidates[0]
        else:
            #No image that fits specs
            return False
    else:
        #getting a specific image
        logging.debug("Retrieving image %s" % image_name)
        where_clause = "group_name='%s' and cloud_name='%s' and name='%s' and checksum='%s'" % (group_name, cloud_name, image_name, image_checksum)
        image_candidates = config.db_query(IMAGES, where=where_clause)
        if image_candidates.count() > 0:
            return image_candidates[0]
        else:
            #No image that fits specs
            return False


# at a length of 16 with a 94 symbol alphabet we have a N/16^94 chance of a collision, pretty darn unlikely
def generate_tx_id(length=16):
    return ''.join(random.choice(ALPHABET) for i in range(length)) 

def delete_keypair(key_name, cloud):
    sess = get_openstack_session(cloud)
    nova = get_nova_client(sess, cloud.region)

    keys = nova.keypairs.list()
    for key in keys:
        if key.name == key_name:
            nova.keypairs.delete(key)
            return True

    return False

def get_keypair(key_name, cloud):
    sess = get_openstack_session(cloud)
    nova = get_nova_client(sess, cloud.region)

    keys = nova.keypairs.list()
    for key in keys:
        if key.name == key_name:
            return key
    return None

def transfer_keypair(keypair, cloud):
    sess = get_openstack_session(cloud)
    nova = get_nova_client(sess, cloud.region)

    nova.keypairs.create(name=keypair.name, public_key=keypair.public_key)
    return True

def create_keypair(key_name, key_string, cloud):
    sess = get_openstack_session(cloud)
    nova = get_nova_client(sess, cloud.region)

    try:
        new_key = nova.keypairs.create(name=key_name, public_key=key_string)
    except Exception as exc:
        raise
    return new_key


def create_new_keypair(key_name, cloud):
    sess = get_openstack_session(cloud)
    nova = get_nova_client(sess, cloud.region)

    try:
        new_key = nova.keypairs.create(name=key_name)
    except Exception as exc:
        raise
    return new_key

def getUser(request, db_config):
    user = request.META.get('REMOTE_USER')
    Glint_User = "csv2_user"
    rc, qmsg, auth_user_list = db_config.db_query(Glint_User)
    for auth_user in auth_user_list:
        if user == auth_user["cert_cn"] or user == auth_user["username"]:
            return auth_user

def verifyUser(request, db_config):
    auth_user = getUser(request, db_config)
    return bool(auth_user)


