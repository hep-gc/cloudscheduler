from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

import bcrypt

'''
UTILITY FUNCTIONS
'''

# Returns the current authorized user from metadata
def getAuthUser(request):
    return request.META.get('REMOTE_USER')

# returns the csv2 user object matching the authorized user from header metadata
def getcsv2User(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_dn == authorized_user:
            return user
    raise PermissionDenied


def verifyUser(request):
    auth_user = getAuthUser(request)
    
    csv2_user_list = csv2_user.objects.all()
    #try to find a user that has "auth_user" as username or cert_dn
    # the uniqueness here will be forced on user creation
    for user in csv2_user_list:
        if user.username == auth_user or user.cert_dn == auth_user:
            return True

    return False

def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_dn == authorized_user:
            return user.is_superuser
    return False



'''
WEB REQUEST VIEWS
'''

def index(request):
    if verifyUser(request):
        csv2_user = getcsv2User(request)
        return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % csv2_user.username)
    else:
        raise PermissionDenied

