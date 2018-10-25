import os
import time
import logging
from ast import literal_eval
import json
import redis
from glintwebui.glint_api import repo_connector
import glintwebui.config as config
from .db_util import get_db_base_and_session

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient


logger = logging.getLogger('glintv2')

# Recieves a tuple of 3-tuples (repo, img_name, img_id) that uniquely identify an image_list
# then sorts them based on their repo and returns them in a json dictionary string
#Format:
#Proj_dict{
#    Repo1Alias{
#        Img_ID1{
#            name
#            state
#            disk_format
#            container_format
#            visibility
#            checksum
#            hidden
#        }
#        Img_ID2{
#            name
#            state
#            disk_format
#            container_format
#            visibility
#            checksum
#            hidden
#        }
#        .
#        .
#        .
#        Img_IDX{
#            name
#            state
#            disk_format
#            container_format
#            visibility
#            checksum
#            hidden
#        }
#    }
#    Repo2Alias{
#    ...
#    }
#    .
#    .
#    .
#    RepoXAlias{
#    ...
#    }
#}

def jsonify_image_list(image_list, repo_list):
    #take img list and sort it into repos
    repo_dict = {}
    # Build repo_dict
    for repo in repo_list:
        img_dict = {}
        for image in image_list:
            if image[0] == repo.project and image[7] == repo.cloud_name:
                img = {}
                img['name'] = image[1]
                img['state'] = 'Present'
                img['disk_format'] = image[3]
                img['container_format'] = image[4]
                img['visibility'] = image[5]
                img['checksum'] = image[6]
                img_dict[image[2]] = img
                if img['visibility'] == "private":
                    img['hidden'] = False
                elif img['visibility'] == "shared":
                    img['hidden'] = False
                else:
                    img['hidden'] = True

        repo_dict[repo.cloud_name] = img_dict
    return json.dumps(repo_dict)


# This function will accept 2 json string dictionaries and find the pending transactions
# from the first and add them to the second then check the queue for any state changes
# apply those final updates and finally return a jsonified dictstring
#
# This function changed significantly when we started using the image name as the unique identifier
# which changed the way the state changes are handled, We can no longer change intuitively change
# the states here based on the information of the two dictionaries. State changes are now handled
# in a seperate function that reads from a queue ()
#
def update_pending_transactions(old_img_dict, new_img_dict):
    #on startup there wont be an old dict
    try:
        old_dict = json.loads(old_img_dict)
    except TypeError:
        logger.info("No old image dictionary, either bad redis entry or first call since startup")
        return new_img_dict
    new_dict = json.loads(new_img_dict)

    for repo_key in old_dict:
        if repo_key not in new_dict:
            #cloud has been removed, we can ignore it
            continue
        repo_dict = old_dict[repo_key]
        for img_key in repo_dict:
            #if a pending one is found, check for it in the new list
            if repo_dict[img_key]['state'] in {"Pending Transfer", "Pending Delete"}:
                try:
                    # if it was a pending transfer change the state to pending:
                    if repo_dict[img_key]['state'] == "Pending Transfer":
                        new_dict[repo_key][img_key]['state'] = "Pending Transfer"
                    # OR if it was pending a delete and it still exists: state -> Pending Delete
                    if repo_dict[img_key]['state'] == "Pending Delete":
                        new_dict[repo_key][img_key]['state'] = "Pending Delete"
                except KeyError:
                    #Doesn't exist in the new one yet
                    # if it was a pending delete
                    if repo_dict[img_key]['state'] == "Pending Delete":
                        new_dict[repo_key][img_key] = repo_dict[img_key]
                    # if it was a pending transfer and it still doesnt exist: add as Pending Xfer
                    if repo_dict[img_key]['state'] == "Pending Transfer":
                        new_dict[repo_key][img_key] = repo_dict[img_key]

            # we also need to check for changes in the hidden status of images
            # the simple way is to just assign the old value to the new dict
            # however if the image is newly created it won't yet have a hidden attribute
            # new images will always be private and recieve "False" for the hidden attribute
            try:
                new_dict[repo_key][img_key]['hidden'] = repo_dict[img_key]['hidden']
            except:
                # need a try block here incase we get here when an image was deleted
                # faster than we could provide the state change. It will be gone already
                # so we can just ignore it and not worry about adding to the dictionary
                try:
                    new_dict[repo_key][img_key]['hidden'] = False
                except:
                    pass

    return json.dumps(new_dict)

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

# accepts a project as key string and a jsonified dictionary of the images and stores them in redis
# Redis info should be moved to a config file
def set_images_for_group(group_name, json_img_dict):
    try:
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        red.set(group_name, json_img_dict)

    except Exception:
        logger.error("Unknown exception while trying to set images for: %s", group_name)


# returns dictionary containing any conflicts for a given account name
def get_conflicts_for_group(group_name):
    if group_name is None:
        logger.info("Couldnt find conflict list; no group provided.")
        return None
    try:
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        conflict_key = group_name + "_conflicts"
        json_conflict_dict = red.get(conflict_key)
        if json_conflict_dict is not None:
            return json.loads(json_conflict_dict)
        else:
            return None
    except KeyError:
        logger.info("Couldnt find conflict list for group %s", group_name)
        return None

def set_conflicts_for_group(group_name, conflict_dict):
    try:
        json_conflict_dict = json.dumps(conflict_dict)
        conflict_key = group_name + "_conflicts"
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        red.set(conflict_key, json_conflict_dict)

    except Exception:
        logger.error("Unknown exception while trying to set conflicts for: %s", group_name)


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


# similar to "get_unique_image_list", this function returns a set of tuples
# representing all the images in glint such that their hidden status can be toggled
def get_hidden_image_list(group_name):
    image_dict = json.loads(get_images_for_group(group_name))
    image_set = set()
    # make a dictionary of all the images in the format key:value = image_id:list_of_repos
    # start by making a list of the keys, using a set will keep them unique
    for repo_key in image_dict:
        for image_id in image_dict[repo_key]:
            image_set.add(image_dict[repo_key][image_id]['name'])
    return sorted(image_set, key=lambda s: s.lower())


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


# Accepts the image dictionary and checks if there are any repos that contain conflicts
#
#   Type 1 - Image1 and Image2 have the same name but are different images.
#   Type 2 - Image1 and Image2 have the same name and are the same image.
#   Type 3 - Image1 and Image2 have different names but are the same image.

def check_for_image_conflicts(json_img_dict):
    image_dict = json.loads(json_img_dict)
    conflicts_dict = {}
    for repo in image_dict:
        conflicts = list()
        for image in image_dict[repo]:
            if image_dict[repo][image]['checksum'] == "No Checksum":
                continue
            for image2 in image_dict[repo]:
                if image_dict[repo][image2]['checksum'] == "No Checksum":
                    continue
                if image is not image2:
                    try:
                        #Check for name conflicts (type 1/type 2)
                        if image_dict[repo][image]['name'] == image_dict[repo][image2]['name']:
                            # Mayday we have a duplicate
                            # check if it is type 1 or type 2 conflint

                            if image_dict[repo][image]['checksum'] == image_dict[repo][image2]['checksum']:
                                logging.error("Type 2 image conflict detected.")
                                # Type 2
                                conflict = {
                                    'type': 2,
                                    'image_one': image,
                                    'image_one_name': image_dict[repo][image]['name'],
                                    'image_one_visibility': image_dict[repo][image]['visibility'],
                                    'image_two': image2,
                                    'image_two_name': image_dict[repo][image2]['name'],
                                    'image_two_visibility': image_dict[repo][image2]['visibility']
                                }
                                duplicate_entry = False
                                for entry in conflicts:
                                    if entry['image_one'] == conflict['image_two'] and entry['image_two'] == conflict['image_one']:
                                        duplicate_entry = True
                                        break
                                if not duplicate_entry:
                                    conflicts.append(conflict)

                            else:
                                logging.error("Type 1 image conflict detected.")
                                # Type 1
                                conflict = {
                                    'type': 1,
                                    'image_one': image,
                                    'image_one_name': image_dict[repo][image]['name'],
                                    'image_one_visibility': image_dict[repo][image]['visibility'],
                                    'image_two': image2,
                                    'image_two_name': image_dict[repo][image2]['name'],
                                    'image_two_visibility': image_dict[repo][image2]['visibility']
                                }
                                duplicate_entry = False
                                for entry in conflicts:
                                    if entry['image_one'] == conflict['image_two'] and entry['image_two'] == conflict['image_one']:
                                        duplicate_entry = True
                                        break
                                if not duplicate_entry:
                                    conflicts.append(conflict)

                        # Check for checksum conflicts
                        # (type 3, since type 2 will be caught by the first check)
                        if image_dict[repo][image]['checksum'] == image_dict[repo][image2]['checksum']:
                            logging.error("Type 3 image conflict detected.")
                            # Type 3
                            conflict = {
                                'type': 3,
                                'image_one': image,
                                'image_one_name': image_dict[repo][image]['name'],
                                'image_one_visibility': image_dict[repo][image]['visibility'],
                                'image_two': image2,
                                'image_two_name': image_dict[repo][image2]['name'],
                                'image_two_visibility': image_dict[repo][image2]['visibility']
                            }
                            duplicate_entry = False
                            for entry in conflicts:
                                if entry['image_one'] == conflict['image_two'] and entry['image_two'] == conflict['image_one']:
                                    duplicate_entry = True
                                    break
                            if not duplicate_entry:
                                conflicts.append(conflict)
                    except Exception as exc:
                        logger.error("Error when checking for conflicts on images: %s and %s",\
                            image, image2)
                        logger.error(exc)
                        logger.error(image_dict)
        if conflicts:
            conflicts_dict[repo] = conflicts


    if conflicts_dict:
        return conflicts_dict
    else:
        return None

# Accepts a list of images (names), a project and a repo
# Cross references the image repo in redis against the given image list
# Either returns a list of transactions or posts them to redis to be
# picked up by another thread.
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


# This function reads pending transactions from a redis queue and spawns celery
# tasks to perform the file transfers. Since our repo dictionaries are using the
# uuid as the image key we need to connect to the repo and create a placeholder
# image and retrieve the img id (uuid) to use as the repo image key
# Then finally we can call the asynch celery tasks
def process_pending_transactions(group_name, json_img_dict):
    from .celery_app import transfer_image, delete_image, upload_image

    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    trans_key = group_name + '_pending_transactions'
    img_dict = json.loads(json_img_dict)

    # seems like there is no assignment in while conditionals for python
    # so We will have to be smart and use break
    while True:
        # setup database objects
        Base, session = get_db_base_and_session()
        Group_Resources = Base.classes.csv2_group_resources
        trans = red.lpop(trans_key)
        if trans is None:
            break
        transaction = json.loads(trans)
        # Update global dict and create transfer or delete task
        if transaction['action'] == 'transfer':
            # First we need to create a placeholder img and get the new image_id
            # This may cause an error if the same repo is added twice, perhaps we
            # can screen for this when repos are added
            repo_obj = session.query(Group_Resources).filter(Group_Resources.group_name == transaction['group_name'], Group_Resources.cloud_name == transaction['cloud_name']).first()


            rcon = repo_connector(
                auth_url=repo_obj.authurl,
                project=repo_obj.project,
                username=repo_obj.username,
                password=repo_obj.password,
                user_domain_name=repo_obj.user_domain_name,
                project_domain_name=repo_obj.project_domain_name)
            new_img_id = rcon.create_placeholder_image(
                transaction['image_name'],
                transaction['disk_format'],
                transaction['container_format'])
            # Make a new img dict
            new_img_dict = {
                'name': transaction['image_name'],
                'state': 'Pending Transfer',
                'disk_format': transaction['disk_format'],
                'container_format': transaction['container_format'],
                'checksum': "No Checksum"
            }
            img_dict[transaction['cloud_name']][new_img_id] = new_img_dict

            # queue transfer task
            transfer_image.delay(
                image_name=transaction['image_name'],
                image_id=new_img_id,
                group_name=group_name,
                auth_url=repo_obj.authurl,
                project_tenant=repo_obj.project,
                username=repo_obj.username,
                password=repo_obj.password,
                requesting_user=transaction['user'],
                cloud_name=repo_obj.cloud_name,
                user_domain_name=repo_obj.user_domain_name,
                project_domain_name=repo_obj.project_domain_name)

        elif transaction['action'] == 'delete':
            # First check if it exists in the redis dictionary, if it doesn't exist we can't delete it
            if img_dict[transaction['cloud_name']].get(transaction['image_id']) is not None:
                # Set state and queue delete task
                repo_obj = session.query(Group_Resources).filter(Group_Resources.group_name == transaction['group_name'], Group_Resources.cloud_name == transaction['cloud_name']).first()

                img_dict[transaction['cloud_name']][transaction['image_id']]['state'] = 'Pending Delete'
                delete_image.delay(
                    image_id=transaction['image_id'],
                    image_name=transaction['image_name'],
                    group_name=group_name,
                    auth_url=repo_obj.authurl,
                    project_tenant=repo_obj.project,
                    username=repo_obj.username,
                    password=repo_obj.password,
                    requesting_user=transaction['user'],
                    cloud_name=repo_obj.cloud_name,
                    user_domain_name=repo_obj.user_domain_name,
                    project_domain_name=repo_obj.project_domain_name)

        elif transaction['action'] == 'upload':
            req_user = transaction['user']
            img_name = transaction['image_name']
            image_path = transaction['local_path']
            disk_format = transaction['disk_format']
            container_format = transaction['container_format']
            repo_obj = session.query(Group_Resources).filter(Group_Resources.group_name == transaction['group_name'], Group_Resources.cloud_name == transaction['cloud_name']).first()
            upload_image.delay(
                image_name=img_name,
                image_path=image_path,
                auth_url=repo_obj.authurl,
                project_tenant=repo_obj.project,
                username=repo_obj.username,
                password=repo_obj.password,
                requesting_user=req_user,
                disk_format=disk_format,
                container_format=container_format,
                user_domain_name=repo_obj.user_domain_name,
                project_domain_name=repo_obj.project_domain_name)

    return json.dumps(img_dict)


# Accepts a list of images (names), a project and a repo
# Cross references the image repo in redis against the given image list
# to toggle the hidden status of images
def parse_hidden_images(group_name, cloud_name, image_list, user):
    try:
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        proj_dict = json.loads(red.get(group_name))
        repo_dict = proj_dict[cloud_name]

        #if the image isn't in the image_list, hidden=False
        for image_key in repo_dict:
            if repo_dict[image_key]['name'] not in image_list:
                if repo_dict[image_key]['hidden'] is True:
                    #queue state change for hidden status (set to False)
                    queue_state_change(
                        group_name,
                        cloud_name,
                        image_key,
                        repo_dict[image_key]['state'], False)
            else:
                # hidde should be true
                if repo_dict[image_key]['hidden'] is False:
                    #queue state change for hidden status (set to True)
                    queue_state_change(
                        group_name,
                        cloud_name,
                        image_key,
                        repo_dict[image_key]['state'], True)
    except:
        logger.error("Error occured when parsing hidden status of images.")
    return True

# Queues a state change in redis for the periodic task to perform
# Key will take the form of project_pending_state_changes
# and thus there will be a seperate queue for each project
def queue_state_change(group_name, cloud_name, img_id, state, hidden):
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    state_key = group_name + '_pending_state_changes'
    if hidden is not None:
        state_change = {
            'state': state,
            'image_id': img_id,
            'cloud_name':cloud_name,
            'hidden': hidden
        }
        increment_transactions()
    else:
        state_change = {
            'state': state,
            'image_id': img_id,
            'cloud_name':cloud_name,
        }
    red.rpush(state_key, json.dumps(state_change))
    return True



def process_state_changes(group_name, json_img_dict):
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    state_key = group_name + '_pending_state_changes'
    img_dict = json.loads(json_img_dict)
    while True:
        raw_state_change = red.lpop(state_key)
        if raw_state_change is None:
            break
        state_change = json.loads(raw_state_change)
        #check if it is a hidden state change or a image state change
        if 'hidden' in state_change:
            #hidden state change
            img_dict[state_change['cloud_name']][state_change['image_id']]['hidden'] = state_change['hidden']
            # only hidden state changes count as transactions since it is the only way to kick
            # the server out of dormant state to proccess the chagnes
            decrement_transactions()
        else:
            #image state change
            if state_change['state'] == "deleted":
                # Remove the key
                img_dict[state_change['cloud_name']].pop(state_change['image_id'], None)
            else:
                # Update the state
                img_dict[state_change['cloud_name']][state_change['image_id']]['state'] = state_change['state']

    return json.dumps(img_dict)

# This function accepts a project and an image name and looks through the image
# dictionary until it finds a match where state='present' and returns a tuple of
# (auth_url, tenant, username, password, img_id)
def find_image_by_name(group_name, image_name):
    # setup database objects
    Base, session = get_db_base_and_session()
    Group_Resources = Base.classes.csv2_group_resources

    image_dict = json.loads(get_images_for_group(group_name))
    for cloud in image_dict:
        for image in image_dict[cloud]:
            if image_dict[cloud][image]['name'] == image_name:
                #if image_dict[cloud][image]['state'] == 'Present' and image_dict[cloud][image]['hidden'] is False:
                if image_dict[cloud][image]['state'] == 'Present':
                    repo_obj = session.query(Group_Resources).filter(Group_Resources.group_name == group_name, Group_Resources.cloud_name == cloud).first()
                    return (repo_obj.authurl, repo_obj.project, repo_obj.username,\
                        repo_obj.password, image, image_dict[cloud][image]['checksum'],\
                        repo_obj.user_domain_name, repo_obj.project_domain_name)
    return False

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

# This function accepts a tuple representing an item in the cache and removes it from the list
def del_cached_image(img_tuple):
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.lrem("glint_img_cache", 0, str(img_tuple))
    return True

# This function checks the cache for a local copy of a given image file
# if found it updates the timestamp and returns the filepath
# Tuple format: (image_name, image_checksum, full_path, current_time)
def check_cached_images(image_name, image_checksum):
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    cache_tuple_list = red.lrange("glint_img_cache", 0, -1)

    for img_tuple in cache_tuple_list:
        img_tuple = literal_eval(img_tuple)
        if image_name == str(img_tuple[0]) and image_checksum == str(img_tuple[1]):
            #update entry and return path
            red.lrem("glint_img_cache", 0, str(img_tuple))
            new_tuple = (img_tuple[0], img_tuple[1], img_tuple[2], int(time.time()))
            red.rpush("glint_img_cache", new_tuple)
            return img_tuple[2]

    return None

# This function checks all the cache folders for files that aren't
# in the image cache and removes them
def do_cache_cleanup():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    cache_tuple_list = red.lrange("glint_img_cache", 0, -1)
    for x in range(0, 11):
        #this is to clean top level folder, range will need to be adjusted once it is configurable
        if x == 10:
            path = "/var/www/glintv2/scratch"
        else:
            path = "/var/www/glintv2/scratch/" + str(x)
        files = os.listdir(path)
        for f in files:
            #check if it is in cache
            file_found = False
            for cached_item in cache_tuple_list:
                cached_item = literal_eval(str(cached_item))
                if path + "/" + f == cached_item[2]:
                    #file in cache, break and go onto next file
                    file_found = True
                    break
            if not file_found:
                try:
                    os.remove(path + "/" + f)
                    logger.info("No cache entry found, removed: " + path + "/" + f)
                except OSError:
                    # Catch attempts to delete directories
                    pass

    # now that the initial cleanup is done we need to check for
    # any items in the cache that are missing locally
    # while we're at it let us check for any expiring items
    expire_time = config.cache_expire_time
    current_time = int(time.time())
    for cached_item in cache_tuple_list:
        cached_item = literal_eval(str(cached_item))
        if not os.path.exists(cached_item[2]):
            #file is missing, remove it from cache
            logger.error("Cached file missing at %s, removing cache entry.", cached_item[2])
            del_cached_image(cached_item)
        elif (int(current_time-cached_item[3])) > expire_time:
            #item has expired and remove it
            logger.info("Cached image %s has expired, removing from cache.", cached_item[0])
            os.remove(cached_item[2])
            del_cached_image(cached_item)

    return None

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


# Applys the delete rules and returns True if its ok to delete, False otherwise
# Rule 1: Can't delete a shared image
# Rule 2: Can't delete the last copy of an image.
def check_delete_restrictions(image_id, group_name, cloud_name):
    json_dict = get_images_for_group(group_name)
    image_dict = json.loads(json_dict)

    # Rule 1: check if image is shared
    if image_dict[cloud_name][image_id]['visibility'] is "public":
        return False

    # Rule 2: check if its the last copy of the image
    for repo in image_dict:
        if repo is not cloud_name:
            for image in image_dict[repo]:
                if image_dict[repo][image]['name'] is image_dict[cloud_name][image_id]['name']:
                    #found one, its ok to delete
                    return True

    return False

# This function checks if image collection has started so we don't accidentally queue
# multiple image collection jobs
def check_collection_task():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    state = red.get("collection_started")
    if state is None:
        return False
    elif state:
        return True
    else:
        return False

def set_collection_task(state):
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.set("collection_started", state)


#
#THESE FUNCTIONS ARE UNUSED BUT MAY BE USEFULL TO PROVIDE REAL TIME FEEDBACK ABOUT TRANSFERS
#
#def post_transfer_progress(key, progress):
#    r = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
#    r.set(key, progress)
#
#def get_transfer_progress(key):
#    r = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
#    progress = r.get(key)
#    return progress

def increment_transactions():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.incr("num_transactions", 1)
    return True

def decrement_transactions():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.decr("num_transactions", 1)
    return True

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

def repo_modified():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.incr("repos_modified")
    return True

def check_for_repo_changes():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    result = red.get("repos_modified")
    if result is None:
        return False
    elif int(result) > 0:
        return True
    else:
        return False

def repo_proccesed():
    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    red.set("repos_modified", 0)

def delete_keypair(key_name, cloud):
    sess = _get_keystone_session(cloud)
    nova = _get_nova_client(sess)

    keys = nova.keypairs.list()
    for key in keys:
        if key.name == key_name:
            nova.keypairs.delete(key)
            return True

    return False

def get_keypair(keypair_key, cloud):
    sess = _get_keystone_session(cloud)
    nova = _get_nova_client(sess)

    split_key = keypair_key.split(";")
    fingerprint = split_key[0]
    key_name = split_key[1]

    keys = nova.keypairs.list()
    for key in keys:
        if key.name == key_name:
            return key
    return None

def transfer_keypair(keypair, cloud):
    sess = _get_keystone_session(cloud)
    nova = _get_nova_client(sess)

    nova.keypairs.create(name=keypair.name, public_key=keypair.public_key)
    return True

def create_keypair(key_name, key_string, cloud):
    sess = _get_keystone_session(cloud)
    nova = _get_nova_client(sess)

    try:
        new_key = nova.keypairs.create(name=key_name, public_key=key_string)
    except Exception as exc:
        raise
    return new_key


def create_new_keypair(key_name, cloud):
    sess = _get_keystone_session(cloud)
    nova = _get_nova_client(sess)

    try:
        new_key = nova.keypairs.create(name=key_name)
    except Exception as exc:
        raise
    return new_key


def __get_image_ids(repo_dict):
    img_trans_dict = {}
    for image in repo_dict:
        img_trans_dict[repo_dict[image]['name']] = image

    return img_trans_dict

#Searches through the image dict until it finds this image and returns the disk/container formats
def __get_image_details(group_name, image):

    red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    proj_dict = json.loads(red.get(group_name))
    for repo in proj_dict:
        for img in proj_dict[repo]:
            if proj_dict[repo][img]['name'] == image:
                return (proj_dict[repo][img]['disk_format'], proj_dict[repo][img]['container_format'])


def _get_keystone_session(cloud):
    authsplit = cloud.authurl.split('/')
    version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))

    if version == 2:
        try:
            auth = v2.Password(
                auth_url=cloud.authurl,
                username=cloud.username,
                password=cloud.password,
                tenant_name=cloud.project)
            sess = session.Session(auth=auth, verify=config.cert_auth_bundle_path)
        except Exception as exc:
            print("Problem importing keystone modules, and getting session: %s" % exc)
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(
                auth_url=cloud.authurl,
                username=cloud.username,
                password=cloud.password,
                project_name=cloud.project,
                user_domain_name=cloud.user_domain_name,
                project_domain_name=cloud.project_domain_name)
            sess = session.Session(auth=auth, verify=config.cert_auth_bundle_path)
        except Exception as exc:
            print("Problem importing keystone modules, and getting session: %s" % exc)
        return sess

def _get_nova_client(session):
    nova = novaclient.Client("2", session=session)
    return nova
    
