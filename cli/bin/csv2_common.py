def _check_keys(gvar, obj_act, mp, op, key_map=None):
    """
    Modify user settings.
    """

    # Summarize the mandatory and optional parameters for the current command.
    mandatory = []
    options = []
    for key in gvar['command_keys']:
        # 0.short_name, 1.long_name, 2.key_value(bool)
        if key[0] in mp:
            mandatory.append([key[0], '%-3s | %s' % (key[0], key[1]), key[1][2:]])
        if key[0] in op or (op == ['*'] and key[0] not in mp):
            options.append([key[0], '%-3s | %s' % (key[0], key[1]), key[1][2:]])

    # If help requested, display the help for the current command and exit.
    if gvar['user_settings']['help']:
        if mandatory:
            print('Help requested for "csv2 %s". The following parameters are required:' % obj_act)
            for key in mandatory:
                print('  %s' % key[1])

        if options:
            if mandatory:
                print('The following optional parameters may be specified:')
            else:
                print('Help requested for "csv2 %s". The following optional parameters may be specified:' % obj_act)
  
            for key in options:
                print('  %s' % key[1])

        if not mandatory and not options:
            print('Help requested for "csv2 %s". There are no parameters for this command.' % obj_act)

        print('For more information, see the csv2 main page.')
        exit(0)


    # If the current command has mandatory parameters and they have not been specified, issue error messages and exit.
    form_data = {}
    missing = []
    for key in mandatory:
        if key[2] in gvar['command_args']:
            if key_map and key[0] in key_map:
                form_data[key_map[key[0]]] = gvar['command_args'][key[2]]
        else:
            missing.append(key[1])

    if missing:
        print('Error: "csv2 %s" requires the following parameters:' % obj_act)
        for key in missing:
            print('  %s' % key)
        print('For more information, see the csv2 main page.')
        exit(1)

    if key_map:
        for key in options:
            if key[0] in key_map and key[2] in gvar['user_settings']:
                form_data[key_map[key[0]]] = gvar['user_settings'][key[2]]

    return form_data

def _requests(gvar, request, form_data={}):
    """
    Make RESTful request and return response.
    """
    
    import os
    import requests

    EXTRACT_CSRF = str.maketrans('=;', '  ')

    if 'csv2-server-url' not in gvar['user_settings']:
        print('Error: user settings for server "%s" does not contain a URL value.' % gvar['server'])
        exit(1)

    if form_data:
        _function = requests.post
        _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf']}}
    else:
        _function = requests.get
        _form_data = {}

    if 'cert' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['cert']) and \
        'key' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['key']):
        _r = _function(
            '%s%s' % (gvar['user_settings']['csv2-server-url'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['csv2-server-url']},
            cert=(gvar['user_settings']['cert'], gvar['user_settings']['key']),
            data=_form_data,
            cookies=gvar['cookies']
            )

    elif 'user' in gvar['user_settings']:
        if 'password' not in gvar['user_settings'] or gvar['user_settings']['password'] == '-':
            gvar['user_settings']['password'] = getpass('Enter your csv2 password for server "%s": ' % gvar['server'])
        _r = _function(
            '%s%s' % (gvar['user_settings']['csv2-server-url'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['csv2-server-url']},
            auth=(gvar['user_settings']['user'], gvar['user_settings']['password']),
            data=_form_data,
            cookies=gvar['cookies'] 
            )

    else:
        print('Error: csv2 servers require certificates or username/password for authentication.')
        exit(1)

    try:
        response = _r.json()
    except:
        response = {'response_code': 2, 'message': 'server "%s", internal server error.' % gvar['server']}

    if gvar['user_settings']['expose-API']:
        print("Expose API requested:\n" \
            "  requests.%s(\n" \
            "    %s%s,\n" \
            "    headers={'Accept': 'application/json', 'Referer': '%s'}," % (
                _function.__name__,
                gvar['user_settings']['csv2-server-url'],
                request,
                gvar['user_settings']['csv2-server-url'],
                )
            )

        if 'cert' in gvar['user_settings'] and \
            os.path.exists(gvar['user_settings']['cert']) and \
            'key' in gvar['user_settings'] and \
            os.path.exists(gvar['user_settings']['key']):
            print("    cert=('%s', '%s')," % (gvar['user_settings']['cert'], gvar['user_settings']['key']))
        else:
            print("    auth=('%s', <password>)," % gvar['user_settings']['user'])

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

    gvar['cookies'] = _r.cookies
    if 'Set-Cookie' in _r.headers:
        gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

    return response

def _show_table(gvar, queryset, columns, allow_null=True):
    """
    Print a table from a django query set.
    """

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

