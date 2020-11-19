from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
config = settings.CSV2_CONFIG

from cloudscheduler.lib.view_utils_na import set_user_groups

import bcrypt


'''
WEB REQUEST VIEWS
'''

def index(request):
    config.db_open()
    rc, msg, active_user, user_groups = set_user_groups(config, request, super_user=False)
    config.db_close()
    return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % active_user.username)

