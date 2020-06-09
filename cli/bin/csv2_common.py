#-------------------------------------------------------------------------------
              
def check_keys(gvar, mp, rp, op, not_optional=[], key_map=None, requires_server=True):
    """
    Modify user settings.
    """

    import csv2_help
    from os import getenv

    # Summarize the mandatory, required, and optional parameters for the current command.
    mandatory = []
    required = []
    options = []
    valid_keys = ['server-address', 'server-password', 'server-user']
#   valid_keys = ['server-address', 'server-grid-cert', 'server-grid-key', 'server-password', 'server-user']
    for key in gvar['command_keys']:
        # 0.short_name, 1.long_name, 2.key_value(bool)
        if key[0] in mp:
            mandatory.append([key[0], '%-4s |  %s' % (key[0], key[1]), key[1][2:]])
        if key[0] in rp:
            required.append([key[0], '%-4s |  %s' % (key[0], key[1]), key[1][2:]])
        if key[0] in op or (op == ['*'] and key[0] not in mp + rp + not_optional):
            options.append([key[0], '%-4s |  %s' % (key[0], key[1]), key[1][2:]])
        if key[0] in mp + rp + op or (op == ['*'] and key[0] not in mp + rp + not_optional):
            valid_keys.append(key[1][2:])
    
    # Check for invalid parameters
    for key in gvar['command_args']:
        if gvar['command_args'][key] and (key not in valid_keys):
            print('Error: The following command line arguments were invalid: {}'.format(key))
            exit(1)

    # Check if help requested.
    csv2_help.help(gvar, mandatory=mandatory, required=required,  options=options, requires_server=requires_server)

    # If the current command has mandatory parameters and they have not been specified, issue error messages and exit.
    form_data = {}
    missing = []
    for key in mandatory:
        if key[2] in gvar['command_args']:
            if key_map and key[0] in key_map:
#               form_data[key_map[key[0]]] = gvar['command_args'][key[2]]
                form_data[key_map[key[0]]] = _check_keys_for_password(gvar, key)
        else:
            missing.append(key[1])

    if missing:
        print('Error: "%s %s %s" - the following mandatory parameters must be specfied on the command line:' % (gvar['command_name'], gvar['object'], gvar['action']))
        for key in missing:
            print('  %s' % key)
        print('For more information, use -H.')
        exit(1)

    missing = []
    for key in required:
        if key[2] in gvar['user_settings']:
            if key_map and key[0] in key_map:
#               form_data[key_map[key[0]]] = gvar['user_settings'][key[2]]
                form_data[key_map[key[0]]] = _check_keys_for_password(gvar, key)
        elif not(key[0] == '-te' and getenv('EDITOR') is not None):
            missing.append(key[1])

    if missing:
        print('Error: "%s %s %s" - no value, neither default nor command line, for the following required parameters:' % (gvar['command_name'], gvar['object'], gvar['action']))
        for key in missing:
            print('  %s' % key)
        print('For more information, use -h or -H.')
        exit(1)

    if key_map:
        for key in options:
            if key[0] in key_map and key[2] in gvar['user_settings']:
                form_data[key_map[key[0]]] = _check_keys_for_password(gvar, key)

    return form_data

#-------------------------------------------------------------------------------
              
def _check_keys_for_password(gvar, key):
    """
    Internal function to prompt for passwords (if requested, iw -upw ?).
    """
    
    from getpass import getpass

    if key[2] != 'server-password' and key[2][-8:] == 'password' and len(gvar['user_settings'][key[2]]) > 0 and gvar['user_settings'][key[2]][0] == '?':
        while(1):
            pw1 = getpass('Enter %s: ' % key[2])
            if len(pw1) > 5:
                if len(gvar['user_settings'][key[2]]) > 1 and gvar['user_settings'][key[2]][1] == '?':
                    pw2 = getpass('Verify %s: ' % key[2])
                    if pw1 == pw2:
                        return pw1
                    else:
                        print('Passwords did not match.')
                else:
                    return pw1
            else:
                print('Passwords must be at least 6 characters long.')
    else:
       return gvar['user_settings'][key[2]]

#-------------------------------------------------------------------------------

def command_hash(gvar):
    """
    Return an md5sum of the command directory.
    """

    from subprocess import Popen, PIPE

    p1 = Popen([
        'ls',
        '-l',
        gvar['command_dir']
        ], stdout=PIPE, stderr=PIPE)

    if gvar['platform'][:6].lower() == 'macos-':
        p2 = Popen([
            'md5'
            ], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)

    else:
        p2 = Popen([
            'md5sum'
            ], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)

    md5sum, stderr = p2.communicate()
    return decode(md5sum).replace('-','').strip()

#-------------------------------------------------------------------------------

def decode(obj):
    if not obj:
        return ''
    elif isinstance(obj, str):
        return obj 
    else:
        return obj.decode('utf-8')

#-------------------------------------------------------------------------------

def get_editor(gvar):
    from shutil import which
    import os

    if 'text-editor' in gvar['user_settings']:
        user_parm = gvar['user_settings']['text-editor']
    else:
        user_parm = os.getenv('EDITOR') or os.getenv('VISUAL')

        if not user_parm:
            print('Error: no editor specified. Use either the "-te" option or set the EDITOR or VISUAL environment variables.')
            exit(1)

    words = user_parm.split()
    editor = which(words[0])

    if not editor:
        print('Error: specified editor "%s" does not exist.' % words[0])
        exit(1)

    return [editor] + words[1:]

#-------------------------------------------------------------------------------
              
def get_grid_proxy(gvar):
    """
    If using x509 certificate authentication, return path to proxy certificate. 
    Otherwise, return None.
    """
    
    import os

    try:
        time_left_list = sys_cmd(['grid-proxy-info', '-timeleft'])
    except:
        return None

    if time_left_list:
        try:
            time_left = int(time_left_list[0])
        except:
            time_left = 0

        if time_left > 60:
            return '/tmp/x509up_u%s' % gvar['uid']

    if os.path.exists('%s/.globus/usercert.pem' % gvar['home_dir']) and \
        os.path.exists('%s/.globus/userkey.pem' % gvar['home_dir']):
        if 'user_settings' in gvar and 'use-x509-authentication' in gvar['user_settings'] and gvar['user_settings']['use-x509-authentication']:
            x509 = 'yes'
        else:
            x509 = input('Would you like to authenticate with your x509 certificate (%s/.globus/{usercert.pem,userkey.pem})? (y|n): ' % gvar['home_dir'])

        if x509.lower() == 'yes'[:len(x509)]:
            for ix in range(3):
                if sys_cmd(['grid-proxy-init'], return_stdout_not_rc=False) == 0:
                    return '/tmp/x509up_u%s' % gvar['uid']
                print('Invalid GRID pass phrase, %s of 3 attemps.' % (ix+1))
            exit(1)
        
    return None
    
#-------------------------------------------------------------------------------

def qc(query, columns, option='keep', filter=None):
    """
    Query Columns takes a row/list of rows and a column/list of columns to keep or
    prune, depending on the option specified. Also, a filter (see qc_filter) may be
    specified, which is used to select rows.
    """

    if isinstance(query, dict):
        query_list = [ query ]
    elif isinstance(query, (list, tuple)):
        query_list = list(query)
    else:    
        raise Exception('Parameter "query" is not a dictionary, list, or tuple (%s).' % type(query))

    if isinstance(columns, str):
        column_list = [ columns ]
    if isinstance(columns, (list, tuple)):
        column_list = list(columns)
    else:    
        raise Exception('Parameter "columns" is not a string, list, or tuple.')

    if len(column_list) < 1:
        raise Exception('No columns were specified in parameter "columns".')

    # Initialize return structures.
    result_list = []
    for row in query_list:
        if filter:
            cols = dict(row)
            if not eval(filter):
                continue

        result_list.append({})
        for column in row:
            if (option == 'keep' and column in column_list) or (option == 'prune' and column not in column_list):
                result_list[-1][column] = row[column]

    if isinstance(query, dict):
        return result_list[0]
    else:
        return result_list
              
#-------------------------------------------------------------------------------

def qc_filter_get(columns, values, aliases=None, and_or='and'):
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
              
def requests(gvar, request, form_data={}, query_data={}, streaming_upload=False):
    """
    Make RESTful requests via the _requests function and return the response. This function will
    obtain a CSRF (for POST requests) prior to making the atual request.
    """
    
    # Obtain a CSRF as required.
    if form_data and not gvar['csrf']:
        response = _requests(gvar, '/settings/prepare/')
    
    # Perform the callers request.
    if streaming_upload:
        return _streaming_request(gvar, request, form_data=form_data, query_data=query_data)
    else:
        return _requests(gvar, request, form_data=form_data, query_data=query_data)

#-------------------------------------------------------------------------------
              
def _requests(gvar, request, form_data={}, query_data={}):
    """
    Make RESTful request and return response.
    """
    
    from getpass import getpass
    import requests as py_requests
    import os

    EXTRACT_CSRF = str.maketrans('=;', '  ')

    if 'server-address' not in gvar['user_settings']:
        requests_no_credentials_error(gvar)

    if 'server-user' in gvar['user_settings']:
        x509 = None
    else:
        x509 = get_grid_proxy(gvar)

    if x509:
        authentication_method = 'x509 proxy'

        _function, _request, _form_data = _requests_insert_controls(gvar, request, form_data, query_data, gvar['user_settings']['server-address'], x509)

        try:
            _r = _function(
                _request,
                headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']},
                cert=(x509),
                data=_form_data,
                cookies=gvar['cookies']
                )

        except py_requests.exceptions.SSLError as exc:
            print(exc)
            exit(1)

    elif 'server-user' in gvar['user_settings']:
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '?':
            gvar['user_settings']['server-password'] = getpass('Enter your %s password for server "%s": ' % (gvar['command_name'], gvar['pid_defaults']['server']))

        authentication_method = '%s, <password>' % gvar['user_settings']['server-user']

        _function, _request, _form_data = _requests_insert_controls(gvar, request, form_data, query_data, gvar['user_settings']['server-address'], gvar['user_settings']['server-user'])

        try:
            _r = _function(
                _request,
                headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']},
                auth=(gvar['user_settings']['server-user'], gvar['user_settings']['server-password']),
                data=_form_data,
                cookies=gvar['cookies'] 
                )

        except py_requests.exceptions.SSLError as exc:
            print(exc)
            exit(1)

    else:
        requests_no_credentials_error(gvar)

    try:
        response = _r.json()
    except:
        if _r.status_code:
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, %s.' % (gvar['pid_defaults']['server'], _r.status_code, py_requests.status_codes._codes[_r.status_code][0])}
        else:
            response = {'response_code': 2, 'message': 'server "%s", internal server error.' % gvar['pid_defaults']['server']}

    if 'Set-Cookie' in _r.headers:
        new_csrf = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]
        if new_csrf[1]:
            gvar['cookies'] = _r.cookies
            gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

    if 'active_group' in response:
        gvar['active_group'] = response['active_group']

    if 'active_user' in response and 'active_group' in response:
        if x509:
            update_pid_defaults(gvar, server_address=gvar['user_settings']['server-address'], user=x509, group=response['active_group'])
        else:
            update_pid_defaults(gvar, server_address=gvar['user_settings']['server-address'], user=response['active_user'], group=response['active_group'])

    if 'super_user' in response:
        gvar['super_user'] = response['super_user']

    if gvar['user_settings']['expose-API']:
        print("Expose API requested:\n" \
            "  py_requests.%s(\n" \
            "    %s\n" \
            "    headers={'Accept': 'application/json', 'Referer': '%s'}\n" \
            "    auth=(%s)\n" \
            "    data=%s\n" \
            "    cookies='%s'\n" \
            "    )\n\n" \
            "  Response: {" % (
                _function.__name__,
                _request,
                gvar['user_settings']['server-address'],
                authentication_method,
                _form_data,
                gvar['cookies']
                )
            )

        for key in response:
            if key == 'fields':
                print("    %s: {" % key)
                for subkey in response(key):
                    print("        %s: %s" % (subkey, response[key][subkey]))
                print("        }")
            else:
                print("    %s: %s" % (key, response[key]))
        print("    }\n")

    if response['response_code'] != 0:
        print('Error: %s' % response['message'])
        exit(1)

    if 'user_groups' in response:
        gvar['user_groups'] = response['user_groups']

    return response

#-------------------------------------------------------------------------------
               
def _streaming_request(gvar, request, form_data={}, query_data={}):
    """
    Make RESTful request and return response.
    """
    
    from getpass import getpass
    import requests as py_requests
    import os
    from requests_toolbelt.multipart import encoder

    """
    session = requests.Session()
    with open('my_file.csv', 'rb') as f:
        form = encoder.MultipartEncoder({
            "documents": ("my_file.csv", f, "application/octet-stream"),
        })
        headers = {"Prefer": "respond-async", "Content-Type": form.content_type}
        resp = session.post(url, headers=headers, data=form)
      session.close()
    """


    EXTRACT_CSRF = str.maketrans('=;', '  ')

    if 'server-address' not in gvar['user_settings']:
        requests_no_credentials_error(gvar)

    if 'server-user' in gvar['user_settings']:
        x509 = None
    else:
        x509 = get_grid_proxy(gvar)

    if x509:
        authentication_method = 'x509 proxy'

        _function, _request, _form_data = _requests_insert_controls(gvar, request, form_data, query_data, gvar['user_settings']['server-address'], x509)

        try:
            with open(gvar['user_settings']['image-path'][6:], 'rb') as f:
                form = encoder.MultipartEncoder({
                    **_form_data,
                    "myfile": (gvar['user_settings']['image-path'][6:], f, "application/octet-stream"),
                    })
                _r = _function(
                    _request,
                    headers={
                        'Accept': 'application/json', 
                        'Referer': gvar['user_settings']['server-address'],
                        'Prefer': "respond-async",
                        'Content-Type': form.content_type
                        },
                    cert=(x509),
                    data=form,
                    cookies=gvar['cookies']
                    )

        except py_requests.exceptions.SSLError as exc:
            print(exc)
            exit(1)

    elif 'server-user' in gvar['user_settings']:
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '?':
            gvar['user_settings']['server-password'] = getpass('Enter your %s password for server "%s": ' % (gvar['command_name'], gvar['pid_defaults']['server']))

        authentication_method = '%s, <password>' % gvar['user_settings']['server-user']

        _function, _request, _form_data = _requests_insert_controls(gvar, request, form_data, query_data, gvar['user_settings']['server-address'], gvar['user_settings']['server-user'])

        try:
            with open(gvar['user_settings']['image-path'][6:], 'rb') as f:
                form = encoder.MultipartEncoder({
                    **_form_data,
                    "myfile": (gvar['user_settings']['image-path'][6:], f, "application/octet-stream"),
                    })
                _r = _function(
                    _request,
                    headers={
                        'Accept': 'application/json',
                        'Referer': gvar['user_settings']['server-address'],
                        'Prefer': "respond-async",
                        'Content-Type': form.content_type
                        },
                    auth=(gvar['user_settings']['server-user'], gvar['user_settings']['server-password']),
                    data=form,
                    cookies=gvar['cookies'] 
                    )

        except py_requests.exceptions.SSLError as exc:
            print(exc)
            exit(1)

    else:
        requests_no_credentials_error(gvar)

    try:
        response = _r.json()
    except:
        if _r.status_code:
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, %s.' % (gvar['pid_defaults']['server'], _r.status_code, py_requests.status_codes._codes[_r.status_code][0])}
        else:
            response = {'response_code': 2, 'message': 'server "%s", internal server error.' % gvar['pid_defaults']['server']}

    if 'Set-Cookie' in _r.headers:
        new_csrf = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]
        if new_csrf[1]:
            gvar['cookies'] = _r.cookies
            gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

    if 'active_group' in response:
        gvar['active_group'] = response['active_group']

    if 'active_user' in response and 'active_group' in response:
        if x509:
            update_pid_defaults(gvar, server_address=gvar['user_settings']['server-address'], user=x509, group=response['active_group'])
        else:
            update_pid_defaults(gvar, server_address=gvar['user_settings']['server-address'], user=response['active_user'], group=response['active_group'])

    if 'super_user' in response:
        gvar['super_user'] = response['super_user']

    if gvar['user_settings']['expose-API']:
        print("Expose API requested:\n" \
            "  py_requests.%s(\n" \
            "    %s\n" \
            "    headers={'Accept': 'application/json', 'Referer': '%s'}\n" \
            "    auth=(%s)\n" \
            "    data=%s\n" \
            "    cookies='%s'\n" \
            "    )\n\n" \
            "  Response: {" % (
                _function.__name__,
                _request,
                gvar['user_settings']['server-address'],
                authentication_method,
                _form_data,
                gvar['cookies']
                )
            )

        for key in response:
            if key == 'fields':
                print("    %s: {" % key)
                for subkey in response(key):
                    print("        %s: %s" % (subkey, response[key][subkey]))
                print("        }")
            else:
                print("    %s: %s" % (key, response[key]))
        print("    }\n")

    if response['response_code'] != 0:
        print('Error: %s' % response['message'])
        exit(1)

    if 'user_groups' in response:
        gvar['user_groups'] = response['user_groups']

    return response

#-------------------------------------------------------------------------------
              
def _requests_insert_controls(gvar, request, form_data, query_data, server_address, server_user):
    """
    Add controls (csrf, group, etc.) to python request.
    """

    import requests as py_requests

    if form_data:
        _function = py_requests.post
        _request = '%s%s' % (server_address, request)

        if 'group' in gvar['command_args']:
            _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf'], 'group': gvar['user_settings']['group']}}
        else:
            if server_address in gvar['pid_defaults']['server_addresses'] and server_user in gvar['pid_defaults']['server_addresses'][server_address]:
                _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf'], 'group': gvar['pid_defaults']['server_addresses'][server_address][server_user]}}
            else:
                _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf']}}

    else:
        _function = py_requests.get

        if 'group' in gvar['command_args']:
            if request[-1] == '/':
                _request = '%s%s?%s' % (server_address, request[:-1], gvar['user_settings']['group'])
            else:
                _request = '%s%s?%s' % (server_address, request, gvar['user_settings']['group'])
        else:
            if server_address in gvar['pid_defaults']['server_addresses'] and server_user in gvar['pid_defaults']['server_addresses'][server_address]:
                if request[-1] == '/':
                    _request = '%s%s?%s' % (server_address, request[:-1], gvar['pid_defaults']['server_addresses'][server_address][server_user])
                else:
                    _request = '%s%s?%s' % (server_address, request, gvar['pid_defaults']['server_addresses'][server_address][server_user])
            else:
                _request = '%s%s' % (server_address, request)

        if query_data:
            query_list = []
            for key in sorted(query_data):
                query_list.append('%s=%s' % (key, query_data[key]))

            if _request[-1] == '/':
               _request = '%s?%s' % (_request[:-1], '&'.join(query_list))
            else:
               _request = '%s&%s' % (_request, '&'.join(query_list))
        
        _form_data = {}

    return _function, _request, _form_data

#-------------------------------------------------------------------------------
              
def requests_no_credentials_error(gvar):
    """
    Print no server or credentials error and exit.
    """

    from getpass import getpass
    import sys

    if 'server_address' in gvar['command_args']:
        server_address = gvar['command_args']['server_address']
    else:
        server_address = input("Please enter the CSV2 server's URL (eg. https://example.ca) that you wish to address: ")

    print(
        '***\n' \
        '*** Servers require one of the following:\n' \
        '***\n' \
        '***    o x509 certificate authentication, or\n' \
        '***    o username/password authentication\n' \
        '***\n' 
        )

    x509 = get_grid_proxy(gvar)
    if x509:
        print('Proxy certificate found, using x509 authentication.')
    else:
        username = input('Please enter your CSV2 username on server "%s": ' % server_address)
        password = getpass('Please enter your CSV2 password for user "%s" on server "%s": ' % (username, server_address))

    save_server = input('\nWould you like to save these server settings for future use? (y|n): ')
    if save_server.lower() == 'yes'[:len(save_server)]:
        if 'server' in gvar['command_args']:
            server_name = gvar['command_args']['server']
        else:
            server_name = input('Please enter a short server name (eg. dev, prod, etc.): ')

        if x509:
            print('***\n*** Issuing "cloudscheduler defaults set -s %s ..." to save server address.' % server_name)
            sys_cmd([sys.argv[0], 'defaults', 'set', '-s', server_name, '-sa', server_address], return_stdout_not_rc=False)
        else:
            print('***\n*** Issuing "cloudscheduler defaults set -s %s ..." to save server address, username, and password.' % server_name)
            sys_cmd([sys.argv[0], 'defaults', 'set', '-s', server_name, '-sa', server_address, '-su', username, '-spw', password], return_stdout_not_rc=False)

        print(
            '***\n' \
            '*** To address this server in the future:\n' \
            '***\n' \
            '***    cloudscheduler -s %s ...\n' \
            '***\n' \
            % server_name
            )

        if x509:
            sys_cmd(sys.argv + ['-s', server_name], return_stdout_not_rc=False)
        else:
            sys_cmd(sys.argv + ['-s', server_name, '-su', username, '-spw', password], return_stdout_not_rc=False)
        exit(0)

    if x509:
        sys_cmd(sys.argv + ['-sa', server_address], return_stdout_not_rc=False)
    else:
        sys_cmd(sys.argv + ['-sa', server_address, '-su', username, '-spw', password], return_stdout_not_rc=False)
    exit(0)

#-------------------------------------------------------------------------------
              
def show_active_user_groups(gvar, response):
    """
    Print the server response header.
    """

    if 'comma-separated-values' not in gvar['user_settings'] and not gvar['user_settings']['view-columns']:
        print('\033[1mServer: %s, Active User: %s, Active Group: %s, User\'s Groups: %s\033[0m' % (gvar['pid_defaults']['server'], response['active_user'], response['active_group'], response['user_groups']))

#-------------------------------------------------------------------------------
              
def show_table(gvar, queryset, columns, allow_null=True, title=None, optional=False):
    """
    Print a table from a SQLAlchemy query set.
    """

    from subprocess import Popen, PIPE
    import json
    import os
    import yaml

    # Organize user views.
    if 'views' not in gvar:
        if os.path.exists('%s/.csv2/views.yaml' % gvar['home_dir']):
            fd = open('%s/.csv2/views.yaml' % gvar['home_dir'])
            gvar['views'] = yaml_full_load(fd.read())
            fd.close()
        else:
            gvar['views'] = {}

        if 'view' in gvar['user_settings']:
            if gvar['object'] not in gvar['views']:
                gvar['views'][gvar['object']] = {}

            gvar['views'][gvar['object']][gvar['action']] = []

            w1 = gvar['user_settings']['view'].split('/')
            for w2 in w1:
                gvar['views'][gvar['object']][gvar['action']].append(w2.split(','))
                if gvar['views'][gvar['object']][gvar['action']][-1] == ['']:
                    gvar['views'][gvar['object']][gvar['action']][-1] = None

            fd = open('%s/.csv2/views.yaml' % gvar['home_dir'], 'w')
            fd.write(yaml.dump(gvar['views']))
            fd.close()

    if gvar['user_settings']['rotate']:
        Rotate = True
    else:
        Rotate = False

    skip_optional = True
    if optional and not gvar['user_settings']['view-columns'] and 'with' in gvar['user_settings']:
        if gvar['user_settings']['with'] == 'ALL':
            skip_optional = False
        else:
            lower_title = title.lower()
            words = gvar['user_settings']['with'].lower().split(',')
            for word in words:
                try:
                    int_word = int(word)
                except:
                    int_word = 0

                if int_word > 0 and int_word == gvar['tables_shown']+1 or \
                    word == lower_title[:len(word)]:
                        skip_optional = False
                        break
            
    if optional and not gvar['user_settings']['view-columns'] and skip_optional:
        gvar['tables_shown'] += 1
        return

    if not gvar['user_settings']['no-view'] and gvar['object'] in gvar['views'] and gvar['action'] in gvar['views'][gvar['object']]:
        Selections = gvar['views'][gvar['object']][gvar['action']]
        if len(Selections) > gvar['tables_shown'] and Selections[gvar['tables_shown']] == ['-']:
            gvar['tables_shown'] += 1
            return

        if len(Selections) > gvar['tables_shown'] and Selections[gvar['tables_shown']] == ['-r']:
            Selections = None
            if Rotate:
                Rotate = False
            else:
                Rotate = True
    else:
        Selections = None

    # Organize table definition.
    Rotated_Table = {
        'headers': {'key': 'Key', 'value': 'Value'},
        'lengths': {'key': 3, 'value': 5},
        'xref': {'key': 0, 'value': 1}
        }

    Table = {
        'columns_common': [],
        'columns_segment': [],
        'headers': {},
        'keys': {},
        'lengths': {},
        'super_headers': {},
        'xref': {}
        }

    if Rotate:
        Table['max_key_length'] = 3
        Table['max_value_length'] = 5

    elif 'display_size' not in gvar:
        p = Popen(['stty', 'size'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            ix = stdout.split()
            gvar['display_size'] = [int(ix[0]), int(ix[1])]
        else:
            gvar['display_size'] = [24, 80]

    if 'comma-separated-values' in gvar['user_settings']:
        if gvar['user_settings']['comma-separated-values'] == '':
            comma_separated_values = []
        else:
            comma_separated_values = gvar['user_settings']['comma-separated-values'].split(',')

    for column_def in columns:
        w1 = column_def.split(',')
        w2 = w1[0].split('/')
        column = w2[0]

        if 'comma-separated-values' in gvar['user_settings'] and len(comma_separated_values)>0 and column not in comma_separated_values:
            continue

        # Set default value for header.
        if len(w2) < 2:
            w2.append(column)
        elif w2[1] == '':
           w2[1] = column

        # Set default value for super_header.
        if len(w2) < 3:
            w2.append('')

        if len(w1) > 1 and w1[1] == 'k':
            Table['keys'][column] = True
        else:
            if not gvar['user_settings']['view-columns']:
                if gvar['command_args']['only-keys']:
                    continue

                if Selections is not None and len(Selections) > gvar['tables_shown'] and Selections[gvar['tables_shown']] and len(Selections[gvar['tables_shown']]) > 0 and column not in Selections[gvar['tables_shown']]:
                    continue

            Table['keys'][column] = False

        Table['headers'][column] = w2[1]
        Table['super_headers'][column] = w2[2]

        if Table['keys'][column]:
           Table['columns_common'].append(column)
           if len(Table['super_headers'][column]) > len(Table['headers'][column]):
               Table['lengths'][column] = len(Table['super_headers'][column])
           else:
               Table['lengths'][column] = len(Table['headers'][column])

        else:
           Table['columns_segment'].append(column)
           if len(Table['super_headers'][column]) > len(Table['headers'][column]):
               Table['lengths'][column] = len(Table['super_headers'][column])
           else:
               Table['lengths'][column] = len(Table['headers'][column])

    for ix in range(len(Table['columns_common'] + Table['columns_segment'])):
        Table['xref'][(Table['columns_common'] + Table['columns_segment'])[ix]] = ix

    # If requested, print column names and return.
    if gvar['user_settings']['view-columns']:
        columns = [ [], [] ]
        for column in Table['columns_common'] + Table['columns_segment']:
            if Table['keys'][column]:
                columns[0].append(column)
            else:
                columns[1].append(column)
        if title:
            if optional:
                title_optional = '%s (optional)' % title
            else:
                title_optional = title

            print('%s %s, %s. %s: keys=%s, columns=%s' % (gvar['object'], gvar['action'], gvar['tables_shown']+1, title_optional, ','.join(Table['columns_common']), ','.join(Table['columns_segment'])))
        else:
            if optional:
                print('%s %s, table #%s (optional): keys=%s, columns=%s' % (gvar['object'], gvar['action'], gvar['tables_shown']+1, ','.join(Table['columns_common']), ','.join(Table['columns_segment'])))
            else:
                print('%s %s, table #%s: keys=%s, columns=%s' % (gvar['object'], gvar['action'], gvar['tables_shown']+1, ','.join(Table['columns_common']), ','.join(Table['columns_segment'])))
        gvar['tables_shown'] += 1
        return

    # Normalize the queryset.
    if isinstance(queryset, str):
        _qs = json.loads(queryset)
    else:
        _qs = queryset

    # extract columns.
    lists = []
    for row in _qs:
        _row = []
        for column in Table['columns_common'] + Table['columns_segment']:
            if column in row:
              _value = row[column]
            elif 'fields' in row and column in row['fields']:
              _value = row['fields'][column]
            else:
              _value = '-'

            if isinstance(_value, bool):
               _len = 5
            elif isinstance(_value, int):
               _len = 11
            elif isinstance(_value, float):
               _len = 21
            elif _value is None:
               _len = 4
            else:
               _len = len(_value)

            if Rotate:
                if Table['super_headers'][column] == '':
                    lists.append([Table['headers'][column], _value])
                else:
                    lists.append(['%s-%s' % (Table['super_headers'][column], Table['headers'][column]), _value])

                if Rotated_Table['lengths']['key'] < len(lists[-1][0]):
                    Rotated_Table['lengths']['key'] = len(lists[-1][0])

                if Rotated_Table['lengths']['value'] < _len:
                    Rotated_Table['lengths']['value'] = _len

            elif Table['keys'][column]:
                _row.append(_value)
                if Table['lengths'][column] < _len:
                    Table['lengths'][column] = _len

            else:
                _row.append(_value)
                if Table['lengths'][column] < _len:
                    Table['lengths'][column] = _len

        if Rotate:
            lists.append(['', ''])
        else:
            lists.append(_row)

    if 'comma-separated-values' in gvar['user_settings']:
        if 'comma-separated-values-separator' in gvar['user_settings']:
            separator =  gvar['user_settings']['comma-separated-values-separator']
        else:
            separator = ','

        for row in lists:
            print(str(separator).join(str(ix) for ix in row))
    else:
        if Rotate:
            segments = [ {'SH': False, 'table': Rotated_Table, 'columns': ['key', 'value'], 'headers': ['Key', 'Value']} ]

        else:
            segments = [ {'SH': False, 'table': Table, 'columns': [], 'super_headers': [],  'super_header_lengths': [], 'headers': [], 'length': 1} ]

            if len(Table['columns_segment']) > 0:
                for column in Table['columns_segment']:
                    # If the next column causes segment to exceed the display width, start a new segment.
                    if segments[-1]['length'] + 3 + Table['lengths'][column] > gvar['display_size'][1] - 5:
                        _show_table_set_segment(segments[-1], None)
                        segments.append({'SH': False, 'table': Table, 'columns': [], 'super_headers': [],  'super_header_lengths': [], 'headers': [], 'length': 1})

                    # If starting a new segment, add all the common (key) columns.
                    if segments[-1]['length'] == 1:
                        for common_column in Table['columns_common']:
                            _show_table_set_segment(segments[-1], common_column)
                        _show_table_set_segment(segments[-1], None)

                    # Process the current (segment) column.
                    _show_table_set_segment(segments[-1], column)
                _show_table_set_segment(segments[-1], None)

            else:
                # The table consists of only common (key) columns; add them all.
                for common_column in Table['columns_common']:
                    _show_table_set_segment(segments[-1], common_column)
                _show_table_set_segment(segments[-1], None)

        for ix in range(len(segments)):
            column_underscore = []
            for column in segments[ix]['columns']:
                column_underscore.append('-' * (segments[ix]['table']['lengths'][column] + 2))
            ruler = '+%s+' % '+'.join(column_underscore)

            if title:
                if len(segments) > 1:
                    print('\n%s: (%s/%s)' % (title, ix+1, len(segments)))
                else:
                    print('\n%s:' % title)
            else:
                if len(segments) > 1:
                    print('\n (%s/%s)' % (ix+1, len(segments)))
                else:
                    print('\n')

            print(ruler)
            if segments[ix]['SH']:
                print('+ %s +' % ' | '.join(segments[ix]['super_headers']))
                print('+ %s +' % ' | '.join(segments[ix]['headers']))
            else:
                print('+ %s +' % ' | '.join(_show_table_pad(segments[ix]['columns'], segments[ix]['table']['headers'], segments[ix]['table']['lengths'])))
            print(ruler)

            for row in lists:
                if Rotate and not allow_null and row[1] == '-':
                    continue

                print('| %s |' % ' | '.join(_show_table_pad(segments[ix]['columns'], row, segments[ix]['table']['lengths'], values_xref=segments[ix]['table']['xref'])))

            print(ruler)

        print('Rows: %s' % len(_qs))
        gvar['tables_shown'] += 1

#-------------------------------------------------------------------------------
              
def _show_table_pad(columns, values, lengths, justify='left', values_xref=None):
    """
    Pad column values with blanks. The parameters have the following format:
       o columns is a list.
       o values is either a list or a dictionary.
       o lengths is a dictionary.
    """

    padded_columns = []

    for ix in range(len(columns)):
        if isinstance(values, list):
            if values_xref is None:
                value = str(values[ix])
            else:
                value = str(values[values_xref[columns[ix]]])
        else:
            value = str(values[columns[ix]])

        value_len = len(value)

        if justify == 'left':
            padded_columns.append('%s%s' % (value, ' ' * (lengths[columns[ix]] - value_len)))
        elif justify == 'right':
            padded_columns.append('%s%s' % (' ' * (lengths[columns[ix]] - value_len), value))
        else:
            len_lp = int((lengths[columns[ix]] - value_len)/2)
            len_rp = lengths[columns[ix]] - len_lp - value_len
            padded_columns.append('%s%s%s' % (' ' * len_lp, value, ' ' * len_rp))

    return padded_columns

#-------------------------------------------------------------------------------
              
def _show_table_set_segment(segment, column):
    """
    Determine if headers are single column or multi-column, setting them appropriately
    """

    # If processing a flush request (no column), finalize segment headers and return.
    if column is None:
        _show_table_set_segment_super_headers(segment)

    # Process new column for segment.
    else:
        # Process segments with super_headers.
        if segment['SH']:
            # Process super_header change.
            if segment['SH_low_ix'] and segment['table']['super_headers'][column] != segment['table']['super_headers'][segment['columns'][segment['SH_low_ix']]]:
                _show_table_set_segment_super_headers(segment)

                column_ix =_show_table_set_segment_insert_new_column(segment, column)

                if segment['table']['super_headers'][column] == '':
                    segment['SH_low_ix'] = None
                    segment['SH_hi_ix'] = None
                else:
                    segment['SH_low_ix'] = column_ix

                if segment['table']['super_headers'][column] == '':
                    segment['super_headers'].append(_show_table_pad([column], [''], segment['table']['lengths'], justify='centre')[0])
                    segment['headers'].append(_show_table_pad([column], [segment['table']['headers'][column]], segment['table']['lengths'], justify='centre')[0])
                else:
                    segment['SH_hi_ix'] = column_ix

            else:
                column_ix =_show_table_set_segment_insert_new_column(segment, column)

                if segment['table']['super_headers'][column] == '':
                    segment['super_headers'].append(_show_table_pad([column], [''], segment['table']['lengths'], justify='centre')[0])
                    segment['headers'].append(_show_table_pad([column], [segment['table']['headers'][column]], segment['table']['lengths'], justify='centre')[0])
                else:
                    if not segment['SH_low_ix']:
                        segment['SH_low_ix'] = column_ix

                    segment['SH_hi_ix'] = column_ix

        # Process segments without super_headers (yet).
        else:
            column_ix =_show_table_set_segment_insert_new_column(segment, column)

            if segment['table']['super_headers'][column] == '':
                segment['super_headers'].append(_show_table_pad([column], [''], segment['table']['lengths'], justify='centre')[0])
                segment['headers'].append(_show_table_pad([column], [segment['table']['headers'][column]], segment['table']['lengths'], justify='centre')[0])
            else:
                segment['SH'] = True
                segment['SH_low_ix'] = column_ix
                segment['SH_hi_ix'] = column_ix

#-------------------------------------------------------------------------------
              
def _show_table_set_segment_insert_new_column(segment, column):
    """
    Insert a new column into the current segment.
    """

    segment['columns'].append(column)
    segment['length'] += 3 + segment['table']['lengths'][column]
    return len(segment['columns']) - 1

#-------------------------------------------------------------------------------
              
def _show_table_set_segment_super_headers(segment):
    """
    Set the super_headers for a segment.
    """

    if segment['SH'] and segment['SH_low_ix']:
        column = segment['columns'][segment['SH_low_ix']]
        segment['headers'].append('   '.join(_show_table_pad(segment['columns'][segment['SH_low_ix']:], segment['table']['headers'], segment['table']['lengths'], justify='centre')))
        segment['super_header_lengths'].append(len(segment['headers'][-1]))
        segment['super_headers'].append(_show_table_pad([column], segment['table']['super_headers'], {column: segment['super_header_lengths'][-1]}, justify='centre')[0])

#-------------------------------------------------------------------------------

def sys_cmd(cmd, return_stdout_not_rc=True):

    from subprocess import Popen, PIPE

    if return_stdout_not_rc:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            return decode(stdout).split('\n')
        else :
            return None

    else:
        p = Popen(cmd)
        p.communicate()
        return p.returncode

#-------------------------------------------------------------------------------

def update_pid_defaults(gvar, server=None, server_address=None, user=None, group=None):
    """
    If the process defaults have changed, update and re-write the pid_file.

    """

    import yaml

    updated = False

    if 'pid_defaults' not in gvar:
        gvar['pid_defaults'] = {'server': '-', 'server_addresses': {}}
        updated = True

    if server and gvar['pid_defaults']['server'] != server:
        gvar['pid_defaults']['server'] = server
        updated = True

    if server_address:
        if server_address not in gvar['pid_defaults']['server_addresses']:
            gvar['pid_defaults']['server_addresses'][server_address] = {}
            updated = True

        if user and group:
            if user not in gvar['pid_defaults']['server_addresses'][server_address] or \
                (user in gvar['pid_defaults']['server_addresses'][server_address] and gvar['pid_defaults']['server_addresses'][server_address][user] != group):
                gvar['pid_defaults']['server_addresses'][server_address][user] = group
                updated = True

    if updated and gvar['pid_file'] != '-':
        fd = open(gvar['pid_file'], 'w')
        fd.write(yaml.dump(gvar['pid_defaults']))
        fd.close()

#-------------------------------------------------------------------------------
def prepare_file(file_path):
    #check if its a file or a url

    # This might not work if the files are very large, perhaps make use of the mmap library
    if file_path.startswith("file://"):
        return { "streaming_upload": True }
    else:
        #it's a url or something else we'lll let the server handle
        return { 'myfileurl': file_path }

#-------------------------------------------------------------------------------

def verify_yaml_file(file_path):
    # Read the entire file.
    fd = open(file_path)
    file_string = fd.read()
    fd.close()

    # Verify yaml files.
    if (len(file_path) > 4 and file_path[-4:] == '.yml') or \
        (len(file_path) > 5 and file_path[-5:] == '.yaml'):

        result = _yaml_load_and_verify(file_string)

        if not result[0]:
            print('Error: Invalid yaml file "%s": %s' % (result[1], result[2]))
            exit(1)

    return {
        'metadata': file_string,
        }

#-------------------------------------------------------------------------------
              
def yaml_full_load(yaml_string):
    import yaml

    if hasattr(yaml, 'full_load'):
        return yaml.full_load(yaml_string)
    else:
        return yaml.load(yaml_string)


#-------------------------------------------------------------------------------
              
def _yaml_load_and_verify(yaml_string):
    import yaml

    try:
        _yaml = yaml_full_load(yaml_string)
        return [1, _yaml]
    except yaml.scanner.ScannerError as ex:
        return [0, 'scanner error', ex]
    except yaml.parser.ParserError as ex:
        return [0, 'parser error', ex]
    except Exception as ex:
        return [0, 'unknown error', ex]

