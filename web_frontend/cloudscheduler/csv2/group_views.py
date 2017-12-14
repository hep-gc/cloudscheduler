from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus

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

