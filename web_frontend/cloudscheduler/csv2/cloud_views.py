from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, _render
from utils.db_utils import db_open
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc


def _db_execute(db_connection, request):
    try:
        db_connection.execute(request)
        return True,None
    except sqlalchemy.exc.IntegrityError as ex:
        return False, ex.orig
    except Exception as ex:
        return False, ex


def _get_user_group_list(request, db_session, db_map):
    active_user = getcsv2User(request)
    user_groups = db_map.classes.csv2_user_groups
    user_group_rows = db_session.query(user_groups).filter(user_groups.username==active_user)
    user_groups = []
    if user_group_rows is not None:
        for row in user_group_rows:
            user_groups.append(row.group_name)

    return active_user,user_groups


def list(request, group_name=None, response_code=0, message=None):
    if not verifyUser(request):
        raise PermissionDenied


    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user and associated group list.
    active_user,user_groups = _get_user_group_list(request, db_session, db_map)

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
    s = select([view_group_resources]).where(view_group_resources.c.group_name == active_user.active_group)
    cloud_list = {'ResultProxy': [dict(r) for r in db_connection.execute(s)]}

    db_connection.close()

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'response_code': response_code,
            'message': message
        }

    return _render(request, 'csv2/clouds.html', context)


def modify(request):
    """
    This function should recieve a post request with a payload of cloud configuration
    to add to a given group's pool of resources (group_resources)
    """

    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    if request.method == 'POST' and 'action' in request.POST and 'cloud_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # map the field list.
        metadata = MetaData(bind=db_engine)
        table = Table('csv2_group_resources', metadata, autoload=True)

        values = {}
        for key in request.POST:
            if key in table.c:
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
            else:
                if key != 'action' and key != 'csrfmiddlewaretoken':
                    return list(request, response_code=1, message='bad parameter "%s" to modify cloud request.' % key)

        if 'group_name' not in values:
            values['group_name'] = getcsv2User(request).active_group


        if request.POST['action'] == 'add':
            if(db_session.query(exists().where(table.c.cloud_name==values['cloud_name'] and table.c.group_name==values['group_name'])).scalar()):
                db_connection.close()
                return list(request, response_code=1, message='request to add existing cloud "%s/%s".' % (values['group_name'], values['cloud_name']))
            else:
                success,message = _db_execute(db_connection, table.insert().values(values))
                db_connection.close()
                if success:
                    return list(request, response_code=0, message='cloud "%s/%s" successfully added.' % (values['group_name'], values['cloud_name']))
                else:
                    return list(request, response_code=1, message='cloud "%s/%s" add failed - %s.' % (values['group_name'], values['cloud_name'], message))

        elif request.POST['action'] == 'delete':
            success,message = _db_execute(db_connection, table.delete(table.c.cloud_name==values['cloud_name'] and table.c.group_name==values['group_name']))
            db_connection.close()
            if success:
                return list(request, response_code=0, message='cloud "%s/%s" successfully deleted.' % (values['group_name'], values['cloud_name']))
            else:
                return list(request, response_code=1, message='cloud "%s/%s" delete failed - %s.' % (values['group_name'], values['cloud_name'], message))

        elif request.POST['action'] == 'modify':
            success,message = _db_execute(db_connection, table.update().where(table.c.cloud_name==values['cloud_name'] and table.c.group_name==values['group_name']).values(values))
            db_connection.close()
            if success:
                return list(request, response_code=0, message='cloud "%s/%s" successfully modified.' % (values['group_name'], values['cloud_name']))
            else:
                return list(request, response_code=1, message='cloud "%s/%s" modify failed - %s.' % (values['group_name'], values['cloud_name'], message))

        else:
            return list(request, response_code=1, message='invalid action "%s" specified.' % request.POST['action'])
    else:
        if request.method == 'POST':
            return list(request, response_code=1, message='invalid method "%s" specified.' % request.method)
        elif 'action' not in request.POST:
            return list(request, response_code=1, message='no action specified.')
        else:
            return list(request, response_code=1, message='no cloud name specified.')

    return list(request, response_code=1, message='internal server error.')


def prepare(request):
    """
    This function returns a minimal response plus a CSRF.
    """

    context = {
            'response_code': 0,
            'message': None
    }
    
    return _render(request, 'csv2/clouds.html', context)


def status(request, group_name=None):
    """
    This function generates a the status of a given groups operations
    VM status, job status, and machine status should all be available for a given group on this page
    """

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user and associated group list.
    active_user,user_groups = _get_user_group_list(request, db_session, db_map)

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

    # get vm and job counts per cloud
    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == active_user.active_group)
    status_list = db_connection.execute(s)

    # get default limits
    Limit = db_map.classes.cloud_limits
    cloud_limits = db_session.query(Limit).filter(Limit.group_name==active_user.active_group)

    # get VM list
    VM = db_map.classes.csv2_vms
    vm_list = db_session.query(VM).filter(VM.group_name==active_user.active_group)
    
    # get jobs list
    Jobs = db_map.classes.condor_jobs
    job_list = db_session.query(Jobs).filter(Jobs.group_name==active_user.active_group)

    db_connection.close()

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'status_list': status_list,
            'cloud_limits': cloud_limits,
            'vm_list': vm_list,
            'job_list': job_list,
            'response_code': 0,
            'message': None,
        }

    return _render(request, 'csv2/status.html', context)
