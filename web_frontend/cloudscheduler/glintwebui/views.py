import time
import os
import json
import logging
import urllib2
import redis
import bcrypt

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
import glintwebui.config as config

from .models import Group_Resources, User_Group, Glint_User, Group
from .forms import addRepoForm
from .glint_api import repo_connector, validate_repo, change_image_name
from .utils import get_unique_image_list, get_images_for_group, parse_pending_transactions, \
    build_id_lookup_dict, repo_modified, get_conflicts_for_group, find_image_by_name, \
    add_cached_image, check_cached_images, increment_transactions, check_for_existing_images,\
    get_hidden_image_list, parse_hidden_images
from .__version__ import version


logger = logging.getLogger('glintv2')

def getUser(request):
    user = request.META.get('REMOTE_USER')
    auth_user_list = Glint_User.objects.all()
    for auth_user in auth_user_list:
        if user == auth_user.cert_cn or user == auth_user.username:
            return auth_user


def verifyUser(request):
    auth_user = getUser(request)
    return bool(auth_user)

def getSuperUserStatus(request):
    auth_user = getUser(request)
    if auth_user is None:
        return False
    else:
        return auth_user.is_superuser


def index(request):

    if not verifyUser(request):
        raise PermissionDenied

    # This is a good place to spawn the data-collection worker thread
    # The one drawback is if someone tries to go directly to another page before hitting this one
    # It may be better to put it in the urls.py file then pass in the repo/image info
    # If it cannot be accessed it means its deed and needs to be spawned again.
    user_obj = getUser(request)
    user_group = User_Group.objects.filter(user=user_obj)
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




def project_details(request, group_name="No groups available", message=None):
    # Since img name, img id is no longer a unique way to identify images across clouds
    # We will instead only use image name, img id will be used as a unique ID inside a given repo
    # this means we now have to create a new unique image set that is just the image names
    if not verifyUser(request):
        raise PermissionDenied
    user_obj = getUser(request)
    if group_name is None or group_name in "No groups available":
        # First time user, lets put them at the first project the have access to
        try:
            group_name = User_Group.objects.filter(user=user_obj).first().group_name.group_name
            if not group_name:
                group_name = "No groups available"
        except Exception:
            # catches nonetype error
            group_name = "No groups available"

    user_obj.active_group = group_name
    user_obj.save()


    try:
        image_set = get_unique_image_list(group_name)
        hidden_image_set = get_hidden_image_list(group_name)
        image_dict = json.loads(get_images_for_group(group_name))
        # since we are using name as the unique identifer we need to pass in a dictionary
        # that lets us get the image id (uuid) from the repo and image name
        # We will have to implement logic here that spots two images with the same name
        # and forces the user to resolve
        reverse_img_lookup = build_id_lookup_dict(image_dict)

    except Exception:
        # No images in database yet may want some logic here forcing it to wait a little on start up
        logger.info("No images yet in database, or possible error collecting image sets")
        image_set = None
        hidden_image_set = None
        image_dict = None
        reverse_img_lookup = None
        # Should render a page here that says no image info available please refresh in 20 seconds

    # The image_list is a unique list of images stored in tuples (img_id, img_name)
    # Still need to add detection for images that have different names but the same ID
    user_groups = User_Group.objects.filter(user=user_obj)
    group_list = []
    for grp in user_groups:
        grp_name = grp.group_name
        group_list.append(grp_name)
    try:
        group_list.remove(group_name)
    except ValueError:
        #list is empty
        pass

    conflict_dict = get_conflicts_for_group(group_name)
    context = {
        'group_name': group_name,
        'group_list': group_list,
        'image_dict': image_dict,
        'image_set': image_set,
        'hidden_image_set': hidden_image_set,
        'image_lookup': reverse_img_lookup,
        'message': message,
        'is_superuser': getSuperUserStatus(request),
        'conflict_dict': conflict_dict,
        'version': version
    }
    return render(request, 'glintwebui/project_details.html', context)



#displays the form for adding a repo to a project and handles the post request
def add_repo(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        form = addRepoForm(request.POST)
        user = getUser(request)

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
                    if Group_Resources.objects.get(group_name=group_name, project=form.cleaned_data['tenant'], authurl=form.cleaned_data['auth_url']) is not None:
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
                    if Group_Resources.objects.get(group_name=group_name, cloud_name=form.cleaned_data['cloud_name']) is not None:
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
                    project_domain_name=form.cleaned_data['project_domain_name'])
                new_repo.save()
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

def save_images(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = getUser(request)
        #get repos
        repo_list = Group_Resources.objects.filter(group_name=group_name)

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
        return project_details(request=request, message=message)
    #Not a post request, display matrix
    else:
        return project_details(request=request, group_name=group_name)


# this function accepts a post request and updates the hidden status of any images within.
def save_hidden_images(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = getUser(request)
        #get repos
        repo_list = Group_Resources.objects.filter(group_name=group_name)

        # need to iterate thru a for loop of the repos in this group and get the list for each and
        # check if we need to change any of the hidden states
        for repo in repo_list:
            check_list = request.POST.getlist(repo.cloud_name)
            parse_hidden_images(
                group_name=group_name,
                cloud_name=repo.cloud_name,
                image_list=check_list,
                user=user.username)

    message = "Please allow glint a few seconds to proccess your request."
    return project_details(request=request, group_name=group_name, message=message)

# Out of date // Unused
def resolve_conflict(request, group_name, cloud_name):
    if not verifyUser(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = getUser(request)
        repo_obj = Group_Resources.objects.get(group_name=group_name, cloud_name=cloud_name)
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


# This page will render manage_repos.html which will allow users to add, edit, or delete repos
# It would be a good idea to redesign the add repo page to be used to update existing repos
# in addition to adding new ones. However it may be easier to just make a copy of it and modify
# it slightly for use updating existing repos.
def manage_repos(request, group_name, feedback_msg=None, error_msg=None):
    if not verifyUser(request):
        raise PermissionDenied
    user_obj = getUser(request)
    repo_list = Group_Resources.objects.filter(group_name=group_name)

    user_groups = User_Group.objects.filter(user=user_obj)
    group_list = []
    for grp in user_groups:
        grp_name = grp.group_name
        group_list.append(grp_name)
    try:
        group_list.remove(group_list)
    except ValueError:
        #list is empty
        pass

    context = {
        'group': group_name,
        'group_list': group_list,
        'repo_list': repo_list,
        'feedback_msg': feedback_msg,
        'error_msg': error_msg,
        'is_superuser': getSuperUserStatus(request),
        'version': version

    }
    return render(request, 'glintwebui/manage_repos.html', context)


def update_repo(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied
    logger.info("Attempting to update repo")
    if request.method == 'POST':
        usr = request.POST.get('username')
        pwd = request.POST.get('password')
        auth_url = request.POST.get('auth_url')
        tenant = request.POST.get('tenant')
        cloud_name = request.POST.get('cloud_name')
        project_domain_name = request.POST.get('project_domain_name')
        user_domain_name = request.POST.get('user_domain_name')

        # probably a more effecient way to do the if below, perhaps to a try without using .get
        if usr is not None and pwd is not None and auth_url is not None and tenant is not None and cloud_name is not None:
            #data is there, check if it is valid
            validate_resp = validate_repo(
                auth_url=auth_url,
                tenant_name=tenant,
                username=usr,
                password=pwd,
                user_domain_name=user_domain_name,
                project_domain_name=project_domain_name)
            if validate_resp[0]:
                # new data is good, grab the old repo and update to the new info
                repo_obj = Group_Resources.objects.get(cloud_name=cloud_name)
                repo_obj.username = usr
                repo_obj.authurl = auth_url
                repo_obj.project = tenant
                repo_obj.password = pwd
                repo_obj.project_domain_name = project_domain_name
                repo_obj.user_domain_name = user_domain_name
                repo_obj.save()
            else:
                #invalid changes, reload manage_repos page with error msg
                return manage_repos(
                    request=request,
                    group_name=group_name,
                    error_msg=validate_resp[1])
        repo_modified()
        return manage_repos(
            request=request,
            group_name=group_name,
            feedback_msg="Update Successful")

    else:
        #not a post, shouldnt be coming here, redirect to matrix page
        return project_details(request, group_name)

def delete_repo(request, group_name):
    if not verifyUser(request):
        logger.info("Verifying User")
        raise PermissionDenied
    if request.method == 'POST':
        #handle delete
        repo = request.POST.get('repo')
        cloud_name = request.POST.get('cloud_name')
        if repo is not None and cloud_name is not None:
            logger.info("Attempting to delete repo: %s", repo)
            Group_Resources.objects.filter(project=repo, cloud_name=cloud_name).delete()
            repo_modified()
            return HttpResponse(True)
        else:
            #invalid post, return false
            return HttpResponse(False)
        #Execution should never reach here, but it it does- return false
        return HttpResponse(False)
    else:
        #not a post, shouldnt be coming here, redirect to matrix page
        return project_details(request, group_name)


def add_user(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        cert_cn = request.POST.get('cert_cn')
        logger.info("Adding user %s", user)
        try:
            # Check that the passwords are valid
            if pass1 is not None and pass2 is not None:
                if pass1 != pass2:
                    logger.error("Passwords do not match")
                    message = "Passwords did not match, add user cancelled"
                    return manage_users(request, message)
                elif len(pass1) < 4:
                    logger.error("Password too short")
                    message = "Password too short, password must be at least 4 characters"
                    return manage_users(request, message)
            else:
                #else at least one of the passwords was empty
                logger.error("One or more passwords empty")
                message = "One or more passwords empty, please make sure they match"
                return manage_users(request, message)
            #passwords should be good at this point


            #check if username exists, if not add it
            user_found = Glint_User.objects.filter(username=user)
            logger.error("Found user %s, already in system", user_found[0])
            #if we get here it means the user already exists
            message = "Unable to add user, username already exists"
            return manage_users(request, message)
        except Exception:
            #If we are here we are good since the username doesnt exist. add it and return
            glint_user = Glint_User(
                username=user,
                cert_cn=cert_cn,
                password=bcrypt.hashpw(pass1.encode(), bcrypt.gensalt(prefix=b"2a")))
            glint_user.save()
            message = "User %s added successfully" % user
            return manage_users(request, message)

    else:
        #not a post, should never come to this page
        pass


def self_update_user(request):
    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        original_user = request.POST.get('old_usr')
        usr_obj = getUser(request)
        if not original_user == usr_obj.username:
            raise PermissionDenied
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        cert_cn = request.POST.get('cert_cn')

        # Check passwords for length and ensure they are both the same,
        # if left empty the password wont be updated
        if pass1 and pass2:
            if pass1 != pass2:
                logger.error("new passwords do not match, unable to update user")
                message = "New passwords did not match, update cancelled"
                return user_settings(request, message)
            elif len(pass1) < 4:
                logger.error("new password too short, cancelling update")
                message = ("New password too short, password must be at least 4"
                           "characters, please try again")
                return user_settings(request, message)

        logger.info("Updating info for user %s", original_user)
        try:
            glint_user_obj = Glint_User.objects.get(username=original_user)
            glint_user_obj.cert_cn = cert_cn
            if len(pass1) > 3:
                glint_user_obj.password = bcrypt.hashpw(pass1.encode(), bcrypt.gensalt(prefix=b"2a"))
            glint_user_obj.save()
            message = "User " + original_user + " updated successfully."
        except Exception as e:
            logger.error("Unable to retrieve user %s, there may be a database inconsistency.", original_user)
            logger.error(e)
            return user_settings(request)

        return redirect('/ui/')
    else:
        #not a post should never come to this page
        pass


def update_user(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        original_user = request.POST.get('old_usr')
        user = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        cert_cn = request.POST.get('cert_cn')
        admin_status = request.POST.get('admin')
        if admin_status is None:
            admin_status = False
        else:
            admin_status = True

        # Check passwords for length and ensure they are both the same,
        # if left empty the password wont be updated
        if pass1 and pass2:
            if pass1 != pass2:
                logger.error("new passwords do not match, unable to update user")
                message = "New passwords did not match, update cancelled"
                return manage_users(request, message)
            elif len(pass1) < 4:
                logger.error("new password too short, cancelling update")
                message = ("New password too short, password must be at least 4"
                           " characters, please try again")
                return manage_users(request, message)

        logger.info("Updating info for user %s", original_user)
        try:
            glint_user_obj = Glint_User.objects.get(username=original_user)
            glint_user_obj.username = user
            glint_user_obj.cert_cn = cert_cn
            glint_user_obj.is_superuser = admin_status
            if len(pass1) > 3:
                glint_user_obj.password = bcrypt.hashpw(pass1.encode(), bcrypt.gensalt(prefix=b"2a"))
            glint_user_obj.save()
            message = "User " + user + " updated successfully."
        except Exception as e:
            logger.error("Unable to retrieve user %s, there may be a database inconsistency.", \
                 original_user)
            logger.error(e)
            return manage_users(request)

        return manage_users(request, message)
    else:
        #not a post should never come to this page
        pass

def delete_user(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = request.POST.get('user')
        logger.info("Attempting to delete user %s", user)
        user_obj = Glint_User.objects.get(username=user)
        user_obj.delete()
        message = "User %s deleted." % user
        return manage_users(request, message)
    else:
        #not a post
        pass

#only glint admins can manage glint users
def manage_users(request, message=None):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    user_list = Glint_User.objects.all()
    user_obj_list = Glint_User.objects.filter(is_superuser=1)
    admin_list = []
    for usr in user_obj_list:
        admin_list.append(usr.username)
    context = {
        'user_list': user_list,
        'admin_list': admin_list,
        'message': message,
        'is_superuser': getSuperUserStatus(request),
        'version': version
    }
    return render(request, 'glintwebui/manage_users.html', context)


def user_settings(request, message=None):
    if not verifyUser(request):
        raise PermissionDenied
    user_obj = getUser(request)

    context = {
        'message': message,
        'is_superuser': getSuperUserStatus(request),
        'user_obj': user_obj,
        'version': version
    }
    return render(request, 'glintwebui/user_settings.html', context)


def delete_user_group(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = request.POST.get('user')
        group = request.POST.get('group')
        logger.info("Attempting to delete user %s from group %s" % (user, group))
        user_obj = Glint_User.objects.get(username=user)
        user_obj.active_group = None
        user_obj.save()
        grp_obj = Group.objects.get(group_name=group)
        user_group_obj = User_Group.objects.get(user=user_obj, group_name=grp_obj)
        user_group_obj.delete()
        message = "User %s deleted from %s" % (user, group)
        return manage_users(request, message)
    else:
        #not a post
        pass

def add_user_group(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        user = request.POST.get('user')
        group = request.POST.get('group')
        user_obj = None
        grp_obj = None
        logger.info("Attempting to add user %s to group %s" % (user, group))
        try:
            user_obj = Glint_User.objects.get(username=user)
            grp_obj = Group.objects.get(group_name=group)
        except Exception as e:
            logger.error("Either user or group does not exist, could not add user_group.")
            logger.error(e)
        try:
            #check to make sure it's not already there
            logger.info("Checking if user already has access.")
            User_Group.objects.get(user=user_obj, group_name=grp_obj)
            #if we continue here the user group already exists and we can return without adding it
            message = "%s already has access to %s" % (user, group)
            return manage_groups(request, message)
        except Exception:
            #If we get here the user group wasn't present and we can safely add it
            logger.info("No previous entry, adding new user_group")
            new_usr_grp = User_Group(user=user_obj, group_name=grp_obj)
            new_usr_grp.save()
            message = "User %s added to %s" % (user, group)
            return manage_groups(request=request, message=message)
    else:
        #not a post
        pass

def delete_group(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        group = request.POST.get('group')
        logger.info("Attempting to delete group %s", group)
        grp_obj = Group.objects.get(group_name=group)
        grp_obj.delete()
        message = "Group %s deleted." % group
        #need to also remove any instanced where this group was the active one for users.
        try:
            users = Glint_User.objects.get(active_group=group)
            if users is not None:
                for user in users:
                    user.active_group = None
                    user.save()
        except:
            #No users tied to this group
            logger.info("No users to clean-up..")
        logger.info("Successfull delete of group %s", group)
        return HttpResponse(True)
    else:
        #not a post
        pass

def update_group(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        old_group = request.POST.get('old_group')
        new_group = request.POST.get('group')
        logger.info("Attempting to update group name %s to %s" % (old_group, new_group))
        #check for groups with the new name
        try:
            new_group_obj = Group.objects.get(group_name=new_group)
            #name already taken, don't edit the name and return
            logger.info("Could not update group name to %s, name already in use", new_group)
            message = "Could not update group name to %s, name already in use" % new_group
            return manage_groups(request=request, message=message)
        except Exception:
            #No group has the new name, proceed freely
            group_obj = Group.objects.get(group_name=old_group)
            group_obj.group_name = new_group
            group_obj.save()
            message = "Successfully updated group name to %s" % new_group
            logger.info("Successfully updated group name to %s", new_group)
            return manage_groups(request=request, message=message)
    else:
        #not a post
        pass

#only glint admins can add new groups
def add_group(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied
    if request.method == 'POST':
        group = request.POST.get('group')
        logger.info("Attempting to add group %s", group)
        try:
            group_obj = Group.objects.get(group_name=group)
            #group exists, return without adding
            message = "Group with that name already exists"
            logger.info("Could not add group %s, name already in use.", group)
            return manage_groups(request=request, message=message)
        except Exception:
            #group doesnt exist, we can go ahead and add it.
            new_grp = Group(group_name=group)
            new_grp.save()
            logging.info("Group '%s' created successfully", group)
            message = "Group '%s' created successfully" % group
            return manage_groups(request=request, message=message)
    else:
        #not a post should never come to this page, redirect to matrix?
        pass

def manage_groups(request, message=None):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    #Retrieve groups, build group:user dictionary
    group_user_dict = {}
    group_list = Group.objects.all()
    user_groups = User_Group.objects.all()
    user_list = Glint_User.objects.all()
    for usr_grp in user_groups:
        #check if this group is in dict yet
        if usr_grp.group_name in group_user_dict:
            #if so append this user to that key
            group_user_dict[usr_grp.group_name].append(usr_grp.user.username)
        else:
            #else create new key with user
            group_user_dict[usr_grp.group_name] = list()
            group_user_dict[usr_grp.group_name].append(usr_grp.user.username)

    context = {
        'group_list': group_list,
        'group_user_dict': group_user_dict,
        'user_list': user_list,
        'message': message,
        'is_superuser': getSuperUserStatus(request),
        'version': version

    }
    return render(request, 'glintwebui/manage_groups.html', context)


def download_image(request, group_name, image_name):
    if not verifyUser(request):
        raise PermissionDenied

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


    response = StreamingHttpResponse((line for line in open(file_full_path, 'r')))
    response['Content-Disposition'] = "attachment; filename={0}".format(filename)
    response['Content-Length'] = os.path.getsize(file_full_path)
    return response

def upload_image(request, group_name):
    if not verifyUser(request):
        raise PermissionDenied

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
        image_data = urllib2.urlopen(img_url)

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
