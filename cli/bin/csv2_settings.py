from csv2_common import check_keys, show_table

import json
import os
import shutil
import yaml

def delete(gvar):
    """
    Delete settings.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-s'], [], ['-y'])

    if os.path.isdir('%s/.csv2/%s' % (gvar['home_dir'], gvar['server'])):
        shutil.rmtree('%s/.csv2/%s' % (gvar['home_dir'], gvar['server']))
    else:
        print('Error: Settings for server "%s" do not exist.' % gvar['server'])
        exit(1)

def list(gvar):
    """
    List settings.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-s'])

    # Retrive all possible option names ordered by 'server' and then alphabetically.
    _keys = ['csv2-server']
    for _ix in range(len(gvar['command_keys'])):
        key = gvar['command_keys'][_ix][1][2:]
        if key not in _keys:
            _keys.append(key)
    _keys = [_keys[0]] + sorted(_keys[1:])

    # Build a queryset of the settings.
    _queryset = []
    for server in os.listdir('%s/.csv2' % gvar['home_dir']):
        server_path = '%s/.csv2//%s' % (gvar['home_dir'], server)
        if os.path.isdir(server_path):
            if 'csv2-server' not in gvar['command_args'] or server == gvar['command_args']['csv2-server']:
                _fd = open('%s/settings.yaml' % server_path)
                _settings = yaml.load(_fd.read())
                _fd.close()

                for key in sorted(_keys):
                    if key not in _settings:
                        if key == 'csv2-server':
                            _settings[key] = server
                
                _queryset.append({'fields': _settings})

    # Display results.
    show_table(gvar, _queryset, _keys, allow_null=False)

def set(gvar):
    """
    Modify settings.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-s'], [], ['*'])

    # Make the server directory, if necessary.
    if not os.path.exists('%s/.csv2/%s' % (gvar['home_dir'], gvar['server'])):
        os.makedirs('%s/.csv2/%s' % (gvar['home_dir'], gvar['server']), mode=0o700)  

    # Write the settings file.
    _fd = open('%s/.csv2/%s/settings.yaml' % (gvar['home_dir'], gvar['server']), 'w')
    _fd.write(yaml.dump(gvar['user_settings']))
    _fd.close()
    os.chmod('%s/.csv2/default/settings.yaml' % gvar['home_dir'], 0o600)

