def _required_settings(gvar, arg_list, mandatory_arguments=False):
    """
    Modify user settings.
    """
    if mandatory_arguments:
      option = 'command_args'
      modifier = 'command arguments'
    else:
      option = 'user_settings'
      modifier = 'user settings'

    # Check for mandatory arguments.
    _missing = []
    for _arg in arg_list:
      if _arg[2:] not in gvar[option]:
          _missing.append(_arg)

    if _missing:
        print('Error: "csv2 config set" requires the following %s: %s' % (modifier, _missing))
        exit(1)

def _requests(gvar, request, form_data={}):
    """
    Make RESTful request and return response.
    """
    
    import os
    import requests

    EXTRACT_CSRF = str.maketrans('=;', '  ')

    if 'url' not in gvar['user_settings']:
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
            '%s%s' % (gvar['user_settings']['url'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['url']},
            cert=(gvar['user_settings']['cert'], gvar['user_settings']['key']),
            data=_form_data,
            cookies=gvar['cookies']
            )

    elif 'user' in gvar['user_settings']:
        if 'password' not in gvar['user_settings'] or gvar['user_settings']['password'] == '-':
            gvar['user_settings']['password'] = getpass('Enter your csv2 password for server "%s": ' % gvar['server'])
        _r = _function(
            '%s%s' % (gvar['user_settings']['url'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['url']},
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
        response = {'response_code': 1, 'message': 'unable to communicate with server "%s".' % gvar['server']}

    if response['response_code'] != 0:
        print('Error: %s' % response['message'])
        exit(1)

    gvar['cookies'] = _r.cookies
    if 'Set-Cookie' in _r.headers:
        gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

    return response

def _show_table(gvar, queryset, columns):
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
            elif _field_names[_ix] in row['fields']:
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

