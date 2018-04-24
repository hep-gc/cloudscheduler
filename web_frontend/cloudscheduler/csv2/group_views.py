from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import db_open, getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, _render
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc

#-------------------------------------------------------------------------------

MODIFY_IGNORE_KEYS = (
    'action',
    'csrfmiddlewaretoken'
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



#-------------------------------------------------------------------------------

def list(
    request, 
    group=None, 
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
            return _render(request, 'csv2/groups.html', {'response_code': 1, 'message': message})

    #get group info
    s = select([view_groups_with_yaml])
    group_list = {'ResultProxy': [dict(r) for r in db_connection.execute(s)]}

    db_connection.close()

    # Position the page.
    obj_act_id = request.path.split('/')
    if group:
        if group == '-':
            current_group = ''
        else:
            current_group = group
    elif len(obj_act_id) > 2 and len(obj_act_id[3]) > 0:
        current_group = str(obj_act_id[3])
    else:
        if len(group_list['ResultProxy']) > 0:
            current_group = str(group_list['ResultProxy'][0]['group_name'])
        else:
            current_group = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'group_list': group_list,
            'current_group': current_group,
            'response_code': 0,
            'message': None
        }

    return _render(request, 'csv2/groups.html', context)


#-------------------------------------------------------------------------------

def modify(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied


    if request.method == 'POST' and 'action' in request.POST and 'group_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        response_code,message,active_user,user_groups = _set_user_groups(request, db_session, db_map)
        if response_code != 0:
            return list(request, group='-', response_code=1, message=message, active_user=active_user, user_groups=user_groups)

        # map the field list.
        metadata = MetaData(bind=db_engine)
        table = Table('csv2_groups', metadata, autoload=True)


        values = [{}, {}]
        for key in request.POST:
            if key in table.c:
                if key == 'group_name':
                    values[0][key] = request.POST[key]
                else:
                    if request.POST[key]:
                        values[1][key] = request.POST[key]
            else:
                if key not in MODIFY_IGNORE_KEYS:
                    return list(request, group='-', response_code=1, message='group modify request contained bad parameter "%s".' % key, active_user=active_user, user_groups=user_groups)


        if request.POST['action'] == 'add':
            if values[0] and values[1]:
                success,message = _db_execute(db_connection, table.insert().values({**values[0], **values[1]}))



            db_connection.close()
            if success:
                return list(request, group=values[0]['group_name'], response_code=0, message='group "%s" successfully added.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, group=values[0]['group_name'], response_code=1, message='group "%s" add failed - %s.' % (values[0]['group_name'], message), active_user=active_user, user_groups=user_groups)

        elif request.POST['action'] == 'delete':

            # Before deleting make sure there are no VMs running accociated with the group.

            view_status = Table('view_cloud_status', metadata, autoload=True)

            if(db_session.query(exists().where((view_status.c.group_name==values[0]['group_name']) & (view_status.c.VMs==0))).scalar()):
                return list(request, group=values[0]['group_name'], response_code=1, message='group "%s" delete failed. VMs exist on accociated clouds.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups)


            # Delete the group and accociated enteries in other tables:

            # Load the tables:
            table_vms = Table('csv2_vms', metadata, autoload=True)
            table_users = Table('csv2_user_groups', metadata, autoload=True)
            table_defaults = Table('csv2_group_defaults', metadata, autoload=True)
            table_resources = Table('csv2_group_resources', metadata, autoload=True)
            table_resources_yaml = Table('csv2_group_resource_yaml', metadata, autoload=True)
            table_yaml = Table('csv2_group_yaml', metadata, autoload=True)
            table_user_groups = Table('csv2_user_groups', metadata, autoload=True)
            table_networks = Table('cloud_networks', metadata, autoload=True)
            table_limits = Table('cloud_limits', metadata, autoload=True)
            table_images = Table('cloud_images', metadata, autoload=True)
            table_flavors = Table('cloud_flavors', metadata, autoload=True)


            # Delete all rows accociated with target group:
            success,message = _db_execute(db_connection,
                table.delete(table.c.group_name==values[0]['group_name']))

            success1,message1 = _db_execute(db_connection,
                table_users.delete(table_vms.c.group_name==values[0]['group_name']))

            success2,message2 = _db_execute(db_connection,
                table_users.delete(table_users.c.group_name==values[0]['group_name']))

            success3,message3 = _db_execute(db_connection,
                table_defaults.delete(table_defaults.c.group_name==values[0]['group_name']))

            success4,message4 = _db_execute(db_connection,
                table_resources.delete(table_resources.c.group_name==values[0]['group_name']))

            success5,message5 = _db_execute(db_connection,
                table_resources_yaml.delete(table_resources_yaml.c.group_name==values[0]['group_name']))

            success6,message6 = _db_execute(db_connection,
                table_yaml.delete(table_yaml.c.group_name==values[0]['group_name']))

            success7,message7 = _db_execute(db_connection,
                table_user_groups.delete(table_user_groups.c.group_name==values[0]['group_name']))

            success8,message8 = _db_execute(db_connection,
                table_users.delete(table_networks.c.group_name==values[0]['group_name']))

            success9,message9 = _db_execute(db_connection,
                table_users.delete(table_limits.c.group_name==values[0]['group_name']))

            success10,message10 = _db_execute(db_connection,
                table_users.delete(table_images.c.group_name==values[0]['group_name']))

            success11,message11 = _db_execute(db_connection,
                table_users.delete(table_flavors.c.group_name==values[0]['group_name']))

            db_connection.close()

            if success:
                return list(request, group=values[0]['group_name'], response_code=0, message='group "%s" successfully deleted.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, group=values[0]['group_name'], response_code=1, message='group "%s" delete failed - %s.' % (values[0]['group_name'], message), active_user=active_user, user_groups=user_groups)


        elif request.POST['action'] == 'modify':
            success,message = _db_execute(db_connection, table.update().where(table.c.group_name==values[0]['group_name']).values(values[1]))
            db_connection.close()
            if success:
                return list(request, group=values[0]['group_name'], response_code=0, message='group "%s" successfully modified.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups)
            else:
                return list(request, group=values[0]['group_name'], response_code=1, message='group "%s" modify failed - %s.' % (values[0]['group_name'], message), active_user=active_user, user_groups=user_groups)

        else:
            return list(request, group=values[0]['group_name'], response_code=1, message='invalid action "%s" specified.' % request.POST['action'], active_user=active_user, user_groups=user_groups)
    else:
        if request.method == 'POST':
            return list(request, response_code=1, message='invalid method "%s" specified.' % request.method)
        elif 'action' not in request.POST:
            return list(request, response_code=1, message='no action specified.')
        else:
            return list(request, response_code=1, message='no group name specified.')


#-------------------------------------------------------------------------------

def prepare(request):
    """
    This function returns a minimal response plus a CSRF.
    """

    context = {
            'response_code': 0,
            'message': None
    }
    
    return _render(request, 'csv2/groups.html', context)
