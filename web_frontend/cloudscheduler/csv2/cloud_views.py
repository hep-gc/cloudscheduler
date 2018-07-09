from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user
from . import config

from .view_utils import \
    db_close, \
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

# lno: CV - error code identifier.

#-------------------------------------------------------------------------------

CLOUD_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':              'lowerdash',
        'cloud_type':              ('csv2_cloud_types', 'cloud_type'),
        'cores_ctl':               'integer',
        'ram_ctl':                 'integer',

        'cores_slider':            'ignore',
        'csrfmiddlewaretoken':     'ignore',
        'group':                   'ignore',
        'ram_slider':              'ignore',
        },
    }

METADATA_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':              'lowerdash',
        'enabled':                 'dboolean',
        'priority':                'integer',
        'metadata':                'metadata',
        'metadata_name':           'lowercase',
        'mime_type':               ('csv2_mime_types', 'mime_type'),

        'csrfmiddlewaretoken':     'ignore',
        'group':                   'ignore',
        },
    }

IGNORE_METADATA_NAME = {
    'format': {
        'metadata_name':            'ignore',
        },
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':     'ignore',
        'group':                   'ignore',
        },
    }

METADATA_LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':     'ignore',
        'group':                   'ignore',
        'metadata_list_option':    ['merge'],
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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [CLOUD_KEYS], db_ctl, ['csv2_group_resources'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s cloud add %s' % (lno('CV01'), msg), active_user=active_user, user_groups=user_groups)

        # Add the cloud.
        table = tables['csv2_group_resources']
        rc, msg = db_execute(db_ctl, table.insert().values(table_fields(fields, table, columns, 'insert')))
        db_connection.close()
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s::%s" successfully added.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add "%s::%s" failed - %s.' % (lno('CV02'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV05'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [CLOUD_KEYS, IGNORE_METADATA_NAME], db_ctl, ['csv2_group_resources', 'csv2_group_resource_metadata'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s cloud delete %s' % (lno('CV06'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any cloud metadata files for the cloud.
        table = tables['csv2_group_resource_metadata']
        rc, msg = db_execute(db_ctl, table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])), allow_no_rows=True)
        if rc != 0:
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-delete "%s::%s.*" failed - %s.' % (lno('CV07'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud.
        table = tables['csv2_group_resources']
        rc, msg = db_execute(
            db_ctl,
            table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name']))
            )
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s::%s" successfully deleted.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud delete "%s::%s" failed - %s.' % (lno('CV08'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud delete, invalid method "%s" specified.' % (lno('CV09'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud delete, no cloud name specified.' % lno('CV10'))

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
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(request, [LIST_KEYS], db_ctl, [], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': '%s cloud list, %s' % (lno('CV11'), msg)})

    s = select([csv2_cloud_types])
    type_list = qt(db_connection.execute(s))

    # Retrieve cloud information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_group_resources_with_metadata_names]).where(view_group_resources_with_metadata_names.c.group_name == active_user.active_group)
        cloud_list = qt(db_connection.execute(s), prune=['password'])
        metadata_dict = {}
    else:
        s = select([view_group_resources_with_metadata]).where(view_group_resources_with_metadata.c.group_name == active_user.active_group)
        cloud_list, metadata_dict = qt(
            db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
                    'cloud_name'
                    ],
                'secondary': [
                    'metadata_name',
                    'metadata_enabled',
                    'metadata_priority',
                    'metadata_mime_type',
                    'metadata',
                    ]
                },
            prune=['password']    
            )

    db_close(db_ctl)

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
            'metadata_dict': metadata_dict,
            'current_cloud': current_cloud,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/clouds.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_add(request):
    """
    This function should recieve a post request with a payload of metadata configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'cloud_name' in request.POST and \
        'metadata_name' in request.POST:

        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV12'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [METADATA_KEYS], db_ctl, ['csv2_group_resource_metadata', 'csv2_group_resources,n'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s cloud metadata-add %s' % (lno('CV13'), msg), active_user=active_user, user_groups=user_groups)

        # Check cloud already exists.
        table = tables['csv2_group_resources']
        s = select([csv2_group_resources]).where(csv2_group_resources.c.group_name == active_user.active_group)
        cloud_list = db_connection.execute(s)
        found = False
        for cloud in cloud_list:
            if active_user.active_group == cloud['group_name'] and fields['cloud_name'] == cloud['cloud_name']:
                found = True
                break

        if not found:
            return list(request, selector='-', response_code=1, message='%s cloud metadata-add failed, cloud name  "%s" does not exist.' % (lno('CV14'), fields['cloud_name']), active_user=active_user, user_groups=user_groups)

        # Add the cloud metadata file.
        table = tables['csv2_group_resource_metadata']
        rc, msg = db_execute(db_ctl, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud metadata file "%s::%s::%s" successfully added.' % (fields['group_name'], fields['cloud_name'], fields['metadata_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-add "%s::%s::%s" failed - %s.' % (lno('CV15'), fields['group_name'], fields['cloud_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud metadata_add, invalid method "%s" specified.' % (lno('CV16'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud metadata_add, no cloud name specified.' % lno('CV17'))

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_collation(request):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV18'), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(request, [METADATA_LIST_KEYS], db_ctl, [], active_user)
    if rc != 0:        
        db_close(db_ctl)
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV19'), msg)})

    # Retrieve cloud/metadata information.
    s = select([view_metadata_collation]).where(view_metadata_collation.c.group_name == active_user.active_group)
    cloud_metadata_list = qt(db_connection.execute(s))

    db_close(db_ctl)

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_metadata_list': cloud_metadata_list,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/cloud_metadata_list.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_delete(request):
    """
    This function should recieve a post request with a payload of metadata configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'cloud_name' in request.POST and \
        'metadata_name' in request.POST:

        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %S' % (lno('CV20'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [METADATA_KEYS], db_ctl, ['csv2_group_resource_metadata'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s cloud metadata-delete %s' % (lno('CV21'), msg), active_user=active_user, user_groups=user_groups)

        # Delete the cloud metadata file.
        table = tables['csv2_group_resource_metadata']
        rc, msg = db_execute(
            db_ctl,
            table.delete( \
                (table.c.group_name==fields['group_name']) & \
                (table.c.cloud_name==fields['cloud_name']) & \
                (table.c.metadata_name==fields['metadata_name']) \
                )
            )
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud metadata file "%s::%s::%s" successfully deleted.' % (fields['group_name'], fields['cloud_name'], fields['metadata_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-delete "%s::%s::%s" failed - %s.' % (lno('CV22'), fields['group_name'], fields['cloud_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud metadata_delete, invalid method "%s" specified.' % (lno('CV23'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud metadata_delete, no cloud name specified.' % lno('CV24'))

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV25'), msg), active_user=active_user, user_groups=user_groups)

    # Retrieve metadata file.
    obj_act_id = request.path.split('/') # /cloud/metadata_fetch/<group>.<cloud>.<metadata>
    if len(obj_act_id) > 3:
        id = obj_act_id[3]
        ids = id.split('::')
        if len(ids) == 2:
            METADATA = db_map.classes.csv2_group_resource_metadata
            METADATAobj = db_session.query(METADATA).filter((METADATA.group_name == active_user.active_group) & (METADATA.cloud_name==ids[0]) & (METADATA.metadata_name==ids[1]))
            if METADATAobj:
                for row in METADATAobj:
                    context = {
                        'group_name': row.group_name,
                        'cloud_name': row.cloud_name,
                        'metadata': row.metadata,
                        'metadata_enabled': row.enabled,
                        'metadata_priority': row.priority,
                        'metadata_mime_type': row.mime_type,
                        'metadata_name': row.metadata_name,
                        'response_code': 0,
                        'message': None,
                        'enable_glint': config.enable_glint
                        }
                
                    db_close(db_ctl)
                    return render(request, 'csv2/clouds.html', context)
             
    db_close(db_ctl)

    if id:
      return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': 'cloud metadata_fetch, received an invalid metadata file id "%s::%s".' % (active_user.active_group, id)})
    else:
      return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': 'cloud metadata_fetch, metadata file id omitted.'})

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_list(request):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV26'), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(request, [METADATA_LIST_KEYS], db_ctl, [], active_user)
    if rc != 0:        
        db_close(db_ctl)
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV27'), msg)})

    # Retrieve cloud/metadata information.
    s = select([csv2_group_resource_metadata]).where(csv2_group_resource_metadata.c.group_name == active_user.active_group)
    cloud_metadata_list = qt(db_connection.execute(s))

    db_close(db_ctl)

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_metadata_list': cloud_metadata_list,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/cloud_metadata_list.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_update(request):
    """
    This function should recieve a post request with a payload of metadata configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and \
        'cloud_name' in request.POST and \
        'metadata_name' in request.POST:

        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV28'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [METADATA_KEYS], db_ctl, ['csv2_group_resource_metadata'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s cloud metadata-update %s' % (lno('CV29'), msg), active_user=active_user, user_groups=user_groups)

        # Update the cloud metadata file.
        table = tables['csv2_group_resource_metadata']
        rc, msg = db_execute(db_ctl, table.update().where( \
            (table.c.group_name==fields['group_name']) & \
            (table.c.cloud_name==fields['cloud_name']) & \
            (table.c.metadata_name==fields['metadata_name']) \
            ).values(table_fields(fields, table, columns, 'update')))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud metadata file "%s::%s::%s" successfully  updated.' % (fields['group_name'], fields['cloud_name'], fields['metadata_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-update "%s::%s::%s" failed - %s.' % (lno('CV30'), fields['group_name'], fields['cloud_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud metadata_update, invalid method "%s" specified.' % (lno('CV31'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud metadata_update, no cloud name specified.' % lno('CV32'))

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
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV33'), msg), active_user=active_user, user_groups=user_groups)

    # get cloud status per group
    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == active_user.active_group)
    cloud_status_list = qt(db_connection.execute(s))

    # get job status per group
    s = select([view_job_status]).where(view_job_status.c.group_name == active_user.active_group)
    job_status_list = qt(db_connection.execute(s))

    db_close(db_ctl)

    cloud_total_list = {}


    cloud_total_list["cores_available"] = 0


    for d in cloud_status_list:
        for key, value in d.items():
            if key in cloud_total_list:
                cloud_total_list[key] += value
            else:
                cloud_total_list[key] = value

        if d["cores_ctl"] == -1 or d["cores_ctl"] > d["cores_idle"]:
            cloud_total_list["cores_available"] += d["cores_idle"] 
        else:
            cloud_total_list["cores_available"] += d["cores_ctl"]
    


    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_status_list': cloud_status_list,
            'cloud_total_list': cloud_total_list,
            'job_status_list': job_status_list,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV34'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [CLOUD_KEYS], db_ctl, ['csv2_group_resources'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s cloud update %s' % (lno('CV35'), msg), active_user=active_user, user_groups=user_groups)

        # update the cloud.
        table = tables['csv2_group_resources']
        rc, msg = db_execute(db_ctl, table.update().where((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])).values(table_fields(fields, table, columns, selection='update')))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s::%s" successfully updated.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update "%s::%s" failed - %s.' % (lno('CV36'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s cloud update, invalid method "%s" specified.' % (lno('CV37'), request.method))
        else:
            return list(request, response_code=1, message='%s cloud update, no cloud name specified.' % lno('CV38'))

