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
                    return 1, None, 'password update received a password but no verify password; both are required.'

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

def manage_user_group_lists(tables, groups, users):

    from sqlalchemy.sql import select

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", groups, users)
    db_engine,db_session,db_connection,db_map = db_open()
    
    #table_users = tables['csv2_user']
    #table_groups = tables['csv2_groups']
    #table_user_groups = tables['csv2_user_groups']

    table = tables['csv2_user_groups']

    if isinstance(users, str):
        users = [users]
        print(">>>>>>>>>>>>>>>>list_test>>>>>>>>>>>>>>>>>>", users)


    for user in users:

        db_groups=[]
        
        
        s = select([table]).where(table.c.username==user)
        user_groups_list = qt(db_connection.execute(s))

        # put all the user's groups in a list
        for group in user_groups_list:
            db_groups.append(group['group_name'])

        # group is on the page and not in the db, add it
        add_groups = [x for x in groups if x not in db_groups]   

        add_fields = {}
        for group in add_groups:
            #add_fields[user]=group
            success,message = db_execute(db_connection, table.insert().values(username=user, group_name=group))

        #success,message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        #success,message = db_execute(db_connection, table.insert().values(add_fields))



        # group is in the db but not the page, remove it
        remove_groups = [x for x in db_groups if x not in groups]
        
        remove_fields = {}
        for group in remove_groups:
            #remove_fields[user]=group
            success,message = db_execute(db_connection,
            table.delete((table.c.username==user) & (table.c.group_name==group))
            )



        '''
        success,message = db_execute(db_connection,
            table.delete( (table.c.username==remove_fields['username']) & (table.c.group_name==remove_fields['group_name']))
            )
        '''

        print(">>>>>>>>>>>>>>>>db_group>s>>>>>>>>>>>>>>>>>>", user, db_groups)
        print(">>>>>>>>>>>>>>>>add_groups>>>>>>>>>>>>>>>>>>", user, add_groups)
        print(">>>>>>>>>>>>>>>remove_groups>>>>>>>>>>>>>>>>", user, remove_groups)
    
    return 0, 'xxx'

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

    if keys and ('primary' not in keys or 'secondary' not in keys):
        raise Exception('view_utils.qt: "keys" dictionary requires both "primary" and "secondary" entries')

    from .view_utils import _qt, _qt_list

    primary_list = []
    secondary_dict = {}

    if query:
        Query = query
    else:
        Query = []
    for row in Query:
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
                        new_row[col] = cols[col]


                primary_list.append(new_row)

        else:
            new_row = {}
            for col in cols:
                if col not in prune:
                  new_row[col] = cols[col]

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

    from django.shortcuts import render as django_render
    from django.http import HttpResponse
    from django.db.models.query import QuerySet
    from sqlalchemy.orm.query import Query
    from sqlalchemy.engine.result import ResultProxy
    from .models import user as csv2_user
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

            if isinstance(obj, Query):
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    data = obj.__getattribute__(field)
                    try:
                        json.dumps(data) # this will fail on non-encodable values, like other classes
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
                # a json-encodable dict
                return json.dumps(fields)

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

def table_fields(Fields, Table, Columns, selection):
    """
    This function returns input fields for the specified table.

    Arguments:

    Table    - Is a table object as returned by validate_fields.

    Columns  - Are the primary and secondary column lists for tables
               as returned by validate_fields.

    Fields   - Is a dictionary of input fields as returned by
               validate_fields.
    """

    output_fields = {}

    if selection == 'insert':
        for field in Columns[Table.name][0]:
            if field in Fields:
                output_fields[field] = Fields[field]

    if selection == 'insert' or selection == 'update':
        for field in Columns[Table.name][1]:
            if field in Fields:
                output_fields[field] = Fields[field]

    return output_fields

#-------------------------------------------------------------------------------

def validate_fields(request, fields, db_engine, tables, active_user):
    """
    This function validates/normalizes form fields/command arguments.

    Arguments:

    requests  - is a web request containing POST data.
    db_engine - An open database connection object.
    tables    - is a list of table names.
    fields    - is a  list of structures in the following format:

               CLOUD_FIELDS = {
                   'auto_active_group': active_user.active_group, # or None.
                   'format': {
                       'cloud_name': 'lowercase',
                       'groupname': 'lowercase',

                       'cores_slider': 'ignore',
                       'csrfmiddlewaretoken': 'ignore',
                       'group': 'ignore',
                       'ram_slider': 'ignore',
                       },
                   }


    Possible format strings are:

    array      - Multiple numbered input fields to be returned as a list eg: group_name.1,
                 group_name.2, etc. returned as { 'group_name': [ 'val1', 'val2', etc. ]}
    az09       - Make sure the input value is all lowercase and nummerics (or error).
    boolean    - A value of True or False will be inserted into the out put fields.
    ignore     - The input field is not defined in the tables but can be ignored.
    lowercase  - Make sure the input value is all lowercase (or error).
    password   - A password value to be checked and hashed
    password1  - A password value to be verified against password2, checked and hashed.
    password2  - A password value to be verified against password1, checked and hashed.
    uppercase  - Make sure the input value is all uppercase (or error).
    """

    from .view_utils import _validate_fields_ignore_field_error, _validate_fields_pw_check
    from sqlalchemy import Table, MetaData
    import re

    # Retrieve relevant (re: tables) schema.
    all_columns = []
    primary_key_columns = []
    Tables = {}
    Columns = {}
    for table_option in tables:
        table = table_option.split(',')
        
        try:
            Tables[table[0]] = Table(table[0], MetaData(bind=db_engine), autoload=True)
        except:
            raise Exception('view_utils.validate_fields: "tables" parameter contains an invalid table name "%s".' % table[0])
            
        if len(table) > 1 and table[1] == 'n':
            continue

        Columns[table[0]] = [[], []]
        for column in Tables[table[0]].c:
            if column not in all_columns:
                all_columns.append(column.name)

            if column.primary_key:
                Columns[table[0]][0].append(column.name)
                if column not in primary_key_columns:
                    primary_key_columns.append(column.name)
            else:
                Columns[table[0]][1].append(column.name)

    # Process fields parameter:
    Formats = {}
    Options = {
        'auto_active_group': False,
        'unnamed_fields_are_bad': False,
        }

    for option_set in fields:
        for option in option_set:
            if option == 'format':
                for field in option_set[option]:
                    Formats[field] = option_set[option][field]
            else:
                Options[option] = option_set[option]

    # Process input fields.
    Fields = {}
    for field in request.POST:
        if Options['unnamed_fields_are_bad'] and field not in Formats:
            return 1, 'request contained a unnamed/bad parameter "%s".' % field, None, None, None

        field_alias = field
        value = request.POST[field]

        if field in Formats:
            if Formats[field] == 'az09':
                if re.match("^[a-z0-9_-]*$", request.POST[field]):
                    value = request.POST[field].lower()
                else:
                    return 1, 'value specified for "%s" must be all lower case and numeric digits.' % field, None, None, None

            if Formats[field] == 'lowercase':
                value = request.POST[field].lower()
                if request.POST[field] != value:
                    return 1, 'value specified for "%s" must be all lower case.' % field, None, None, None

            elif Formats[field] == 'password':
                rc, value = _validate_fields_pw_check(request.POST[field])
                if rc != 0:
                    return 1, value, None, None, None

            elif Formats[field] == 'password1':
                field_alias = '%s2' % field[:-1]
                pw2 = request.POST.get(field_alias)
                if not pw2:
                    if not request.POST[field]:
                        continue
                    return 1, 'password update received a password but no verify password; both are required.', None, None, None

                rc, value = _validate_fields_pw_check(request.POST[field],pw2=pw2)
                if rc != 0:
                    return 1, value, None, None, None
                field_alias = field[:-1]

            elif Formats[field] == 'password2':
                field_alias = '%s1' % field[:-1]
                if not request.POST.get(field_alias):
                    if not request.POST[field]:
                        continue
                    return 1, 'password update received a verify password but no password; both are required.', None, None, None
                continue

            elif Formats[field] == 'uppercase':
                value = request.POST[field].upper()
                if request.POST[field] != value:
                    return 1, 'value specified for "%s" must be all upper case.' % field, None, None, None

        if field_alias in all_columns:
            if value or field_alias != 'password':
                Fields[field_alias] = value
        else: 
            array_field = field.split('.')
            if array_field[0] in all_columns:
                if array_field[0] not in Fields:
                    Fields[array_field[0]] = []
                Fields[array_field[0]].append(value)
            else:
                if not _validate_fields_ignore_field_error(Formats, field):
                    return 1, 'request contained a bad parameter "%s".' % field, None, None, None

    if Options['auto_active_group'] and 'group_name' not in Fields:
        Fields['group_name'] = active_user.active_group

    for field in primary_key_columns:
        if field not in Fields and not _validate_fields_ignore_field_error(Formats, field):
            return 1, 'request did not contain mandatory parameter "%s".' % field, None, None, None

    for field in Formats:
        if Formats[field] == 'boolean':
            if request.POST.get(field):
                Fields[field] = True
            else:
                Fields[field] = False

    return 0, None, Fields, Tables, Columns

#-------------------------------------------------------------------------------

def _validate_fields_ignore_field_error(Formats, field):
    """
    Check if a field error should be ignore.
    """

    if field in Formats and Formats[field] == 'ignore':
        return True

    return False
#-------------------------------------------------------------------------------

def _validate_fields_pw_check(pw1, pw2=None):
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

def verifyUser(request):
    auth_user = getAuthUser(request)

    csv2_user_list = csv2_user.objects.all()
    #try to find a user that has "auth_user" as username or cert_cn
    # the uniqueness here will be forced on user creation
    for user in csv2_user_list:
        if user.username == auth_user or user.cert_cn == auth_user:
            return True

    return False

