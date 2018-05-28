def check_keys(gvar, mp, rp, op, key_map=None, requires_server=True):
    """
    Modify user settings.
    """

    import csv2_help

    # Summarize the mandatory, required, and optional parameters for the current command.
    mandatory = []
    required = []
    options = []
    for key in gvar['command_keys']:
        # 0.short_name, 1.long_name, 2.key_value(bool)
        if key[0] in mp:
            mandatory.append([key[0], '%-4s |  %s' % (key[0], key[1]), key[1][2:]])
        if key[0] in rp:
            required.append([key[0], '%-4s |  %s' % (key[0], key[1]), key[1][2:]])
        if key[0] in op or (op == ['*'] and key[0] not in mp + rp):
            options.append([key[0], '%-4s |  %s' % (key[0], key[1]), key[1][2:]])

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
        print('Error: "csv2 %s %s" - the following mandatory parameters must be specfied on the command line:' % (gvar['object'], gvar['action']))
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
        else:
            missing.append(key[1])

    if missing:
        print('Error: "csv2 %s %s" - no value, neither default nor command line, for the following required parameters:' % (gvar['object'], gvar['action']))
        for key in missing:
            print('  %s' % key)
        print('For more information, use -h or -H.')
        exit(1)

    if key_map:
        for key in options:
            if key[0] in key_map and key[2] in gvar['user_settings']:
                form_data[key_map[key[0]]] = _check_keys_for_password(gvar, key)

    return form_data

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

def requests(gvar, request, form_data={}):
    """
    Make RESTful requests via the _requests function and return the response. This function will
    obtain a CSRF (for POST requests) prior to making the atual request.
    """
    
    # Obtain a CSRF as required.
    if form_data and not gvar['csrf']:
        response = _requests(gvar, '/settings/prepare/')
    
    # Group change requested but the request is not a POST.
    elif not form_data and 'group' in gvar['command_args']:
        if not gvar['csrf']:
            response = _requests(gvar, '/settings/prepare/')
    
        response = _requests(gvar,
                '/settings/prepare',
                form_data = {
                    'group': gvar['user_settings']['group'],
                    }       
            ) 
        
    # Perform the callers request.
    return _requests(gvar, request, form_data=form_data)

def _requests(gvar, request, form_data={}):
    """
    Make RESTful request and return response.
    """
    
    from getpass import getpass
    import os
    import requests as py_requests

    EXTRACT_CSRF = str.maketrans('=;', '  ')

    if 'server-address' not in gvar['user_settings']:
        print('Error: user settings for server "%s" does not contain a URL value.' % gvar['server'])
        exit(1)

    if form_data:
        _function = py_requests.post
        _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf']}}
    else:
        _function = py_requests.get
        _form_data = {}

    if 'server-grid-cert' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-cert']) and \
        'server-grid-key' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-key']):
        _r = _function(
            '%s%s' % (gvar['user_settings']['server-address'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']},
            cert=(gvar['user_settings']['server-grid-cert'], gvar['user_settings']['server-grid-key']),
            data=_form_data,
            cookies=gvar['cookies']
            )

    elif 'server-user' in gvar['user_settings']:
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '-':
            gvar['user_settings']['server-password'] = getpass('Enter your csv2 password for server "%s": ' % gvar['server'])
        _r = _function(
            '%s%s' % (gvar['user_settings']['server-address'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']},
            auth=(gvar['user_settings']['server-user'], gvar['user_settings']['server-password']),
            data=_form_data,
            cookies=gvar['cookies'] 
            )

    else:
        print('Error: csv2 servers require certificates or username/password for authentication.')
        exit(1)

    try:
        response = _r.json()
    except:
        if _r.status_code:
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, %s.' % (gvar['server'], _r.status_code, py_requests.status_codes._codes[_r.status_code][0])}
        else:
            response = {'response_code': 2, 'message': 'server "%s", internal server error.' % gvar['server']}

    if gvar['user_settings']['expose-API']:
        print("Expose API requested:\n" \
            "  py_requests.%s(\n" \
            "    %s%s,\n" \
            "    headers={'Accept': 'application/json', 'Referer': '%s'}," % (
                _function.__name__,
                gvar['user_settings']['server-address'],
                request,
                gvar['user_settings']['server-address'],
                )
            )

        if 'server-grid-cert' in gvar['user_settings'] and \
            os.path.exists(gvar['user_settings']['server-grid-cert']) and \
            'server-grid-key' in gvar['user_settings'] and \
            os.path.exists(gvar['user_settings']['server-grid-key']):
            print("    cert=('%s', '%s')," % (gvar['user_settings']['server-grid-cert'], gvar['user_settings']['server-grid-key']))
        else:
            print("    auth=('%s', <password>)," % gvar['user_settings']['server-user'])

        print("    data=%s,\n" \
            "    cookies='%s'\n" \
            "    )\n\n" \
            "  Response: {" % (
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

    if 'Set-Cookie' in _r.headers:
        new_csrf = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]
        if new_csrf[1]:
            gvar['cookies'] = _r.cookies
            gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

    if 'active_group' in response:
        gvar['active_group'] = response['active_group']

    if 'super_user' in response:
        gvar['super_user'] = response['super_user']

    return response

def show_header(gvar, response):
    """
    Print the server response header.
    """

    print('Server: %s, Active User: %s, Active Group: %s, User\'s Groups: %s' % (gvar['server'], response['active_user'], response['active_group'], response['user_groups']))

def show_table(gvar, queryset, columns, allow_null=True):
    """
    Print a table from a SQLAlchemy query set.
    """

    import json

    # Normalize column definitions.
    _field_names = []
    _column_names = []
    
    if gvar['user_settings']['rotate']:
        _column_lengths = [3, 5]
    else:
        _column_lengths = []

    for column in columns:
        _w = column.split('/')
        if len(_w) < 2:
          _w.append(_w[0])

        _field_names.append(_w[0])
        _column_names.append(_w[1])

        if gvar['user_settings']['rotate']:
            if _column_lengths[0] < len(_w[1]):
                _column_lengths[0] = len(_w[1])
        else:
            _column_lengths.append(len(_w[1]))

    # Normalize the queryset.
    if isinstance(queryset, str):
        _qs = json.loads(queryset)
    else:
        _qs = queryset

    # extract columns.
    _list = []
    for row in _qs:
        _row = []
        for _ix in range(len(_field_names)):
            if _field_names[_ix] in row:
              _value = row[_field_names[_ix]]
            elif 'fields' in row and _field_names[_ix] in row['fields']:
              _value = row['fields'][_field_names[_ix]]
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

            if gvar['user_settings']['rotate']:
                _list.append([_column_names[_ix], _value])
                if _column_lengths[1] < _len:
                    _column_lengths[1] = _len
            else:
                _row.append(_value)
                if _column_lengths[_ix] < _len:
                    _column_lengths[_ix] = _len

        if gvar['user_settings']['rotate']:
            _list.append(['', ''])
        else:
            _list.append(_row)

    _column_underscore = []
    for _ix in range(len(_column_lengths)):
        _column_underscore.append('-' * (_column_lengths[_ix] + 2))
    _ruler = '+%s+' % '+'.join(_column_underscore)

    print(_ruler)
    if gvar['user_settings']['rotate']:
        print('+ %s +' % ' | '.join(_show_table_pad(_column_lengths, ['Key', 'Value'])))
    else:
        print('+ %s +' % ' | '.join(_show_table_pad(_column_lengths, _column_names)))
    print(_ruler)

    for _row in _list:
        if gvar['user_settings']['rotate'] and not allow_null and _row[1] == '-':
            continue

        print('| %s |' % ' | '.join(_show_table_pad(_column_lengths, _row)))

    print(_ruler)

def _show_table_pad(lens, cols):
    """
    Pad column values with blanks; lens contains the maximum length for each column. 
    """

    padded_columns = []

    for _ix in range(len(lens)):
        padded_columns.append('%s%s' % (cols[_ix], ' ' * (lens[_ix] - len(str(cols[_ix])))))

    return padded_columns

def verify_yaml_file(file_path):
    # Read the entire file.
    fd = open(file_path)
    file_string = fd.read()
    fd.close()

#   # Verify attribute line.
#   attribute, yaml = file_string.split('\n',1)
#   if len(attribute) > 1 and attribute[0] == '#':
#       attributes = '\n'.join(' '.join(attribute[1:].split()).split(', '))
#       result = _yaml_load_and_verify(attributes)
#   else:
#       print('Error: No attribute line, format: # yaml_enabled: <True | False>, yaml_mime_type = <cloud-config | ...>')
#       exit(1)
#
#   if not result[0]:
#       print('Error: Invalid attribute line "%s": %s' % (result[1], result[2]))
#       exit(1)
#
#   if 'yaml_enabled' in result[1]:
#       if result[1]['yaml_enabled'] == True:
#           yaml_enabled = 1
#       else:
#           yaml_enabled = 0
#   else:
#       print('Error: yaml_enabled missing from attribute line.')
#       exit(1)
#
#   if 'yaml_mime_type' in result[1]:
#       yaml_mime_type = result[1]['yaml_mime_type']
#   else:
#       print('Error: yaml_mime_type missing from attribute line.')
#       exit(1)

    # Verify the remaining yaml.
    result = _yaml_load_and_verify(yaml)
    if not result[0]:
        print('Error: Invalid yaml file "%s": %s' % (result[1], result[2]))
        exit(1)

    return {
        'yaml': yaml,
        'enabled': yaml_enabled, 
        'mime_type': yaml_mime_type, 
        }

def _yaml_load_and_verify(yaml_string):
    import yaml

    try:
        _yaml = yaml.load(yaml_string)
        return [1, _yaml]
    except yaml.scanner.ScannerError as ex:
        return [0, 'scanner error', ex]
    except yaml.parser.ParserError as ex:
        return [0, 'parser error', ex]

