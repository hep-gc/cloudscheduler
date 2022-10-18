import time
import logging
import os
import json
import urllib3
import datetime
import magic
import tarfile

from django.conf import settings

config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse, StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import filesizeformat

from .glint_utils import delete_image, check_cache, generate_tx_id, get_image, download_image, upload_image, \
    sparsify_convert_compress

from cloudscheduler.lib.view_utils import \
    render, \
    lno, \
    qt, \
    set_user_groups, \
    validate_fields
from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.web_profiler import silk_profile as silkp

from .celery_app import pull_request, tx_request

logger = logging.getLogger('glintv2')
MODID = "IV"

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken': 'ignore',
        'group': 'ignore',
        'group-name': 'ignore',
        'group_name': 'ignore',
        'cloud': 'ignore',
        'cloud-name': 'ignore',
        'cloud_name': 'ignore',
    },
}

TRANSFER_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken': 'ignore',
        'group': 'ignore',
        'group-name': 'ignore',
        'group_name': 'ignore',
        'cloud': 'ignore',
        'cloud-name': 'ignore',
        'cloud_name': 'ignore',
        'image_name': 'ignore',
        'image_index': 'ignore',
        'image-index': 'ignore',
        'image_date': 'ignore',
        'image_checksum': 'ignore',
    },
}


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

def _trim_image_list(image_list, group, cloud=None):
    new_image_list = []
    for image in image_list:
        if image["group_name"] == group:
            if cloud is not None:
                if image["cloud_name"] == cloud:
                    if image.get("size"):
                        # format image size to human readable format
                        image["size"] = filesizeformat(int(image["size"]))
                    new_image_list.append(image)
            else:
                new_image_list.append(image)
    return new_image_list


def _build_image_dict(image_list, transaction_list):
    image_dict = {}
    image_dates = {}
    for image in image_list:
        if image["name"] is None or image["checksum"] is None:
            # We don't like images without a name, lets ignore it
            continue
        if image["name"] + "---" + image["checksum"] not in image_dict.keys():
            # first time seeing this image, make a new entry
            new_dict = {
                "name": image["name"],
                "checksum": image["checksum"],
                "created_at": image["created_at"],
                image["cloud_name"]: {
                    "status": "present",
                    "visibility": image["visibility"],
                    "id": image["id"],
                    "message": ""
                }
            }
            image_dict[image["name"] + "---" + image["checksum"]] = new_dict
            image_dates[image["name"] + "---" + image["checksum"]] = image["created_at"] + "---" + str(image["size"])
        else:
            # image already exits, just need to add the cloud name dict for this entry
            image_dict[image["name"] + "---" + image["checksum"]][image["cloud_name"]] = {
                "status": "present",
                "visibility": image["visibility"],
                "id": image["id"],
                "message": ""
            }

    # now that we have a complete picture of the images in the database we need to add the transaction data for pending image transfers
    for tx in transaction_list:
        if tx["image_name"] + "---" + tx["checksum"] not in image_dict.keys():
            # this shouldnt be possible since the image must exist to be transfered
            # only way you could end up here is if multiple deletes were queued on the same image or the image was deleted while this transaction was queued
            # ignore fore now
            continue
        else:
            # update relevent cloud dict
            if tx["target_cloud_name"] not in image_dict[tx["image_name"] + "---" + tx["checksum"]].keys():
                # make a new dict for it, probably a transfer request, or an upload
                image_dict[tx["image_name"] + "---" + tx["checksum"]][tx["target_cloud_name"]] = {
                    "status": tx["status"],
                    "visibility": "pending",
                    "id": tx["image_id"],
                    "message": tx["message"]
                }
                image_dates[tx["image_name"] + "---" + tx["checksum"]] = "-"
            else:
                # the image exists already, probably the result of multiple queue'd transfers
                # we can probably ignore this case but may want to keep whatever status/message from the tx table
                continue
    return image_dict, image_dates


# The image matrix will be a dinctionary with each value being a list of tuples where the order of the tuples is the order of clouds:
# matrix[image_name+checksum] = ((status1, message1, visibility1),(status2, message2, visibility2)....(statusN, messageN, visibilityN))
def _build_image_matrix(image_dict, cloud_list):
    image_matrix = {}

    for image_key in image_dict:
        row_list = []
        for cloud in cloud_list:
            if cloud["cloud_name"] in image_dict[image_key].keys():
                # image is here
                row_list.append((image_dict[image_key][cloud["cloud_name"]]["status"],
                                 image_dict[image_key][cloud["cloud_name"]]["message"],
                                 image_dict[image_key][cloud["cloud_name"]]["visibility"], cloud["cloud_name"]))
            else:
                # image is not here
                row_list.append(("missing", "", "", cloud["cloud_name"]))
        image_matrix[image_key] = row_list

    return image_matrix


# Checks if the image already exists for target cloud, and if it doesnt it also checks that this
#   transfer request doesn't already exist (and isn't in an error state)
# returns true if image exists or a pull request is already queued and false if
#    the image exists at target location
def _check_image(config, target_group, target_cloud, image_name, image_checksum):
    logger.debug("Checking for image: %s on target cloud: %s" % (image_name, target_cloud))
    IMAGES = "cloud_images"
    IMAGE_TX = "csv2_image_transactions"

    images = None
    # Check target cloud for image
    if image_checksum is not None:
        where_clause = "cloud_name='%s' and group_name='%s' and name='%s' and checksum='%s'" % (
        target_cloud, target_group, image_name, image_checksum)
    else:
        where_clause = "cloud_name='%s' and group_name='%s' and name='%s'" % (target_cloud, target_group, image_name)
    rc, msg, images = config.db_query(IMAGES, where=where_clause)
    if len(images) != 0:
        return False  # found the image so we don't need to transfer it

    # now we need to check if a transfer request exists
    logger.debug("Checking for image: %s in queued transfer requests" % image_name)
    if image_checksum is not None:
        where_clause = "target_cloud_name='%s' and target_group_name='%s' and image_name='%s' and checksum='%s'" % (
        target_cloud, target_group, image_name, image_checksum)
    else:
        where_clause = "target_cloud_name='%s' and target_group_name='%s' and image_name='%s'" % (
        target_cloud, target_group, image_name)
    rc, qmsg, images = config.db_query(IMAGE_TX, where=where_clause)
    if len(images) != 0:
        # there is a row, lets check the status and there might be multiple rows if no checksum was provided
        for image_trans in images:
            if "pending" in image_trans["status"] or "claimed" in image_trans["status"]:
                # Transfer already requested
                return False

    # If we get here we never found it in the image list or transaction list so we can go ahead with the xfer
    return True


# Check uploaded image file type
def _get_file_type(file_path):
    IMAGE_DICT = {
        "QEMU QCOW Image": "qcow2",
        "ISO 9660 CD-ROM": "iso",
        "x86 boot sector": "raw",
        "VMware4 disk image": "vmdk",
        "VirtualBox Disk Image": "vdi",
        "POSIX tar archive": "ova"
    }

    TYPE_LIST = ["aki", "ami", "ari", "qcow2", "iso", "vmdk", "vdi", "ova"]

    if file_path.split(".")[-1] in TYPE_LIST:
        return file_path.split(".")[-1]
    file_type = magic.from_file(file_path)
    for type in IMAGE_DICT:
        if type in file_type:
            if IMAGE_DICT[type] == "ova":
                tar_file_content = tarfile.open(file_path)
                tar_ovf = False
                tar_vmdk = False
                for file in tar_file_content.getnames():
                    if file and not tar_ovf and ".ovf" in file:
                        tar_ovf = True
                        if tar_ovf and tar_vmdk:
                            return IMAGE_DICT[type]
                    if file and not tar_vmdk and ".vmdk" in file:
                        tar_vmdk = True
                        if tar_ovf and tar_vmdk:
                            return IMAGE_DICT[type]
            else:
                return IMAGE_DICT[type]


#
# Djnago View Functions
#

@silkp(name="Image List")
@requires_csrf_token
# This functions supports the webui producing the image matrix
def list(request, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = "cloud_images"
    IMAGE_TX = "csv2_image_transactions"
    CLOUDS = "csv2_clouds"
    GROUPS = "csv2_groups"

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, qmsg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
    msg = message

    group = active_user.active_group
    where_clause = "group_name='%s' and cloud_type='%s'" % (group, "openstack")
    rc, qmsg, images = config.db_query(IMAGES, where=where_clause)
    rc, qmsg, clouds = config.db_query(CLOUDS, where=where_clause)
    where_clause = "group_name='%s'" % group
    rc, qmsg, defaults_list = config.db_query(GROUPS, where=where_clause)
    defaults = defaults_list[0]
    if defaults["vm_image"] is None or defaults["vm_image"] == "":
        default_image = None
    else:
        default_image = defaults["vm_image"]

    where_clause = "target_group_name='%s'" % group
    rc, qmsg, pending_tx = config.db_query(IMAGE_TX, where=where_clause)
    image_dict, image_dates = _build_image_dict(images, pending_tx)
    matrix = _build_image_matrix(image_dict, clouds)

    # build context and render matrix

    context = {
        # function specific data
        'image_dict': matrix,
        'image_dates': image_dates,
        'cloud_list': clouds,
        'default_image': default_image,

        # view agnostic data
        'active_user': active_user.username,
        'active_group': active_user.active_group,
        'user_groups': active_user.user_groups,
        'response_code': rc,
        'message': msg,
        'is_superuser': active_user.is_superuser,
        'version': config.get_version()
    }

    config.db_close()
    return render(request, 'glintwebui/images.html', context)


@silkp(name="Image Transfer")
@requires_csrf_token
def transfer(request, args=None, response_code=0, message=None):
    config.db_open()
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)}))

    if request.method == 'POST':
        IMAGES = "cloud_images"
        IMAGE_TX = "csv2_image_transactions"

        # If it's a json payload its coming from javascript on the webfrontend else its a cli request
        post_data = None
        try:
            post_data = json.loads(request.body)
            image_name = ""
            image_checksum = None
        except:
            # not a json payload, didnt come from webfrontend
            image_name = ""
            image_checksum = None

        if post_data and "image_key" in post_data:
            # this is a request from the web, the CLI doesn't build the composite key
            # Should have the following data in POST:
            #    (image_name + '---' + image_checksum, target_cloud, group)
            # 
            image_key = post_data.get("image_key")
            target_cloud = post_data.get("cloud_name")
            target_group = post_data.get("group_name")
            key_list = image_key.split("---")
            if len(key_list) != 2:
                if image_checksum is None:
                    # we don't have the image checksum so we need to try and figure out what it is via the database
                    # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                    # checksum and continue as normal
                    where_clause = "group_name='%s' and name='%s'" % (target_group, image_key)
                    rc, msg, image_candidates = config.db_query(IMAGES, where=where_clause)
                    if len(image_candidates) > 1:
                        config.db_close()
                        # ambiguous image name, need a checksum
                        return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                        lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                    else:
                        image_checksum = image_candidates[0].checksum
                # Once we get here we have the checksum so assign the image_name and continue as normal
                image_name = image_key
            else:
                # key is normal
                image_name = key_list[0]
                image_checksum = key_list[1]

            # Double check that the request doesn't exist and that the image is really missing from that cloud
            # if so then check if the image is in the cache, if not queue pull request and finally queue a transfer request
            if not _check_image(config, target_group, target_cloud, image_name, image_checksum):
                config.db_close()
                # Image or request already exists, return  with message
                return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                lno(MODID), 'Image request exists or image already on cloud')}))

            # if we get here everything is golden and we can queue up tha transfer request, but first lets check if the image
            # is in the cache or we should queue up a pull request, check cache returns True if it is found/queued or false
            # if it was unable to find the image
            cache_result = check_cache(config, image_name, image_checksum, target_group, active_user)
            if cache_result is False:
                config.db_close()
                return HttpResponse(json.dumps(
                    {'response_code': 1, 'message': '%s %s' % (lno(MODID), "Could not find a source image...")}))
            target_image = get_image(config, image_name, image_checksum, target_group)
            tx_id = generate_tx_id()
            tx_req = {
                "tx_id": tx_id,
                "status": "pending",
                "target_group_name": target_group,
                "target_cloud_name": target_cloud,
                "image_name": image_name,
                "image_id": target_image["id"],
                "checksum": target_image["checksum"],
                "requester": active_user.username,
            }

            config.db_merge(IMAGE_TX, tx_req)
            config.db_commit()
            config.db_close()
            # tx_request.delay(tx_id = tx_id)
            logger.info("Transfer queued")
            tx_request.apply_async((tx_id,), queue='tx_requests')
            logger.info("Transfer image")
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transfer queued..'}))

        else:
            # command line request
            #  options:
            #    image_date
            #    image_index
            #    image_name
            #    image_checksum
            #    target_cloud
            #    group

            # Validate input fields.
            rc, msg, fields, tables, columns = validate_fields(config, request, [TRANSFER_KEYS], [], active_user)
            if rc != 0:
                config.db_close()
                # Invalid fields, return message
                return HttpResponse(json.dumps({'response_code': rc, 'message': msg}))

            group_name = active_user.active_group
            target_cloud = fields.get("cloud_name")
            image_name = fields.get("image_name")
            image_checksum = fields.get("image_checksum")
            image_date = fields.get("image_date")
            image_index = fields.get("image_index")
            if image_index is not None:
                image_index = int(image_index) - 1

            if image_name is None and image_index is None:
                config.db_close()
                return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                lno(MODID), "No image name or index, please supply at least one to identify target image")}))

            target_image = None

            if image_index is not None:
                # get target image by index
                sql = "select rank() over (partition by rank order by group_name,cloud_name,name,created_at,checksum) as rank,group_name,cloud_name,name,created_at,checksum,id from (select 1 as rank,i.* from (select * from cloud_images) as i) as i where cloud_type='openstack';"
                rc, msg = config.db_execute(sql)
                image_list = []
                for row in config.db_cursor:
                    image_list.append(row)
                target_image = image_list[image_index]
                if image_name is not None:
                    if str(target_image["name"]) != str(image_name):
                        config.db_close()
                        return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID),
                                                                                                  "Image name (%s) from index (%s) does not match supplied image name (%s) please check your request and try again." % (
                                                                                                  target_image["name"],
                                                                                                  image_index,
                                                                                                  image_name))}))
            else:
                # we have at least an image name, lets build the where clause
                where = "name='%s'" % image_name
                if image_checksum is not None:
                    where = where + " and checksum='%s'" % image_checksum
                if image_date is not None:
                    where = where + " and created_at like '%s'" % image_date

                sql = "select * from cloud_images where %s" % where
                rc, msg, = config.db_execute(sql)
                image_list = []
                for row in config.db_cursor:
                    image_list.append(row)

                if len(image_list) > 1:
                    config.db_close()
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID),
                                                                                              "Unable to uniquely identify target image with given parameters, %s images matched." % len(
                                                                                                  image_list))}))
                elif len(image_list) == 0:
                    config.db_close()
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                    lno(MODID), "No images matched sepcified parameters, please check your request and try again.")}))
                else:
                    target_image = image_list[0]

            # we have target image, create the transaction request
            # First check the cache for the image and create a pull request if it's abscent
            check_cache(config, target_image["name"], target_image["checksum"], active_user.active_group, active_user,
                        target_image)
            tx_id = generate_tx_id()
            try:

                tx_req = {
                    "tx_id": tx_id,
                    "status": "pending",
                    "target_group_name": active_user.active_group,
                    "target_cloud_name": target_cloud,
                    "image_name": target_image["name"],
                    "image_id": target_image["id"],
                    "checksum": target_image["checksum"],
                    "requester": active_user.username,
                }
                config.db_merge(IMAGE_TX, tx_req)
                config.db_commit()
                config.db_close()
                tx_request.apply_async((tx_id,), queue='tx_requests')
                context = {
                    'response_code': 0,
                    'message': "Transfer queued for image %s to cloud %s" % (target_image["name"], target_cloud)
                }
                return HttpResponse(json.dumps(context))
            except Exception as exc:
                logging.error(exc)
                message = "Failed to queue transfer: %s" % exc
                context = {
                    'response_code': 1,
                    'message': message
                }
                config.db_close()
                return HttpResponse(json.dumps(context))




    else:
        # Not a post request, render image page again or do nothing
        config.db_close()
        return None


@silkp(name="Image Delete")
@requires_csrf_token
def delete(request, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = "cloud_images"
    CLOUDS = "csv2_clouds"

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        # return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
        return None

    # Delete can be done right now without queing up a transaction since it is a fast call to openstack
    # may want to use a timeout for openstack in case it's busy. How long would the user want to wait?
    if request.method == 'POST':

        # If it's a json payload its coming from javascript on the webfrontend else its a cli request
        post_data = None
        try:
            post_data = json.loads(request.body)
            image_name = ""
            image_checksum = None
        except:
            # not a json payload, didnt come from webfrontend
            image_name = ""
            image_checksum = None

        if post_data and "image_key" in post_data:
            # Should have the following data in POST:
            #    (image_name + '---' + image_checksum, target_cloud, group)
            image_key = post_data.get("image_key")
            target_cloud = post_data.get("cloud_name")
            target_group = post_data.get("group_name")
            key_list = image_key.split("---")
            if len(key_list) != 2:
                if image_checksum is None:
                    # we don't have the image checksum so we need to try and figure out what it is via the database
                    # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                    # checksum and continue as normal
                    where_clause = "group_name='%s' and name='%s'" % (target_group, image_key)
                    rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
                    if len(image_candidates) > 1:
                        # ambiguous image name, need a checksum
                        config.db_close()
                        return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                        lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                    else:
                        image_checksum = image_candidates[0]["checksum"]
                # Once we get here we have the checksum so assign the image_name and continue as normal
                image_name = image_key
            else:
                # key is normal
                image_name = key_list[0]
                image_checksum = key_list[1]

            logger.info("GETTING IMAGE: %s::%s::%s::%s" % (image_name, image_checksum, target_group, target_cloud))
            target_image = get_image(config, image_name, image_checksum, target_group, target_cloud)
            where_clause = "group_name='%s' and cloud_name='%s'" % (target_group, target_cloud)
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            cloud = cloud_list[0]
            result = delete_image(cloud, target_image["id"])

            if result[0] == 0:
                # Remove image row
                config.db_delete(IMAGES, target_image)
                config.db_commit()
                config.db_close()
                # return render(request, 'glintwebui/images.html', {'response_code': 0, 'message': '%s %s' % (lno(MODID), "Delete successful")})
                return HttpResponse(
                    json.dumps({'response_code': 0, 'message': '%s %s' % (lno(MODID), "Delete successful")}))
            else:
                config.db_close()
                # return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s: %s' % (lno(MODID), "Delete failed", result[1])})
                return HttpResponse(json.dumps(
                    {'response_code': 1, 'message': '%s %s: %s' % (lno(MODID), "Delete failed...", result[1])}))
        else:
            # command line request
            #  options:
            #    image_date
            #    image_index
            #    image_name
            #    image_checksum
            #    target_cloud
            #    group

            # Validate input fields.
            rc, msg, fields, tables, columns = validate_fields(config, request, [TRANSFER_KEYS], [], active_user)
            if rc != 0:
                config.db_close()
                # Invalid fields, return message
                return HttpResponse(json.dumps({'response_code': rc, 'message': msg}))

            group_name = active_user.active_group
            cloud_name = fields.get("cloud-name")
            image_name = fields.get("image_name")
            image_checksum = fields.get("image_checksum")
            image_date = fields.get("image_date")
            image_index = fields.get("image-index")
            if image_index is not None:
                image_index = int(image_index) - 1

            if image_name is None and image_index is None:
                config.db_close()
                return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                lno(MODID), "No image name or index, please supply at least one to identify target image")}))

            target_image = None

            if image_index is not None:
                # get target image by index
                sql = "select rank() over (partition by rank order by group_name,cloud_name,name,created_at,checksum) as rank,group_name,cloud_name,name,created_at,checksum,id from (select 1 as rank,i.* from (select * from cloud_images) as i) as i where cloud_type='openstack';"
                rc, msg = config.db_execute(sql)
                image_list = []
                for row in config.db_cursor:
                    image_list.append(row)
                target_image = image_list[image_index]
                if image_name is not None:
                    if str(target_image["name"]) != str(image_name):
                        config.db_close()
                        return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID),
                                                                                                  "Image name (%s) from index (%s) does not match supplied image name (%s) please check your request and try again." % (
                                                                                                  target_image["name"],
                                                                                                  image_index,
                                                                                                  image_name))}))
                if cloud_name is not None:
                    if str(target_image["cloud_name"]) != str(cloud_name):
                        config.db_close()
                        return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID),
                                                                                                  "cloud name (%s) from index (%s) does not match supplied cloud name (%s) please check your request and try again." % (
                                                                                                  target_image[
                                                                                                      "cloud_name"],
                                                                                                  image_index,
                                                                                                  cloud_name))}))
            else:
                # we have at least an image name, lets build the where clause
                where = "name='%s'" % image_name
                if image_checksum is not None:
                    where = where + " and checksum='%s'" % image_checksum
                if image_date is not None:
                    where = where + " and created_at like '%s'" % image_date
                if cloud_name is not None:
                    where = where + " and cloud_name='%s'" % cloud_name

                sql = "select * from cloud_images where %s" % where
                rc, msg, image_list = config.db_query(IMAGES, where=where)
                if len(image_list) > 1:
                    config.db_close()
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID),
                                                                                              "Unable to uniquely identify target image with given parameters, %s images matched." % len(
                                                                                                  image_list))}))
                elif len(image_list) == 0:
                    config.db_close()
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                    lno(MODID), "No images matched sepcified parameters, please check your request and try again.")}))
                else:
                    target_image = image_list[0]

            # we have target image, lets delete it
            where_clause = "group_name='%s' and cloud_name='%s'" % (
            target_image["group_name"], target_image["cloud_name"])
            rc, msg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            cloud = cloud_list[0]
            result = delete_image(cloud, target_image["id"])

            if result[0] == 0:
                # Successful delete, now delete it from csv2 database - build delete statement
                sql = "delete from cloud_images where group_name='%s' and cloud_name='%s' and id='%s';" % (
                target_image["group_name"], target_image["cloud_name"], target_image["id"])
                try:
                    config.db_execute(sql)
                    config.db_commit()
                except Exction as exc:
                    config.db_close()
                    context = {
                        "response_code": 1,
                        "message": "Failed to execute delete for image %s: %s" % (target_image["name"], exc)
                    }
                    return HttpResponse(json.dumps(context))

                context = {
                    "response_code": 0,
                    "message": "Image %s deleted successfully" % target_image["name"]
                }
                config.db_close()
                return HttpResponse(json.dumps(context))
            else:
                config.db_close()
                return HttpResponse(json.dumps(
                    {'response_code': 1, 'message': '%s %s: %s' % (lno(MODID), "Delete failed...", result[1])}))

    else:
        # Not a post request, render image page again
        config.db_close()
        return None


@silkp(name='Image Upload')
@requires_csrf_token
def upload(request, group_name=None):
    config.db_open()

    IMAGES = "cloud_images"
    IMAGE_TX = "csv2_image_transactions"
    CLOUDS = "csv2_clouds"
    CACHE_IMAGES = "csv2_image_cache"

    rc, qmsg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        # return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
        return None
    try:
        image_file = request.FILES['myfile']
    except Exception:
        # no file means it's not a POST or it's an upload by URL
        image_file = False

    if request.method == 'POST' and image_file:
        logger.info("File to upload: %s" % image_file.name)
        if group_name is None:
            # need to figure out where to get group name
            group_name = active_user.active_group

        # process image upload
        image_file = request.FILES['myfile']
        file_path = config.categories["glintPoller.py"][
                        "image_cache_dir"] + image_file.name  # This file will have to be renamed with the checksum after uploading to a cloud

        # before we save it locally let us check if it is already in the repos
        cloud_name_list = request.POST.getlist('clouds')

        # ---------added------if the initial cloud_name_list is empty, return error message--
        if len(cloud_name_list) == 0:
            msg = "Upload failed because no target cloud is selected"
        # ---------added-----------------------------------------------------------------

        if len(cloud_name_list) == 1 and "," in cloud_name_list[0]:
            # could be a cli command packaged as a string,
            cloud_name_list = cloud_name_list[0].replace(" ", "").split(",")

        where_clause = "name='%s' and group_name='%s'" % (image_file.name, group_name)
        rc, qmsg, image_list = config.db_query(IMAGES, where=where_clause)
        bad_clouds = []
        if len(image_list) > 0:
            # we've got some images by this name already lets see if any are in the target clouds
            for image in image_list:
                if image["cloud_name"] in cloud_name_list:
                    bad_clouds.append(image["cloud_name"])
        if len(bad_clouds) > 0:
            for cloud in bad_clouds:
                if cloud in cloud_name_list: cloud_name_list.remove(cloud)
            msg = ("Upload failed for one or more projects because the image name was already in use.")

        if len(cloud_name_list) == 0:
            # if we have eliminated all the target clouds, return with error message
            msg = "Upload failed to all target projects because the image name was already in use."
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        # And finally before we save locally double check that file doesn't already exist
        if os.path.exists(file_path):
            # Filename exists locally, lets add some random suffix and check again
            suffix = 1
            new_path = file_path + str(suffix)
            while os.path.exists(new_path):
                suffix = suffix + 1
                new_path = file_path + str(suffix)
            file_path = new_path

        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # added code -----------------------------------------------------
        with_conversion = bool(request.POST.get('operation0'))
        virt_sparsify = bool(request.POST.get('operation1'))
        with_compression = bool(request.POST.get('operation2'))

        if with_conversion:
            file_path = sparsify_convert_compress(file_path, virt_sparsify, with_compression)
            if virt_sparsify:
                image_file.name += '.reorganized'
            if with_compression:
                image_file.name += '.compressed'
            image_file.name += '.qcow2'
        # added code -----------------------------------------------------

        disk_format = request.POST.get('disk_format')
        if disk_format == '':
            try:
                disk_format = _get_file_type(file_path)
            except Exception as exc:
                logger.error("Failed to detect disk format: %s" % exc)
        if disk_format == '':
            logger.error("Unabled to detect the disk format for image %s" % image_file.name)
            msg = "Unabled to detect the disk format for image: %s" % image_file.name
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        # Now we have a source file we need to upload it to one of the clouds to get a checksum so we can queue up transfer requests
        # get a cloud of of the list, first one is fine
        target_cloud_name = cloud_name_list[0]
        # get the cloud row for this cloud
        where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, target_cloud_name)
        rc, qmsg, target_cloud_list = config.db_query(CLOUDS, where=where_clause)
        try:
            target_cloud = target_cloud_list[0]
        except IndexError:
            logger.error("Unable to find target cloud: %s" % target_cloud_name)
            msg = "Unable to find target cloud: %s" % target_cloud_name
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        if disk_format == "ova":
            disk_format = "vmdk"
            container_format = "ova"
        else:
            container_format = "bare"

        logger.info("uploading image %s to cloud %s" % (image_file.name, target_cloud_name))
        image = upload_image(target_cloud, None, image_file.name, file_path, disk_format=disk_format,
                             container_format=container_format)
        if image is False:
            logger.error("Upload failed for image %s" % image_file.name)
            msg = "Upload failed for image: %s" % image_file.name
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        logger.info("Upload result: %s" % image)
        # add it to the cloud_images table
        if image.size == "" or image.size is None:
            size = 0
        else:
            size = image.size
        created_datetime = datetime.datetime.now()
        created_time = created_datetime.strftime("%Y-%m-%d %H:%M:%S")
        new_image_dict = {
            'group_name': target_cloud["group_name"],
            'cloud_name': target_cloud["cloud_name"],
            'container_format': image.container_format,
            'checksum': image.checksum,
            'cloud_type': "openstack",
            'disk_format': image.disk_format,
            'min_ram': image.min_ram,
            'id': image.id,
            'size': size,
            'visibility': image.visibility,
            'min_disk': image.min_disk,
            'name': image.name,
            'created_at': created_time,
            'last_updated': time.time()
        }
        img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=new_image_dict, config=config)
        if unmapped:
            logging.error("Unmapped attributes found during mapping, discarding:")
            logging.error(unmapped)
        config.db_merge(IMAGES, img_dict)
        config.db_commit()

        # now we have the os image object, lets rename the file and add it to out cache
        cache_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_file.name + "---" + image.checksum
        os.rename(file_path, cache_path)

        cache_dict = {
            "image_name": image_file.name,
            "checksum": image.checksum,
            "container_format": image.container_format,
            "disk_format": image.disk_format
        }
        config.db_merge(CACHE_IMAGES, cache_dict)
        config.db_commit()

        # now we need to queue transfer requests for the remaining clouds
        cloud_name_list.remove(target_cloud_name)
        if len(cloud_name_list) == 0:
            # we are done and can return successfully
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "true",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': rc,
                'message': "Upload Successful: image %s uploaded to %s-%s" % (
                image.name, group_name, target_cloud_name),
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        else:
            # loop over remaining clouds and queue transfers
            logger.info("Queuing additonal uploads...")
            for cloud in cloud_name_list:
                tx_id = generate_tx_id()
                tx_req = {
                    "tx_id": tx_id,
                    "status": "pending",
                    "target_group_name": group_name,
                    "target_cloud_name": cloud,
                    "image_name": image_file.name,
                    "image_id": image.id,
                    "checksum": image.checksum,
                    "requester": active_user.username,
                }
                config.db_merge(IMAGE_TX, tx_req)
                config.db_commit()
                logger.info("Transfer id:%s queued" % tx_id)
                tx_request.apply_async((tx_id,), queue='tx_requests')

        # return to project details page with message
        msg = "Upload successfully queued, returning to images..."
        where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
        rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
        context = {
            'group_name': group_name,
            'cloud_list': cloud_list,
            'max_repos': len(cloud_list),
            'redirect': "true",

            # view agnostic data
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'response_code': rc,
            'message': msg,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }
        config.db_close()
        return render(request, 'glintwebui/upload_image.html', context)

    elif request.method == 'POST' and request.POST.get('myfileurl'):
        if group_name is None:
            logger.error("No group name, using user's default")
            group_name = active_user.active_group

        # download the image
        img_url = request.POST.get('myfileurl')
        image_name = img_url.rsplit("/", 1)[-1]
        logger.info("File to upload: %s" % image_name)
        file_path = config.categories["glintPoller.py"][
                        "image_cache_dir"] + image_name  # This file will have to be renamed with the checksum after uploading to a cloud

        # check if a file with that name already exists
        if os.path.exists(file_path):
            # Filename exists locally, lets add some suffix and check again
            suffix = 1
            new_path = file_path + str(suffix)
            while os.path.exists(new_path):
                suffix = suffix + 1
                new_path = file_path + str(suffix)
            file_path = new_path

        # before we save it locally let us check if it is already in the repos
        cloud_name_list = request.POST.getlist('clouds')
        where_clause = "name='%s' and group_name='%s'" % (image_name, group_name)
        rc, qmsg, image_list = config.db_query(IMAGES, where=where_clause)
        bad_clouds = []

        # ---------added------if the initial cloud_name_list is empty, return error message--
        if len(cloud_name_list) == 0:
            msg = "Upload failed because no target cloud is selected"
        # ---------added------if the initial cloud_name_list is empty, return error message--

        if len(image_list) > 0:
            # we've got some images by this name already lets see if any are in the target clouds
            for image in image_list:
                if image["cloud_name"] in cloud_name_list:
                    bad_clouds.append(image["cloud_name"])
        if len(bad_clouds) > 0:
            for cloud in bad_clouds:
                cloud_name_list.remove(cloud)
            msg = ("Upload failed for one or more projects because the image name was already in use.")

        if len(cloud_name_list) == 0:
            # if we have eliminated all the target clouds, return with error message
            msg = ("Upload failed to all target projects because the image name was already in use.")
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        http = urllib3.PoolManager()
        image_data = http.request('GET', img_url)

        with open(file_path, "wb") as image_file:
            image_file.write(image_data.data)

        # added code in elif----------------------------------------------
        with_conversion = bool(request.POST.get('operation0'))
        virt_sparsify = bool(request.POST.get('operation1'))
        with_compression = bool(request.POST.get('operation2'))

        if with_conversion:
            file_path = sparsify_convert_compress(file_path, virt_sparsify, with_compression)
            if virt_sparsify:
                image_name += '.reorganized'
            if with_compression:
                image_name += '.compressed'
            image_name += '.qcow2'
        # added code -----------------------------------------------------

        disk_format = request.POST.get('disk_format')
        if disk_format == '':
            try:
                disk_format = _get_file_type(file_path)
            except Exception as exc:
                logger.error('Failed to detect disk format: %s' % exc)
        if disk_format == '':
            logger.error("Unabled to detect the disk format for image %s" % image_name)
            msg = "Unabled to detect the disk format for image: %s, please select one" % image_name
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        if disk_format == "ova":
            disk_format = "vmdk"
            container_format = "ova"
        else:
            container_format = "bare"

        # Now we have a source file we need to upload it to one of the clouds to get a checksum so we can queue up transfer requests
        # get a cloud of of the list, first one is fine
        target_cloud_name = cloud_name_list[0]
        # get the cloud row for this cloud
        where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, target_cloud_name)
        rc, qmsg, target_cloud_list = config.db_query(CLOUDS, where=where_clause)
        target_cloud = target_cloud_list[0]

        image = upload_image(target_cloud, None, image_name, file_path, disk_format=disk_format,
                             container_format=container_format)
        if image is False:
            logger.error("Upload failed for image %s" % image_name)
            msg = "Upload failed for image: %s" % image_name
            where_clause = "group_name='%s' and cloud_type='%s'" % (group_name, "openstack")
            rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': len(cloud_list),
                'redirect': "false",

                # view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': 1,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
            config.db_close()
            return render(request, 'glintwebui/upload_image.html', context)

        logger.info("Upload result: %s" % image)

        # add it to the cloud_images table
        if image.size == "" or image.size is None:
            size = 0
        else:
            size = image.size
        created_datetime = datetime.datetime.now()
        created_time = created_datetime.strftime("%Y-%m-%d %H:%M:%S")
        new_image_dict = {
            'group_name': target_cloud["group_name"],
            'cloud_name': target_cloud["cloud_name"],
            'container_format': image.container_format,
            'checksum': image.checksum,
            'cloud_type': "openstack",
            'disk_format': image.disk_format,
            'min_ram': image.min_ram,
            'id': image.id,
            'size': size,
            'visibility': image.visibility,
            'min_disk': image.min_disk,
            'name': image.name,
            'created_at': created_time,
            'last_updated': time.time()
        }
        img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=new_image_dict, config=config)
        if unmapped:
            logging.error("Unmapped attributes found during mapping, discarding:")
            logging.error(unmapped)
        config.db_merge(IMAGES, img_dict)
        config.db_commit()
        # now we have the os image object, lets rename the file and add it to out cache
        cache_path = image_file.name + "---" + image.checksum
        os.rename(file_path, cache_path)

        cache_dict = {
            "image_name": image_name,
            "checksum": image.checksum,
            "container_format": image.container_format,
            "disk_format": image.disk_format
        }
        config.db_merge(CACHE_IMAGES, cache_dict)
        config.db_commit()

        # now we need to queue transfer requests for the remaining clouds
        cloud_name_list.remove(target_cloud_name)
        if len(cloud_name_list) == 0:
            # we are done and can return successfully
            pass
        else:
            # loop over remaining clouds and queue transfers
            for cloud in cloud_name_list:
                tx_id = generate_tx_id()
                tx_req = {
                    "tx_id": tx_id,
                    "status": "pending",
                    "target_group_name": group_name,
                    "target_cloud_name": cloud,
                    "image_name": image_name,
                    "image_id": image.id,
                    "checksum": image.checksum,
                    "requester": active_user.username,
                }
                config.db_merge(IMAGE_TX, tx_req)
                config.db_commit()
                logger.info("Transfer id:%s queued" % tx_id)
                tx_request.apply_async((tx_id,), queue='tx_requests')

        # return to project details page with message
        msg = "Upload successfully queued, returning to images..."
        where_clause = "group_name='%s' and cloud_type='openstack'" % group_name
        rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
        context = {
            'group_name': group_name,
            'cloud_list': cloud_list,
            'max_repos': len(cloud_list),
            'redirect': "true",

            # view agnostic data
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'response_code': rc,
            'message': msg,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }
        config.db_close()
        return render(request, 'glintwebui/upload_image.html', context)
    else:
        # render page to upload image
        if request.META['HTTP_ACCEPT'] != 'application/json' and active_user and active_user.active_group:
            group_name = active_user.active_group
        where_clause = "group_name='%s' and cloud_type='openstack'" % group_name
        rc, qmsg, cloud_list = config.db_query(CLOUDS, where=where_clause)
        context = {
            'group_name': group_name,
            'cloud_list': cloud_list,
            'max_repos': len(cloud_list),
            'redirect': "false",

            # view agnostic data
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'response_code': rc,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }
        config.db_close()
        return render(request, 'glintwebui/upload_image.html', context)


@silkp(name="Image Download")
@requires_csrf_token
def download(request, group_name, image_key, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = "cloud_images"
    CACHE_IMAGES = "csv2_image_cache"
    CLOUD = "csv2_clouds"

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # unbox request and figure out if we've got the image in the cache
    image_name = None
    image_checksum = None
    key_list = image_key.split("---")
    if len(key_list) != 2:
        if image_checksum is None:
            # we don't have the image checksum so we need to try and figure out what it is via the database
            # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
            # checksum and continue as normal
            where_clause = "group_name='%s' and name='%s'" % (group_name, image_key)
            rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
            if len(image_candidates) > 1:
                config.db_close()
                return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
            else:
                image_checksum = image_candidates[0]["checksum"]
        # Once we get here we have the checksum so assign the image_name and continue as normal
        image_name = image_key
    else:
        # key is normal
        image_name = key_list[0]
        image_checksum = key_list[1]

    logger.info("Downloading image %s" % image_name)
    # if the image is not in the cache, download it and update the cache table
    where_clause = "image_name='%s' and checksum='%s'" % (image_name, image_checksum)
    rc, qmsg, cached_images = config.db_query(CACHE_IMAGES, where=where_clause)
    if len(cached_images) > 0:
        # we've got the image cached already, we can go ahead and serve from this file
        image_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_name + "---" + image_checksum
        response = StreamingHttpResponse((line for line in open(image_path, 'rb')))
        response['Content-Disposition'] = "attachment; filename={0}".format(image_name)
        response['Content-Length'] = os.path.getsize(image_path)
        config.db_close()
        logger.info("Finish downloading image %s" % image_name)
        return response


    else:
        # we need to download the image first and update the cache
        # find a source image
        where_clause = "group_name='%s' and name='%s' and checksum='%s'" % (group_name, image_name, image_checksum)
        rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
        if len(image_candidates) == 0:
            # we didnt find a source
            config.db_close()
            return False  # report error
        else:
            src_image = image_candidates[0]
        where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, src_image["cloud_name"])
        rc, qmsg, cloud_row_list = config.db_query(CLOUD, where=where_clause)
        cloud_row = cloud_row_list[0]
        result_tuple = download_image(cloud_row, image_name, src_image["id"], image_checksum,
                                      config.categories["glintPoller.py"]["image_cache_dir"])
        if result_tuple[0]:
            # successful download, update the cache and remove transaction
            cache_dict = {
                "image_name": image_name,
                "checksum": image_checksum,
                "container_format": result_tuple[3],
                "disk_format": result_tuple[2]
            }

            config.db_merge(CACHE_IMAGES, cache_dict)
            config.db_commit()
            # ok we've got the image we can finally serve it up
            image_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_name + "---" + image_checksum
            response = StreamingHttpResponse((line for line in open(image_path, 'rb')))
            response['Content-Disposition'] = "attachment; filename={0}".format(image_name)
            response['Content-Length'] = os.path.getsize(image_path)
            config.db_close()
            logger.info("Finish downloading image %s" % image_name)
            return response


        else:
            # Download failed for whatever reason, update message and return to images page
            # check result_tuple for error message
            logger.error("Failed to download the image %s" % result_tuple[1])
            config.db_close()
            return None

    config.db_close()
    return None


@silkp(name="Retry Tansaction")
@requires_csrf_token
def retry(request, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = "cloud_images"
    CLOUDS = "csv2_clouds"
    IMG_TX = "csv2_image_transactions"

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return None

    if request.method == 'POST':
        # Should have the following data in POST:
        #    (image_name + '---' + image_checksum, target_cloud, group)
        post_data = json.loads(request.body)
        image_checksum = ""
        image_name = ""
        image_key = post_data.get("image_key")
        target_cloud = post_data.get("cloud_name")
        target_group = post_data.get("group_name")
        key_list = image_key.split("---")
        if len(key_list) != 2:
            if image_checksum is None:
                # we don't have the image checksum so we need to try and figure out what it is via the database
                # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                # checksum and continue as normal
                where_clause = "group_name='%s' and name='%s'" % (target_group, image_key)
                rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
                if len(image_candidates) > 1:
                    config.db_close()
                    # ambiguous image name, need a checksum
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                    lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                else:
                    image_checksum = image_candidates[0]["checksum"]
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]
            image_checksum = key_list[1]

        where_clause = "image_name='%s' and checksum='%s' and target_cloud_name='%s' and target_group_name='%s'" % (
        image_name, image_checksum, target_cloud, target_group)
        rc, qmsg, image_tx = config.db_query(IMG_TX, where=where_clause)
        if len(image_tx) == 0:
            # no transaction found
            config.db_close()
            logger.error(
                "No transaction found for image:%s on group::cloud: %s::%s" % (image_name, target_group, target_cloud))
            return HttpResponse(json.dumps({'response_code': 1,
                                            'message': "No transaction found for image:%s on group::cloud: %s::%s" % (
                                            image_name, target_group, target_cloud)}))
        elif len(image_tx) == 1:
            # found the bugger, lets update the status to pending and queue a new transaction
            redo_tx = image_tx[0]
            redo_tx["status"] = "pending"
            redo_tx["message"] = "Retrying..."
            config.db_merge(IMG_TX, redo_tx)
            config.db_commit()
            tx_request.apply_async((redo_tx["tx_id"],), queue='tx_requests')
            logger.info("Transfer re-queued")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transfer re-queued..'}))
        else:
            # if we get here it means we have multiple identical transactions queue'd up so lets report the error and just take the first one
            logger.warning(
                "Multiple identical transactions found, there is probably a database issue or a problem with defaults replication")
            redo_tx = image_tx[0]
            redo_tx["status"] = "pending"
            redo_tx["message"] = "Retrying..."
            config.db_merge(IMG_TX, redo_tx)
            config.db_commit()
            tx_request.apply_async((redo_tx["tx_id"],), queue='tx_requests')
            logger.info("Transfer re-queued")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transfer re-queued..'}))
    else:
        # not a post
        config.db_close()
        return None


@silkp(name="Clear Tansaction")
@requires_csrf_token
def clear(request, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = "cloud_images"
    CLOUDS = "csv2_clouds"
    IMG_TX = "csv2_image_transactions"

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return None

    if request.method == 'POST':
        # Should have the following data in POST:
        #    (image_name + '---' + image_checksum, target_cloud, group)
        post_data = json.loads(request.body)
        image_checksum = ""
        image_name = ""
        image_key = post_data.get("image_key")
        target_cloud = post_data.get("cloud_name")
        target_group = post_data.get("group_name")
        key_list = image_key.split("---")
        if len(key_list) != 2:
            if image_checksum is None:
                # we don't have the image checksum so we need to try and figure out what it is via the database
                # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                # checksum and continue as normal
                where_clause = "group_name='%s' and name='%s'" % (target_group, image_key)
                rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
                if len(image_candidates) > 1:
                    config.db_close()
                    # ambiguous image name, need a checksum
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (
                    lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                else:
                    image_checksum = image_candidates[0]["checksum"]
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]
            image_checksum = key_list[1]

        where_clause = "image_name='%s' and checksum='%s' and target_cloud_name='%s' and target_group_name='%s'" % (
        image_name, image_checksum, target_cloud, target_group)
        rc, qmsg, image_tx = config.db_query(IMG_TX, where=where_clause)
        if len(image_tx) == 0:
            # no transaction found
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0,
                                            'message': "No transaction found for image:%s on group::cloud: %s::%s" % (
                                            image_name, target_group, target_cloud)}))
        elif len(image_tx) == 1:
            # found the bugger, lets update the status to pending and queue a new transaction
            tx = image_tx[0]
            config.db_delete(IMG_TX, tx)
            config.db_commit()
            logger.info("Transaction Removed")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transaction removed'}))
        else:
            # if we get here it means we have multiple identical transactions queue'd up so lets report how many we found and remove them
            logger.warning(
                "Multiple identical transactions found (%s), there is probably a database issue or a problem with defaults replication" % len(
                    image_tx))
            tx = image_tx[0]
            config.db_delete(IMG_TX, tx)
            config.db_commit()
            logger.info("Transfer re-queued")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transaction removed'}))
    else:
        # not a post
        config.db_close()
        return None


@silkp(name="CLI Image List")
@requires_csrf_token
def image_list(request):
    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        # return error http response
        return HttpResponse(json.dumps({'response_code': rc, 'message': msg}))

    # Validate input fields.
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0:
        # Invalid fields, return message
        config.db_close()
        return HttpResponse(json.dumps({'response_code': rc, 'message': msg}))

    # Retrieve image info information.
    # from requests get group, cloud (optional)
    group = active_user.active_group
    if "cloud-name" in fields:
        cloud = fields["cloud-name"]
    elif "cloud_name" in fields:
        cloud = fields["cloud_name"]
    else:
        cloud = None

    sql = "select rank() over (partition by rank order by group_name,cloud_name,name,created_at,checksum) as rank,group_name,cloud_name,name,created_at,checksum,size from (select 1 as rank,i.* from (select * from cloud_images) as i) as i where cloud_type='openstack';"
    config.db_execute(sql)
    image_list = []
    for row in config.db_cursor:
        image_list.append(row)
    image_list = _trim_image_list(image_list, group, cloud)

    config.db_close()

    # Render the page.
    context = {
        'active_user': active_user.username,
        'active_group': active_user.active_group,
        'user_groups': active_user.user_groups,
        'image_list': image_list,
        'response_code': 0,
        'message': None,
        'version': config.get_version()
    }

    return HttpResponse(json.dumps(context))
