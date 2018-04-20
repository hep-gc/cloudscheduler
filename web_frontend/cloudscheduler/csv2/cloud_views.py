from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import db_open, getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, _qt, _render
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc

MODIFY_IGNORE_KEYS = (
    'action',
    'cores_slider',
    'csrfmiddlewaretoken',
    'ram_slider',
    )

YAML_MODIFY_IGNORE_KEYS = (
    'action',
    )

def _db_execute(db_connection, request):
    try:
        db_connection.execute(request)
        return True,None
    except sqlalchemy.exc.IntegrityError as ex:
        return False, ex.orig
    except Exception as ex:
        return False, ex


def _set_user_groups(request, db_session, db_map):
    active_user = getcsv2User(request)
    user_groups = db_map.classes.csv2_user_groups
    user_group_rows = db_session.query(user_groups).filter(user_groups.username==active_user)
    user_groups = []
    if user_group_rows is not None:
        for row in user_group_rows:
            user_groups.append(row.group_name)

    if not user_groups:
        return 1,'user "%s" is not a member of any group.' % active_user,active_user,user_groups

    # if the POST request specified a group, validate and set the specified group as the active group.
    if request.method == 'POST':
        group_name = request.POST.get('group')
        if group_name is not None:
            if group_name in user_groups:
                active_user.active_group = group_name
                active_user.save()
            else:
                return 1,'cannnot switch to invalid group "%s".' % group_name,active_user,user_groups

    # if no active group, set first group as default.
    if active_user.active_group is None:
        active_user.active_group = user_groups[0]
        active_user.save()

    return 0,None,active_user,user_groups

def list(
    request,
    selector=None,
    group_name=None,
    response_code=0,
    message=None,
    active_user=None,
    user_groups=None
    ):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        response_code,message,active_user,user_groups = _set_user_groups(request, db_session, db_map)
        if response_code != 0:
            db_connection.close()
            return _render(request, 'csv2/clouds.html', {'response_code': 1, 'message': message})

    # Retrieve cloud information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_group_resources_with_yaml_names]).where(view_group_resources_with_yaml_names.c.group_name == active_user.active_group)
        cloud_list = _qt(db_connection.execute(s), prune=['password'])
        yaml_dict = {}
    else:
        # cloud_list = {'ResultProxy': [dict(r) for r in db_connection.execute(s)]}
        s = select([view_group_resources_with_yaml]).where(view_group_resources_with_yaml.c.group_name == active_user.active_group)
        cloud_list, yaml_dict = _qt(
            db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
                    'cloud_name'
                    ],
                'secondary': [
                    'yaml_name',
                    'yaml_enabled',
                    'yaml_mime_type',
                    'yaml',
                    ]
                },
            prune=['password']    
            )

    db_connection.close()

    # Position the page.
    obj_act_id = request.path.split('/')
    if selector:
        if selector == '-':
            current_cloud = ''
        else:
            current_cloud = selector
    elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
        current_cloud = str(obj_act_id[3])
    else:
        if len(cloud_list) > 0:
            current_cloud = str(cloud_list[0]['cloud_name'])
        else:
            current_cloud = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_list': {'ResultProxy': cloud_list},
            'yaml_dict': yaml_dict,
            'current_cloud': current_cloud,
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

    if request.method == 'POST' and 'action' in request.POST and 'cloud_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        response_code,message,active_user,user_groups = _set_user_groups(request, db_session, db_map)
        if response_code != 0:
            return list(request, selector='-', response_code=1, message=message, active_user=active_user, user_groups=user_groups)

        # map the field list.
        metadata = MetaData(bind=db_engine)
        table = Table('csv2_group_resources', metadata, autoload=True)

        values = [{}, {}]
        for key in request.POST:
            if key in table.c:
                if key == 'group_name' or key == 'cloud_name':
                    values[0][key] = request.POST[key]
                else:
                    if key != 'password' or request.POST[key]:
                        values[1][key] = request.POST[key]
            else:
                if key not in MODIFY_IGNORE_KEYS:
                    return list(request, selector='-', response_code=1, message='cloud modify request contained bad parameter "%s".' % key, active_user=active_user, user_groups=user_groups)

        if 'group_name' not in values[0]:
            values[0]['group_name'] = getcsv2User(request).active_group

#       print(">>>>> object=cloud, action=%s, values=%s" % (request.POST['action'], values))

        ### Add.
        if request.POST['action'] == 'add':
            success,message = _db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
            db_connection.close()
            if success:
                return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s/%s" successfully added.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud "%s/%s" add failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups)

        ### Delete.
        elif request.POST['action'] == 'delete':
            success,message = _db_execute(
                db_connection,
                table.delete((table.c.group_name==values[0]['group_name']) & (table.c.cloud_name==values[0]['cloud_name']))
                )
            db_connection.close()
            if success:
                return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s/%s" successfully deleted.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud "%s/%s" delete failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups)

        ### modify.
        elif request.POST['action'] == 'modify':
            success,message = _db_execute(db_connection, table.update().where((table.c.group_name==values[0]['group_name']) & (table.c.cloud_name==values[0]['cloud_name'])).values(values[1]))
            db_connection.close()
            if success:
                return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s/%s" successfully modified.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud "%s/%s" modify failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups)

        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='invalid action "%s" specified.' % request.POST['action'], active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='invalid method "%s" specified.' % request.method)
        elif 'action' not in request.POST:
            return list(request, response_code=1, message='no action specified.')
        else:
            return list(request, response_code=1, message='no cloud name specified.')

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

    # Retrieve the active user, associated group list and optionally set the active group.
    response_code,message,active_user,user_groups = _set_user_groups(request, db_session, db_map)
    if response_code != 0:
        return _render(request, 'csv2/status.html', {'response_code': 1, 'message': message})

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

def yaml_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    response_code,message,active_user,user_groups = _set_user_groups(request, db_session, db_map)
    if response_code != 0:
        return _render(request, 'csv2/status.html', {'response_code': 1, 'message': message})

    id = ''
    obj_act_id = request.path.split('/')
    if len(obj_act_id) > 3:
        id = obj_act_id[3]
        ids = id.split('.')
        if len(ids) > 1:
            YAML = db_map.classes.csv2_group_resource_yaml
            YAMLobj = db_session.query(YAML).filter((YAML.group_name==active_user.active_group) & (YAML.cloud_name==ids[0]) & (YAML.yaml_name==ids[1]))
            if YAMLobj:
                for row in YAMLobj:
                    context = {
                        'group_name': row.group_name,
                        'cloud_name': row.cloud_name,
                        'yaml': row.yaml,
                        'yaml_enabled': row.enabled,
                        'yaml_mime_type': row.mime_type,
                        'yaml_name': row.yaml_name,
                        'response_code': 0,
                        'message': None
                        }
                
                    return _render(request, 'csv2/clouds.html', context)
             
    return _render(request, 'csv2/clouds.html', {'response_code': 1, 'message': 'cloud yaml_fetch received an invalid key "%s".' % id})

def yaml_modify(request):
    """
    This function should recieve a post request with a payload of yaml configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'action' in request.POST and \
        'cloud_name' in request.POST and \
        'yaml_name' in request.POST:

        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        response_code,message,active_user,user_groups = _set_user_groups(request, db_session, db_map)
        if response_code != 0:
            return list(request, selector='-', response_code=1, message=message, active_user=active_user, user_groups=user_groups)

        # map the field list.
        metadata = MetaData(bind=db_engine)
        table = Table('csv2_group_resource_yaml', metadata, autoload=True)

        values = [{}, {}]
        for key in request.POST:
            if key in table.c:
                if key == 'group_name' or key == 'cloud_name' or key == 'yaml_name':
                    values[0][key] = request.POST[key]
                else:
                    if key != 'password' or request.POST[key]:
                        values[1][key] = request.POST[key]
            else:
                if key not in YAML_MODIFY_IGNORE_KEYS:
                    return list(request, selector='-', response_code=1, message='cloud modify request contained bad parameter "%s".' % key, active_user=active_user, user_groups=user_groups)

        if 'group_name' not in values[0]:
            values[0]['group_name'] = getcsv2User(request).active_group

#       print(">>>>> object=cloud, action=%s, values=%s" % (request.POST['action'], values))

        ### Add.
        if request.POST['action'] == 'add':
            success,message = _db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
            db_connection.close()
            if success:
                return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s/%s" successfully added.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud "%s/%s" add failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups)

        ### Delete.
        elif request.POST['action'] == 'delete':
            success,message = _db_execute(
                db_connection,
                table.delete( \
                    (table.c.group_name==values[0]['group_name']) & \
                    (table.c.cloud_name==values[0]['cloud_name']) & \
                    (table.c.yaml_name==values[0]['yaml_name']) \
                    )
                )
            db_connection.close()
            if success:
                return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s/%s" successfully deleted.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud "%s/%s" delete failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups)

        ### Modify.
        elif request.POST['action'] == 'modify':
            success,message = _db_execute(db_connection, table.update().where( \
                (table.c.group_name==values[0]['group_name']) & \
                (table.c.cloud_name==values[0]['cloud_name']) & \
                (table.c.yaml_name==values[0]['yaml_name']) \
                ).values(values[1]))
            db_connection.close()
            if success:
                return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s/%s" successfully modified.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud "%s/%s" modify failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups)

        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='invalid action "%s" specified.' % request.POST['action'], active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='invalid method "%s" specified.' % request.method)
        elif 'action' not in request.POST:
            return list(request, response_code=1, message='no action specified.')
        else:
            return list(request, response_code=1, message='no cloud name specified.')

