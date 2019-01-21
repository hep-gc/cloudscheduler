from django.core.exceptions import PermissionDenied

import time
from sqlalchemy.orm.session import make_transient

'''
UTILITY FUNCTIONS
'''

#-------------------------------------------------------------------------------

def diff_lists(list1,list2, option=None):
    """
    if option equal 'and', return a list of items which are in both list1
    and list2. Otherwise, return a list of items in list1 but not in list2.
    """

    if option and option == 'and':
        return [x for x in list1 if x in list2] 
    else:
        return [x for x in list1 if x not in list2] 

#-------------------------------------------------------------------------------
# returns the csv2 user object matching the authorized user from header metadata
def getcsv2User(request, db_config):
    authorized_user = request.META.get('REMOTE_USER')
    # need to get user objects from database here
    Csv2_User = db_config.db_map.classes.csv2_user
    csv2_user_list = db_config.db_session.query(Csv2_User)
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_cn == authorized_user:
            return user
    raise PermissionDenied

#-------------------------------------------------------------------------------

def kill_retire(config, group_name, cloud_name, option, count):
    from cloudscheduler.lib.schema import view_vm_kill_retire_priority_age, view_vm_kill_retire_priority_idle

    # Process "control [cores, ram]".
    if option == 'control':
        s = 'set @cores=0; set @ram=0; create or replace temporary table kill_retire_priority_list as select * from (select *,(@cores:=@cores+flavor_cores) as cores,(@ram:=@ram+flavor_ram) as ram from view_vm_kill_retire_priority_age where group_name="%s" and cloud_name="%s" and killed<1 and retired<1 order by priority asc) as kpl where cores>%s or ram>%s;' % (group_name, cloud_name, count[0], count[1])
        config.db_connection.execute(s)
        config.db_connection.execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set terminate=1 where kpl.machine is null;')
        config.db_connection.execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set retire=1 where kpl.machine is not null;')
    
    # Process "kill N".
    elif option == 'kill':
        if cloud_name == '-':
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_idle where group_name="%s" and killed<1 order by priority desc limit %s;' % (group_name, count)
        else:
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_idle where group_name="%s" and cloud_name="%s" and killed<1 order by priority desc limit %s;' % (group_name, cloud_name, count)

        config.db_connection.execute(s)
        config.db_connection.execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set terminate=1;')

    # Process "retire N".
    elif option == 'retire':
        if cloud_name == '-':
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_idle where group_name="%s" and machine is not null and killed<1 and retired<1 order by priority desc limit %s;' % (group_name, count)
        else:
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_idle where group_name="%s" and cloud_name="%s" and machine is not null and killed<1 and retired<1 order by priority desc limit %s;' % (group_name, cloud_name, count)

        config.db_connection.execute(s)
        config.db_connection.execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set retire=1;')

    # Process "retain N".
    elif option == 'retain':
        if cloud_name == '-':
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_age where group_name="%s" and killed<1 and retired<1 order by priority asc limit %s, 999999999999;' % (group_name, count)
        else:
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_age where group_name="%s" and cloud_name="%s" and killed<1 and retired<1 order by priority asc limit %s, 999999999999;' % (group_name, cloud_name, count)

        config.db_connection.execute(s)
        config.db_connection.execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set terminate=1 where kpl.machine is null;')
        config.db_connection.execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set retire=1 where kpl.machine is not null;')
    
    retired_list = qt(config.db_connection.execute('select count(*) as count from kill_retire_priority_list;'))
    return retired_list[0]['count']

#-------------------------------------------------------------------------------

def lno(id):
    """
    This function returns the source file line number of the caller.
    """

    from inspect import currentframe

    cf = currentframe()
    return '%s-%s' % (id, cf.f_back.f_lineno)

#-------------------------------------------------------------------------------

def manage_group_users(config, tables, group, users, option=None):
    """
    Ensure all the specified users and only the specified users are
    members of the specified group. The specified group and users
    have all been pre-verified.
    """

    from sqlalchemy.sql import select

    table = tables['csv2_user_groups']

    # if there is only one user, make it a list anyway
    if users:
        if isinstance(users, str):
            user_list = users.split(',')
        else:
            user_list = users
    else:
        user_list = []

    # Retrieve the list of users already in the group.
    db_users=[]

    s = select([table]).where(table.c.group_name==group)
    user_groups_list = qt(config.db_connection.execute(s))

    for row in user_groups_list:
        db_users.append(row['username'])

    if not option or option == 'add':
        # Get the list of users specified that are not already in the group.
        add_users = diff_lists(user_list, db_users)

        # Add the missing users.
        for user in add_users:
            rc, msg = config.db_session_execute(table.insert().values(username=user, group_name=group))
            if rc != 0:
                return 1, msg

    if not option:
        # Get the list of users that the group currently has but were not specified.
        remove_users = diff_lists(db_users, user_list)
        
        # Remove the extraneous users.
        for user in remove_users:
            rc, msg = config.db_session_execute(table.delete((table.c.username==user) & (table.c.group_name==group)))
            if rc != 0:
                return 1, msg

    elif option == 'delete':
        # Get the list of users that the group currently has and were specified.
        remove_users = diff_lists(user_list, db_users, option='and')
        
        # Remove the extraneous users.
        for user in remove_users:
            rc, msg = config.db_session_execute(table.delete((table.c.username==user) & (table.c.group_name==group)))
            if rc != 0:
                return 1, msg

    return 0, None

#-------------------------------------------------------------------------------

def manage_user_groups(config, tables, user, groups, option=None):
    """
    Ensure all the specified groups and only the specified groups are
    have the specified user as a member. The specified user and groups
    have all been pre-verified.
    """

    from sqlalchemy.sql import select

    table = tables['csv2_user_groups']

    # if there is only one group, make it a list anyway
    if groups:
        if isinstance(groups, str):
            group_list = groups.split(',')
        else:
            group_list = groups
    else:
        group_list = []

    # Retrieve the list of groups the user already has.
    db_groups=[]
    
    s = select([table]).where(table.c.username==user)
    user_groups_list = qt(config.db_connection.execute(s))

    for row in user_groups_list:
        db_groups.append(row['group_name'])

    if not option or option == 'add':
        # Get the list of groups specified that the user doesn't already have.
        add_groups = diff_lists(group_list, db_groups)

        # Add the missing groups.
        for group in add_groups:
            rc, msg = config.db_session_execute(table.insert().values(username=user, group_name=group))
            if rc != 0:
                return 1, msg

    if not option:
        # Get the list of groups that the user currently has but were not specified.
        remove_groups = diff_lists(db_groups, group_list)
        
        # Remove the extraneous groups.
        for group in remove_groups:
            rc, msg = config.db_session_execute(table.delete((table.c.username==user) & (table.c.group_name==group)))
            if rc != 0:
                return 1, msg

    elif option == 'delete':
        # Get the list of groups that the user currently has and were specified.
        remove_groups = diff_lists(group_list, db_groups, option='and')
        
        # Remove the extraneous groups.
        for group in remove_groups:
            rc, msg = config.db_session_execute(table.delete((table.c.username==user) & (table.c.group_name==group)))
            if rc != 0:
                return 1, msg

    return 0, None

#-------------------------------------------------------------------------------

def manage_user_group_verification(config, tables, users, groups):
    """
    Make sure the specified users and groups exist.
    """

    from sqlalchemy.sql import select

    if users:
        # if there is only one user, make it a list anyway
        if isinstance(users, str):
            user_list = users.split(',')
        else:
            user_list = users

        # Get the list of valid users.
        table = tables['csv2_user']
        s = select([table])
        db_user_list = qt(config.db_connection.execute(s))

        valid_users = {}
        for row in db_user_list:
            valid_users[row['username']] = False

        # Check the list of specified users.
        for user in user_list:
            if user not in valid_users:
                return 1, 'specified user "%s" does not exist' % user
            elif valid_users[user]:
                return 1, 'user "%s" was specified twice' % user
            else:
                valid_users[user] = True


    if groups:
        # if there is only one group, make it a list anyway
        if isinstance(groups, str):
            group_list = groups.split(',')
        else:
            group_list = groups

        # Get the list of valid groups.
        table = tables['csv2_groups']
        s = select([table])
        db_group_list = qt(config.db_connection.execute(s))

        valid_groups = {}
        for row in db_group_list:
            valid_groups[row['group_name']] = False

        # Check the list of specified groups.
        for group in group_list:
            if group not in valid_groups:
                return 1, 'specified group "%s" does not exist' % group
            elif valid_groups[group]:
                return 1, 'group "%s" was specified twice' % group
            else:
                valid_groups[group] = True

    return 0, None

#-------------------------------------------------------------------------------

def qt(query, keys=None, prune=[], filter=None, convert=None):
    """
    Query Transform takes a list of dictionaries (eg. the result of an SqlAlchemy query)
    and transforms it into a standard python list (repeatably iterable). In the process,
    it can make the following transformations:

        o It can filter rows based on the result of an evaluated string; True is
          retained, and False is dropped.

        o It can delete columns from the rows (prune=[col1, col2,..]).

        o It can convert column values from rows (convert={'col1': 'datetime', ...}).

        o For a list of primary keys, it can sum a list of columns. For example, given
          the following "keys" specification:

            keys = {
                'primary': ['group_name', 'cpus']
                'sum': ['slots', 'test']
                }

          and the following queryset (note the mixture of integers, floats, and strings):

            [
                {'group_name': 'atlas', 'cloud_name': 'cloud9', 'cpus': 1, 'slots': 8, 'test': 1.0},
                {'group_name': 'atlas', 'cloud_name': 'cloud9', 'cpus': 8, 'slots': 8, 'test': 2.9},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 1, 'slots': '8', 'test': '3.8'},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 2, 'slots': '4', 'test': '4.7'},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 4, 'slots': '2', 'test': '5.6'},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 8, 'slots': '1', 'test': '6.5'},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 1, 'slots': 8, 'test': 7.4},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 2, 'slots': 4, 'test': 8.3},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 4, 'slots': '2', 'test': '9.2'},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 8, 'slots': '1', 'test': '0.1'},
            ]

          would produce the following results:

            [
                {'group_name': 'atlas', 'cpus': 1, 'slots': 8, 'test': 1.0},
                {'group_name': 'atlas', 'cpus': 8, 'slots': 8, 'test': 2.9},
                {'group_name': 'testing', 'cpus': 1, 'slots': 16, 'test': 11.2},
                {'group_name': 'testing', 'cpus': 2, 'slots': 8, 'test': 13.0},
                {'group_name': 'testing', 'cpus': 4, 'slots': 4, 'test': 14.8},
                {'group_name': 'testing', 'cpus': 8, 'slots': 2, 'test': 6.6}
            ]
          
          NOTE: Numeric summation columns can either be integer or float or a 
                character string that can be converted by int() or float(). The
                result of summation is always an integer or a float.

        o It can split the query into a list and corresponding dictionaries (
          (keys={ 'primary': [...], 'secondary': [...], 'match_list': [...]).

          when the keys parameter specifies both a 'primary' and 'secondary' key
          lists (and optionally, a 'match_list'), the input query, must contain
          all primary and secondary keys. For each row in the queryset, qt uses
          the two key lists as follows:
  
          * For all keys in the primary list and any other key in the query not 
            mentioned in the secondary list, qt copies the values from the query
            into the primary output list.

          * For all keys in the primary list, plus the first key in the secondary
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
        
          A practical example of list splitting can be found in user_views.py, which
          does the following:
        
          # Retrieve the user list but loose the passwords.
          s = select([view_user_groups])
          user_list = qt(config.db_connection.execute(s), prune=['password'])

          # Retrieve user/groups list (dictionary containing list for each user).
          s = select([csv2_user_groups])
          ignore1, ignore2, groups_per_user = qt(
              config.db_connection.execute(s),
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
          s = select([view_user_groups])
          ignore1, ignore2, available_groups_per_user = qt(
              config.db_connection.execute(s),
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

    if keys and not ( ('primary' in keys and 'sum' in keys) or ('primary' in keys and 'secondary' in keys) ):
        raise Exception('view_utils.qt: "keys" dictionary requires either a "primary/sum" specification or a "primary/secondary" specification.')
    elif keys and 'match_list' in keys and 'secondary' not in keys:
        raise Exception('view_utils.qt: "keys" dictionary requires a "primary/secondary" specification if "match_list" is also specified.')

    from decimal import Decimal
    from .view_utils import _qt, _qt_list, _qt_list_sum
    import time

    # Initialize return structures.
    primary_list = []
    secondary_dict = {}
    matched_dict = {}

    # Handle an null query.
    if query:
        Query = query
    else:
        Query = []

    # Process query rows.
    for row in Query:
        # If specified, apply the row filter.
        if filter:
            cols = dict(row)
            if not eval(filter):
                continue

        # Prune and convert columns.
        cols = {}
        for col in dict(row):
            if col not in prune:
                if convert and col in convert and dict(row)[col] != None:
                    if convert[col] == 'datetime':
                        cols[col] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dict(row)[col]))
                else:
                    cols[col] = dict(row)[col]

        if not keys:
            primary_list.append(cols)

        elif keys and 'primary' in keys and 'sum' in keys:
            secondary_dict_ptr = secondary_dict
            for key in keys['primary']:
                ignore, secondary_dict_ptr = _qt(False, secondary_dict_ptr, cols, key)

            for col in keys['sum']:
                if col in cols:
                    if col not in secondary_dict_ptr:
                        secondary_dict_ptr[col] = 0

                    if isinstance(cols[col], int):
                        secondary_dict_ptr[col] += cols[col]
                    elif isinstance(cols[col], float):
                        secondary_dict_ptr[col] = float(Decimal(str(secondary_dict_ptr[col])) + Decimal(str(cols[col])))
                    else:
                        try:
                            secondary_dict_ptr[col] += int(cols[col])
                        except:
                            try:
                                secondary_dict_ptr[col] = float(Decimal(str(secondary_dict_ptr[col])) + Decimal(cols[col]))
                            except:
                                pass

        elif keys and 'primary' in keys and 'secondary' in keys:
            add_row = False
            secondary_dict_ptr = secondary_dict
            for key in keys['primary']:
                add_row, secondary_dict_ptr = _qt(add_row, secondary_dict_ptr, cols, key)
             
            if keys['secondary']:
                ignore, secondary_dict_ptr = _qt(False, secondary_dict_ptr, cols, keys['secondary'][0])
            
            for col in cols:
                if col in keys['secondary'] and cols[col]:
                    secondary_dict_ptr[col] = cols[col]
            
            if add_row:
                new_row = {}
                for col in cols:
                    if col not in keys['secondary']:
                        new_row[col] = cols[col]


                primary_list.append(new_row)

    if not keys:
        return primary_list

    elif keys and 'primary' in keys and 'sum' in keys:
         _qt_list_sum(primary_list, {}, secondary_dict, keys['primary'], 0)
         return primary_list

    elif keys and 'primary' in keys and 'secondary' in keys:
        if 'match_list' in keys:
            for row in keys['match_list']:
                matched_dict_ptr = matched_dict
                for key in keys['primary'][:-1]:
                    add_row, matched_dict_ptr = _qt(add_row, matched_dict_ptr, row, key)

                matched_dict_ptr[row[keys['primary'][-1]]] = []

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

def _qt_list_sum(primary_list, primary_dict_parent, secondary_dict_ptr, key_list, ix):
    """
    This sub-function is called by view_utils.qt to list a queryset's sums.
    It is NOT meant to be called directly.
    """

    if len(secondary_dict_ptr) > 0 and isinstance(secondary_dict_ptr[list(secondary_dict_ptr)[0]], dict) :
        for key in secondary_dict_ptr:
            primary_dict = dict(primary_dict_parent)
            primary_dict.update({key_list[ix]: key})
            _qt_list_sum(primary_list, primary_dict, secondary_dict_ptr[key], key_list, ix+1)

    else:
        primary_list.append(primary_dict_parent)
        primary_list[-1].update(secondary_dict_ptr)

#-------------------------------------------------------------------------------

def qt_filter_get(columns, values, aliases=None, and_or='and'):
    """
    Return an eveluation string to filter the rows of a queryset. This function takes the
    following arguments:
        o "columns" is a list of columns to be matched against items within the "values"
           parameter.

        o "values" is either a list or a dictionary. If it is a dictionary, the keys are
          column names identified by the columns parameter. If it is a list, the values 
          in the list have an index value corresponding to the columns argument. A value
          for a column can have one of five formats:
              1. An integer.
              2. A string. A string of "null" will match column is null.
              3. A string containing a comma separated list.
              4. A list.
              5. An alias ("aliases" parameter required, see below). Each alias is 
                 replaced by its corresponding value.

        o "aliases" is a structure with the following format:
              aliases = {
                  <column_name_1>: {
                      <alias_1>: <value>,
                      <alias_2>: <value>,
                       . 
                      },
                  <column_name_2>: {
                      <alias_1>: <value>,
                      <alias_2>: <value>,
                       . 
                      },
                   .
                  }

          The "value" for an alias can be any one of the first four formats. 

        o "and_or" is either "and" default) or "or" and is used as the boolean operator
          between column selections.
    """

    key_value_list = []
    for ix in range(len(columns)):
        if isinstance(values, dict):
            if columns[ix] in values:
                value = values[columns[ix]]
            else:
                continue

        else:
            if ix < len(values):
                value = values[ix]
            else:
                break

        if value == '':
            continue

        if aliases and columns[ix] in aliases and value in aliases[columns[ix]]:
            value = aliases[columns[ix]][value]

        try:
            x = float(value)
            key_value_list.append("cols['%s'] == %s" % (columns[ix], value))
        except:
            if isinstance(value, list):
                key_value_list.append("cols['%s'] in %s" % (columns[ix], value))
            elif value == 'null':
                key_value_list.append("cols['%s'] is null" % columns[ix])
            elif ',' in value:
                key_value_list.append("cols['%s'] in %s" % (columns[ix], value.split(',')))
            else:
              key_value_list.append("cols['%s'] == '%s'" % (columns[ix], value))

    if len(key_value_list) < 1:
        return None
    else:
        return (' %s ' % and_or).join(key_value_list)

#-------------------------------------------------------------------------------

def render(request, template, context):
    """
    If the "Accept" HTTP header contains "application/json", return a json string. Otherwise,
    return an HTML string.
    """

    from django.shortcuts import render as django_render
    from django.http import HttpResponse
    from sqlalchemy.orm.query import Query
    from sqlalchemy.engine.result import ResultProxy
    import datetime
    import decimal
    import json

    class csv2Encoder(json.JSONEncoder):
        def default(self, obj):
            if str(obj.__class__).split("'")[1].split('.')[0] == 'sqlalchemy':
                return str(obj)

            if isinstance(obj, datetime.date):
                return str(obj)

            if isinstance(obj, decimal.Decimal):
                return str(obj)

            if isinstance(obj, dict) and 'ResultProxy' in obj:
                return json.dumps(obj['ResultProxy'])

            if isinstance(obj, Query):
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' ]:
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
    end_time = time.time()
    print("Render time: %f.5" % end_time)
    return response

#-------------------------------------------------------------------------------

def service_msg(service_name):
    
    import os

    return os.popen("service "+service_name+" status | grep 'Active' | cut -c12-").read()    

#-------------------------------------------------------------------------------
# this function gets and sets the user groups for the active user as well as authenticates the active user
# if super_user is true and the requesting user doesn't have super user status a permission denied is raised
# if super user is false then skip the check for super user
def set_user_groups(config, request, super_user=True):
    active_user = getcsv2User(request, config)
    make_transient(active_user)
    if super_user and not active_user.is_superuser:
        raise PermissionDenied
        
    user_groups = config.db_map.classes.csv2_user_groups
    user_group_rows = config.db_session.query(user_groups).filter(user_groups.username==active_user.username)
    user_groups = []
    if user_group_rows is not None:
        for row in user_group_rows:
            user_groups.append(row.group_name)

    if not user_groups:
        return 1,'user "%s" is not a member of any group.' % active_user.username,active_user,user_groups

    # if the POST request specified a group, validate and set the specified group as the active group.
    if request.method == 'POST' and 'group' in request.POST:
        group_name = request.POST.get('group')
        if group_name and active_user.active_group != group_name:
            if group_name in user_groups:
                active_user.active_group = group_name
                config.db_session.merge(active_user)
                config.db_session.commit()
            else:
                return 1,'cannot switch to invalid group "%s".' % group_name, active_user, user_groups

    # if no active group, set first group as default.
    if active_user.active_group is None:
        active_user.active_group = user_groups[0]
        config.db_session.merge(active_user)
        config.db_session.commit()

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

def validate_by_filtered_table_entries(config, value, field, table_name, column_name, filter_list, allow_value_list=False):
    """
    This function validates that a value is present in a filtered table column
    
    Arguments:

    value       - the value or list of values (see allow_value_list option) to be validated.
    field       - the name of the field being validated(for error message only).
    table_name  - the name of the table.
    column_name - then name of the column.
    filter_list - the list of filters in the following format:

                  [[col1, val1], [col2, val2], ...]
    """

    from sqlalchemy.sql import select
    import cloudscheduler.lib.schema

    table = cloudscheduler.lib.schema.__dict__[table_name]

    options = []
    s = select([table])
    for filter in filter_list:
        if len(filter) != 2:
            return 1, 'incorrect filter format'
        c1 = table.c[filter[0]]
        s = s.where(c1 == filter[1])
    for row in config.db_connection.execute(s):
        if column_name in row and (not row[column_name] in options):
            options.append(row[column_name])

    if allow_value_list:

        if isinstance(value, str):
            values = value.split(',')
        else:
            values = value

        for val in values:
            if val not in options:
                msg = 'specified value in list of values does not exist: {}={}'.format(field, val)
                for filter in filter_list:
                    msg += ', {}={}'.format(filter[0], filter[1])
                return 1, msg
        return 0, None
    else:
        if value in options:
            return 0, None
        else:
            msg = 'specified item does not exist: {}={}'.format(field, value)
            for filter in filter_list:
                msg += ', {}={}'.format(filter[0], filter[1])
            return 1, msg

#-------------------------------------------------------------------------------

def validate_fields(config, request, fields, tables, active_user):
    """
    This function validates/normalizes form fields/command arguments.

    Arguments:

    config    - A configuration object.
    requests  - is a web request containing POST data.
    tables    - is a list of table names.
    fields    - is a  list of structures in the following format:

               CLOUD_FIELDS = {
                   'auto_active_group': active_user.active_group, # or None.
                   'format': {
                       'cloud_name': 'lowerdash',
                       'group_name': 'lowerdash',

                       'cores_slider': 'ignore',
                       'csrfmiddlewaretoken': 'ignore',
                       'group': 'ignore',
                       'ram_slider': 'ignore',
                       },
                   }


    Possible format strings are:

    ['opt1', 'opt2', ...]  - A list of valid options.
    ('table', 'column')    - A list of valid options derrived from the named table and column.
    boolean                - A value of True or False will be inserted into the output fields.
    dboolean               - Database boolean values are either 0 or 1; allow and
                             convert true/false/yes/no.
    float                  - A floating point value.
    ignore                 - Ignore missing mandatory fields or fields for undefined columns.
    integer                - An integer value.
    lowercase              - Make sure the input value is all lowercase (or error).
    lowerdash              - Make sure the input value is all lowercase, nummerics, and dashes but 
                             can't start or end with a dash (or error).
    metadata               - Identifies a pair of fields (eg. "xxx' and xxx_name) that contain ar
                             metadata string and a metadata filename. If the filename conforms to
                             pre-defined patterns (eg. ends with ".yaml"), the string will be 
                             checked to conform with the associated file type.
    password               - A password value to be checked and hashed
    password1              - A password value to be verified against password2, checked and hashed.
    password2              - A password value to be verified against password1, checked and hashed.
    reject                 - Reject an otherwise valid field.
    uppercase              - Make sure the input value is all uppercase (or error).

    POSTed fields in the form "name.1", "name.2", etc. will be treated as array fields, 
    returning the variable "name" as a list of strings. 

    """

    from .view_utils import _validate_fields_pw_check
    from sqlalchemy import Table, MetaData
    from sqlalchemy.sql import select
    import cloudscheduler.lib.schema
    import re

    # Retrieve relevant (re: tables) schema.
    all_columns = []
    primary_key_columns = []
    Tables = {}
    Columns = {}
    for table_option in tables:
        table = table_option.split(',')
        
        try:
            Tables[table[0]] = Table(table[0], MetaData(bind=config.db_engine), autoload=True)
        except:
            raise Exception('view_utils.validate_fields: "tables" parameter contains an invalid table name "%s".' % table[0])
            
        if len(table) > 1 and table[1] == 'n':
            continue

        Columns[table[0]] = [[], []]
        for column in Tables[table[0]].c:
            if column.name not in all_columns:
                all_columns.append(column.name)

            if column.primary_key:
                Columns[table[0]][0].append(column.name)
                if column.name not in primary_key_columns:
                    primary_key_columns.append(column.name)
            else:
                Columns[table[0]][1].append(column.name)

    # Process fields parameter:
    Formats = {}
    Mandatory = []
    NotEmpty = []
    Options = {
        'accept_primary_keys_only': False,
        'auto_active_group': False,
        'auto_active_user': False,
        'unnamed_fields_are_bad': False,
        }

    for option_set in fields:
        for option in option_set:
            if option == 'format':
                for field in option_set[option]:
                    Formats[field] = option_set[option][field]
            elif option == 'mandatory':
                if isinstance(option_set[option], list):
                    Mandatory += option_set[option]
                else:
                    Mandatory.append(option_set[option])
            elif option == 'not_empty':
                if isinstance(option_set[option], list):
                    NotEmpty += option_set[option]
                else:
                    NotEmpty.append(option_set[option])
            else:
                Options[option] = option_set[option]

    # Process input fields.
    Fields = {}
    if request.method == 'POST':
        for field in sorted(request.POST):
            if Options['accept_primary_keys_only'] and field not in primary_key_columns:
                if not (field in Formats and Formats[field] == 'ignore'):
                    return 1, 'request contained superfluous parameter "%s".' % field, None, None, None
            if Options['unnamed_fields_are_bad'] and field not in Formats:
                return 1, 'request contained a unnamed/bad parameter "%s".' % field, None, None, None

            field_alias = field
            value = request.POST[field]

            if field in Formats:
                if isinstance(Formats[field], (list, tuple)):
                    if isinstance(Formats[field], tuple):
                        options = []
                        s = select([cloudscheduler.lib.schema.__dict__[Formats[field][0]]])
                        for row in config.db_connection.execute(s):
                           if Formats[field][1] in row and (not row[Formats[field][1]] in options):
                              options.append(row[Formats[field][1]])
                    else:
                        options = Formats[field]

                    lower_value = value.lower()
                    value = None
                    for opt in options:
                        if lower_value == opt.lower():
                            value = opt
                            break

                    if not value:
                        return 1, 'value specified for "%s" must be one of the following options: %s.' % (field, sorted(options)), None, None, None

                elif Formats[field] == 'dboolean':
                    lower_value = value.lower()
                    if lower_value == 'true' or lower_value == 'yes' or lower_value == '1':
                        value = 1
                    elif lower_value == 'false' or lower_value == 'no' or lower_value == '0':
                        value = 0
                    else:
                        return 1, 'boolean value specified for "%s" must be one of the following: true, false, yes, no, 1, or 0.' % field, None, None, None

                elif Formats[field] == 'float':
                    try:
                        float_value = float(value)
                    except:
                        return 1, 'value specified for "%s" must be a floating point value.' % field, None, None, None

                elif Formats[field] == 'integer':
                    try:
                        integer = int(value)
                    except:
                        return 1, 'value specified for "%s" must be an integer value.' % field, None, None, None

                elif Formats[field] == 'lowerdash':
                    if len(request.POST[field]) > 0 and re.match("^[a-z0-9\-]*$", request.POST[field]) and request.POST[field][0] != '-' and request.POST[field][-1] != '-':
                        value = request.POST[field]
                    else:
                        return 1, 'value specified for "%s" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.' % field, None, None, None

                elif Formats[field] == 'lowercase':
                    value = request.POST[field].lower()
                    if request.POST[field] != value:
                        return 1, 'value specified for "%s" must be all lower case.' % field, None, None, None

                elif Formats[field] == 'mandatory':
                    if value.strip() == '':
                        return 1, 'value specified for "%s" must not be an empty string.' % field, None, None, None

                elif Formats[field] == 'metadata':
                    filename = '%s_name' % field
                    if filename in request.POST:
                        # Verify yaml files.
                        if (len(request.POST[filename]) > 4 and request.POST[filename][-4:] == '.yml') or \
                            (len(request.POST[filename]) > 5 and request.POST[filename][-5:] == '.yaml') or \
                            (len(request.POST[filename]) > 7 and request.POST[filename][-7:] == '.yml.j2') or \
                            (len(request.POST[filename]) > 8 and request.POST[filename][-8:] == '.yaml.j2'):

                            import yaml

                            try:    
                                temp_data = yaml.load(value)
                            except yaml.scanner.ScannerError as ex:
                                return 1, 'yaml value specified for "%s (%s)" is invalid - scanner error - %s' % (field, filename, ex), None, None, None
                            except yaml.parser.ParserError as ex:
                                return 1, 'yaml value specified for "%s (%s)" is invalid - parser error - %s' % (field, filename, ex), None, None, None

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

                elif Formats[field] == 'reject':
                    return 1, 'request contained a rejected/bad parameter "%s".' % field, None, None, None

                elif Formats[field] == 'uppercase':
                    value = request.POST[field].upper()
                    if request.POST[field] != value:
                        return 1, 'value specified for "%s" must be all upper case.' % field, None, None, None

            if field_alias in all_columns:
                Fields[field_alias] = value
            else: 
                array_field = field.split('.')
                print(">>>>>>>>>>>>>>>>>>>", array_field)
                if len(array_field) > 1 and (array_field[0] in all_columns or array_field[0] in Formats):
                    if array_field[0] not in Fields:
                        Fields[array_field[0]] = []
                    Fields[array_field[0]].append(value)
                else:
                    if field in Formats:
                        Fields[field] = value
                    else:
                        return 1, 'request contained a bad parameter "%s".' % field, None, None, None

        if Options['auto_active_group'] and 'group_name' not in Fields:
            Fields['group_name'] = active_user.active_group

        if Options['auto_active_user'] and 'username' not in Fields:
            Fields['username'] = active_user

        # Process booleans fields.
        for field in Formats:
            if Formats[field] == 'boolean':
                if request.POST.get(field):
                    if request.POST[field] == 'invalid-unit-test':
                        Fields[field] = 'invalid-unit-test'
                    else:
                        Fields[field] = True
                else:
                    Fields[field] = False

        for field in primary_key_columns + Mandatory:
            if field not in Fields and (field not in Formats or  Formats[field] != 'ignore'):
                return 1, 'request did not contain mandatory parameter "%s".' % field, None, None, None

        if NotEmpty:
            for field in Fields:
                if field in NotEmpty and Fields[field] == '':
                    return 1, 'parameter "%s" contains an empty string which is specifically disallowed.' % field, None, None, None

    return 0, None, Fields, Tables, Columns

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

