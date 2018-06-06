def _caller():
    import inspect
    import os
    if inspect.stack()[-3][1] == '<string>':
        return os.path.basename(inspect.stack()[-4][1]).split('.')[0]
    return os.path.basename(inspect.stack()[-3][1]).split('.')[0]

def _execute_selections(gvar, request, expected_text, expected_values):
    from unit_test_common import _caller
    
    gvar['ut_count'] += 1
    if len(gvar['selections']) < 1 or str(gvar['ut_count']) in gvar['selections']:
        return True
    else:
        gvar['ut_skipped'] += 1
        print('%03d %s Skipping: %s, %s, %s' % (gvar['ut_count'], _caller(), request, expected_text, expected_values))
        return False
   
def execute_csv2_command(gvar, expected_rc, expected_ec, expected_text, cmd):

    from subprocess import Popen, PIPE
    from unit_test_common import _caller, _execute_selections

    if _execute_selections(gvar, cmd, expected_text, None):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        failed = False

        if expected_rc and expected_rc != p.returncode:
            failed = True

        error_code = str(stdout)[9:13]
        if expected_ec and expected_ec != error_code:
            failed = True

        if expected_text and str(stdout).find(expected_text) < 0:
            failed = True

        if failed:
            gvar['ut_failed'] += 1
            print('\n%03d %s Failed: %s, %s, %s, %s' % (gvar['ut_count'], _caller(), cmd, expected_rc, expected_ec, expected_text))
            print('    return code=%s' % p.returncode)
            print('    error code=%s' % error_code)
            print('    stdout=%s' % str(stdout))
            print('    stderr=%s\n' % str(stderr))

            return 1
        else:
            print('%03d %s OK: %s, %s, %s, %s' % (gvar['ut_count'], _caller(), cmd, expected_rc, expected_ec, expected_text))
            return 0
    else:
        return 0

def execute_csv2_request(gvar, expected_rc, expected_ec, expected_text, request, form_data={}, list=None, filter=None, values=None, server_user=None, server_pw=None):
    """
    Make RESTful requests via the _requests function and return the response. This function will
    obtain a CSRF (for POST requests) prior to making the atual request.
    """

    from unit_test_common import _caller, _execute_selections, _requests
    
    if _execute_selections(gvar, '%s %s' % (request, form_data), expected_text, values):
        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        # Obtain a CSRF as required.
        if form_data and not gvar['csrf']:
            response = _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)
        
        # Group change requested but the request is not a POST.
        elif not form_data and 'group' in gvar['command_args']:
            if not gvar['csrf']:
                response = _requests(gvar, '/settings/prepare/', server_user=server_user, server_pw=server_pw)
        
            response = _requests(gvar,
                    '/settings/prepare',
                    form_data = {
                        'group': gvar['command_args']['group'],
                        },
                    server_user=server_user,
                    server_pw=server_pw       
                ) 
            
        # Perform the callers request.
        response = _requests(gvar, request, form_data=form_data, server_user=server_user, server_pw=server_pw)

        if server_user and server_pw:
            gvar['csrf'] = None
            gvar['cookies'] = None

        if gvar['hidden']:
            return 0

        failed = False

        if expected_rc and expected_rc != response['response_code']:
            failed = True

        error_code = str(response['message'])[0:4]
        if expected_ec and expected_ec != error_code:
            failed = True

        if expected_text and str(response['message']).find(expected_text) < 0:
            failed = True

        if failed:
            gvar['ut_failed'] += 1
            print('\n%03d %s Failed: %s, %s, %s, %s, %s' % (gvar['ut_count'], _caller(), request, form_data, expected_rc, expected_ec, expected_text))
            print('    response code=%s' % response['response_code'])
            print('    error code=%s' % error_code)
            print('    message=%s\n' % response['message'])

            return 1
        else:
            if list and filter and values and list in response:
                failed = False
                for row in response[list]:
                    for key in filter:
                        if row[key] == filter[key]:
                            for key in values:
                                if row[key] != values[key]:
                                    failed = True
                                    print('\n%03d %s Failed: %s, %s, %s, %s' % (gvar['ut_count'], _caller(), request, list, filter, values))
                                    print('    row=%s\n' % row)

                if failed:
                    gvar['ut_failed'] += 1
                    return 1
                else:
                    print('%03d %s OK: request=%s, %s, %s, %s, %s' % (gvar['ut_count'], _caller(), request, form_data, list, filter, values))
                    return 0

            print('%03d %s OK: %s, %s, %s, %s, %s' % (gvar['ut_count'], _caller(), request, form_data, expected_rc, expected_ec, expected_text))
    else:
        return 0

def initialize_csv2_request(gvar, command, selections=None, hidden=False):
    import os
    import yaml

    if not os.path.isfile('%s/.csv2/unit-test/settings.yaml' % os.path.expanduser('~')):
        raise Exception('You must create a minimal cloudscheduler defaults for server "unit-test" containing the server address and user credentials.')

    gvar['command_args'] = {}
    gvar['cookies'] = None
    gvar['csrf'] = None
    gvar['server'] = 'unit-test'
    gvar['ut_count'] = 0
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
#       print(gvar['selections'])
    else:
        gvar['selections'] = []

    fd = open('%s/.csv2/unit-test/settings.yaml' % os.path.expanduser('~'))
    gvar['user_settings'] = yaml.load(fd.read())
    fd.close()

    return

def _requests(gvar, request, form_data={}, server_user=None, server_pw=None):
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

    if server_user and server_pw:
        _r = _function(
            '%s%s' % (gvar['user_settings']['server-address'], request),
            headers={'Accept': 'application/json', 'Referer': gvar['user_settings']['server-address']},
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
        if _r.status_code and _r.status_code == 401:   
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, unauthorized.' % (gvar['server'], _r.status_code)}
        elif _r.status_code and _r.status_code == 403:   
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s, forbidden.' % (gvar['server'], _r.status_code)}
        elif _r.status_code:   
            response = {'response_code': 2, 'message': 'server "%s", HTTP response code %s.' % (gvar['server'], _r.status_code)}
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

    if response['response_code'] == 0:
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

def ut_id(gvar, IDs):
    ids = IDs.split(',')
    return '%s-%s' % (gvar['user_settings']['server-user'], (',%s-' % gvar['user_settings']['server-user']).join(ids))

def main():
    return

if __name__ == "__main__":
    main()

