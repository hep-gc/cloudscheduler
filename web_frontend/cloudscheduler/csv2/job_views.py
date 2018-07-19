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

# lno: JV - error code identifier.

#-------------------------------------------------------------------------------

CLOUD_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':          'lowerdash',

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
        'cloud_name':          'lowerdash',
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

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':     'ignore',
        'group':                   'ignore',
        },
    }

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
            return render(request, 'csv2/jobs.html', {'response_code': 1, 'message': '%s job list, %s' % (lno('JV00'), msg)})

    # Retrieve VM information.
    s = select([view_condor_jobs_group_defaults_applied]).where(view_condor_jobs_group_defaults_applied.c.group_name == active_user.active_group)
    job_list = qt(db_connection.execute(s), convert={'entered_current_status': 'datetime', 'q_date': 'datetime'})

    db_close(db_ctl)

#   # Position the page.
#   obj_act_id = request.path.split('/')
#   if selector:
#       if selector == '-':
#           current_cloud = ''
#       else:
#           current_cloud = selector
#   elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
#       current_cloud = str(obj_act_id[3])
#   else:
#       if len(cloud_list) > 0:
#           current_cloud = str(cloud_list[0]['cloud_name'])
#       else:
#           current_cloud = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'attributes': attributes,
            'user_groups': user_groups,
            'job_list': job_list,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/jobs.html', context)

