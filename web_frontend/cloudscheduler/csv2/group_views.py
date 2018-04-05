from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, _render
from utils import db_utils
from collections import defaultdict
import bcrypt
# 


def list(request, group_name=None):
    if not verifyUser(request):
        raise PermissionDenied

    active_user = getcsv2User(request)
    user_groups = db_utils.get_user_groups(active_user)

    #check to see if specified group is a valid one for this user, if it is set it as active
    if request.method == 'POST':
        group_name = request.POST.get('group_select')
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

    group_list = {'ResultProxy': [dict(r) for r in db_utils.get_groups()]}
    #group_list = db_utils.get_groups()

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'group_list': group_list,
            'response_code': 0,
            'message': None
        }

    return _render(request, 'csv2/groups.html', context)


def prepare(request):

    context = {
            'response_code': 0,
            'message': None
    }
    
    return _render(request, 'csv2/groups.html', context)


def modify(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    active_user = getcsv2User(request)

    if request.method == 'POST':
        if 'group_name' not in request.POST:
            return list(request, response_code=1, message="Missing group_name")

        for key in request.POST:
            values[key] = request.POST[key]

        db_utils.put_groups(values)

        action = request.POST.get('action')
        group_name = request.POST.get('group_name')

        if action == 'add':
            message = 'Group "%s" added.' % group_name
        elif action == 'delete':
            message = 'Group "%s" deleted.' % group_name
        else:
            message = 'Group "%s" updated.' % group_name

        response_code = 0
    else:
        message = 'No data recieved.'
        response_code = 1

    return list(request, response_code=response_code, message=message)
