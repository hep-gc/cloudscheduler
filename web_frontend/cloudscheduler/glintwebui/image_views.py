import time
import os
import json
import logging
import urllib3
import redis
import bcrypt

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
import glintwebui.config as config
from django.conf import settings
db_config = settings.CSV2_CONFIG


from .glint_api import repo_connector
from .glint_utils import get_unique_image_list, get_images_for_group, parse_pending_transactions, \
    build_id_lookup_dict, repo_modified, find_image_by_name, add_cached_image, \
    check_cached_images, increment_transactions, check_for_existing_images, get_num_transactions

from .__version__ import version

from cloudscheduler.lib.web_profiler import silk_profile as silkp


logger = logging.getLogger('glintv2')

def getUser(request):
    user = request.META.get('REMOTE_USER')
    db_config.db_open()
    session = db_config.db_session
    Glint_User = db_config.db_map.classes.csv2_user
    auth_user_list = session.query(Glint_User)
    for auth_user in auth_user_list:
        if user == auth_user.cert_cn or user == auth_user.username:
            db_config.db_close()
            return auth_user
    db_config.db_close()


def verifyUser(request):
    auth_user = getUser(request)
    return bool(auth_user)

def getSuperUserStatus(request):
    auth_user = getUser(request)
    if auth_user is None:
        return False
    else:
        return auth_user.is_superuser

''' Index is longer used as it was simply creating overhead, index requests now go directly to project details
@silkp(name='Images Index')
def index(request):

    if not verifyUser(request):
        raise PermissionDenied

    # set up database objects
    Base, session = get_db_base_and_session()
    User_Group = Base.classes.csv2_user_groups


    user_obj = getUser(request)
    user_group = session.query(User_Group).filter(User_Group.username == user_obj.username)
    if user_group is None:
        #User has access to no groups yet, tell them to contact admin
        #Render index page that has the above info
        pass
    else:
        #Else go to the last group that was active for that user
        active_group = user_obj.active_group
        return project_details(request, active_group)

    context = {
        'groups': User_Group.objects.all(),
        'user': getUser(request).username,
        'all_users': User.objects.all(),
    }
    return render(request, 'glintwebui/index.html', context)

'''

@silkp(name='View Image Matrix')
def project_details(request, group_name=None, message=None):
    # Since img name, img id is no longer a unique way to identify images across clouds
    # We will instead only use image name, img id will be used as a unique ID inside a given repo
    # this means we now have to create a new unique image set that is just the image names
    if not verifyUser(request):
        raise PermissionDenied

    # set up database objects
    user_obj = getUser(request)
    db_config.db_open()
    session = db_config.db_session
    User_Group = db_config.db_map.classes.csv2_user_groups
    Group_Defaults = db_config.db_map.classes.csv2_group_defaults

    

    if group_name is None:
        group_name = user_obj.active_group
    if group_name is None:
        # First time user, lets put them at the first project the have access to
        try:
            group_name = session.query(User_Group).filter(User_Group.username == user_obj.username).first().group_name.group_name
            if not group_name:
                group_name = "No groups available"
        except Exception:
            # catches nonetype error
            group_name = "No groups available"

    defaults = session.query(Group_Defaults).get(group_name)
    if defaults.vm_image is None or defaults.vm_image=="":
        default_image = None
    else:
        default_image = defaults.vm_image

    user_obj.active_group = group_name
    session.merge(user_obj)
    session.commit()


    try:
        image_set = get_unique_image_list(group_name)
        #hidden_image_set = get_hidden_image_list(group_name)
        json_dict = get_images_for_group(group_name)
        if json_dict:
            image_dict = json.loads(json_dict)
            # since we are using name as the unique identifer we need to pass in a dictionary
            # that lets us get the image id (uuid) from the repo and image name
            # We will have to implement logic here that spots two images with the same name
            # and forces the user to resolve
            reverse_img_lookup = build_id_lookup_dict(image_dict)
        else:
            image_dict = None
            reverse_img_lookup = None
    except Exception as exc:
        # No images in database yet may want some logic here forcing it to wait a little on start up
        logger.info("No images yet in database, or possible error collecting image sets")
        logger.error(exc)
        image_set = None
        #hidden_image_set = None
        image_dict = None
        reverse_img_lookup = None
        # Should render a page here that says no image info available please refresh in 20 seconds

    # The image_list is a unique list of images stored in tuples (img_id, img_name)
    # Still need to add detection for images that have different names but the same ID
    user_groups = session.query(User_Group).filter(User_Group.username == user_obj.username)
    group_list = []
    for grp in user_groups:
        grp_name = grp.group_name
        group_list.append(grp_name)

    #conflict_dict = get_conflicts_for_group(group_name)
    num_tx = get_num_transactions()
    if num_tx is None:
        num_tx = 0
    context = {
        'active_group': group_name,
        'user_groups': group_list,
        'image_dict': image_dict,
        'image_set': image_set,
        #'hidden_image_set': hidden_image_set,
        'image_lookup': reverse_img_lookup,
        'message': message,
        'is_superuser': getSuperUserStatus(request),
        #'conflict_dict': conflict_dict,
        'version': version,
        'num_tx': num_tx,
        'default_image': default_image,
        'enable_glint': True
    }
    db_config.db_close()
    return render(request, 'glintwebui/project_details.html', context)


'''
#displays the form for adding a repo to a project and handles the post request
def add_repo(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        form = addRepoForm(request.POST)
        user = getUser(request)
        # setup database objects
        Base, session = get_db_base_and_session()
        Group_Resources = Base.classes.csv2_clouds

        #Check if the form data is valid
        if form.is_valid():
            logger.info("Attempting to add new repo for User:" + user.username)
            # all data is exists, check if the repo is valid
            validate_resp = validate_repo(
                auth_url=form.cleaned_data['auth_url'],
                tenant_name=form.cleaned_data['tenant'],
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                user_domain_name=form.cleaned_data['user_domain_name'],
                project_domain_name=form.cleaned_data['project_domain_name'])
            if validate_resp[0]:
                #check if repo/auth_url combo already exists
                try:
                    if session.query(Group_Resources).filter(Group_Resources.group_name == group_name, Group_Resources.project == form.cleaned_data['tenant'], Group_Resources.authurl == form.cleaned_data['auth_url']).first() is not None:
                        #This combo already exists
                        context = {
                            'group_name': group_name,
                            'error_msg': "Repo already exists"
                        }
                        return render(request, 'glintwebui/add_repo.html', context, {'form': form})
                except Exception:
                    # this exception could be tightened around the django "DoesNotExist" exception
                    pass
                #check if cloud_name is already in use
                try:
                    if session.query(Group_Resources).filter(Group_Resources.group_name == group_name, Group_Resources.cloud_name == form.cleaned_data['cloud_name']).first() is not None:
                        #This cloud_name already exists
                        context = {
                            'group_name': group_name,
                            'error_msg': "Cloud name already in use"
                        }
                        return render(request, 'glintwebui/add_repo.html', context, {'form': form})
                except Exception:
                    # this exception could be tightened around the django "DoesNotExist" exception
                    pass

                new_repo = Group_Resources(
                    group_name=group_name,
                    authurl=form.cleaned_data['auth_url'],
                    project=form.cleaned_data['tenant'],
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    cloud_name=form.cleaned_data['cloud_name'],
                    user_domain_name=form.cleaned_data['user_domain_name'],
                    project_domain_name=form.cleaned_data['project_domain_name'],
                    cloud_type="openstack")
                session.merge(new_repo)
                session.commit()
                repo_modified()


                #return to manage repos page after saving the new repo
                return manage_repos(
                    request,
                    group_name,
                    feedback_msg="Project: " + form.cleaned_data['tenant'] + " added")
            else:
                #something in the repo information is bad
                form = addRepoForm()
                context = {
                    'group_namegroup_name': group_name,
                    'error_msg': validate_resp[1]
                }
                logger.error("Failed to add repo.")
            return render(request, 'glintwebui/add_repo.html', context, {'form': form})

        # Else there has been an error in the entry, display form with error msg
        else:
            form = addRepoForm()
            context = {
                'group_namegroup_name': group_name,
                'error_msg': "Invalid form enteries."
            }
            return render(request, 'glintwebui/add_repo.html', context, {'form': form})

    #Not a post request, display form
    else:
        form = addRepoForm()
        context = {
            'group_name': group_name,
        }
        return render(request, 'glintwebui/add_repo.html', context, {'form': form})
'''

@silkp(name='Save Images')
def save_images(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        # set up database objects
        user = getUser(request)
        db_config.db_open()
        session = db_config.db_session
        Group_Resources = db_config.db_map.classes.csv2_clouds
        
        #get repos
        repo_list = session.query(Group_Resources).filter(Group_Resources.group_name == group_name)

        # need to iterate thru a for loop of the repos in this group and get the list for each and
        # check if we need to update any states. Every image will have to be checked since if
        # they are not present it means they need to be deleted
        for repo in repo_list:
            # these check lists will have all of the images that are checked and need to be cross
            # referenced against the images stored in redis to detect changes in state
            check_list = request.POST.getlist(repo.cloud_name)
            parse_pending_transactions(
                group_name=group_name,
                cloud_name=repo.cloud_name,
                image_list=check_list,
                user=user.username)

        #give collection thread a couple seconds to process the request
        #ideally this will be removed in the future
        time.sleep(2)
        message = "Please allow glint a few seconds to proccess your request."
        db_config.db_close()
        return project_details(request=request, message=message)
    #Not a post request, display matrix
    else:
        return project_details(request=request, group_name=group_name)

'''
# Out of date // Unused
def resolve_conflict(request, group_name, cloud_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = getUser(request)

        #setup database objects
        Base, session = get_db_base_and_session()
        Group_Resources = Base.classes.csv2_clouds

        repo_obj = session.query(Group_Resources).filter(Group_Resources.group_name == group_name, Group_Resources.cloud_name == cloud_name).first()
        image_dict = json.loads(get_images_for_group(group_name))
        changed_names = 0
        #key is img_id, calue is image name
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                # check if the name has been changed, if it is different, send update
                if value != image_dict[cloud_name][key]['name']:
                    change_image_name(
                        repo_obj=repo_obj,
                        img_id=key,
                        old_img_name=image_dict[cloud_name][key]['name'],
                        new_img_name=value,
                        user=user.username)
                    changed_names = changed_names+1
        if changed_names == 0:
            # Re render resolve conflict page
            # for now this will do nothing and we trust that the user will change the name.
            context = {
                'groups': User_Group.objects.all(),
                'user': user.username,
                'all_users': User.objects.all(),
            }
            return render(request, 'glintwebui/index.html', context)

    repo_modified()
    time.sleep(6)
    return project_details(request, group_name, "")
'''


@silkp(name='Download Image')
def download_image(request, image_name, group_name=None):
    if not verifyUser(request):
        raise PermissionDenied
    user_obj = getUser(request)
    if group_name is None:
        group_name = user_obj.active_group


    logger.info("Preparing to download image file.")
    image_info = find_image_by_name(group_name=group_name, image_name=image_name)

    # Find image location
    image_id = image_info[4]

    # Check download location to see if image is there already
    # This function should update the timestamp if it finds a hit
    tentative_path = check_cached_images(image_name, image_info[5])
    if tentative_path is not None:
        #return the image using this path
        logger.info("Found cached local copy...")
        filename = image_name
        response = StreamingHttpResponse((line for line in open(tentative_path, 'r')))
        response['Content-Disposition'] = "attachment; filename={0}".format(filename)
        response['Content-Length'] = os.path.getsize(tentative_path)
        return response

    # Download image

    if not os.path.exists("/var/www/glintv2/scratch/"):
        os.makedirs("/var/www/glintv2/scratch/")
    logger.info("No cached copy found, downloading image file.")
    rcon = repo_connector(
        auth_url=image_info[0],
        project=image_info[1],
        username=image_info[2],
        password=image_info[3])
    rcon.download_image(
        image_name=image_name,
        image_id=image_id,
        scratch_dir="/var/www/glintv2/scratch/")

    # add to download table in redis
    filename = image_name
    file_full_path = "/var/www/glintv2/scratch/" + image_name
    add_cached_image(image_name, image_checksum=image_info[5], full_path=file_full_path)


    response = StreamingHttpResponse((line for line in open(file_full_path, 'rb')))
    response['Content-Disposition'] = "attachment; filename={0}".format(filename)
    response['Content-Length'] = os.path.getsize(file_full_path)
    return response

@silkp(name='Upload Image')
def upload_image(request, group_name=None):
    if not verifyUser(request):
        raise PermissionDenied
    user_obj = getUser(request)
    if group_name is None:
        group_name = user_obj.active_group
    try:
        image_file = request.FILES['myfile']
    except Exception:
        # no file means it's not a POST or it's an upload by URL
        image_file = False

    if request.method == 'POST' and image_file:

        #process image upload
        image_file = request.FILES['myfile']
        file_path = "/var/www/glintv2/scratch/" + image_file.name

        #before we save it locally let us check if it is already in the repos
        cloud_name_list = request.POST.getlist('clouds')
        bad_clouds = check_for_existing_images(group_name, cloud_name_list, image_file.name)
        if len(bad_clouds) > 0:
            for cloud in bad_clouds:
                cloud_name_list.remove(cloud)
            message = ("Upload failed for one or more projects because"
                       " the image name was already in use.")

        if len(cloud_name_list) == 0:
            #if we have eliminated all the target clouds, return with error message
            message = ("Upload failed to all target projects because"
                       " the image name was already in use.")
            image_dict = json.loads(get_images_for_group(group_name))
            context = {
                'group_name': group_name,
                'image_dict': image_dict,
                'max_repos': len(image_dict),
                'message': message
            }
            return render(request, 'glintwebui/upload_image.html', context)

        #And finally before we save locally double check that file doesn't already exist
        valid_path = True
        if os.path.exists(file_path):
            valid_path = False
            # Filename exists locally, we need to use a temp folder
            for x in range(0, 10):
                #first check if the temp folder exists
                file_path = "/var/www/glintv2/scratch/" + str(x)
                if not os.path.exists(file_path):
                    #create temp folder and break since it is definitly empty
                    os.makedirs(file_path)
                    file_path = "/var/www/glintv2/scratch/" + str(x) + "/" + image_file.name
                    valid_path = True
                    break

                #then check if the file is in that folder
                file_path = "/var/www/glintv2/scratch/" + str(x) + "/" + image_file.name
                if not os.path.exists(file_path):
                    valid_path = True
                    break

        if not valid_path:
            #turn away request since there is already multiple files with this name being uploaded
            image_dict = json.loads(get_images_for_group(group_name))
            context = {
                'group_name': group_name,
                'image_dict': image_dict,
                'max_repos': len(image_dict),
                'message': ("Too many images by that name being uploaded,"
                            " please try again in a few minutes.")
            }
            return render(request, 'glintwebui/upload_image.html', context)

        disk_format = request.POST.get('disk_format')
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # now queue the uploads to the destination clouds
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        user = getUser(request)
        for cloud in cloud_name_list:
            logger.info("Queing image upload to %s", cloud)
            transaction = {
                'user': user.username,
                'action':  'upload',
                'group_name': group_name,
                'repo': cloud,
                'image_name': image_file.name,
                'local_path': file_path,
                'disk_format': disk_format,
                'container_format': "bare"
            }
            trans_key = group_name + "_pending_transactions"
            red.rpush(trans_key, json.dumps(transaction))
            increment_transactions()

        #return to project details page with message
        return redirect('project_details', group_name=group_name)

    elif request.method == 'POST' and request.POST.get('myfileurl'):

        #download the image
        img_url = request.POST.get('myfileurl')
        image_name = img_url.rsplit("/", 1)[-1]
        file_path = "/var/www/glintv2/scratch/" + image_name
        # check if a file with that name already exists
        valid_path = True
        if os.path.exists(file_path):
            valid_path = False
            # Filename exists locally, we need to use a temp folder
            for x in range(0, 10):
                #first check if the temp folder exists
                file_path = "/var/www/glintv2/scratch/" + str(x)
                if not os.path.exists(file_path):
                    #create temp folder and break since it is definitly empty
                    os.makedirs(file_path)
                    file_path = "/var/www/glintv2/scratch/" + str(x) + "/" + image_name
                    valid_path = True
                    break

                #then check if the file is in that folder
                file_path = "/var/www/glintv2/scratch/" + str(x) + "/" + image_name
                if not os.path.exists(file_path):
                    valid_path = True
                    break

        if not valid_path:
            #turn away request since there is already multiple files with this name being uploaded
            image_dict = json.loads(get_images_for_group(group_name))
            context = {
                'group_name': group_name,
                'image_dict': image_dict,
                'max_repos': len(image_dict),
                'message': "Too many images by that name being uploaded or bad URL, please check the url and try again in a few minutes."
            }
            return render(request, 'glintwebui/upload_image.html', context)

        # Probably could use some checks here to make sure it is a valid image file.
        # In reality the user should be smart enough to only put in an image file and
        # in the case where they aren't openstack will still except the garbage file
        # as a raw image.
        image_data = urllib3.urlopen(img_url)

        with open(file_path, "wb") as image_file:
            image_file.write(image_data.read())

        disk_format = request.POST.get('disk_format')
        # now upload it to the destination clouds
        cloud_name_list = request.POST.getlist('clouds')
        red = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
        user = getUser(request)
        for cloud in cloud_name_list:
            transaction = {
                'user': user.username,
                'action':  'upload',
                'group_name': group_name,
                'repo': cloud,
                'image_name': image_name,
                'local_path': file_path,
                'disk_format': disk_format,
                'container_format': "bare"
            }
            trans_key = group_name + "_pending_transactions"
            red.rpush(trans_key, json.dumps(transaction))
            increment_transactions()

        #return to project details page with message
        return redirect('project_details', group_name=group_name)
    else:
        #render page to upload image

        image_dict = json.loads(get_images_for_group(group_name))
        context = {
            'group_name': group_name,
            'image_dict': image_dict,
            'max_repos': len(image_dict),
            'message': None
        }
        return render(request, 'glintwebui/upload_image.html', context)

