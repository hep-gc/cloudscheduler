def _caller():
    import inspect
    import os
    if inspect.stack()[-3][1] == '<string>':
        return os.path.basename(inspect.stack()[-4][1]).split('.')[0]
    return os.path.basename(inspect.stack()[-3][1]).split('.')[0]

def _execute_selections(gvar, request, expected_text, expected_values):
    from unit_test_common import _caller
    
    gvar['ut_count'][0] += 1
    gvar['ut_count'][1] += 1
    if len(gvar['selections']) < 1 or str(gvar['ut_count'][0]) in gvar['selections']:
        return True
    else:
        gvar['ut_skipped'] += 1
        # print('%04d (%04d) %s Skipping: \'%s\', %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, repr(expected_text), expected_values))
        return False
   
def execute_csv2_command(gvar, expected_rc, expected_modid, expected_text, cmd, expected_list=None, columns=None, timeout=None):

    from subprocess import PIPE, run, TimeoutExpired
    from unit_test_common import _caller, _execute_selections
    import re

    if _execute_selections(gvar, cmd, expected_text, None):

        # If the `-s` flag is not used tests will sometimes hang because cloudscheduler is waiting for a server web address (but this prompt is not visible to the tester)
        if '-s' not in cmd:
            cmd.extend(['-s', 'unit-test'])
        if '-spw' not in cmd:
            try:
                su_index = cmd.index('-su')
                if cmd[su_index + 1] == gvar['user_settings']['server-user']:
                    cmd.extend(['-spw', gvar['user_settings']['server-password']])
                else:
                    cmd.extend(['-spw', gvar['user_secret']])
            except ValueError:
                pass
        
        try:
            process = run(cmd, stdout=PIPE, stderr=PIPE, timeout=timeout)
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()
            return_code = process.returncode
        except TimeoutExpired as err:
            stdout = err.stdout.decode()
            stderr = err.stderr.decode()
            return_code = None

        failed = False

        # Comparison with None is necessary because we want to compare expected and actual if expected is 0.
        if expected_rc != None and expected_rc != return_code:
            failed = True

        if return_code == 0 or not expected_modid:
            modid = expected_modid
        else:
            modid = stdout.replace('-', ' ').split()[1]
            if expected_modid and modid != expected_modid:
                failed = True

        list_error = ''
        if expected_list:
            if expected_list not in stdout:
                failed = True
                list_error = 'list \'{}\' not found'.format(expected_list)
            elif columns:
                columns_found = set()
                rows = stdout.split('\n')
                for row in rows:
                    if len(row) > 1 and row[:2] == '+ ':
                        row_trimmed = row[2:-2].strip()
                        # Split on either '<zero or more spaces>|<zero or more spaces>' occurring one or more times, or two or more spaces in a row. Then filter out empty strings.
                        columns_found.update(filter(None, re.split(r'(?:\s*\|\s*)+|(?:\s{2,})', row_trimmed)))
                columns_expected = set(columns)
                if columns_expected != columns_found:
                    failed = True
                    list_error = '\tActual columns found: {}\n \
                    \tColumns expected but not found: {}\n \
                    \tColumns not expected but found: {}\n'\
                    .format(columns_found, columns_expected - columns_found, columns_found - columns_expected)

        if expected_text and expected_text not in stdout:
            failed = True

        if failed:
            gvar['ut_failed'] += 1
            if not gvar['hidden']:
                # repr() is used because it puts quotes around strings *unless* they are None.
                print('\n%04d (%04d) %s \033[91mFailed\033[0m: expected_rc=%s, expected_modid=%s, expected_text=%s, cmd=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), expected_rc, repr(expected_modid), repr(expected_text), cmd))
                print('\treturn code=%s' % return_code)
                print('\tmodule ID=%s' % repr(modid))
                print('\tstdout=%s' % stdout)
                print('\tstderr=%s' % stderr)
                if list_error:
                    print('List error: {}'.format(list_error))
                print()

            return 1
        else:
            if not gvar['hidden']:
                print('%04d (%04d) %s \033[92mOK\033[0m: expected_rc=%s, expected_modid=%s, expected_text=%s, cmd=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), expected_rc, repr(expected_modid), repr(expected_text), cmd))
            return 0
    else:
        return 0

def execute_csv2_request(gvar, expected_rc, expected_modid, expected_text, request, group=None, form_data={}, query_data={}, expected_list=None, list_filter=None, values=None, server_user=None, server_pw=None, html=False):
    """
    Make RESTful requests via the _requests function and return the response. This function will
    obtain a CSRF (for POST requests) prior to making the actual request.
    """

    from unit_test_common import _caller, _execute_selections, _requests

    # If a test user was specified, insert the test password.
    # Note that if neither server_user nor server_pw is specified, _requests() pulls both from gvar['user_settings'].
    if server_user and server_pw == None and server_user != gvar['user_settings']['server-user']:
        server_pw = gvar['user_secret']

    if _execute_selections(gvar, 'req=%s, group=%s, form=%s, query=%s' % (request, group, form_data, query_data), expected_text, values):
        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        # For POST requests (form_data is not null), ensure we have CSRF and insert
        # the current active group.
        if form_data:
            if not gvar['csrf']:
                _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)

        # Perform the callers request.
        response = _requests(gvar, request, group, form_data=form_data, query_data=query_data, server_user=server_user, server_pw=server_pw, html=html)

        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        failed = False

        # Comparison with None is necessary because we want to compare expected and actual if expected is 0.
        if expected_rc != None and expected_rc != response['response_code']:
            failed = True

        if response['response_code'] == 0 or not expected_modid:
            modid = expected_modid
        else:
            modid = response['message'].replace('-', ' ').split()[0]
            if expected_modid and modid != expected_modid:
                failed = True

        if expected_text and str(response['message']).find(expected_text) < 0:
            failed = True

        # Colour a missing group red.
        if not group:
            group = '\033[91mNone\033[0m'

        if failed:
            gvar['ut_failed'] += 1

            if not gvar['hidden']:
                print('\n%04d (%04d) %s \033[91mFailed\033[0m: expected_rc=%s, expected_modid=%s, expected_text=%s, request=\'%s\', group=%s, form_data=%s, query_data=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), expected_rc, repr(expected_modid), repr(expected_text), request, group, form_data, query_data))
                if gvar['user_settings']['server-address'] in gvar['active_server_user_group'] and server_user in gvar['active_server_user_group'][gvar['user_settings']['server-address']]:
                    print('    server=%s, user=%s, group=%s' % (repr(gvar['server']), repr(server_user), repr(gvar['active_server_user_group'][gvar['user_settings']['server-address']][server_user])))
                else:
                    print('    server=%s, user=%s, group=\033[91mNone\033[0m' % (repr(gvar['server']), repr(server_user)))
                print('    response code=%s' % response['response_code'])
                if response['response_code'] != 0:
                    print('    module ID=%s' % repr(modid))
                print('    message=\'%s\'\n' % response['message'])

            return 1
        elif expected_list and list_filter and values:
            if expected_list not in response:
                failed = True
                if not gvar['hidden']:
                    print('\n%04d (%04d) %s \033[91mFailed\033[0m: request=\'%s\', group=%s, expected_list=\'%s\', list_filter=%s, values=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, group, expected_list, list_filter, values))
                    print('\tNo list \'%s\' in response. The message from the server was: \'%s\'\n' % (expected_list, response['message']))
            # expected_list in response
            else:
                found_perfect_row = False
                filtered_rows = []
                mismatches_in_filtered_rows = []
                for row in response[expected_list]:
                    if all((key in row) and (list_filter[key] == row[key]) for key in list_filter):
                        filtered_rows.append(row)

                for row in filtered_rows:
                    mismatches = []
                    for expected_key in values:
                        if expected_key not in row:
                            mismatches.append((expected_key, values[expected_key]))
                        elif values[expected_key] != row[expected_key]:
                            mismatches.append((expected_key, values[expected_key], row[expected_key]))
                    if mismatches:
                        mismatches_in_filtered_rows.append(mismatches)
                    else:
                        if not gvar['hidden']:
                            print('%04d (%04d) %s \033[92mOK\033[0m: request=\'%s\', group=%s, form_data=%s, expected_list=%s, list_filter=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, group, form_data, expected_list, list_filter))
                            return 0

                # At this point we know the test has failed.
                # Found mismatched values.
                if mismatches_in_filtered_rows:
                    if not gvar['hidden']:
                        print('\n%04d (%04d) %s \033[91mRow Check\033[0m: request=\'%s\', group=%s, expected_list=\'%s\', list_filter=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, group, expected_list, list_filter))
                        print('\t%s rows were accepted by the filter.' % len(mismatches_in_filtered_rows))
                        for row_index, mismatches_in_row in enumerate(mismatches_in_filtered_rows):
                            print('\tRow %s:' % (row_index + 1))
                            print('\t\tActual values in response: %s' % filtered_rows[row_index])
                            for mismatch in mismatches_in_row:
                                if len(mismatch) == 2:
                                    print('\t\tFor the key %s: expected %s, but the key was not in the response.' % mismatch)
                                # len(mismatch) == 3
                                else:
                                    print('\t\tFor the key %s: expected %s, but got %s.' % mismatch)
                    print()
                # All rows were rejected by the filter.
                else:
                    if not gvar['hidden']:
                        print('\n%04d (%04d) %s \033[91mFailed\033[0m: request=\'%s\', group=%s, expected_list=%s, list_filter=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, group, expected_list, list_filter))
                        print('\tFilter did not match any rows. The message from the server was: \'%s\'\n' % response['message'])

                gvar['ut_failed'] += 1
                return 1

        # not failed
        elif not gvar['hidden']:
            print('%04d (%04d) %s \033[92mOK\033[0m: expected_rc=%s, expected_modid=%s, expected_text=%s, request=\'%s\', group=%s, form_data=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), expected_rc, repr(expected_modid), repr(expected_text), request, group, form_data))

    # _execute_selections returned False.
    else:
        return 0

def sanity_requests(gvar, request, group, server_user, userless_group, groupless_server_user):
    '''Perform sanity checks that should pass for all non-CLI tests.'''
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        request, group=group, server_user='invalid-unit-test'
    )
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(groupless_server_user),
        request, group=group, server_user=groupless_server_user
    )
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        request, group=group, server_user=server_user, server_pw='invalid-unit-test'
    )
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        request, group='invalid-unit-test', server_user=server_user
    )
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(userless_group),
        request, group=userless_group, server_user=server_user
    )

def parameters_requests(gvar, request, group, server_user, PARAMETERS):
    '''
    Execute requests with missing parameters and bad parameters.
    PARAMETERS is a dictionary in which each key is the name of a parameter (str), and each key is itself a dictionary, containing:
    0. 'test_cases': A dictionary of test cases. Each key should be an invalid value for this parameter (which will be cast to a str). Each value should be the message to expect when this invalid value is sent in an otherwise valid request (str). Giving only invalid values in this dict means that none of the requests sent my this function should actually change anything on the server side (because they are all invalid in one way or another).
    1. 'valid': A valid value for the parameter (which will be cast to a str). If the parameter is mandatory, this will be sent in requests that contain bad values for other parameters.
    [2. Optional: 'mandatory': A boolean indicating whether this parameter must be provided in all requests. If not given, the parameter will be treated as optional.]
    [3. Optional: 'allows_multiple': A boolean indicating whether giving multiple values for this parameter using the `{'param.1': value1, 'param.2': value2}` syntax is allowed. If not given, this will be treated as False.]
    '''

    mandatory_params = {name: details['valid'] for name, details in PARAMETERS.items() if details.get('mandatory')}
    # Omit form_data entirely.
    execute_csv2_request(
        gvar, 1, None, ' invalid method "GET" specified.',
        request, group=group, server_user=server_user
    )
    # Give an invalid parameter.
    execute_csv2_request(
        gvar, 1, None, 'request contained a bad parameter "invalid-unit-test".',
        request, group=group, form_data={'invalid-unit-test': 'invalid-unit-test', **mandatory_params}, server_user=server_user
    )

    for p_name, p_details in PARAMETERS.items():
        if p_details.get('mandatory'):
            # Temporarily remove.
            del mandatory_params[p_name]
            # If there are other mandatory parameters, send a request without the current one.
            if mandatory_params:
                execute_csv2_request(
                    gvar, 1, None, 'request did not contain mandatory parameter "{}".'.format(p_name),
                    request, group=group, form_data=mandatory_params, server_user=server_user
                )
            # Else see if we can find an optional one to send by itself (to avoid 'invalid method').
            else:
                try:
                    optional_name, optional_value = next(((name, details['valid']) for name, details in PARAMETERS.items() if not details.get('mandatory')))
                    execute_csv2_request(
                        gvar, 1, None, 'request did not contain mandatory parameter "{}".'.format(p_name),
                        request, group=group, form_data={optional_name: optional_value}, server_user=server_user
                    )
                # We have exactly one parameter, and it is mandatory, so we cannot exclude it without getting 'invalid method' (which we already tested for).
                except StopIteration:
                    pass
        if not p_details.get('allows_multiple'):
            # Provide the parameter twice.
            execute_csv2_request(
                gvar, 1, None, '>>>>>>>>>>>>>>>>>> TODO',
                request, group=group, form_data={'{}.1'.format(p_name): p_details['valid'], '{}.2'.format(p_name): p_details['valid'], **mandatory_params}, server_user=server_user
            )
        # Give the parameter with invalid values.
        for value, message in p_details['test_cases'].items():
            execute_csv2_request(
                gvar, 1, None, message,
                request, group=group, form_data={p_name: value, **mandatory_params}, server_user=server_user
            )
        # Add the parameter back in if it was mandatory.
        if p_details.get('mandatory'):
            mandatory_params[p_name] = p_details['valid']

def generate_secret():
    from string import ascii_letters, digits
    from random import SystemRandom, choice
    alphabet = ascii_letters + digits
    while True:
        user_secret = ''.join(SystemRandom().choice(alphabet) for _ in range(10))
        if (any(c.islower() for c in user_secret)
                and any(c.isupper() for c in user_secret)
                and sum(c.isdigit() for c in user_secret) >= 3):
            break
    return user_secret

def html_message(text):
    import re
    p = re.compile(r'Error: (.*)</b>')
    m = p.search(text.replace('\n', ''))
    if m and m.group(1):
        return True, m.group(1)
    p = re.compile(r'<div class="footer"(.*)</div>')
    m = p.search(text.replace('\n', ''))
    if m and m.group(1):
        return False, re.sub(r'</?[a-z]{2}>', '', m.group(1).strip())
    return False, 'no message found'

# The command parameter is never used.
def initialize_csv2_request(gvar, selections=None, hidden=False):
    from getpass import getpass
    import os
    import re
    import yaml

    gvar['active_server_user_group'] = {}
    gvar['cloud_credentials'] = {}
    gvar['command_args'] = {}
    gvar['cookies'] = None
    gvar['csrf'] = None
    # Used as the htcondor_fqdn of test groups.
    gvar['fqdn'] = None
    gvar['server'] = 'unit-test'
    gvar['ut_count'] = [0, 0]
    gvar['ut_failed'] = 0
    gvar['ut_skipped'] = 0
    gvar['hidden'] = hidden

    if selections:
        gvar['selections'] = []
        tmp_selections = selections.split(',')
        for ix in range(len(tmp_selections)):
            w = tmp_selections[ix].split('-')
            if len(w) == 2:
                for iy in range(int(w[0]), int(w[1])+1):
                    gvar['selections'].append(str(iy))
            else:
                gvar['selections'].append(tmp_selections[ix])
    else:
        gvar['selections'] = []

    try:
        with open(os.path.expanduser('~/.csv2/unit-test/settings.yaml')) as settings_file:
            gvar['user_settings'] = yaml.full_load(settings_file.read())
    except FileNotFoundError:
        raise Exception('You must create a minimal cloudscheduler defaults for server "unit-test" containing the server address and user credentials.')

    gvar['fqdn'] = re.sub(r'^https?://', '', gvar['user_settings']['server-address'])

    # Get user_secret and cloud credentials.
    CREDENTIALS_PATH = os.path.expanduser('~/cloudscheduler/unit_tests/credentials.yaml')
    os.umask(0)
    try:
        with open(os.path.expanduser('~/cloudscheduler/unit_tests/credentials.yaml'), 'r') as credentials_file:
            credentials = yaml.full_load(credentials_file.read())
            gvar.update(credentials)
    except FileNotFoundError:
        print('No unit test credentials file found at {}. Prompting for credentials to use when creating clouds.'.format(CREDENTIALS_PATH))
        gvar['user_secret'] = generate_secret()
        gvar['cloud_credentials']['authurl'] = input('authurl (cloud address): ')
        gvar['cloud_credentials']['username'] = input('username: ')
        gvar['cloud_credentials']['password'] = getpass('password: ')
        gvar['cloud_credentials']['region'] = input('region: ')
        gvar['cloud_credentials']['project'] = input('project: ')
        # Create credentials file with read / write permissions for the current user and none for others. Save user_secret there in plain text.
        os.makedirs(CREDENTIALS_PATH.rsplit('/', maxsplit=1)[0], exist_ok=True)
        with open(os.open(CREDENTIALS_PATH, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as credentials_file:
            credentials_file.write(yaml.dump({'user_secret': gvar['user_secret'], 'cloud_credentials': gvar['cloud_credentials']}))
    except yaml.YAMLError as err:
        print('YAML encountered an error while parsing {}: {}'.format(CREDENTIALS_PATH, err))

    return

def _requests(gvar, request, group=None, form_data={}, query_data={}, server_user=None, server_pw=None, html=False):
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

    if html:
        headers={'Referer': gvar['user_settings']['server-address']}
    else:
        headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']}

    if server_user and server_pw:
        _function, _request, _form_data = _requests_insert_controls(gvar, request, group, form_data, query_data, gvar['user_settings']['server-address'], server_user)

        _r = _function(
            _request,
            headers=headers,
            auth=(server_user, server_pw),
            data=_form_data,
            cookies=gvar['cookies'] 
            )

    elif 'server-grid-cert' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-cert']) and \
        'server-grid-key' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-key']):

        _function, _request, _form_data = _requests_insert_controls(gvar, request, group, form_data, query_data, gvar['user_settings']['server-address'], gvar['user_settings']['server-grid-cert'])

        _r = _function(
            _request,
            headers=headers,
            cert=(gvar['user_settings']['server-grid-cert'], gvar['user_settings']['server-grid-key']),
            data=_form_data,
            cookies=gvar['cookies']
            )

    elif 'server-user' in gvar['user_settings']:
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '-':
            gvar['user_settings']['server-password'] = getpass('Enter your csv2 password for server "%s": ' % gvar['server'])

        _function, _request, _form_data = _requests_insert_controls(gvar, request, group, form_data, query_data, gvar['user_settings']['server-address'], gvar['user_settings']['server-user'])

        _r = _function(
            _request,
            headers=headers,
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
        if _r.status_code and _r.status_code == 401:   
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, unauthorized.' % (gvar['server'], _r.status_code)}
        elif _r.status_code and _r.status_code == 403:   
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, forbidden.' % (gvar['server'], _r.status_code)}
        elif html and _r.status_code and _r.status_code == 200:
            error, message = html_message(_r.text)
            if error:
                response = {'response_code': 1, 'message': message.replace('&quot;', '"')}
            else:
                response = {'response_code': 0, 'message': message.replace('&quot;', '"')}
        elif _r.status_code:   
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s.' % (gvar['server'], _r.status_code)}
        else:
            response = {'response_code': 2, 'message': 'server "%s", internal server error.' % gvar['server']}

    if 'Set-Cookie' in _r.headers:
        new_csrf = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]
        if new_csrf[1]:
            gvar['cookies'] = _r.cookies
            gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

    if 'response_code' in response and response['response_code'] == 0:
        if 'active_user' in response and 'active_group' in response:
            if gvar['user_settings']['server-address'] not in gvar['active_server_user_group']:
                gvar['active_server_user_group'][gvar['user_settings']['server-address']] = {}

            gvar['active_server_user_group'][gvar['user_settings']['server-address']][response['active_user']] = response['active_group']

    if 'super_user' in response:
        gvar['super_user'] = response['super_user']

    if gvar['user_settings']['expose-API']:
        print("Expose API requested:\n" \
            "  py_requests.%s(\n" \
            "    %s%s,\n" \
            "    headers=%s," % (
                _function.__name__,
                gvar['user_settings']['server-address'],
                request,
                headers,
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

    return response

#-------------------------------------------------------------------------------
              
def _requests_insert_controls(gvar, request, group, form_data, query_data, server_address, server_user):
    """
    Add controls (csrf, group, etc.) to python request.
    """

    import requests as py_requests

    if form_data:
        _function = py_requests.post
        _request = '%s%s' % (server_address, request)

        if group:
            _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf'], 'group': group}}
        else:
            if server_address in gvar['active_server_user_group'] and server_user in gvar['active_server_user_group'][server_address]:
                _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf'], 'group': gvar['active_server_user_group'][server_address][server_user]}}
            else:
                _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf']}}

    else:
        _function = py_requests.get

        if group:
            if request[-1] == '/':
                _request = '%s%s?%s' % (server_address, request[:-1], group)
            else:
                _request = '%s%s?%s' % (server_address, request, group)
        else:    
            if server_address in gvar['active_server_user_group'] and server_user in gvar['active_server_user_group'][server_address]:
                if request[-1] == '/':
                    _request = '%s%s?%s' % (server_address, request[:-1], gvar['active_server_user_group'][server_address][server_user])
                else:
                    _request = '%s%s?%s' % (server_address, request, gvar['active_server_user_group'][server_address][server_user])
            else:
                _request = '%s%s' % (server_address, request)

        if query_data:
            query_list = ['%s=%s' % (key, query_data[key]) for key in query_data]

            if _request[-1] == '/':
               _request = '%s?%s' % (_request[:-1], '&'.join(query_list))
            else:
               _request = '%s&%s' % (_request, '&'.join(query_list))
         
        _form_data = {}

    return _function, _request, _form_data

#-------------------------------------------------------------------------------

def ut_id(gvar, IDs):
    ids = IDs.split(',')
    return '%s-%s' % (gvar['user_settings']['server-user'], (',%s-' % gvar['user_settings']['server-user']).join(ids))
 
def condor_setup(gvar):
    '''Check that condor is installed and find and return the address of the unit-test server.
    Used only by database tests.'''
    import os.path
    import re
    import subprocess
    import yaml

    # Check that condor is installed so that we can submit a job to view using /job/list/
    requirements = ['condor_submit', 'condor_rm']
    for requirement in requirements:
        if subprocess.run(['which', requirement], stdout=subprocess.DEVNULL).returncode != 0:
            condor_error('{} is not installed'.format(requirement))
            return None

    # Get the address of the unit-test server
    try:
        YAML_PATH = os.path.expanduser('~/.csv2/unit-test/settings.yaml')
        with open(YAML_PATH) as yaml_file:
            server_address = yaml.safe_load(yaml_file)['server-address']
    except FileNotFoundError:
        condor_error('{} does not exist'.format(YAML_PATH))
        return None
    except yaml.YAMLError as err:
        condor_error('YAML encountered an error while parsing {}: {}'.format(YAML_PATH, err))
        return None
    if server_address.startswith('http'):
        return re.match(r'https?://(.*)', server_address)[1]
    else:
        condor_error('the server address in {} is \'{}\', which does not start with \'http\''.format(YAML_PATH, server_address))
        return None

def condor_error(gvar, err):
    '''Used only by database tests.'''
    print('\n\033[91mSkipping all database tests because {}.\033[0m'.format(err))
    gvar['ut_failed'] += 1

def main():
    return

if __name__ == "__main__":
    main()
