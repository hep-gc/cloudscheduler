from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

'''
UTILITY FUNCTIONS
'''
#-------------------------------------------------------------------------------

def db_execute(db_connection, request):
    """
    Execute a DB request and return the response. Also, trap and return errors.
    """

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
    Provide a database connection and mapping.
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

def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_cn == authorized_user:
            return user.is_superuser
    return False

#-------------------------------------------------------------------------------

def lno(id):
    """
    This function returns the source file line number of the caller.
    """

    from inspect import currentframe

    cf = currentframe()
    return '%s-%s' % (id, cf.f_back.f_lineno)

#-------------------------------------------------------------------------------

def map_parameter_to_field_values(request, db_engine, query, table_keys, active_user):
    """
    This function maps form fields/command arguments to table columns.
    """

    # Set up to handle table_keys, mandatory: auto_active_group (bolean), primary(list), 
    # optional: secondary_filter(list), ignore_bad(list), and format(dict).

    auto_active_group = table_keys['auto_active_group']
    primary_keys = table_keys['primary']

    if 'secondary_filter' in table_keys:
        secondary_filter = table_keys['secondary_filter']
    else:
        secondary_filter = None

    if 'ignore_bad' in table_keys:
        ignore_bad = table_keys['ignore_bad']
    else:
        ignore_bad = None

    if 'format' in table_keys:
        format = table_keys['format']
    else:
        format = None

    from sqlalchemy import Table, MetaData
    from .view_utils import _map_parameter_to_field_values_pw_check

    metadata = MetaData(bind=db_engine)
    table = Table(query, metadata, autoload=True)

    values = [{}, {}, []]
    for key in request.POST:
        rekey = key
        value = request.POST[key]

        if format and key in format:
            if format[key] == 'l':
                value = request.POST[key].lower()
                if request.POST[key] != value:
                    return 1, None, 'value specified for "%s" must be all lower case.' % key

            elif format[key] == 'p':
                rc, value = _map_parameter_to_field_values_pw_check(request.POST[key])
                if rc != 0:
                    return 1, None, value

            elif format[key] == 'p1':
                rekey = '%s2' % key[:-1]
                pw2 = request.POST.get(rekey)
                if not pw2:
                    return 1, 'password update received a password but no verify password; both are required.'

                rc, value = _map_parameter_to_field_values_pw_check(request.POST[key],pw2=pw2)
                if rc != 0:
                    return 1, None, value
                rekey = key[:-1]

            elif format[key] == 'p2':
                rekey = '%s1' % key[:-1]
                if not request.POST.get(rekey):
                    return 1, None, 'password update received a verify password but no password; both are required.'
                rekey = None

            elif format[key] == 'u':
                value = request.POST[key].upper()
                if request.POST[key] != value:
                    return 1, None, 'value specified for "%s" must be all upper case.' % key

        if rekey and rekey in table.c:
            if key in primary_keys:
                values[0][rekey] = value
            else:
                if not secondary_filter or key in secondary_filter:
                    if value or not (key in format and format[key][0] == 'p'):
                        values[1][rekey] = value
        else:
            if rekey and key not in ignore_bad:
                return 1, None, 'request contained a bad parameter "%s".' % key

    if auto_active_group and 'group_name' not in values[0]:
        values[0]['group_name'] = active_user.active_group

    if format:
        for key in format:
            if format[key] == 'b':
                if request.POST.get(key):
                    boolean_value = True
                else:
                    boolean_value = False

                if key in primary_keys:
                    values[0][key] = boolean_value
                else:
                    values[1][key] = boolean_value

    for key in table.c:
        values[2].append(key.name)

    return 0, table, values

#-------------------------------------------------------------------------------

def _map_parameter_to_field_values_pw_check(pw1, pw2=None):
    """
    Ensure passwords conform to certain standards.
    """
    import bcrypt

    if len(pw1) < 6:
      return 1, 'value specified for a password is less than 6 characters.'

    if len(pw1) < 16:
      rc =   any(pwx.islower() for pwx in pw1) and any(pwx.isupper() for pwx in pw1) and any(pwx.isnumeric() for pwx in pw1)
      if not rc:
        return 1, 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.'

    if pw2 and pw2 != pw1:
        return 1, 'values specified for passwords do not match.'


    return 0, bcrypt.hashpw(pw1.encode(), bcrypt.gensalt(prefix=b"2a"))

#-------------------------------------------------------------------------------

def qt(query, keys=None, prune=[]):
    """
    Query Transform takes a list of dictionaries (eg. the result of an SqlAlchemy query)
    and transforms it into a standard python list (repeatably iterable). In the process,
    it can make the following transformations:

        o It can delete columns from the rows (prune=[col1, col2,..]).
        o It can split the query into a list and corresponding dictionaries (
          (keys={ 'primary': [...], 'secondary': [...], 'match_list': [...]).

    Splitting a query into a list and corresponding dictionaries:

    If the keys parameter is specified, it must contain both a 'primary' and
    'secondary' list of keys, and optionally, a 'match_lst'.  For each row in
    the input query, which must contain all primary/secondary keys, qt uses
    the two key lists as follows:

    o For all keys in the primary list and any other key in the query not 
      mentioned in the secondary list, qt copies the values from the query
      into the primary output list.

    o For all keys in the primary list, plus the first key in the secondary
      list, qt creates a multi-level, nested output dictionary and copies
      the values for all secondary keys from the query into the lowest level
      dictionary.

    The 'match_list' is both a switch (requesting additional processing) and
    complimantary input. It causes qt to generate and return a multi-level
    nested dictionary/list of all secondary key values per compound primary
    key. The match list must contain all the primary keys and is used to
    build an empty structure with all possible compound privary key values.
    Subsequently, qt scans the secondary dictionary extracting the secondary
    keys to be listed.
    
    An practical example of list splitting can be found in user_views.py, which
    doese the following:
    
    # Retrieve the user list but loose the passwords.
    s = select([view_user_groups_and_available_groups])
    user_list = qt(db_connection.execute(s), prune=['password'])

    # Retrieve user/groups list (dictionary containing list for each user).
    s = select([csv2_user_groups])
    ignore1, ignore2, groups_per_user = qt(
        db_connection.execute(s),
        keys = {
            'primary': [
                'username',
                ],
            'secondary': [
                'group_name',
                ],
            'match_list': user_list,
            }
        )

    # Retrieve  available groups list (dictionary containing list for each user).
    s = select([view_user_groups_available])
    ignore1, ignore2, available_groups_per_user = qt(
        db_connection.execute(s),
        keys = {
            'primary': [
                'username',
                ],
            'secondary': [
                'group_name',
                'available',
                ],
            'match_list': user_list,
            }
        )
    """

    from .view_utils import _qt, _qt_list

    if keys and ('primary' not in keys or 'secondary' not in keys):
        raise Exception('view_utils.qt: "keys" dictionary requires both "primary" and "secondary" entries')

    primary_list = []
    secondary_dict = {}

    for row in query:
        cols = dict(row)

        if keys:
            add_row = False
            secondary_dict_ptr = secondary_dict
            for key in keys['primary']:
                add_row, secondary_dict_ptr = _qt(add_row, secondary_dict_ptr, cols, key)
             
            if keys['secondary']:
                ignore, secondary_dict_ptr = _qt(add_row, secondary_dict_ptr, cols, keys['secondary'][0])
            
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
        if 'match_list' in keys:
            matched_dict = {}

            for row in keys['match_list']:
                matched_dict_ptr = matched_dict
                for key in keys['primary'][:-1]:
                    add_row, matched_dict_ptr = _qt(add_row, matched_dict_ptr, row, key)

                matched_dict_ptr[row[key]] = []

            secondary_dict_ptr = secondary_dict
            matched_dict_ptr = matched_dict

            for secondary_key1 in secondary_dict_ptr:
                if secondary_key1 not in matched_dict_ptr:
                    matched_dict_ptr[secondary_key1] = []

                for secondary_key2 in secondary_dict_ptr[secondary_key1]:
                    matched_dict_ptr[secondary_key1].append(secondary_key2)

            return primary_list, secondary_dict, matched_dict
        else:
            return primary_list, secondary_dict
    else:
        return primary_list

#-------------------------------------------------------------------------------

def _qt(add_row, secondary_dict_ptr, cols, key):
    """
    This sub-function is called by view_utils.qt to add keys to the secondary_dict and
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

def _qt_list(secondary_dict_ptr, secondary_key_list_ptr, cols, key):
    """
    This sub-function is called by view_utils.qt to add keys to the secondary_key_list and
    is NOT meant to be called directly.
    """

    if cols[key]:
        if cols[key] not in secondary_key_list_ptr:
            secondary_key_list_ptr[cols[key]] = {}

        return secondary_dict_ptr[cols[key]], secondary_key_list_ptr[cols[key]]
    else:
      return secondary_dict_ptr, secondary_key_list_ptr

#-------------------------------------------------------------------------------

def render(request, template, context):
    """
    If the "Accept" HTTP header contains "application/json", return a json string. Otherwise,
    return an HTML string.
    """

    from django.contrib.auth.models import User
    from django.shortcuts import render as django_render
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
        response = django_render(request, template, context)

    return response

#-------------------------------------------------------------------------------

def set_user_groups(request, db_session, db_map):
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
    if request.method == 'POST' and 'group' in request.POST:
        group_name = request.POST.get('group')
        if group_name and active_user.active_group != group_name:
            if group_name in user_groups:
                active_user.active_group = group_name
                active_user.save()
            else:
                return 1,'cannnot switch to invalid group "%s".' % group_name, active_user, user_groups

    # if no active group, set first group as default.
    if active_user.active_group is None:
        active_user.active_group = user_groups[0]
        active_user.save()

    return 0, None, active_user, user_groups

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

