def _caller():
    import inspect
    import os
    if inspect.stack()[-3][1] == '<string>':
        return os.path.basename(inspect.stack()[-4][1]).split('.')[0]
    return os.path.basename(inspect.stack()[-3][1]).split('.')[0]

def decode_bytes(obj):
    if isinstance(obj, str):
        return obj

    return obj.decode('utf-8')

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
   
def execute_csv2_command(gvar, expected_rc, expected_modid, expected_text, cmd, expected_list=None, columns=None):

    from subprocess import Popen, PIPE
    from unit_test_common import _caller, _execute_selections

    if _execute_selections(gvar, cmd, expected_text, None):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        failed = False

        if expected_rc and expected_rc != p.returncode:
            failed = True

        if p.returncode == 0 or not expected_modid:
            modid = expected_modid
        else:
            modid = decode_bytes(stdout).replace('-', ' ').split()[1]
            if expected_modid and modid != expected_modid:
                failed = True

        list_error = ''
        if expected_list:
            list_index = str(stdout).find(expected_list)
            row_index = str(stdout).find('Rows:', list_index)
            if list_index < 0:
                failed = True
                list_error = 'list \'{}\' not found'.format(expected_list)
            elif columns:
                columns_found = []
                rows = decode_bytes(stdout).split('\n')
                for row in rows:
                    if len(row) > 1 and row[:2] == '+ ':
                        columns_found += row[2:-2].replace('|', ' ').split()
                if set(columns) != set(columns_found):
                    failed = True
                    list_error = 'columns expected:{}\n\t\tcolumns found:{}'.format(columns, columns_found)

        if expected_text and str(stdout).find(expected_text) < 0:
            failed = True

        if failed:
            gvar['ut_failed'] += 1
            if not gvar['hidden']:
                # repr() is used because it puts quotes around strings *unless* they are None.
                print('\n%04d (%04d) %s \033[91mFailed\033[0m: expected_rc=%s, expected_modid=%s, expected_text=%s, cmd=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), expected_rc, repr(expected_modid), repr(expected_text), cmd))
                print('    return code=%s' % p.returncode)
                print('    module ID=%s' % repr(modid))
                print('    stdout=%s' % str(stdout))
                print('    stderr=%s' % str(stderr))
                if list_error:
                    print('\tlist_error={}'.format(list_error))
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
    obtain a CSRF (for POST requests) prior to making the atual request.
    """

    from unit_test_common import _caller, _execute_selections, _requests

    if _execute_selections(gvar, 'req=%s, group=%s, form=%s, query=%s' % (request, group, form_data, query_data), expected_text, values):
        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        # For POST requests (form_data is not null), ensure we have CSRF and insert
        # the current active group.
        if form_data:
            if not gvar['csrf']:
                response = _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)

        # Perform the callers request.
        response = _requests(gvar, request, group, form_data=form_data, query_data=query_data, server_user=server_user, server_pw=server_pw, html=html)

        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        failed = False

        if expected_rc and expected_rc != response['response_code']:
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
                            print('\tRow %s:' % row_index)
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

def initialize_csv2_request(gvar, command, selections=None, hidden=False):
    import os
    import yaml

    if not os.path.isfile('%s/.csv2/unit-test/settings.yaml' % os.path.expanduser('~')):
        raise Exception('You must create a minimal cloudscheduler defaults for server "unit-test" containing the server address and user credentials.')

    gvar['active_server_user_group'] = {}
    gvar['command_args'] = {}
    gvar['cookies'] = None
    gvar['csrf'] = None
    gvar['server'] = 'unit-test'
    gvar['ut_count'] = [0,0]
    gvar['ut_failed'] = 0
    gvar['ut_skipped'] = 0
    gvar['ut_dir'] = os.path.dirname(os.path.abspath(command))
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

    fd = open('%s/.csv2/unit-test/settings.yaml' % os.path.expanduser('~'))
    gvar['user_settings'] = yaml.full_load(fd.read())
    fd.close()

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

#   if form_data:
#       _function = py_requests.post
#       _form_data = {**form_data, **{'csrfmiddlewaretoken': gvar['csrf']}}
#   else:
#       _function = py_requests.get
#       _form_data = {}
    
    if html:
        headers={'Referer': gvar['user_settings']['server-address']}
    else:
        headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']}

    if server_user and server_pw:
        _function, _request, _form_data = _requests_insert_controls(gvar, request, group, form_data, query_data, gvar['user_settings']['server-address'], server_user)

        _r = _function(
            _request,
#           '%s%s' % (gvar['user_settings']['server-address'], request),
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
#           '%s%s' % (gvar['user_settings']['server-address'], request),
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
#           '%s%s' % (gvar['user_settings']['server-address'], request),
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

def ut_id(gvar, IDs):
    ids = IDs.split(',')
    return '%s-%s' % (gvar['user_settings']['server-user'], (',%s-' % gvar['user_settings']['server-user']).join(ids))

def main():
    return

if __name__ == "__main__":
    main()

