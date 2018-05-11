from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import \
    db_execute, \
    db_open, \
    getAuthUser, \
    getcsv2User, \
    getSuperUserStatus, \
    lno, \
    qt, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields, \
    verifyUser
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc

#-------------------------------------------------------------------------------

CLOUD_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':          'lowercase',

        'cores_slider':        'ignore',
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        'ram_slider':          'ignore',
        },
    }

YAML_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':          'lowercase',
        'yaml_name':           'lowercase',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

IGNORE_YAML_NAME = {
    'format': {
        'yaml_name':           'ignore',
        },
    }

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [CLOUD_KEYS], db_engine, ['csv2_group_resources'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s cloud add %s' % (lno('CV01'), msg), active_user=active_user, user_groups=user_groups)

        # Add the cloud.
        table = tables['csv2_group_resources']
        success,message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        db_connection.close()
        if success:
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s.%s" successfully added.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add "%s.%s" failed - %s.' % (lno('CV02'), fields['group_name'], fields['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud add, invalid method "%s" specified.' % (lno('CV03'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud add, no cloud name specified.' % lno('CV04'))

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV05'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [CLOUD_KEYS, IGNORE_YAML_NAME], db_engine, ['csv2_group_resources', 'csv2_group_resource_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s cloud delete %s' % (lno('CV06'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any cloud/YAML files for the cloud.
        table = tables['csv2_group_resource_yaml']
        success,message = db_execute(db_connection, table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])))
        if not success:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud yaml-delete "%s.%s.*" failed - %s.' % (lno('CV07'), fields['group_name'], fields['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud.
        table = tables['csv2_group_resources']
        success,message = db_execute(
            db_connection,
            table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name']))
            )
        db_connection.close()
        if success:
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s.%s" successfully deleted.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud delete "%s.%s" failed - %s.' % (lno('CV07'), fields['group_name'], fields['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud delete, invalid method "%s" specified.' % (lno('CV08'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud delete, no cloud name specified.' % lno('CV09'))

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

    s = select([csv2_cloud_types])
    type_list = qt(db_connection.execute(s))

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
            'type_list': type_list,
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
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV10'), msg), active_user=active_user, user_groups=user_groups)

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV11'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [CLOUD_KEYS], db_engine, ['csv2_group_resources'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s cloud update %s' % (lno('CV12'), msg), active_user=active_user, user_groups=user_groups)

        # update the cloud.
        table = tables['csv2_group_resources']
        success, message = db_execute(db_connection, table.update().where((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])).values(table_fields(fields, table, columns, selection='update')))
        db_connection.close()
        if success:
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s.%s" successfully updated.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update "%s.%s" failed - %s.' % (lno('CV13'), fields['group_name'], fields['cloud_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud update, invalid method "%s" specified.' % (lno('CV14'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud update, no cloud name specified.' % lno('CV15'))

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV16'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [YAML_KEYS], db_engine, ['csv2_group_resource_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s cloud yaml-add %s' % (lno('CV17'), msg), active_user=active_user, user_groups=user_groups)

        # Add the cloud yaml file.
        table = tables['csv2_group_resource_yaml']
        success,message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        db_connection.close()
        if success:
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud YAML file "%s.%s.%s" successfully added.' % (fields['group_name'], fields['cloud_name'], fields['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud yaml-add "%s.%s.%s" failed - %s.' % (lno('CV18'), fields['group_name'], fields['cloud_name'], fields['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud yaml_add, invalid method "%s" specified.' % (lno('CV19'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud yaml_add, no cloud name specified.' % lno('CV20'))

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
            return list(request, selector='-', response_code=1, message='%s %S' % (lno('CV21'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [YAML_KEYS], db_engine, ['csv2_group_resource_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s cloud yaml-delete %s' % (lno('CV22'), msg), active_user=active_user, user_groups=user_groups)

        # Delete the cloud yaml file.
        table = tables['csv2_group_resource_yaml']
        success,message = db_execute(
            db_connection,
            table.delete( \
                (table.c.group_name==fields['group_name']) & \
                (table.c.cloud_name==fields['cloud_name']) & \
                (table.c.yaml_name==fields['yaml_name']) \
                )
            )
        db_connection.close()
        if success:
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud YAML file "%s.%s.%s" successfully deleted.' % (fields['group_name'], fields['cloud_name'], fields['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud yaml-delete "%s.%s.%s" failed - %s.' % (lno('CV23'), fields['group_name'], fields['cloud_name'], fields['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud yaml_delete, invalid method "%s" specified.' % (lno('CV24'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud yaml_delete, no cloud name specified.' % lno('CV25'))

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
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV26'), msg), active_user=active_user, user_groups=user_groups)

    # Retrieve YAML file.
    obj_act_id = request.path.split('/') # /cloud/yaml_fetch/<group>.<cloud>.<yaml>
    if len(obj_act_id) > 3:
        id = obj_act_id[3]
        ids = id.split('.')
        if len(ids) == 3:
            YAML = db_map.classes.csv2_group_resource_yaml
            YAMLobj = db_session.query(YAML).filter((YAML.group_name==ids[0]) & (YAML.cloud_name==ids[1]) & (YAML.yaml_name==ids[2]))
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV27'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [YAML_KEYS], db_engine, ['csv2_group_resource_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s cloud yaml-update %s' % (lno('CV28'), msg), active_user=active_user, user_groups=user_groups)

        # Update the cloud yaml file.
        table = tables['csv2_group_resource_yaml']
        success,message = db_execute(db_connection, table.update().where( \
            (table.c.group_name==fields['group_name']) & \
            (table.c.cloud_name==fields['cloud_name']) & \
            (table.c.yaml_name==fields['yaml_name']) \
            ).values(table_fields(fields, table, columns, 'update')))
        db_connection.close()
        if success:
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud YAML file "%s.%s.%s" successfully  updated.' % (fields['group_name'], fields['cloud_name'], fields['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud yaml-update "%s.%s.%s" failed - %s.' % (lno('CV29'), fields['group_name'], fields['cloud_name'], fields['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud yaml_update, invalid method "%s" specified.' % (lno('CV30'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud yaml_update, no cloud name specified.' % lno('CV31'))

