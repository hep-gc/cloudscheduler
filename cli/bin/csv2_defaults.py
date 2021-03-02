from csv2_common import check_keys, show_table, yaml_full_load

import json
import os
import shutil
import yaml

def delete(gvar):
    """
    Delete settings.
    """

    mandatory = ['-s']
    required = []
    optional = ['-H', '-h', '-v', '-Y']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional, requires_server=False)

    if os.path.isdir('%s/.csv2/%s' % (gvar['home_dir'], gvar['pid_defaults']['server'])):
        # Confirm settings delete.
        if not gvar['user_settings']['yes']:
            print('Are you sure you want to delete the settings for server "%s"? (yes|..)' % gvar['pid_defaults']['server'])
            _reply = input()
            if _reply != 'yes':
                print('%s settings delete "%" cancelled.' % gvar['pid_defaults']['server'] % gvar['command_name'])
                exit(0)

        shutil.rmtree('%s/.csv2/%s' % (gvar['home_dir'], gvar['pid_defaults']['server']))
    else:
        print('Error: Settings for server "%s" do not exist.' % gvar['pid_defaults']['server'])
        exit(1)

def list(gvar):
    """
    List settings.
    """

    mandatory = []
    required = []
    optional = ['-CSV', '-CSEP', '-H', '-h', '-NV', '-ok', '-r', '-s', '-v', '-V', '-VC', '-w']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional, requires_server=False)

    # Retrive all possible option names ordered by 'server' and then alphabetically.
    if os.path.isfile('%s/.csv2/default_server' % gvar['home_dir']):
        fd = open('%s/.csv2/default_server' % gvar['home_dir'])
        default_server = fd.read()
        fd.close
        report_title = 'Defaults (default server = %s)' % default_server
    else:
        report_title = 'Defaults'

    # Retrive all possible option names ordered by 'server' and then alphabetically.
    _keys = ['server,k']
    for _ix in range(len(gvar['command_keys'])):
        key = gvar['command_keys'][_ix][1][2:]
        if key not in _keys and '%s,k' % key not in _keys:
            _keys.append(key)
    _keys = [_keys[0]] + sorted(_keys[1:])

    # Build a queryset of the settings.
    _queryset = []
    for server in os.listdir('%s/.csv2' % gvar['home_dir']):
        if server[0] == '.':
            continue

        server_path = '%s/.csv2//%s' % (gvar['home_dir'], server)
        if os.path.isdir(server_path):
            if 'server' not in gvar['command_args'] or server == gvar['command_args']['server']:
                _fd = open('%s/settings.yaml' % server_path)
                _settings = yaml_full_load(_fd.read())
                _fd.close()

                for key in sorted(_keys):
                    if key not in _settings:
                        if key == 'server':
                            _settings[key] = server
                
                _queryset.append({'fields': _settings})

    # Display results.
    show_table(gvar, _queryset, _keys, allow_null=False, title=report_title)

def set(gvar):
    """
    Modify settings.
    """

    mandatory = ['-s']
    required = []
    optional = ['*']
    not_optional = ['-br']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional, not_optional=not_optional, requires_server=False)

    # If this is the user's first server, make it the default.
    if len(os.listdir('%s/.csv2' % gvar['home_dir'])) < 1:
        gvar['set_default_server'] = True

    # Make the server directory, if necessary.
    if not os.path.exists('%s/.csv2/%s' % (gvar['home_dir'], gvar['pid_defaults']['server'])):
        os.makedirs('%s/.csv2/%s' % (gvar['home_dir'], gvar['pid_defaults']['server']), mode=0o700)  

    # Write the default server file.
    if gvar['set_default_server']:
        _fd = open('%s/.csv2/default_server' % gvar['home_dir'], 'w')
        _fd.write(gvar['pid_defaults']['server'])
        _fd.close()
        os.chmod('%s/.csv2/default_server' % gvar['home_dir'], 0o600)

    # Write the settings file.
    _fd = open('%s/.csv2/%s/settings.yaml' % (gvar['home_dir'], gvar['pid_defaults']['server']), 'w')
    _fd.write(yaml.dump(gvar['user_settings']))
    _fd.close()
    os.chmod('%s/.csv2/%s/settings.yaml' % (gvar['home_dir'], gvar['pid_defaults']['server']), 0o600)

