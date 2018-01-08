from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus
from utils import db_utils

# 
# This function should recieve a post request with a payload of yaml to add to a given group
# (group_yaml)
#
def add_group_yaml(request):
    return None

# 
# This function should recieve a post request with a payload of yaml to add to a given cloud
# (group_resources_yaml)
#
def add_cloud_yaml(request):
    return None

# 
# This function should recieve a post request with a payload of cloud configuration
# to add to a given group's pool of resources (group_resources)
#
def add_cloud_resources(request):
    return None

#
# This function generates a the status of a given groups operations
# VM status, job status, and machine status should all be available for a given group on this page
#
def system_status(request, group_name=None):
    if not verifyUser(request):
        raise PermissionDenied

    active_user = getcsv2User(request)
    user_groups = db_utils.get_user_groups(active_user)
    #check to see if specified group is a valid one for this user, if it is set it as active
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
    for cloud in cloud_list:
        vm_count.update({cloud.cloud_name:len(db_utils.get_vms(group_name=active_user.active_group, cloud_name=cloud.cloud_name)})
    
    #get default quotas
    cloud_quotas = db_utils.get_quotas(group_name=active_user.active_group)

    #get jobs
    job_list = db_utils.get_condor_jobs(group_name=active_user.active_group)

    #get condor machines
    # machine list does not yet have a group_name attribute, some discussion
    # is required to develop a strategy to deal with this
    #machine_list = db_utils.get_condor_machines(group_name=active_user.active_group)

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'active_cloud': active_user.active_group.active_cloud,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'vm_list': vm_list,
            'vm_count': vm_count,
            'cloud_quotas': cloud_quotas,
            'job_list': job_list,
            #'machine_list': machine_list, #Not yet implemented

        }

    return render(request, 'csv2/system_status.html', context)

