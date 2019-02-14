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
        print('%04d (%04d) %s Skipping: %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, expected_text, expected_values))
        return False
   
def execute_csv2_command(gvar, expected_rc, expected_ec, expected_text, cmd, list=None, columns=None):

    from subprocess import Popen, PIPE
    from unit_test_common import _caller, _execute_selections

    if _execute_selections(gvar, cmd, expected_text, None):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        failed = False

        if (expected_rc != None) and (expected_rc != p.returncode):
            failed = True

        error_code = str(stdout)[9:13]
        if expected_ec and expected_ec != error_code:
            failed = True

        list_error = ''
        if list:
            list_index = str(stdout).find(list)
            row_index = str(stdout).find('Rows:', list_index)
            if list_index < 0:
                failed = True
                list_error = 'list "{}" not found'.format(list)
            elif columns:
                rows = str(stdout)[list_index:row_index].strip().split('\\n')
                column_list = []
                for row in rows:
                    if row.startswith('+ '):
                        for column_name in row[1:-1].split('|'):
                            for col_name in column_name.strip().split('  '):
                                if col_name.strip() and (col_name.strip() not in column_list):
                                    column_list.append(col_name.strip())
                if set(columns) != set(column_list):
                    failed = True
                    list_error = 'columns expected:{}\n\t\tcolumns found:{}'.format(columns, column_list)

        if expected_text and str(stdout).find(expected_text) < 0:
            failed = True

        if failed:
            gvar['ut_failed'] += 1
            if not gvar['hidden']:
                print('\n%04d (%04d) %s Failed: %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), cmd, expected_rc, expected_ec, expected_text))
                print('    return code=%s' % p.returncode)
                print('    error code=%s' % error_code)
                print('    stdout=%s' % str(stdout))
                print('    stderr=%s' % str(stderr))
                if list_error:
                    print('\tlist_error={}'.format(list_error))
                print('')

            return 1
        else:
            if not gvar['hidden']:
                print('%04d (%04d) %s OK: %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), cmd, expected_rc, expected_ec, expected_text))
            return 0
    else:
        return 0

def execute_csv2_request(gvar, expected_rc, expected_ec, expected_text, request, form_data={}, list=None, filter=None, values=None, server_user=None, server_pw=None, html=False):
    """
    Make RESTful requests via the _requests function and return the response. This function will
    obtain a CSRF (for POST requests) prior to making the atual request.
    """

    from unit_test_common import _caller, _execute_selections, _requests

    # Retrieve the current user.
    if server_user and server_pw:
        current_user = server_user

    elif 'server-grid-cert' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-cert']) and \
        'server-grid-key' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-key']):
        current_user = gvar['user_settings']['server-grid-cert']

    elif 'server-user' in gvar['user_settings']:
        current_user = gvar['user_settings']['server-user']
    
    if current_user not in gvar['active_user_group']:
        gvar['active_user_group'][current_user] = '-'

    if current_user not in gvar['active_user_group']:
        gvar['active_user_group'][current_user] = '-'

    if _execute_selections(gvar, '%s %s' % (request, form_data), expected_text, values):
        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        # For POST requests (form_data is not null), ensure we have CSRF and insert
        # the current active group.
        if form_data:
            if not gvar['csrf']:
                response = _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)

            group_request = request
            group_form_data = form_data

            if 'group' not in form_data and gvar['active_user_group'][current_user] != '-':
                group_form_data['group'] = gvar['active_user_group'][current_user]
        
        # For GET requests (form_data is null), insert the current active group.
        else:
            group_form_data = {}
            if gvar['active_user_group'][current_user] != '-':
                if request[-1] == '/':
                    group_request = '%s?%s' % (request[:-1], gvar['active_user_group'][current_user])
                else:
                    group_request = '%s?%s' % (request, gvar['active_user_group'][current_user])
            else:
                group_request = request

###########################################################################################################################
#       # Obtain a CSRF as required.
#       if form_data and not gvar['csrf']:
#           response = _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)
#       
#       # Group change requested but the request is not a POST.
#       elif not form_data and 'group' in gvar['command_args']:
#           if not gvar['csrf']:
#               response = _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)
#       
#           response = _requests(gvar,
#                   '/settings/prepare/',
#                   form_data = {
#                       'group': gvar['command_args']['group'],
#                       },
#                   server_user=server_user,
#                   server_pw=server_pw       
#               ) 
###########################################################################################################################

        # Perform the callers request.
        response = _requests(gvar, group_request, form_data=group_form_data, server_user=server_user, server_pw=server_pw, html=html)

        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        failed = False

        if (expected_rc != None) and (expected_rc != response['response_code']):
            failed = True

        error_code = str(response['message'])[0:4]
        if expected_ec and expected_ec != error_code:
            failed = True

        if expected_text and str(response['message']).find(expected_text) < 0:
            failed = True

        if failed:
            gvar['ut_failed'] += 1

            if not gvar['hidden']:
                print('\n%04d (%04d) %s Failed: %s, %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, form_data, expected_rc, expected_ec, expected_text))
                if server_user in gvar['active_user_group']:
                    print('    server=%s, user=%s, group=%s' % (gvar['server'], server_user, gvar['active_user_group'][server_user]))
                else:
                    print('    server=%s, user=%s, group=None' % (gvar['server'], server_user))
                print('    response code=%s' % response['response_code'])
                print('    error code=%s' % error_code)
                print('    message=%s\n' % response['message'])

            return 1
        else:
            if list and filter and values and (list not in response):
                failed = True
                if not gvar['hidden']:
                    print('\n%04d (%04d) %s Failed: %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, list, filter, values))
                    print('\tNo list "{}" in response.\n'.format(list))
            if list and filter and values and list in response:
                found = False
                for row in response[list]:
                    match = True
                    for key in filter:
                        if (key not in row.keys()) or (filter[key] != row[key]):
                            match = False
                            break

                    if match:
                        found = True
                        failed = False
                        for key in values:
                            if (key not in row.keys()) or (values[key] != row[key]):
                                failed = True
                                if not gvar['hidden']:
                                    print('\n%04d (%04d) %s Row Check: %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, list, filter, values))
                                    print('\trow=%s\n' % row)
                                break
                        if not failed:
                            break

                if not found:
                    failed = True
                    if not gvar['hidden']:
                        print('\n%04d (%04d) %s Failed: %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, list, filter, values))
                        print('\tFilter didn\'t match any rows\n')

                if failed:
                    gvar['ut_failed'] += 1
                    return 1
                else:
                    if not gvar['hidden']:
                        print('%04d (%04d) %s OK: request=%s, %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, form_data, list, filter, values))
                    return 0

            if not gvar['hidden']:
                print('%04d (%04d) %s OK: %s, %s, %s, %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, form_data, expected_rc, expected_ec, expected_text))
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

    gvar['active_user_group'] = {}
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
    gvar['user_settings'] = yaml.load(fd.read())
    fd.close()

    return

def _requests(gvar, request, form_data={}, server_user=None, server_pw=None, html=False):
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

    if html:
        headers={'Referer': gvar['user_settings']['server-address']}
    else:
        headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']}

    if server_user and server_pw:
        _r = _function(
            '%s%s' % (gvar['user_settings']['server-address'], request),
            headers=headers,
            auth=(server_user, server_pw),
            data=_form_data,
            cookies=gvar['cookies'] 
            )

    elif 'server-grid-cert' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-cert']) and \
        'server-grid-key' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-key']):
        _r = _function(
            '%s%s' % (gvar['user_settings']['server-address'], request),
            headers=headers,
            cert=(gvar['user_settings']['server-grid-cert'], gvar['user_settings']['server-grid-key']),
            data=_form_data,
            cookies=gvar['cookies']
            )

    elif 'server-user' in gvar['user_settings']:
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '-':
            gvar['user_settings']['server-password'] = getpass('Enter your csv2 password for server "%s": ' % gvar['server'])
        _r = _function(
            '%s%s' % (gvar['user_settings']['server-address'], request),
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

    if response['response_code'] == 0:
        if 'Set-Cookie' in _r.headers:
            new_csrf = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]
            if new_csrf[1]:
                gvar['cookies'] = _r.cookies
                gvar['csrf'] = _r.headers['Set-Cookie'].translate(EXTRACT_CSRF).split()[1]

        if 'active_user' in response:
            if 'active_group' in response:
                gvar['active_user_group'][response['active_user']] = response['active_group']
            else:
                gvar['active_user_group'][response['active_user']] = '-'

        if 'super_user' in response:
            gvar['super_user'] = response['super_user']

    return response

def ut_id(gvar, IDs):
    ids = IDs.split(',')
    return '%s-%s' % (gvar['user_settings']['server-user'], (',%s-' % gvar['user_settings']['server-user']).join(ids))

def main():
    return

if __name__ == "__main__":
    main()

