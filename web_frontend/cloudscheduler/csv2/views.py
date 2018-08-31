from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus

import bcrypt


'''
WEB REQUEST VIEWS
'''

def index(request):
    if verifyUser(request):
        csv2_user = getcsv2User(request)
        return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % csv2_user.username)
    else:
        raise PermissionDenied

