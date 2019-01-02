from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
config = settings.CSV2_CONFIG

from .view_utils import getcsv2User, verifyUser

import bcrypt


'''
WEB REQUEST VIEWS
'''

def index(request):
    if verifyUser(request):
        config.db_open()
        csv2_user = getcsv2User(request, config)
        config.db_close()
        return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % csv2_user.username)
    else:
        raise PermissionDenied

