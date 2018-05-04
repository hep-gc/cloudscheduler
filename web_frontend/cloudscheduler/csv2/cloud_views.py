from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import db_execute, db_open, getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, map_parameter_to_field_values, qt, render, set_user_groups
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc

#-------------------------------------------------------------------------------

CLOUD_KEYS = (
    # The following fields are the key fields for the table:
    (
        'group_name',
        'cloud_name',
        ),
    # The following fields maybe in the input form but should be ignored.
    (    
        'cores_slider',
        'csrfmiddlewaretoken',
        'group',
        'ram_slider',
        ),
    {
        'group_name': 'l',
        'cloud_name': 'l',
        },
    )

YAML_KEYS = (
    # The following fields are the key fields for the table:
    (
        'group_name',
        'cloud_name',
        'yaml_name',
        ),
    # The following fields maybe in the input form but should be ignored.
    (    
        'csrfmiddlewaretoken',
        'group',
        ),
    )

#-------------------------------------------------------------------------------

@requires_csrf_token
def add(request):
    """
    This function should recieve a post request with a payload of cloud configuration
    to add a cloud to a given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'cloud_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resources', CLOUD_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud add %s' % values, active_user=active_user, user_groups=user_groups)

        # Add the cloud.
        success,message = db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
        db_connection.close()
        if success:
            return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s.%s" successfully added.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud add "%s.%s" failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='cloud add, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='cloud add, no cloud name specified.')

#-------------------------------------------------------------------------------

@requires_csrf_token
def delete(request):
    """
    This function should recieve a post request with a payload of cloud name
    to be deleted.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'cloud_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list for cloud/YAML files.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resource_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud delete %s.' % values, active_user=active_user, user_groups=user_groups)

        # Delete any cloud/YAML files for the cloud.
        s = select([view_group_resources_with_yaml_names]).where(
          (view_group_resources_with_yaml_names.c.group_name == values[0]['group_name']) & (view_group_resources_with_yaml_names.c.cloud_name == values[0]['cloud_name'])
          )
        cloud_list = qt(db_connection.execute(s))
        for row in cloud_list:
            if row['group_name'] == values[0]['group_name'] and row['cloud_name'] == values[0]['cloud_name'] and row['yaml_names']:
                yaml_names = row['yaml_names'].split(',')
                for yaml_name in yaml_names:
                    # Delete the cloudYAML file.
                    success,message = db_execute(
                        db_connection,
                        table.delete((table.c.group_name==values[0]['group_name']) & (table.c.cloud_name==values[0]['cloud_name']) & (table.c.yaml_name==yaml_name))
                        )

        # Map the field list for clouds.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resources', CLOUD_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud delete %s' % values, active_user=active_user, user_groups=user_groups)

        # Delete the cloud.
        success,message = db_execute(
            db_connection,
            table.delete((table.c.group_name==values[0]['group_name']) & (table.c.cloud_name==values[0]['cloud_name']))
            )
        db_connection.close()
        if success:
            return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s.%s" successfully deleted.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud delete "%s.%s" failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='cloud delete, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='cloud delete, no cloud name specified.')

#-------------------------------------------------------------------------------

@requires_csrf_token
def list(
    request,
    selector=None,
    group_name=None,
    response_code=0,
    message=None,
    active_user=None,
    user_groups=None,
    attributes=None
    ):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Retrieve cloud information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_group_resources_with_yaml_names]).where(view_group_resources_with_yaml_names.c.group_name == active_user.active_group)
        cloud_list = qt(db_connection.execute(s), prune=['password'])
        yaml_dict = {}
    else:
        s = select([view_group_resources_with_yaml]).where(view_group_resources_with_yaml.c.group_name == active_user.active_group)
        cloud_list, yaml_dict = qt(
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
            'attributes': attributes,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'yaml_dict': yaml_dict,
            'current_cloud': current_cloud,
            'response_code': response_code,
            'message': message
        }

    return render(request, 'csv2/clouds.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
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
    rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
    if rc != 0:
        db_connection.close()
        return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

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

    return render(request, 'csv2/status.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
def update(request):
    """
    This function should recieve a post request with a payload of cloud configuration
    to update a given cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'cloud_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resources', CLOUD_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud update %s.' % values, active_user=active_user, user_groups=user_groups)

        # Update the cloud.
        success, message = db_execute(db_connection, table.update().where((table.c.group_name==values[0]['group_name']) & (table.c.cloud_name==values[0]['cloud_name'])).values(values[1]))
        db_connection.close()
        if success:
            return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud "%s.%s" successfully updated.' % (values[0]['group_name'], values[0]['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud update "%s.%s" failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='cloud update, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='cloud update, no cloud name specified.')

#-------------------------------------------------------------------------------

@requires_csrf_token
def yaml_add(request):
    """
    This function should recieve a post request with a payload of yaml configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'cloud_name' in request.POST and \
        'yaml_name' in request.POST:

        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resource_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud yaml-add %s' % values, active_user=active_user, user_groups=user_groups)

        # Add the cloud yaml file.
        success,message = db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
        db_connection.close()
        if success:
            return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud YAML file "%s.%s.%s" successfully added.' % (values[0]['group_name'], values[0]['cloud_name'], values[0]['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud yaml-add "%s.%s.%s" failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], values[0]['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='cloud yaml_add, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='cloud yaml_add, no cloud name specified.')

#-------------------------------------------------------------------------------

@requires_csrf_token
def yaml_delete(request):
    """
    This function should recieve a post request with a payload of yaml configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'cloud_name' in request.POST and \
        'yaml_name' in request.POST:

        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resource_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud yaml-delete %s' % values, active_user=active_user, user_groups=user_groups)

        # Delete the cloud yaml file.
        success,message = db_execute(
            db_connection,
            table.delete( \
                (table.c.group_name==values[0]['group_name']) & \
                (table.c.cloud_name==values[0]['cloud_name']) & \
                (table.c.yaml_name==values[0]['yaml_name']) \
                )
            )
        db_connection.close()
        if success:
            return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud YAML file "%s.%s.%s" successfully deleted.' % (values[0]['group_name'], values[0]['cloud_name'], values[0]['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud yaml-delete "%s.%s.%s" failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], values[0]['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='cloud yaml_delete, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='cloud yaml_delete, no cloud name specified.')

#-------------------------------------------------------------------------------

@requires_csrf_token
def yaml_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
    if rc != 0:
        db_connection.close()
        return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

    # Retrieve YAML file.
    obj_act_id = request.path.split('/') # /cloud/yaml_fetch/<group>.<cloud>.<yaml>
    if len(obj_act_id) > 3:
        id = obj_act_id[3]
        ids = id.split('.')
        print(">>>>>>>>>>", ids)
        if len(ids) == 3:
            YAML = db_map.classes.csv2_group_resource_yaml
            YAMLobj = db_session.query(YAML).filter((YAML.group_name==ids[0]) & (YAML.cloud_name==ids[1]) & (YAML.yaml_name==ids[2]))
            print(">>>>>>>>>>", type(YAMLobj))
            if YAMLobj:
                for row in YAMLobj:
                    print(">>>>>>>>>>", row)
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
                
                    return render(request, 'csv2/clouds.html', context)
             
    if id:
      return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': 'cloud yaml_fetch, received an invalid YAML file id "%s".' % id})
    else:
      return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': 'cloud yaml_fetch, received no YAML file id.'})

#-------------------------------------------------------------------------------

@requires_csrf_token
def yaml_update(request):
    """
    This function should recieve a post request with a payload of yaml configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'cloud_name' in request.POST and \
        'yaml_name' in request.POST:

        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_resource_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='cloud yaml-update %s' % values, active_user=active_user, user_groups=user_groups)

        # Update the cloud yaml file.
        success,message = db_execute(db_connection, table.update().where( \
            (table.c.group_name==values[0]['group_name']) & \
            (table.c.cloud_name==values[0]['cloud_name']) & \
            (table.c.yaml_name==values[0]['yaml_name']) \
            ).values(values[1]))
        db_connection.close()
        if success:
            return list(request, selector=values[0]['cloud_name'], response_code=0, message='cloud YAML file "%s.%s.%s" successfully  updated.' % (values[0]['group_name'], values[0]['cloud_name'], values[0]['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['cloud_name'], response_code=1, message='cloud yaml-update "%s.%s.%s" failed - %s.' % (values[0]['group_name'], values[0]['cloud_name'], values[0]['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='cloud yaml_update, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='cloud yaml_update, no cloud name specified.')

