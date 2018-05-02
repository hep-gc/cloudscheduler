from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

'''
UTILITY FUNCTIONS
'''
#-------------------------------------------------------------------------------

def _db_execute(db_connection, request):
    import sqlalchemy.exc

    try:
        db_connection.execute(request)
        return True,None
    except sqlalchemy.exc.IntegrityError as ex:
        return False, ex.orig
    except Exception as ex:
        return False, ex

#-------------------------------------------------------------------------------

def db_open():
    """
    Provide a database connection and optionally mapping.
    """

    from csv2 import config
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.automap import automap_base

    db_engine = create_engine(
        "mysql://%s:%s@%s:%s/%s" % (
            config.db_user,
            config.db_password,
            config.db_host,
            str(config.db_port),
            config.db_name
            )
        )

    db_session = Session(db_engine)
    db_connection = db_engine.connect()
    db_map = automap_base()
    db_map.prepare(db_engine, reflect=True)

    return db_engine,db_session,db_connection,db_map

#-------------------------------------------------------------------------------

# Returns the current authorized user from metadata
def getAuthUser(request):
    return request.META.get('REMOTE_USER')

#-------------------------------------------------------------------------------

# returns the csv2 user object matching the authorized user from header metadata
def getcsv2User(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_cn == authorized_user:
            return user
    raise PermissionDenied

#-------------------------------------------------------------------------------

def verifyUser(request):
    auth_user = getAuthUser(request)

    csv2_user_list = csv2_user.objects.all()
    #try to find a user that has "auth_user" as username or cert_cn
    # the uniqueness here will be forced on user creation
    for user in csv2_user_list:
        if user.username == auth_user or user.cert_cn == auth_user:
            return True

    return False

#-------------------------------------------------------------------------------

def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_cn == authorized_user:
            return user.is_superuser
    return False

#-------------------------------------------------------------------------------

def map_parameter_to_field_values(request, db_engine, query, table_keys, active_user):
    """
    This internal function retrieves and classifies cloud update fields.
    """

    import lib.schema

    metadata = lib.schema.MetaData(bind=db_engine)
    table = lib.schema.Table(query, metadata, autoload=True)

    values = [{}, {}, []]
    for key in request.POST:
        if key in table.c:
            if key in table_keys[0]:
                values[0][key] = request.POST[key]
            else:
                if key != 'password' or request.POST[key]:
                    values[1][key] = request.POST[key]
        else:
            if key not in table_keys[1]:
                return 1, table, key

    if 'group_name' not in values[0]:
        values[0]['group_name'] = active_user.active_group

    for key in table.c:
        values[2].append(key.name)

    return 0, table, values

#-------------------------------------------------------------------------------

def _qt(query, keys=None, prune=[]):
    """
    Query Transform takes a list of dictionaries (eg. the result of an SqlAlchemy query)
    and transforms it into a standard python list (repeatably iterable). In the process,
    it can make the following transformations:

        o It can delete columns from the rows (prune=[col1, col2,..]).
        o It can remove columns from the primary list and create a related
          sub-dictionary. For example:

          keys={
              'primary': ['group_name', 'cloud_name'],
              'secondary': ['yaml_name', 'yaml_enabled', 'yaml_mime_type', 'yaml']
              }
        
          from an input list containing those columns, would return:

          primary_list = [
              {'group_name': <val>, 'cloud_name': <val, <other_non_secodary_columns>},
              {'group_name': <val>, 'cloud_name': <val, <other_non_secodary_columns>},
                  .
                  .
              ],
          secondary_dict = {  
              '<group_name_val>': {
                  '<cloud_name_val>': {
                      'yaml_name_val': {
                          'yaml_name': <val>,
                          'yaml_enabled': <val>,
                          'yaml_mime_type': <val>,
                          'yaml': <val>
                          }
                      }
                  }
              }

    If the "keys" argument is given, the function returns both the primary_list and the
    secondary_dict. Otherwise, only the primary_list is returned.
    """
    from .view_utils import _qtx

    primary_list = []
    secondary_dict = {}

    for row in query:
        cols = dict(row)

        if keys:
            add_row = False
            secondary_dict_ptr = secondary_dict
            for key in keys['primary']:
                add_row, secondary_dict_ptr = _qtx(add_row, secondary_dict_ptr, cols, key)
             
            if keys['secondary']:
                ignore, secondary_dict_ptr = _qtx(add_row, secondary_dict_ptr, cols, keys['secondary'][0])
            
            for col in cols:
                if col in keys['secondary'] and cols[col]:
                    secondary_dict_ptr[col] = cols[col]
            
            if add_row:
                new_row = {}
                for col in cols:
                    if col not in keys['secondary'] + prune:
                      if cols[col]:
                          new_row[col] = cols[col]
                      else:
                          new_row[col] = None

                primary_list.append(new_row)

        else:
            new_row = {}
            for col in cols:
                if col not in prune:
                  if cols[col]:
                      new_row[col] = cols[col]
                  else:
                      new_row[col] = None

            primary_list.append(new_row)

    if keys:
        return primary_list, secondary_dict
    else:
        return primary_list

#-------------------------------------------------------------------------------

def _qtx(add_row, secondary_dict_ptr, cols, key):
    """
    This sub-function is called by view_utils._qt to add keys to the secondary_dict and
    is NOT meant to be called directly.
    """

    if cols[key]:
        if cols[key] in secondary_dict_ptr:
            return add_row, secondary_dict_ptr[cols[key]]
        else:
            secondary_dict_ptr[cols[key]] = {}
            return True, secondary_dict_ptr[cols[key]]
    else:
        return add_row, secondary_dict_ptr

#-------------------------------------------------------------------------------

def _render(request, template, context):
    """
    If the "Accept" HTTP header contains "application/json", return a json string. Otherwise,
    return an HTML string.
    """

    from django.contrib.auth.models import User
    from django.shortcuts import render
    from django.http import HttpResponse
    from django.core import serializers
    from django.db.models.query import QuerySet
    from .models import user as csv2_user
    from sqlalchemy.engine import result as sql_result
    import datetime
    import decimal
    import json

    class csv2Encoder(json.JSONEncoder):
        def default(self, obj):
#           print(">>>>>>>>>>>>>>>>", type(obj), obj)

            if isinstance(obj, csv2_user):
                return str(obj)

            if isinstance(obj, datetime.date):
                return str(obj)

            if isinstance(obj, decimal.Decimal):
                return str(obj)

            if isinstance(obj, dict) and 'ResultProxy' in obj:
                return json.dumps(obj['ResultProxy'])

            return json.JSONEncoder.default(self, obj)

    if request.META['HTTP_ACCEPT'] == 'application/json':
        response = HttpResponse(json.dumps(context, cls=csv2Encoder), content_type='application/json')
    else:
        response = render(request, template, context)
    return response

#       serialized_context = {}
#       for item in context:
#           if isinstance(context[item], int):
#               serialized_context[item] = context[item]
#           elif isinstance(context[item], QuerySet):
#               serialized_context[item] = serializers.serialize("json", context[item])
#           elif isinstance(context[item], sql_result.ResultProxy):
#               serialized_context[item] = json.dumps([dict(r) for r in context[item]], cls=csv2Encoder)
#           elif isinstance(context[item], dict) and 'ResultProxy' in context[item]:
#               serialized_context[item] = json.dumps(context[item]['ResultProxy'], cls=csv2Encoder)
#           else:
#               serialized_context[item] = str(context[item])
#               if serialized_context[item] == 'None':
#                 serialized_context[item] = None

#-------------------------------------------------------------------------------

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


