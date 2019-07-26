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

from cloudscheduler.lib.view_utils import \
    render, \
    lno, \
    set_user_groups

from cloudscheduler.lib.web_profiler import silk_profile as silkp

logger = logging.getLogger('glintv2')
ALPHABET = string.ascii_letters + string.digits + string.punctuation


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
                row_list.append((image_dict[image_key][cloud.cloud_name]["status"],image_dict[image_key][cloud.cloud_name]["message"],image_dict[image_key][cloud.cloud_name]["visibility"]))
            else:
                #image is not here
                row_list.append(("missing","",""))
        image_matrix[image_key] = row_list


    return image_matrix


# at a length of 16 with a 94 symbol alphabet we have a N/16^94 chance of a collision, pretty darn unlikely
def _generate_tx_id(length=16):
    return ''.join(random.choice(ALPHABET) for i in range(length)) 



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
        return render(request, 'glint/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

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

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glint/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    #Double check that the request doesn't exist and that the image is really missing from that cloud
    #if so then check if the image is in the cache, if not queue pull request and finally queue a transfer request
    if request.method == 'POST':
        return None

    else:
        #Not a post request, render image page again or do nothing
        return None


@silkp(name="Image Delete")
@requires_csrf_token
def delete(request, args=None, response_code=0, message=None):

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glint/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    #Delete can be done right now without queing up a transaction since it is a fast call to openstack
    #may want to use a timeout for openstack in case it's busy. How long would the user want to wait?
    if request.method == 'POST':
        return None

    else:
        #Not a post request, render image page again
        return None


@silkp(name="Image Upload")
@requires_csrf_token
def upload(request, args=None, response_code=0, message=None):

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glint/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

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
        return render(request, 'glint/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
    #check the cache for the file, if not there queue a pull request and wait for it to appear in the cache then upload to use
    if request.method == 'POST':
        return None

    else:
        #Not a post request, render image page again
        return None

