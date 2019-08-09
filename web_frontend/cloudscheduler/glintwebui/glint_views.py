import json
import time
import logging
import os
import string
import random

from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from .glint_utils import get_openstack_session, get_glance_client, delete_image

from cloudscheduler.lib.view_utils import \
    render, \
    lno, \
    set_user_groups

from cloudscheduler.lib.web_profiler import silk_profile as silkp

logger = logging.getLogger('glintv2')
ALPHABET = string.ascii_letters + string.digits + string.punctuation
MODID = "IV"

# This dictionary is set up for the initial processing so we dont accidentally overwrite images with the same name
# after this dict has been generated it is again parsed into a dictionary of lists to make it easier to render in a django template
# Image Dictionary structure:
#
# img_name + "---" + checksum { 
#    name
#    cloud_nameX {
#        status
#        visibility(public/private/shared/pending)
#        img_id
#    }
#    cloud_nameY {
#        status
#        visibility(public/private/shared/pending)
#        img_id
#    }
#    .
#    .
#    .
# }
#    
# When rendering we can loop over the clouds for each fow:
# for image in image_dict:
#     for cloud in cloud_list:
#         #check if dict exists for cloud
#         if cloud not in image.keys():
#              #render image doesnt exist (ie xfer button)
#         elif image[cloud]['status'] == 'present':
#             # render image exists (ie delete button/visibility)
#         elif image[cloud]['status'] == 'pending transfer':
#              #render pending xfer
#         elif image[cloud]['status'] == 'pending delete':
#              #render pending delete
#         elif image[cloud]['status'] == 'error':
#              #render error message
#         else:
               # unknown state
#
#         
# Support Functions
#
def _build_image_dict(image_list, transaction_list):
    image_dict = {}
    for image in image_list:
        if image.name is None or image.checksum is None:
            # We don't like images without a name, lets ignore it
            continue
        if image.name + "---" + image.checksum not in image_dict.keys():
            #first time seeing this image, make a new entry
            new_dict = {
                "name": image.name,
                "checksum": image.checksum,
                image.cloud_name: {
                    "status": "present",
                    "visibility": image.visibility,
                    "id": image.id,
                    "message": ""
                }
            }
            image_dict[image.name + "---" + image.checksum] = new_dict
        else:
            #image already exits, just need to add the cloud name dict for this entry
            image_dict[image.name + "---" + image.checksum][image.cloud_name] = {
                "status": "present",
                "visibility": image.visibility,
                "id": image.id,
                "message": ""
            }

    # now that we have a complete picture of the images in the database we need to add the transaction data for pending image transfers
    for tx in transaction_list:
        if tx.image_name + "---" + tx.checksum not in image_dict.keys():
            # this shouldnt be possible since the image must exist to be transfered
            # only way you could end up here is if multiple deletes were queued on the same image or the image was deleted while this transaction was queued
            # ignore fore now
            continue
        else:
            # update relevent cloud dict
            if tx.target_cloud_name not in image_dict[tx.image_name + "---" + tx.checksum].keys():
                # make a new dict for it, probably a transfer request, or an upload
                image_dict[tx.image_name + "---" + tx.checksum][tx.target_cloud_name] = {
                    "status": tx.status,
                    "visibility": "pending",
                    "id": tx.image_id,
                    "message": tx.message
                }
            else:
                # the image exists already, probably the result of multiple queue'd transfers
                # we can probably ignore this case but may want to keep whatever status/message from the tx table
                continue
    return image_dict


# The image matrix will be a dinctionary with each value being a list of tuples where the order of the tuples is the order of clouds:
# matrix[image_name+checksum] = ((status1, message1, visibility1),(status2, message2, visibility2)....(statusN, messageN, visibilityN))
def _build_image_matrix(image_dict, cloud_list):
    image_matrix = {}

    for image_key in image_dict:
        row_list = []
        for cloud in cloud_list:
            logger.info("cloud: %s \nkeys: %s" % (cloud.cloud_name, image_dict[image_key].keys()))
            if cloud.cloud_name in image_dict[image_key].keys():
                #image is here
                row_list.append((image_dict[image_key][cloud.cloud_name]["status"],image_dict[image_key][cloud.cloud_name]["message"],image_dict[image_key][cloud.cloud_name]["visibility"], cloud.cloud_name))
            else:
                #image is not here
                row_list.append(("missing","","",cloud.cloud_name))
        image_matrix[image_key] = row_list


    return image_matrix


# at a length of 16 with a 94 symbol alphabet we have a N/16^94 chance of a collision, pretty darn unlikely
def _generate_tx_id(length=16):
    return ''.join(random.choice(ALPHABET) for i in range(length)) 


# Checks if the image already exists for target cloud, and if it doesnt it also checks that this
#   transfer request doesn't already exist (and isn't in an error state)
# returns true if image exists or a pull request is already queued and false if
#    the image exists at target location
def _check_image(config, target_group, target_cloud, image_name, image_checksum):
    logger.debug("Checking for image: %s on target cloud: %s" % (image_name, target_cloud))
    db_session = config.db_session
    IMAGES = config.db_map.classes.cloud_images
    IMAGE_TX = config.db_map.classes.csv2_image_transactions

    images = None
    #Check target cloud for image
    if image_checksum is not None:
        images = db_session.query(IMAGES).filter(IMAGES.cloud_name == target_cloud, IMAGES.group_name == target_group, IMAGES.name == image_name, IMAGES.checksum == image_checksum)
    else:
        images = db_session.query(IMAGES).filter(IMAGES.cloud_name == target_cloud, IMAGES.group_name == target_group, IMAGES.name == image_name)
    if images.count() != 0:
        return False # found the image so we don't need to transfer it


    #now we need to check if a transfer request exists
    logger.debug("Checking for image: %s in queued transfer requests" % image_name)
    if image_checksum is not None:
        images = db_session.query(IMAGE_TX).filter(IMAGE_TX.target_cloud_name == target_cloud, IMAGE_TX.target_group_name == target_group, IMAGE_TX.image_name == image_name, IMAGE_TX.checksum == image_checksum)
    else:
        images = db_session.query(IMAGE_TX).filter(IMAGE_TX.target_cloud_name == target_cloud, IMAGE_TX.target_group_name == target_group, IMAGE_TX.image_name == image_name)
    if images.count() != 0:
        # there is a row, lets check the status and there might be multiple rows if no checksum was provided
        for image_trans in images:
            if  "pending" in image_trans.status or "claimed" in image_trans.status:
                # Transfer already requested
                return False

    # If we get here we never found it in the image list or transaction list so we can go ahead with the xfer
    return True
    

#
#
#
def _get_image(config, image_name, image_checksum, group_name):
    IMAGES = config.db_map.classes.cloud_images
    db_session = config.db_session
    if image_checksum is not None:
        image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == group_name, IMAGES.name == image_name, IMAGES.checksum == image_checksum)
    else:
        image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == group_name, IMAGES.name == image_name)
    if image_candidates.count() > 1:
        return image_candidates[0]
    else:
        #No image that fits specs
        return False

#
# Check image cache and queue up a pull request if target image is not present
#
def _check_cache(config, image_name, image_checksum, group_name, user):
    IMAGE_CACHE = config.db_map.classes.csv2_image_cache
    db_session = config.db_session

    if image_checksum is not None:
        image = db_session.query(IMAGE_CACHE).filter(IMAGE_CACHE.image_name == image_name, IMAGE_CACHE.checksum == image_checksum)
    else:
        image = db_session.query(IMAGE_CACHE).filter(IMAGE_CACHE.image_name == image_name)

    if image.count() > 0:
        # we found something in the cache we can skip queueing a pull request
        return True
    else:
        # nothing in the cache lets queue up a pull request
        target_image = _get_image(config, image_name, image_checksum, group_name)
        if target_image is False:
            # unable to find target image
            return False #maybe raise an error here

        PULL_REQ = config.db_map.classes.csv2_image_pull_requests
        # check if a pull request already exists for this image? or just let the workers sort it out?
        #  #todo?
        preq = {
            "tx_id": _generate_tx_id(),
            "target_group_name": target_image.group_name,
            "target_cloud_name": target_image.cloud_name,
            "image_name": image_name,
            "image_id": target_image.id,
            "checksum": target_image.checksum,
            "status": "pending",
            "requester": user.username,
        }
        new_preq = PULL_REQ(**preq)
        db_session.merge(new_preq)
        db_session.commit()
        return True


#
# Djnago View Functions
#

@silkp(name="Image List")
@requires_csrf_token
def list(request, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = config.db_map.classes.cloud_images
    IMAGE_TX = config.db_map.classes.csv2_image_transactions
    CLOUDS = config.db_map.classes.csv2_clouds
    db_session = config.db_session

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    group = active_user.active_group
    images = db_session.query(IMAGES).filter(IMAGES.group_name == group, IMAGES.cloud_type == "openstack")
    clouds = db_session.query(CLOUDS).filter(CLOUDS.group_name == group, CLOUDS.cloud_type == "openstack")
    pending_tx = db_session.query(IMAGE_TX).filter(IMAGE_TX.target_group_name == group)
    image_dict = _build_image_dict(images, pending_tx)
    matrix = _build_image_matrix(image_dict, clouds)

    #build context and render matrix



    context = {
        #function specific data
        'image_dict': matrix,
        'cloud_list': clouds,

        #view agnostic data
        'active_user': active_user.username,
        'active_group': active_user.active_group,
        'user_groups': active_user.user_groups,
        'response_code': rc,
        'message': msg,
        'enable_glint': config.enable_glint,
        'is_superuser': active_user.is_superuser,
        'version': config.get_version()
    }


    return render(request, 'glintwebui/images.html', context)


@silkp(name="Image Transfer")
@requires_csrf_token
def transfer(request, args=None, response_code=0, message=None):

    config.db_open()
    db_session = config.db_session
    logger.info("GOT TRANSFER POST")
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    if request.method == 'POST':
        IMAGES = config.db_map.classes.cloud_images
        IMAGE_TX = config.db_map.classes.csv2_image_transactions


        # Should have the following data in POST:
        #    (image_name + '---' + image_checksum, target_cloud, group)
        post_data = json.loads(request.body)
        image_name = ""
        image_key = post_data.get("image_key")
        target_cloud = post_data.get("cloud_name")
        target_group = post_data.get("group_name")
        image_checksum = post_data.get("image_checksum")
        key_list = image_key.split("---")
        if len(key_list) != 2:
            if image_checksum is None:
                # we don't have the image checksum so we need to try and figure out what it is via the database
                # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                # checksum and continue as normal
                image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == target_group, IMAGES.name == image_key)
                if len(image_candidates) > 1:
                    #ambiguous image name, need a checksum
                    return HttpResponse('Ambiguous image name, please provide checksum') 
                else:
                    image_checksum = image_candidates[0].checksum
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]


        # Double check that the request doesn't exist and that the image is really missing from that cloud
        # if so then check if the image is in the cache, if not queue pull request and finally queue a transfer request
        if not _check_image(config, target_group, target_cloud, image_name, image_checksum):
            # Image or request already exists, return  with message
            return HttpResponse('Image request exists or image already on cloud')

        # if we get here everything is golden and we can queue up tha transfer request, but first lets check if the image
        # is in the cache or we should queue up a pull request, check cache returns True if it is found/queued or false
        # if it was unable to find the image
        cache_result = _check_cache(config, image_name, image_checksum, target_group, active_user)
        if cache_result is False:
            return HttpResponse('Could not find a source image...')
        target_image = _get_image(config, image_name, image_checksum, target_group)
        tx_req = {
            "tx_id":             _generate_tx_id(),
            "status":            "pending",
            "target_group_name": target_group,
            "target_cloud_name": target_cloud,
            "image_name":        image_name,
            "image_id":          target_image.id,
            "checksum":          target_image.checksum,
            "requester":         active_user.username,
        }
        new_tx_req = IMAGE_TX(**tx_req)
        db_session.merge(new_tx_req)
        db_session.commit()
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 0, 'message': '%s %s' % (lno(MODID), "Transfer queued..")})

    else:
        #Not a post request, render image page again or do nothing
        config.db_close()
        return None


@silkp(name="Image Delete")
@requires_csrf_token
def delete(request, args=None, response_code=0, message=None):
    config.db_open()
    db_session = config.db_session
    IMAGES = config.db_map.classes.cloud_images
    CLOUDS = config.db_map.classes.csv2_clouds

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        #return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
        return None

    #Delete can be done right now without queing up a transaction since it is a fast call to openstack
    #may want to use a timeout for openstack in case it's busy. How long would the user want to wait?
    if request.method == 'POST':
        # Should have the following data in POST:
        #    (image_name + '---' + image_checksum, target_cloud, group)
        post_data = json.loads(request.body)
        image_name = ""
        image_key = post_data.get("image_key")
        target_cloud = post_data.get("cloud_name")
        target_group = post_data.get("group_name")
        image_checksum = post_data.get("image_checksum")
        key_list = image_key.split("---")
        if len(key_list) != 2:
            if image_checksum is None:
                # we don't have the image checksum so we need to try and figure out what it is via the database
                # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                # checksum and continue as normal
                image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == target_group, IMAGES.name == image_key)
                if len(image_candidates) > 1:
                    #ambiguous image name, need a checksum
                    return HttpResponse('Ambiguous image name, please provide checksum') 
                else:
                    image_checksum = image_candidates[0].checksum
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]


        target_image = _get_image(config, image_name, image_checksum, target_group)
        cloud =  db_session.query(CLOUDS).get((target_group, target_cloud))


        os_session = get_openstack_session(cloud)
        glance = get_glance_client(os_session, cloud.region)
        result = delete_image(glance, target_image.id)

        if result[0] == 0:
            #Remove image row
            db_session.delete(target_image)
            db_session.commit()
            config.db_close()
            #return render(request, 'glintwebui/images.html', {'response_code': 0, 'message': '%s %s' % (lno(MODID), "Delete successful")})
            return HttpResponse(json.dumps({'response_code':0 , 'message': '%s %s' % (lno(MODID), "Delete successful")}))
        else:
            #return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s: %s' % (lno(MODID), "Delete failed", result[1])})
            return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s: %s' % (lno(MODID), "Delete failed...", result[1])}))

    else:
        #Not a post request, render image page again
        return None


@silkp(name="Image Upload")
@requires_csrf_token
def upload(request, args=None, response_code=0, message=None):

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    #Need to queue a transaction after downloading the uploaded image and placing it into the cache
    if request.method == 'POST':
        return None

    else:
        #Not a post request, render image page again
        return None


@silkp(name="Image Download")
@requires_csrf_token
def download(request, args=None, response_code=0, message=None):

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
    #check the cache for the file, if not there queue a pull request and wait for it to appear in the cache then upload to use
    if request.method == 'POST':
        return None

    else:
        #Not a post request, render image page again
        return None

