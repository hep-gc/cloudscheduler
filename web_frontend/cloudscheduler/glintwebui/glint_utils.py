import time
from ast import literal_eval
import json
import redis
import logging


import glintwebui.config as config

from .keypair_utils import get_keypair, delete_keypair, transfer_keypair, create_keypair, create_new_keypair


logger = logging.getLogger('glintv2')



def get_num_transactions():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    num_tx = red.get("num_transactions")
    if num_tx is None:
        num_tx = 0
        red.set("num_transactions", num_tx)
    if int(num_tx) < 0:
        num_tx = 0
        red.set("num_transactions", num_tx)
    return int(num_tx)



# This function accepts account name, a list of cloud names and an image name
# Using the image dictionary it checks the provided clouds for the given image name
# It returns a list of cloud names where the image was found, if none were found it returns empty list
def check_for_existing_images(group_name, cloud_name_list, image_name):
    json_dict = get_images_for_group(group_name)
    image_dict = json.loads(json_dict)

    image_found_cloud_name = list()

    for cloud in cloud_name_list:
        for image in image_dict[cloud]:
            if image_dict[cloud][image]['name'] == image_name:
                image_found_cloud_name.append(cloud)

    return image_found_cloud_name



def increment_transactions():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.incr("num_transactions", 1)
    return True


# This function checks the cache for a local copy of a given image file
# if found it updates the timestamp and returns the filepath
# Tuple format: (image_name, image_checksum, full_path, current_time)
def check_cached_images(image_name, image_checksum):
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    cache_tuple_list = red.lrange("glint_img_cache", 0, -1)

    for img_tuple in cache_tuple_list:
        img_tuple = literal_eval(str(img_tuple))
        if image_name == str(img_tuple[0]) and image_checksum == str(img_tuple[1]):
            #update entry and return path
            red.lrem("glint_img_cache", 0, str(img_tuple))
            new_tuple = (img_tuple[0], img_tuple[1], img_tuple[2], int(time.time()))
            red.rpush("glint_img_cache", new_tuple)
            return img_tuple[2]

    return None


# This function accepts info to uniquely identify an image as well as
# the local location of the image such that the image can be used for
# download or a transfer without having to download the image again.
# Tuple format: (image_name, image_checksum, full_path, current_time)
def add_cached_image(image_name, image_checksum, full_path):
    current_time = int(time.time())
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    img_tuple = (image_name, image_checksum, full_path, current_time)
    red.rpush("glint_img_cache", img_tuple)
    return False


# This function accepts a project and an image name and looks through the image
# dictionary until it finds a match where state='present' and returns a tuple of
# (auth_url, tenant, username, password, img_id)
def find_image_by_name(group_name, image_name):
    from django.conf import settings
    db_config = settings.CSV2_CONFIG
    
    # setup database objects
    db_config.db_open()
    session = db_config.db_session
    Group_Resources = db_config.db_map.classes.csv2_clouds

    image_dict = json.loads(get_images_for_group(group_name))
    for cloud in image_dict:
        for image in image_dict[cloud]:
            if image_dict[cloud][image]['name'] == image_name:
                #if image_dict[cloud][image]['state'] == 'Present' and image_dict[cloud][image]['hidden'] is False:
                if image_dict[cloud][image]['state'] == 'Present':
                    repo_obj = session.query(Group_Resources).filter(Group_Resources.group_name == group_name, Group_Resources.cloud_name == cloud).first()
                    db_config.db_close()
                    return (repo_obj.authurl, repo_obj.project, repo_obj.username,\
                        repo_obj.password, image, image_dict[cloud][image]['checksum'],\
                        repo_obj.user_domain_name, repo_obj.project_domain_name)
    db_config.db_close()
    return False



def repo_modified():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.incr("repos_modified")
    return True


# accepts image dictionary and returns a dictionary that inverses the format to
# repo1{
#    img_name: img_key
#   ...
#}
# repo2{
#    img_name: img_key
#   ...
#}
def build_id_lookup_dict(image_dict):
    reverse_dict = {}
    for repo in image_dict:
        reversed_repo = {}
        for image in image_dict[repo]:
            reversed_repo[image_dict[repo][image]['name']] = image
        reverse_dict[repo] = reversed_repo
    return reverse_dict


def parse_pending_transactions(group_name, cloud_name, image_list, user):
    try:
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        proj_dict = json.loads(red.get(group_name))
        repo_dict = proj_dict[cloud_name]

        # This function takes a repo dictionary and returns a dictionary that has the format:
        # image_name: image_id
        # This is needed since we are now using image name as the unique identifier not the img id
        img_translation = __get_image_ids(repo_dict)

        for image in image_list:
            # If image is not in the image list we need to make a pending transfer
            if not img_translation.get(image, False):
                # MAKE TRANSFER
                # We need to get disk_format and container_format
                # from another repo that has this image
                img_details = __get_image_details(group_name=group_name, image=image)
                disk_format = img_details[0]
                container_format = img_details[1]
                transaction = {
                    'user': user,
                    'action': 'transfer',
                    'group_name': group_name,
                    'cloud_name': cloud_name,
                    'image_name': image,
                    'disk_format': disk_format,
                    'container_format': container_format
                }
                trans_key = group_name + "_pending_transactions"
                red.rpush(trans_key, json.dumps(transaction))
                increment_transactions()
            #else it is already there and do nothing
            else:
                pass

        # Now we need to check deletes
        for image_key in repo_dict:
            #If the key exists but it isn't in the image list make a pending delete unless it is hidden
            if repo_dict[image_key]['name'] not in image_list and repo_dict[image_key]['hidden'] is False:
                # if its pending already we don't need to touch it
                if repo_dict[image_key].get('state') not in {'Pending Delete', 'Pending Transfer'}:
                    # MAKE DELETE
                    transaction = {
                        'user': user,
                        'action':  'delete',
                        'group_name': group_name,
                        'cloud_name': cloud_name,
                        'image_id': image_key,
                        'image_name': repo_dict[image_key].get('name')
                    }
                    trans_key = group_name + "_pending_transactions"
                    red.rpush(trans_key, json.dumps(transaction))
                    increment_transactions()

    except KeyError as exc:
        logger.error(exc)
        logger.error("Couldnt find image list for group %s", group_name)
        return False


# returns a jsonified python dictionary containing the image list for a given project
# If the image list doesn't exist in redis it returns False
# Redis info should be moved to a config file
def get_images_for_group(group_name):
    try:
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        return red.get(group_name)
    except KeyError:
        logger.error("Couldnt find image list for group %s", group_name)
        return False


# Returns a unique list of (image, name) tuples that are not hidden in glint
# May be a problem if two sites have the same image (id) but with different names
# as the tuple will no longer be unique
def get_unique_image_list(group_name):
    image_dict = json.loads(get_images_for_group(group_name))
    image_set = set()
    # make a dictionary of all the images in the format key:value = image_id:list_of_repos
    # start by making a list of the keys, using a set will keep them unique
    for repo_key in image_dict:
        for image_id in image_dict[repo_key]:
#            if not image_dict[repo_key][image_id]['hidden']:
            image_set.add(image_dict[repo_key][image_id]['name'])
    return sorted(image_set, key=lambda s: s.lower())




