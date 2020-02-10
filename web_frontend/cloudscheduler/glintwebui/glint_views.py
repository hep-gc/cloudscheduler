import time
import logging
import os
import json
import urllib3

from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse, StreamingHttpResponse
from django.core.exceptions import PermissionDenied

from .glint_utils import get_openstack_session, get_glance_client, delete_image, check_cache, generate_tx_id, get_image, download_image, upload_image

from cloudscheduler.lib.view_utils import \
    render, \
    lno, \
    set_user_groups
from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.web_profiler import silk_profile as silkp

from .celery_app import pull_request, tx_request

logger = logging.getLogger('glintv2')
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
            if cloud.cloud_name in image_dict[image_key].keys():
                #image is here
                row_list.append((image_dict[image_key][cloud.cloud_name]["status"],image_dict[image_key][cloud.cloud_name]["message"],image_dict[image_key][cloud.cloud_name]["visibility"], cloud.cloud_name))
            else:
                #image is not here
                row_list.append(("missing","","",cloud.cloud_name))
        image_matrix[image_key] = row_list


    return image_matrix



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
# Djnago View Functions
#

@silkp(name="Image List")
@requires_csrf_token
def list(request, args=None, response_code=0, message=None):
    config.db_open()
    IMAGES = config.db_map.classes.cloud_images
    IMAGE_TX = config.db_map.classes.csv2_image_transactions
    CLOUDS = config.db_map.classes.csv2_clouds
    GROUPS = config.db_map.classes.csv2_groups
    db_session = config.db_session

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
    msg=message

    group = active_user.active_group
    images = db_session.query(IMAGES).filter(IMAGES.group_name == group, IMAGES.cloud_type == "openstack")
    clouds = db_session.query(CLOUDS).filter(CLOUDS.group_name == group, CLOUDS.cloud_type == "openstack")
    defaults = db_session.query(GROUPS).get(group)
    if defaults.vm_image is None or defaults.vm_image=="":
        default_image = None
    else:   
        default_image = defaults.vm_image



    pending_tx = db_session.query(IMAGE_TX).filter(IMAGE_TX.target_group_name == group)
    image_dict = _build_image_dict(images, pending_tx)
    matrix = _build_image_matrix(image_dict, clouds)
    
    #build context and render matrix



    context = {
        #function specific data
        'image_dict': matrix,
        'cloud_list': clouds,
        'default_image': default_image,

        #view agnostic data
        'active_user': active_user.username,
        'active_group': active_user.active_group,
        'user_groups': active_user.user_groups,
        'response_code': rc,
        'message': msg,
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
        return HttpResponse(json.dumps({'response_code': 1,  'message': '%s %s' % (lno(MODID), msg)}))

    if request.method == 'POST':
        IMAGES = config.db_map.classes.cloud_images
        IMAGE_TX = config.db_map.classes.csv2_image_transactions


        # Should have the following data in POST:
        #    (image_name + '---' + image_checksum, target_cloud, group)
        post_data = json.loads(request.body)
        image_name = ""
        image_checksum = None
        image_key = post_data.get("image_key")
        target_cloud = post_data.get("cloud_name")
        target_group = post_data.get("group_name")
        key_list = image_key.split("---")
        if len(key_list) != 2:
            if image_checksum is None:
                # we don't have the image checksum so we need to try and figure out what it is via the database
                # if it is an ambiguous image name we can't fufill the request otherwise we can fill in the
                # checksum and continue as normal
                image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == target_group, IMAGES.name == image_key)
                if len(image_candidates) > 1:
                    #ambiguous image name, need a checksum
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
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
            # Image or request already exists, return  with message
            return HttpResponse(json.dumps({'response_code': 1,  'message': '%s %s'  % (lno(MODID), 'Image request exists or image already on cloud')}))

        # if we get here everything is golden and we can queue up tha transfer request, but first lets check if the image
        # is in the cache or we should queue up a pull request, check cache returns True if it is found/queued or false
        # if it was unable to find the image
        cache_result = check_cache(config, image_name, image_checksum, target_group, active_user)
        if cache_result is False:
            return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), "Could not find a source image...")}))
        target_image = get_image(config, image_name, image_checksum, target_group)
        tx_id = generate_tx_id()
        tx_req = {
            "tx_id":             tx_id,
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
        #tx_request.delay(tx_id = tx_id)
        logger.info("Transfer queued")
        tx_request.apply_async((tx_id,), queue='tx_requests')
        return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transfer queued..'}))

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
        image_checksum = None
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
                image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == target_group, IMAGES.name == image_key)
                if len(image_candidates) > 1:
                    #ambiguous image name, need a checksum
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                else:
                    image_checksum = image_candidates[0].checksum
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]
            image_checksum = key_list[1]


        logger.error("GETTING IMAGE: %s::%s::%s::%s" % (image_name, image_checksum, target_group, target_cloud))
        target_image = get_image(config, image_name, image_checksum, target_group, target_cloud)
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


@silkp(name='Image Upload')
@requires_csrf_token
def upload(request, group_name=None):
    config.db_open()

    IMAGES = config.db_map.classes.cloud_images
    IMAGE_TX = config.db_map.classes.csv2_image_transactions
    CLOUDS = config.db_map.classes.csv2_clouds
    CACHE_IMAGES = config.db_map.classes.csv2_image_cache

    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        #return render(request, 'glintwebui/images.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
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
            logger.error("No group name, using user's default")
            group_name = active_user.default_group

        #process image upload
        image_file = request.FILES['myfile']
        file_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_file.name # This file will have to be renamed with the checksum after uploading to a cloud

        #before we save it locally let us check if it is already in the repos
        cloud_name_list = request.POST.getlist('clouds')
        image_list = config.db_session.query(IMAGES).filter(IMAGES.name == image_file.name, IMAGES.group_name == group_name)
        bad_clouds = []
        if image_list.count() > 0:
            #we've got some images by this name already lets see if any are in the target clouds
            for image in image_list:
                if image.cloud_name in cloud_name_list:
                    bad_clouds.append(image.cloud_name)
        if len(bad_clouds) > 0:
            for cloud in bad_clouds:
                cloud_name_list.remove(cloud)
            msg = ("Upload failed for one or more projects because the image name was already in use.")

        if len(cloud_name_list) == 0:
            #if we have eliminated all the target clouds, return with error message
            msg = "Upload failed to all target projects because the image name was already in use."
            cloud_list = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group_name, CLOUDS.cloud_type == "openstack")
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': cloud_list.count(),
                'redirect': "false",

                #view agnostic data
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

        #And finally before we save locally double check that file doesn't already exist
        if os.path.exists(file_path):
            # Filename exists locally, lets add some random suffix and check again
            suffix = 1
            new_path = file_path + str(suffix)
            while os.path.exists(new_path):
                suffix = suffix + 1
                new_path = file_path + str(suffix)
            file_path = new_path
            

        disk_format = request.POST.get('disk_format')
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # Now we have a source file we need to upload it to one of the clouds to get a checksum so we can queue up transfer requests
        # get a cloud of of the list, first one is fine
        target_cloud_name = cloud_name_list[0]
        # get the cloud row for this cloud
        target_cloud = config.db_session.query(CLOUDS).get((group_name, target_cloud_name))
        os_session = get_openstack_session(target_cloud)
        glance = get_glance_client(os_session, target_cloud.region)

        logger.info("uploading image %s to cloud %s" % (image_file.name, target_cloud_name))

        image = upload_image(glance, None, image_file.name, file_path, disk_format=request.POST.get('disk_format'))
        logger.info("Upload result: %s" % image)
        # add it to the csv2_images table
        if image.size == "":
            size = 0
        else:
            size = image.size
        new_image_dict = {
            'group_name': target_cloud.group_name,
            'cloud_name': target_cloud.cloud_name,
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
            'last_updated': time.time()
        }
        img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=new_image_dict)
        if unmapped:
            logging.error("Unmapped attributes found during mapping, discarding:")
            logging.error(unmapped)
        new_image = IMAGES(**new_image_dict)
        config.db_session.merge(new_image)
        config.db_session.commit()


        # now we have the os image object, lets rename the file and add it to out cache
        cache_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_file.name + "---" + image.checksum
        os.rename(file_path, cache_path)

        cache_dict = {
                "image_name": image_file.name,
                "checksum": image.checksum,
                "container_format": image.container_format,
                "disk_format": image.disk_format
        }
        new_cache_item = CACHE_IMAGES(**cache_dict)
        config.db_session.merge(new_cache_item)
        config.db_session.commit()

        #now we need to queue transfer requests for the remaining clouds
        cloud_name_list.remove(target_cloud_name)
        if len(cloud_name_list) == 0:
            # we are done and can return successfully
            cloud_list = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group_name, CLOUDS.cloud_type == "openstack")
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': cloud_list.count(),
                'redirect': "true",

                #view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': rc,
                'message': "Upload Successful, returning to images...",
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
                    "tx_id":             tx_id,
                    "status":            "pending",
                    "target_group_name": group_name,
                    "target_cloud_name": cloud,
                    "image_name":        image_file.name,
                    "image_id":          image.id,
                    "checksum":          image.checksum,
                    "requester":         active_user.username,
                }
                new_tx_req = IMAGE_TX(**tx_req)
                config.db_session.merge(new_tx_req)
                config.db_session.commit()
                logger.info("Transfer id:%s queued" % tx_id)
                tx_request.apply_async((tx_id,), queue='tx_requests')

        #return to project details page with message
        msg="Uploads successfully queued, returning to images..."
        cloud_list = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group_name, CLOUDS.cloud_type == "openstack")
        context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': cloud_list.count(),
                'redirect': "true",

                #view agnostic data
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
            group_name = active_user.default_group


        #download the image
        img_url = request.POST.get('myfileurl')
        image_name = img_url.rsplit("/", 1)[-1]
        logger.info("File to upload: %s" % image_name)
        file_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_name # This file will have to be renamed with the checksum after uploading to a cloud

        # check if a file with that name already exists
        if os.path.exists(file_path):
            # Filename exists locally, lets add some suffix and check again
            suffix = 1
            new_path = file_path + str(suffix)
            while os.path.exists(new_path):
                suffix = suffix + 1
                new_path = file_path + str(suffix)
            file_path = new_path

        #before we save it locally let us check if it is already in the repos
        cloud_name_list = request.POST.getlist('clouds')
        image_list = config.db_session.query(IMAGES).filter(IMAGES.name == image_name, IMAGES.group_name == group_name)
        bad_clouds = []
        if image_list.count() > 0:
            #we've got some images by this name already lets see if any are in the target clouds
            for image in image_list:
                if image.cloud_name in cloud_name_list:
                    bad_clouds.append(image.cloud_name)
        if len(bad_clouds) > 0:
            for cloud in bad_clouds:
                cloud_name_list.remove(cloud)
            msg = ("Upload failed for one or more projects because the image name was already in use.")

        if len(cloud_name_list) == 0:
            #if we have eliminated all the target clouds, return with error message
            message = ("Upload failed to all target projects because the image name was already in use.")
            cloud_list = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group_name, CLOUDS.cloud_type == "openstack")
            context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': cloud_list.count(),
                'redirect': "false",

                #view agnostic data
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
            

        http = urllib3.PoolManager()
        image_data = http.request('GET', img_url)

        with open(file_path, "wb") as image_file:
            image_file.write(image_data.read())

        disk_format = request.POST.get('disk_format')
        
        #Now we have a source file we need to upload it to one of the clouds to get a checksum so we can queue up transfer requests
        # get a cloud of of the list, first one is fine
        target_cloud_name = cloud_name_list[0]
        # get the cloud row for this cloud
        target_cloud = config.db_session.query(CLOUDS).get((group_name, target_cloud_name))
        os_session = get_openstack_session(target_cloud)
        glance = get_glance_client(os_session, target_cloud.region)

        image = upload_image(glance, None, image_file.name, file_path, disk_format=request.POST.get('disk_format'))
        # add it to the csv2_images table
        if image.size == "":
            size = 0
        else:
            size = image.size
        new_image_dict = {
            'group_name': target_cloud.group_name,
            'cloud_name': target_cloud.cloud_name,
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
            'last_updated': time.time()
        }
        img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=new_image_dict)
        if unmapped:
            logging.error("Unmapped attributes found during mapping, discarding:")
            logging.error(unmapped)
        new_image = IMAGES(**new_image_dict)
        config.db_session.merge(new_image)
        config.db_session.commit()
        # now we have the os image object, lets rename the file and add it to out cache
        cache_path = image_file.name + "---" + image.checksum
        os.rename(file_path, cache_path)

        cache_dict = {
                "image_name": image_file.name,
                "checksum": image.checksum,
                "container_format": image.container_format,
                "disk_format": image.disk_format
        }
        new_cache_item = CACHE_IMAGES(**cache_dict)
        config.db_session.merge(new_cache_item)
        config.db_session.commit()

        #now we need to queue transfer requests for the remaining clouds
        cloud_name_list.remove(target_cloud_name)
        if len(cloud_name_list) == 0:
            # we are done and can return successfully
            pass
        else:
            # loop over remaining clouds and queue transfers
            for cloud in cloud_name_list:
                tx_id = generate_tx_id()
                tx_req = {
                    "tx_id":             tx_id,
                    "status":            "pending",
                    "target_group_name": group_name,
                    "target_cloud_name": cloud,
                    "image_name":        image_file.name,
                    "image_id":          image.id,
                    "checksum":          image.checksum,
                    "requester":         active_user.username,
                }
                new_tx_req = IMAGE_TX(**tx_req)
                config.db_session.merge(new_tx_req)
                config.db_session.commit()
                logger.info("Transfer id:%s queued" % tx_id)
                tx_request.apply_async((tx_id,), queue='tx_requests')

        #return to project details page with message
        cloud_list = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group_name, CLOUDS.cloud_type == "openstack")
        context = {
                'group_name': group_name,
                'cloud_list': cloud_list,
                'max_repos': cloud_list.count(),
                'redirect': "true",

                #view agnostic data
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': rc,
                'message': "Uploads queued successfully, returning to images...",
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            }
        config.db_close()
        return render(request, 'glintwebui/upload_image.html', context)
    else:
        #render page to upload image
        cloud_list = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group_name, CLOUDS.cloud_type == "openstack")
        context = {
            'group_name': group_name,
            'cloud_list': cloud_list,
            'max_repos': cloud_list.count(),
            'redirect': "false",

            #view agnostic data
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



@silkp(name="Image Download")
@requires_csrf_token
def download(request, group_name, image_key, args=None, response_code=0, message=None):
    config.db_open()
    db_session = config.db_session
    IMAGES = config.db_map.classes.cloud_images
    CACHE_IMAGES = config.db_map.classes.csv2_image_cache
    CLOUD = config.db_map.classes.csv2_clouds

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
            image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == group_name, IMAGES.name == image_key)
            if len(image_candidates) > 1:
                return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
            else:
                image_checksum = image_candidates[0].checksum
        # Once we get here we have the checksum so assign the image_name and continue as normal
        image_name = image_key
    else:
        # key is normal
        image_name = key_list[0]
        image_checksum = key_list[1]


    #if the image is not in the cache, download it and update the cache table
    cached_images = db_session.query(CACHE_IMAGES).filter(CACHE_IMAGES.image_name == image_name, CACHE_IMAGES.checksum == image_checksum)
    if cached_images.count() > 0:
        # we've got the image cached already, we can go ahead and serve from this file
        image_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_name + "---" + image_checksum
        response = StreamingHttpResponse((line for line in open(image_path, 'rb')))
        response['Content-Disposition'] = "attachment; filename={0}".format(image_name)
        response['Content-Length'] = os.path.getsize(image_path)
        config.db_close()
        return response


    else:
        # we need to download the image first and update the cache
        # find a source image
        image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == group_name, IMAGES.name == image_name, IMAGES.checksum == image_checksum)
        if image_candidates.count() == 0:
            # we didnt find a source
            return False # report error
        else:
            src_image = image_candidates[0]
        cloud_row = config.db_session.query(CLOUD).get((group_name, src_image.cloud_name))
        os_session = get_openstack_session(cloud_row)
        glance = get_glance_client(os_session, cloud_row.region)
        result_tuple = download_image(glance, image_name, src_image.id, image_checksum, config.categories["glintPoller.py"]["image_cache_dir"])
        if result_tuple[0]:
            # successful download, update the cache and remove transaction
            cache_dict = {
                "image_name": image_name,
                "checksum": image_checksum,
                "container_format": result_tuple[3],
                "disk_format": result_tuple[2]
            }
            new_cache_item = CACHE_IMAGES(**cache_dict)
            config.db_session.merge(new_cache_item)
            config.db_session.commit()
            # ok we've got the image we can finally serve it up
            image_path = config.categories["glintPoller.py"]["image_cache_dir"] + image_name + "---" + image_checksum
            response = StreamingHttpResponse((line for line in open(image_path, 'rb')))
            response['Content-Disposition'] = "attachment; filename={0}".format(image_name)
            response['Content-Length'] = os.path.getsize(image_path)
            config.db_close()
            return response


        else:
            # Download failed for whatever reason, update message and return to images page
            # check result_tuple for error message
            return None

    return None



@silkp(name="Retry Tansaction")
@requires_csrf_token
def retry(request, args=None, response_code=0, message=None):
    config.db_open()
    db_session = config.db_session
    IMAGES = config.db_map.classes.cloud_images
    CLOUDS = config.db_map.classes.csv2_clouds
    IMG_TX = config.db_map.classes.csv2_image_transactions

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
                image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == target_group, IMAGES.name == image_key)
                if len(image_candidates) > 1:
                    #ambiguous image name, need a checksum
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                else:
                    image_checksum = image_candidates[0].checksum
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]
            image_checksum = key_list[1]
        
        image_tx = config.db_session.query(IMG_TX).filter(IMG_TX.image_name == image_name, IMG_TX.checksum == image_checksum, IMG_TX.target_cloud_name == target_cloud, IMG_TX.target_group_name == target_group)
        if image_tx.count() == 0:
            # no transaction found
            logger.error("No transaction found for image:%s on group::cloud: %s::%s" % (image_name, target_group, target_cloud))
            return HttpResponse(json.dumps({'response_code': 1, 'message': "No transaction found for image:%s on group::cloud: %s::%s" % (image_name, target_group, target_cloud)}))
        elif image_tx.count() == 1:
            #found the bugger, lets update the status to pending and queue a new transaction
            redo_tx = image_tx[0]
            redo_tx.status = "pending"
            redo_tx.message = "Retrying..."
            config.db_session.merge(redo_tx)
            config.db_session.commit()
            tx_request.apply_async((redo_tx.tx_id,), queue='tx_requests')
            logger.info("Transfer re-queued")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transfer re-queued..'}))
        else:
            #if we get here it means we have multiple identical transactions queue'd up so lets report the error and just take the first one
            logger.warning("Multiple identical transactions found, there is probably a database issue or a problem with defaults replication")
            redo_tx = image_tx[0]
            redo_tx.status = "pending"
            redo_tx.message = "Retrying..."
            config.db_session.merge(redo_tx)
            config.db_session.commit()
            tx_request.apply_async((redo_tx.tx_id,), queue='tx_requests')
            logger.info("Transfer re-queued")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transfer re-queued..'}))
    else:
        #not a post
        return None


@silkp(name="Clear Tansaction")
@requires_csrf_token
def clear(request, args=None, response_code=0, message=None):
    config.db_open()
    db_session = config.db_session
    IMAGES = config.db_map.classes.cloud_images
    CLOUDS = config.db_map.classes.csv2_clouds
    IMG_TX = config.db_map.classes.csv2_image_transactions

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
                image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == target_group, IMAGES.name == image_key)
                if len(image_candidates) > 1:
                    #ambiguous image name, need a checksum
                    return HttpResponse(json.dumps({'response_code': 1, 'message': '%s %s' % (lno(MODID), "Ambigous image name, please remove duplicate names or provide a checksum")}))
                else:
                    image_checksum = image_candidates[0].checksum
            # Once we get here we have the checksum so assign the image_name and continue as normal
            image_name = image_key
        else:
            # key is normal
            image_name = key_list[0]
            image_checksum = key_list[1]
        
        image_tx = config.db_session.query(IMG_TX).filter(IMG_TX.image_name == image_name, IMG_TX.checksum == image_checksum, IMG_TX.target_cloud_name == target_cloud, IMG_TX.target_group_name == target_group)
        if image_tx.count() == 0:
            # no transaction found
            return HttpResponse(json.dumps({'response_code': 0, 'message': "No transaction found for image:%s on group::cloud: %s::%s" % (image_name, target_group, target_cloud)}))
        elif image_tx.count() == 1:
            #found the bugger, lets update the status to pending and queue a new transaction
            tx = image_tx[0]
            config.db_session.delete(tx)
            config.db_session.commit()
            logger.info("Transaction Removed")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transaction removed'}))
        else:
            #if we get here it means we have multiple identical transactions queue'd up so lets report how many we found and remove them 
            logger.warning("Multiple identical transactions found (%s), there is probably a database issue or a problem with defaults replication" % image_tx.count())
            tx = image_tx[0]
            config.db_session.delete(tx)
            config.db_session.commit()
            logger.info("Transfer re-queued")
            config.db_close()
            return HttpResponse(json.dumps({'response_code': 0, 'message': 'Transaction removed'}))
    else:
        #not a post
        return None


