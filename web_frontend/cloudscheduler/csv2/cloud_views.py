from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, _render
from utils import db_utils
from collections import defaultdict
import bcrypt


def list(request, group_name=None, response_code=0, message=None):
    if not verifyUser(request):
        raise PermissionDenied


    active_user = getcsv2User(request)
    user_groups = db_utils.get_user_groups(active_user)

    #check to see if specified group is a valid one for this user, if it is set it as active
    if request.method == 'POST':
        group_name = request.POST.get('group')
        if group_name is not None:
            if group_name in user_groups:
                active_user.active_group = group_name
                active_user.save()

    if len(user_groups)==0:
        # active user isn't registered to any groups, display blank page with msg
        #TODO#
        pass
    # get data based on active group, if no active group pick the first from the list
    if active_user.active_group is None:
        active_user.active_group = user_groups[0]
        active_user.save()

    #get cloud info
    cloud_list = {'ResultProxy': [dict(r) for r in db_utils.get_group_resources(group_name=active_user.active_group)]}

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'response_code': response_code,
            'message': message
        }

    return _render(request, 'csv2/clouds.html', context)


def prepare(request):

    context = {
            'response_code': 0,
            'message': None
    }
    
    return _render(request, 'csv2/clouds.html', context)


#
# This function generates a the status of a given groups operations
# VM status, job status, and machine status should all be available for a given group on this page
#
def status(request, group_name=None):
    if not verifyUser(request):
        raise PermissionDenied

    active_user = getcsv2User(request)
    user_groups = db_utils.get_user_groups(active_user)

    #check to see if specified group is a valid one for this user, if it is set it as active
    if request.method == 'POST':
        group_name = request.POST.get('group')
        if group_name is not None:
            if group_name in user_groups:
                active_user.active_group = group_name
                active_user.save()

    if len(user_groups)==0:
        # active user isn't registered to any groups, display blank page with msg
        #TODO#
        pass
    # get data based on active group, if no active group pick the first from the list
    if active_user.active_group is None:
        active_user.active_group = user_groups[0]
        active_user.save()

    #get cloud info
    cloud_list = db_utils.get_group_resources(group_name=active_user.active_group)

    #get vms
    vm_list = db_utils.get_vms(group_name=active_user.active_group)
    
    #vm count per cloud
    count_list = db_utils.get_counts(group_name=active_user.active_group)

    #get default limits
    cloud_limits = db_utils.get_limits(group_name=active_user.active_group)

    #get jobs
    job_list = db_utils.get_condor_jobs(group_name=active_user.active_group)

    status_list = db_utils.get_cloud_status(group_name=active_user.active_group)

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'count_list': count_list,
            'cloud_limits': cloud_limits,
            'job_list': job_list,
            'status_list': status_list,
            #'machine_list': machine_list, #Not yet implemented

        }

    return _render(request, 'csv2/status.html', context)


# 
# This function should recieve a post request with a payload of cloud configuration
# to add to a given group's pool of resources (group_resources)
#
def update(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    active_user = getcsv2User(request)

    if request.method == 'POST':
        if 'cloud_name' not in request.POST:
            return list(request, response_code=1, message="Missing cloud_name")

        values = {'group_name': active_user.active_group}

        for key in request.POST:

            if key == 'core_lock':
                if request.POST[key] == 'lock':
                    cores_ctl = -1
                else:
                    cores_ctl = cores

                values['cores_ctl'] = cores_ctl

            elif key == 'ram_lock':
                if request.POST[key] == 'lock':
                    ram_ctl = -1
                else:
                    ram_ctl = ram

                values['ram_ctl'] = ram_ctl
 
            else:
                values[key] = request.POST[key]

        db_utils.put_group_resources(values)


        action = request.POST.get('action')
        cloud_name = request.POST.get('cloud_name')

        if action == 'add':
            message = 'Cloud "%s" added.' % cloud_name
        elif action == 'delete':
            message = 'Cloud "%s" deleted.' % cloud_name
        else:
            message = 'Cloud "%s" updated.' % cloud_name

    else:
        message = 'No data recieved.'

    return list(request, message=message)
