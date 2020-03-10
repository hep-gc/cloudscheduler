def _caller():
    '''Determine which unit test has called my caller, which is probably a common function.'''
    import inspect
    import os
    if inspect.stack()[-3][1] == '<string>':
        return os.path.basename(inspect.stack()[-4][1]).split('.')[0]
    return os.path.basename(inspect.stack()[-3][1]).split('.')[0]

def _execute_selections(gvar, request, expected_text, expected_values):
    '''Tell execute_csv2_* whether or not it should run a particular test based on the user's selections.'''
    from unit_test_common import _caller
    
    gvar['ut_count'][0] += 1
    gvar['ut_count'][1] += 1
    if len(gvar['selections']) < 1 or str(gvar['ut_count'][0]) in gvar['selections']:
        return True
    else:
        gvar['ut_skipped'] += 1
        # print('%04d (%04d) %s Skipping: \'%s\', %s, %s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, repr(expected_text), expected_values))
        return False
   
def execute_csv2_command(gvar, expected_rc, expected_modid, expected_text, cmd, expected_list=None, columns=[], timeout=None):
    '''
    Execute a Cloudscheduler CLI command using subprocess and print a message explaining whether the output of the command was as expected.
    `cmd` (list, tuple, or other iterable of strs) contains the parameters to be given to the `cloudscheduler` command, e.g. `['alias', 'add', '-H']`. 'cloudscheduler' should be excluded, because it is automatically added at the beginning of the list.
    `expected_list` (str) is the title of a table that is expected to be in the output, e.g. 'Aliases'.
    `columns` (list of strs) contains the expected headers of the table specified by `expected_list`. These should be what is acutally displayed (e.g. 'Alias') not the name used in the CLI code (e.g. 'alias_name'). This list must contain all the expected headers, not just a subset. Ignored if `expected_list` is not specified.
    '''
    import subprocess
    from unit_test_common import _caller, _execute_selections
    import re

    if _execute_selections(gvar, cmd, expected_text, None):

        # Allow int and float values to be specified. (subprocess raises an exception if given ints or floats.)
        cmd = [str(c) for c in cmd]
        cmd.insert(0, 'cloudscheduler')
        # If the `-s` flag is not used tests will sometimes hang because cloudscheduler is waiting for a server web address (but this prompt is not visible to the tester).
        if '-s' not in cmd:
            cmd.extend(['-s', 'unit-test'])
        if '-spw' not in cmd:
            try:
                su_index = cmd.index('-su')
                if cmd[su_index + 1] == gvar['user_settings']['server-user']:
                    cmd.extend(['-spw', gvar['user_settings']['server-password']])
                else:
                    cmd.extend(['-spw', gvar['user_secret']])
            # `-su` has been omitted.
            except ValueError:
                # As a privileged user in a group, `clu4` is very often the server user, so it is useful to make it the default.
                cmd.extend(['-su', ut_id(gvar, 'clu4'), '-spw', gvar['user_secret']])
        
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()
            return_code = process.returncode
        except subprocess.TimeoutExpired as err:
            stdout = err.stdout.decode()
            stderr = err.stderr.decode()
            return_code = -1

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
        if expected_text and expected_text not in stdout:
            failed = True


        list_error = ''
        if not failed and expected_list:
            if '\n{}:'.format(expected_list) in stdout:
                stdout_lines = stdout.split('\n')
                # Columns are initially saved in a list rather than a set so that their order is preserved when checking values later.
                columns_ordered = []
                for row in stdout_lines:
                    if row.startswith('+ ') and row.endswith(' +'):
                        row_trimmed = row[2:-2].strip()
                        # Split on either '<zero or more spaces>|<zero or more spaces>' occurring one or more times, or two or more spaces in a row. Then filter out empty strings.
                        # The non-capturing nature of the `(?:)` parentheses prevents these groups from being added to the list produced by split().
                        columns_ordered.extend(filter(None, re.split(r'(?:\s*\|\s*)+|(?:\s{2,})', row_trimmed)))

                if columns:
                    columns_expected = set(columns)
                    columns_actual = set(columns_ordered)
                    if columns_expected != columns_actual:
                        failed = True
                        list_error = '\tActual columns found: {}\n \
                        \tColumns expected but not found: {}\n \
                        \tColumns not expected but found: {}\n'\
                        .format(columns_actual, columns_expected - columns_actual, columns_actual - columns_expected)

            # expected_list not in stdout
            else:
                failed = True
                list_error = 'Expected list \'{}\' not found'.format(expected_list)

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
    Make RESTful requests via the _requests function and print a message explaining whether the response was as expected.
    This function will obtain a CSRF (for POST requests) prior to making the actual request.
    `form_data` (dict) is send in the body of a POST request, while `query_data` (dict) is for adding parameters to the URL of a GET request.
    `expected_list` (str) is the name of a list to expect in the response.
    `list_filter` (dict) specifies key-value pairs that rows in the expected list must have to be rows of interest.
    `values` (dict) specifies key-value pairs that at least one row of interest is expected to have (for the test to succeed). The matching row may have other keys that are not in `values`.
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
        if form_data and not gvar['csrf']:
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
            modid = response['message'].replace('-', ' ').split(maxsplit=1)[0]
            if expected_modid and modid != expected_modid:
                failed = True

        if expected_text and (not response['message'] or expected_text not in response['message']):
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
        elif expected_list:
            if expected_list not in response:
                failed = True
                if not gvar['hidden']:
                    print('\n%04d (%04d) %s \033[91mFailed\033[0m: request=\'%s\', group=%s, expected_list=\'%s\', list_filter=%s, values=%s' % (gvar['ut_count'][0], gvar['ut_count'][1], _caller(), request, group, expected_list, list_filter, values))
                    print('\tNo list \'%s\' in response. The message from the server was: \'%s\'\n' % (expected_list, response['message']))
            # expected_list in response
            elif list_filter and values:
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
    # Attempt as a non-existent user.
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        request, group=group, server_user='invalid-unit-test'
    )
    # Attempt as a user who is not in any groups.
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(groupless_server_user),
        request, group=group, server_user=groupless_server_user
    )
    # Attempt with an incorrect password.
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        request, group=group, server_user=server_user, server_pw='invalid-unit-test'
    )
    # Attempt to change to a group that does not exist.
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        request, group='invalid-unit-test', server_user=server_user
    )
    # Attempt to change to a group that the user is not in.
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(userless_group),
        request, group=userless_group, server_user=server_user
    )

def parameters_requests(gvar, request, group, server_user, parameters):
    '''
    Execute requests with missing parameters and bad parameters.
    request is the location to make the requests too, e.g. `/alias/add/`.
    `parameters` is a dictionary in which each key is the name of a parameter (str), and each value is itself a dictionary, containing:
        'test_cases': A dictionary of test cases. Each key should be an invalid value for this parameter (which will be cast to a str). Each value should be the message to expect when this invalid value is sent in an otherwise valid request (str). Giving only invalid values in this dict means that none of the requests sent my this function should actually change anything on the server side (because they are all invalid in one way or another).
        'valid': A valid value for the parameter (which will be cast to a str). If the parameter is mandatory, this will be sent in requests that contain bad values for other parameters.
        [Optional: 'mandatory' (bool): Indicates whether this parameter must be provided in all requests. (In the terminology of the server code, this includes 'mandatory' parameters and 'required' parameters.) If not given, the parameter will be treated as optional.]
        [Optional: 'array_field' (bool): Indicates whether giving multiple values for this parameter using the `{'param.1': value1, 'param.2': value2}` syntax is allowed. If not given, this will be treated as False.]
    GET requests are assumed to be invalid.
    '''

    mandatory_params = {name: details['valid'] for name, details in parameters.items() if details.get('mandatory')}
    # Omit form_data entirely.
    execute_csv2_request(
        gvar, 1, None, 'invalid method "GET" specified.',
        request, group=group, server_user=server_user
    )
    # Give an invalid parameter.
    execute_csv2_request(
        # Response is sometimes 'request contained a bad parameter...' and sometimes 'request contained superfluous parameter...'.
        gvar, 1, None, 'parameter "invalid-unit-test".',
        request, group=group, form_data={'invalid-unit-test': 'invalid-unit-test', **mandatory_params}, server_user=server_user
    )

    for p_name, p_details in parameters.items():
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
                    optional_name, optional_value = next(((name, details['valid']) for name, details in parameters.items() if not details.get('mandatory')))
                    execute_csv2_request(
                        gvar, 1, None, 'request did not contain mandatory parameter "{}".'.format(p_name),
                        request, group=group, form_data={optional_name: optional_value}, server_user=server_user
                    )
                # We have exactly one parameter, and it is mandatory, so we cannot exclude it without getting 'invalid method' (which we already tested for).
                except StopIteration:
                    pass
        if p_details.get('array_field'):
            # Mix single and multiple parameter syntaxes.
            execute_csv2_request(
                gvar, 1, None, 'request contained parameter "{0}.1" and parameter "{0}".'.format(p_name),
                request, group=group, form_data={p_name: p_details['valid'], '{}.1'.format(p_name): p_details['valid'], **mandatory_params}, server_user=server_user
            )
        else:
            # Provide the parameter twice.
            execute_csv2_request(
                gvar, 1, None, 'parameter "{}.1".'.format(p_name),
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

def sanity_commands(gvar, obj, action=None):
    '''
    Perform sanity checks that should pass for all CLI tests.
    Group and user names are hardcoded because they are the same regardless of the obj / action pair.
    '''
    request = [obj, action] if action else [obj]

    # 01 Attempt as a non-existent user.
    execute_csv2_command(
        gvar, 1, None, 'HTTP response code 401, unauthorized.', request + ['-su', 'invalid-unit-test']
    )
    # 02 Attempt with a blank password.
    execute_csv2_command(
        gvar, 1, None, 'HTTP response code 401, unauthorized.', request + ['-su', ut_id(gvar, 'clu4'), '-spw', '']
    )
    # 03 Attempt with an incorrect password.
    execute_csv2_command(
        gvar, 1, None, 'HTTP response code 401, unauthorized.', request + ['-su', ut_id(gvar, 'clu4'), '-spw', 'invalid-unit-test']
    )
    # 04 Attempt as a user who is not in any groups.
    # execute_csv2_command inserts the correct password for us.
    execute_csv2_command(
        gvar, 1, 'SV', 'user "grobertson-clu1" is not a member of any group.', request + ['-su', ut_id(gvar, 'clu1')]
    )
    # 05 Attempt to change to a group that does not exist.
    # execute_csv2_command inserts `-su` (`clu4`) and `-spw` for us.
    execute_csv2_command(
        gvar, 1, 'SV', 'cannot switch to invalid group "invalid-unit-test".', request + ['-g', 'invalid-unit-test']
    )
    # 06 Attempt to change to a group that the user is not in.
    execute_csv2_command(
        gvar, 1, 'SV', 'cannot switch to invalid group "grobertson-clg2".', request + ['-g', ut_id(gvar, 'clg2'), '-su', ut_id(gvar, 'clu4')]
    )
    # 07 Fail to specify an action.
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "{}"'.format(obj), [obj]
    )
    # 08 Specify an invalid action.
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "{}"'.format(obj), [obj, 'invalid-unit-test']
    )
    # 09 Specify an unknown server.
    execute_csv2_command(
        gvar, -1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.', request + ['-s', 'invalid-unit-test'], timeout=8
    )
    # 10 Request short help.
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler {}".'.format(' '.join(request)), request + ['-h']
    )
    # 11 Request long help.
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual', request + ['-H']
    )
    # 12 Request version. `expected_rc` is not specified because it depends on whether the command has mandatory parameters.
    execute_csv2_command(
        gvar, None, None, 'Cloudscheduler CLI, Version:', request + ['-v']
    )
    # 13 Request exposed API.
    execute_csv2_command(
        gvar, None, None, 'Expose API requested:', request + ['-xA']
    )
    # 14 Give an invalid parameter.
    if action:
        execute_csv2_command(
            gvar, 1, None, 'Error: The following command line arguments were unrecognized: [\'--invalid-unit-test\', \'invalid-unit-test\']',
            request + ['--invalid-unit-test', 'invalid-unit-test']
        )


def parameters_commands(gvar, obj, action, group, server_user, parameters):
    '''
    Execute commands with missing parameters and bad parameters.
    The structure of `parameters` is similar to parameters_requests's `parameters`, with two exceptions:
        Parameter names should be given in the form they are given to the CLI, e.g. '-an' or '--alias-name' (not 'alias_name').
        'array_field' is ignored, because the CLI does not send multiple values for a parameter unless the server expects this.
    There is no way to specify parameters that do not take values (like `--rotate` for tables), so these must be tested separately.
    '''

    # `-spw` added by execute_csv2_command.
    base_cmd = [obj, action, '-su', server_user, '-g', group]
    for name, details in parameters.items():
        if details.get('mandatory'):
            base_cmd.extend([name, details['valid']])

    for p_name, p_details in parameters.items():
        if p_details.get('mandatory'):
            # Temporarily remove.
            p_index = base_cmd.index(p_name)
            base_cmd.pop(p_index)
            base_cmd.pop(p_index)
            # Execute a command without the current parameter.
            # The message is usually 'the following mandatory parameters must be specified...', but is not always (e.g. --text-editor in cli_cloud_metadata_edit).
            execute_csv2_command(gvar, 1, None, p_name, base_cmd.copy())
        # Give the parameter with invalid values.
        for value, message in p_details['test_cases'].items():
            execute_csv2_command(gvar, 1, None, message, base_cmd + [p_name, value])
        # Add the parameter back in if it was mandatory.
        if p_details.get('mandatory'):
            base_cmd.extend([p_name, p_details['valid']])

def table_commands(gvar, obj, action, group, server_user, table_headers):
    '''
    Test options that are common to all table-printing commands.
    `server_user` is assumed to have `gvar['user_secret']` as their password (which will be inserted by `execute_csv2_command()`).
    The `obj` / `action` pair must support the `--view_columns` option, and the output of `--view-columns` is assumed to be correct.
    `table_headers` is a dictionary in which each key is the name of a table to test, and its value is a complete list of all of the table's expected keys and columns (as strs). These must be in the order that they are listed when `--view-columns` is specified (keys being before columns). Optional tables can be omitted from testing by omitting them from `table_headers` (but default tables must be included). Any specifications of non-existent tables will be ignored.
    The options tested are `--comma-separated-values` (`-CSV`), `--comma-separated-values-separator` (`-CSEP`), `--no-view` (`-NV`), `--only-keys` (`-ok`), `--rotate` (`-r`), `--view` (`-V`), and `--with` (`-w`).
    'headers' is used to refer to keys and columns collectively.
    '''

    import subprocess
    import re

    tables = []
    all_headers = []
    default_headers = []
    default_keys = []

    process = subprocess.run(['cloudscheduler', obj, action, '--view-columns', '-g', group, '-su', server_user, '-spw', gvar['user_secret']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = process.stdout.decode()
    # Omit the last char, which should be '\n'.
    stdout_lines = stdout[:-1].split('\n')
    stderr = process.stderr.decode()
    for line in stdout_lines:
        if stderr:
            print('Error retrieving table metadata: {}'.format(stderr))
            exit(1)
        try:
            name, optional_str, keys_str, columns_str = re.search(r'(\w+)( \(optional\))?: keys=([\w,]*?), columns=([\w,]*)', line).groups()
        except AttributeError:
            print('Error parsing `--view-columns` output. The specified obj / action pair might not support this option, or the regex in table_commands() may need to be updated to match a change in the format of the output produced by specifying `--view-columns`. stdout was:\n{}'.format(stdout))
        display_headers = table_headers.get(name)
        if display_headers:
            keys = keys_str.split(',') if keys_str else []
            optional = bool(optional_str)
            tables.append((name, optional, keys, columns_str.split(',') if columns_str else [], display_headers))
            all_headers.extend(display_headers)
            # If boolean is given and True.
            if not optional:
                default_headers.extend(display_headers)
                default_keys.extend(display_headers[:len(keys)])

    user_group_message = 'Server: unit-test, Active User: {}, Active Group: {}'.format(server_user, group)
    for i, table in enumerate(tables):
        name, optional, keys, columns, display_headers = table
        base_cmd = [obj, action, '-g', group, '-su', server_user]
        headers = display_headers + default_headers if optional else display_headers

        if optional:
            # --with using table name.
            execute_csv2_command(
                gvar, 0, None, user_group_message,
                base_cmd + ['--with', name],
                expected_list=name, columns=headers
            )

            # --with using table index.
            execute_csv2_command(
                gvar, 0, None, user_group_message,
                base_cmd + ['--with', i + 1],
                expected_list=name, columns=headers
            )

            # --with using 'ALL'.
            execute_csv2_command(
                gvar, 0, None, user_group_message,
                base_cmd + ['--with', 'ALL', '--view', ''],
                # All columns in all tables.
                expected_list=name, columns=all_headers
            )

            base_cmd.extend(['--with', name])

        view_headers = (display_headers[:-1] if columns else display_headers) + (default_headers if optional else [])
        # --view.
        execute_csv2_command(
            gvar, 0, None, user_group_message,
            base_cmd + ['--view', ('/' * i) + (','.join(columns[:-1]) if len(columns) > 1 else keys[0])],
            expected_list=name, columns=view_headers
        )

        # --no-view. Temporarily override the view.
        execute_csv2_command(
            gvar, 0, None, user_group_message, base_cmd + ['--no-view'],
            expected_list=name, columns=headers
        )

        # --rotate.
        execute_csv2_command(
            gvar, 0, None, user_group_message, base_cmd + ['--rotate'],
            expected_list=name, columns=['Key', 'Value']
        )

        # --comma-separated-values[-separator].
        execute_csv2_command(
            gvar, 0, None, '.',
            base_cmd + ['--comma-separated-values', '', '--comma-separated-values-separator', '.']
        )

        # The view defined above should still have effect here.
        execute_csv2_command(
            # Check that specifying `--with` for a table that is already included does not cause problems.
            gvar, 0, None, user_group_message, base_cmd + ['--with', name],
            expected_list=name, columns=view_headers
        )

        # Remove the view.
        execute_csv2_command(
            gvar, 0, None, user_group_message,
            base_cmd + ['--view', '', '-su', server_user],
            expected_list=name, columns=headers
        )

        # --only-keys.
        execute_csv2_command(
            gvar, 0, None, user_group_message, base_cmd + ['--only-keys'],
            expected_list=name, columns=display_headers[:len(keys)] + default_keys
        )


def generate_secret():
    '''Generate a new, pseudorandom password to use as the password for test users.'''
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

def initialize_csv2_request(gvar, selections=None, hidden=False):
    '''Setup gvar before running unit tests.'''
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
        for sel in tmp_selections:
            bounds = sel.split('-')
            if len(bounds) == 2:
                for i in range(int(bounds[0]), int(bounds[1]) + 1):
                    gvar['selections'].append(str(i))
            else:
                gvar['selections'].append(sel)
    else:
        gvar['selections'] = []

    try:
        with open(os.path.expanduser('~/.csv2/unit-test/settings.yaml')) as settings_file:
            gvar['user_settings'] = yaml.full_load(settings_file.read())
    except FileNotFoundError:
        raise Exception('You must create a minimal cloudscheduler defaults for server "unit-test" containing the server address and user credentials.')

    gvar['fqdn'] = re.sub(r'^https?://', '', gvar['user_settings']['server-address'], count=1)

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
        os.makedirs(os.path.dirname(CREDENTIALS_PATH), mode=0o700, exist_ok=True)
        with open(os.open(CREDENTIALS_PATH, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as credentials_file:
            credentials_file.write(yaml.dump({'user_secret': gvar['user_secret'], 'cloud_credentials': gvar['cloud_credentials']}))
    except yaml.YAMLError as err:
        print('YAML encountered an error while parsing {}: {}'.format(CREDENTIALS_PATH, err))

    return

def _requests(gvar, request, group=None, form_data={}, query_data={}, server_user=None, server_pw=None, html=False):
    """
    Make a RESTful request and return the response.
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
    Add controls (CSRF, group, etc.) to a Python request.
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
    '''Format the test runner's username with IDs (str) to create a unique ID for a test object.'''
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
