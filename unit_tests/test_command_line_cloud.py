from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"',
        ['cloudscheduler', 'cloud']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "cloud"',
        ['cloudscheduler', 'cloud', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"; use -h or -H for help.',
        ['cloudscheduler', 'cloud', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud".',
        ['cloudscheduler', 'cloud', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', '-H']
    )

    #### ADD ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'add', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'add', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'add', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud add".',
        ['cloudscheduler', 'cloud', 'add', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'add', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'add', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'add', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', r'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'invalid-unit-test',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV02', r'Data too long for column \'cloud_name\' at row 1',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'thiscloudnameistoolongtobeinserted',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'Invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test-',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid!unit?test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cores_ctl" must be a integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-vc', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "ram_ctl" must be a integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-vr', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-ce', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "vm_keep_alive" must be a integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-vka', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cp', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-ce', 'yes',
            '-vka', '10',
            '-vi', 'command-line-cloud-ten',
            '-vf', 'command-line-cloud-ten'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV02', 'Duplicate entry \\\'{}-{}\\\' for key \\\'PRIMARY\\\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cp', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10')
        ]
    )

    #### DELETE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'delete', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'delete', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud delete".',
        ['cloudscheduler', 'cloud', 'delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'delete', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'delete', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", cloud doesn\\\'t exist in group "{}".'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'delete', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc1')),
        ['cloudscheduler', 'cloud', 'delete', '-cn', ut_id(gvar, 'clc1'), '-Y']
    )

    #### LIST ####
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'list', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud list".',
        ['cloudscheduler', 'cloud', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'list', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-ok'],
        list='Clouds', columns=['Group', 'Cloud']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud list, table #1 columns: keys=group_name,cloud_name, columns=enabled,authurl,project_domain_name,project,user_domain_name,username,region,cloud_type,keyname,cores_ctl,cores_max,ram_ctl,ram_max,vm_flavor,vm_image,vm_keep_alive,cacertificate,metadata_names',
        ['cloudscheduler', 'cloud', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-NV'],
        list='Clouds', columns=['Cores', 'RAM', 'Group', 'Cloud', 'Enabled', 'URL', 'Project Domain', 'Project', 'User Domain', 'User', 'Region', 'Cloud Type', 'Keyname', 'Control', 'Max', 'VM', 'Flavor', 'Image', 'Keep Alive', 'CA Certificate', 'Metadata Filenames']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-V', 'enabled,authurl'],
        list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list'],
        list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-r'],
        list='Clouds', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-V', ''],
        list='Clouds', columns=['Cores', 'RAM', 'Group', 'Cloud', 'Enabled', 'URL', 'Project Domain', 'Project', 'User Domain', 'User', 'Region', 'Cloud Type', 'Keyname', 'Control', 'Max', 'VM', 'Flavor', 'Image', 'Keep Alive', 'CA Certificate', 'Metadata Filenames']
    )

    #### METADATA-DELETE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line:',
        ['cloudscheduler', 'cloud', 'metadata-delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-delete".',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot delete "{}::invalid-unit-test::invalid-unit-test", file doesn\\\'t exist.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-Y']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm1'), '-Y']
    )

    #### METADATA-EDIT ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-edit".',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'no value, neither default nor command line, for the following required parameters',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )
    
    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::invalid-unit-test::invalid-unit-test".'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::{}::invalid-unit-test".'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::invalid-unit-test::{}".'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test']
    )

    # The edit scripts in the next 4 tests will break easily as they rely on some system variables
    # execute_csv2_command(
    #     gvar, 0, None, 'completed, no changes.',
    #     ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', './editscript1']
    # )

    # execute_csv2_command(
    #     gvar, 0, None, 'successfully  updated.',
    #     ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', './editscript5']
    # )

    # execute_csv2_command(
    #     gvar, 0, None, 'successfully  updated.',
    #     ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript6']
    # )

    # execute_csv2_command(
    #     gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
    #     ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript7']
    # )

    #### METADATA-LIST ####
    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-list".',
        ['cloudscheduler', 'cloud', 'metadata-list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mn', ut_id(gvar, 'clm2')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-mlo\', \'invalid-unit-test\']',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mlo', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-ok'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-list, table #1 columns: keys=group_name,cloud_name,metadata_name, columns=enabled,priority,mime_type',
        ['cloudscheduler', 'cloud', 'metadata-list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-NV'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-V', 'endabled'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-r'],
        list='Clouds/Metadata', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-V', ''],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

    #### METADATA-LOAD ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-load']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-load', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['cloudscheduler', 'cloud', 'metadata-load', '-ok']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-load', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-load', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-load".',
        ['cloudscheduler', 'cloud', 'metadata-load', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-load', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-load', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-load', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-load', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The specified metadata file "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', 'invalid-unit-test', '-f', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'cloud name  "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', 'invalid-unit-test', '-f', 'ut.yaml', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV13', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'ut.yaml', '-mn', 'invalid-unit-test', '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV13', r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'ut.yaml', '-mn', 'invalid-unit-test', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV13', 'value specified for "priority" must be a integer value.',
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'ut.yaml', '-mn', 'invalid-unit-test', '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV13', 'value specified for "metadata (metadata_name)" is invalid - scanner error',
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'notyamlfile.txt', '-mn', 'invalid-unit-test.yaml']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm10')),
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'notyamlfile.txt', '-mn', ut_id(gvar, 'clm10')]
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm10.yaml')),
        ['cloudscheduler', 'cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'ut.yaml', '-mn', ut_id(gvar, 'clm10.yaml')]
    )

    #### METADATA-UPDATE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-project',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-update".',
        ['cloudscheduler', 'cloud', 'metadata-update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-update', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV30', 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-me', '0']
    )

    execute_csv2_command(
        gvar, 1, 'CV30', 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-me', '0']
    )

    execute_csv2_command(
        gvar, 1, 'CV29', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV29', r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV29', 'value specified for "priority" must be a integer value.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 'false']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mmt', 'ucernvm-config']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', '1']
    )

    #### STATUS ####
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'status', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'status', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'status', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud status".',
        ['cloudscheduler', 'cloud', 'status', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'status', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'status', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'status', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'status', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clc2'),
        ['cloudscheduler', 'cloud', 'status']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'status', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok'],
        list='Cloud status', columns=['Group', 'Cloud']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok'],
        list='Job status', columns=['Group']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud status, table #1 columns: keys=group_name, columns=Jobs,Idle,Running,Completed,Other\\ncloud status, table #2 columns: keys=group_name,cloud_name, columns=enabled,default_flavor,default_image,keep_alive,VMs,VMs_unregistered,VMs_running,VMs_retiring,VMs_manual,VMs_in_error,VMs_other,cores_max,cores_ctl,cores_idle,cores_native,ram_max,ram_ctl,ram_idle,ram_native,slots_max,slots_used,Foreign_VMs,cores_foreign,ram_foreign',
        ['cloudscheduler', 'cloud', 'status', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV'],
        list='Cloud status', columns=['Defaults', 'VMs', 'Cores', 'Group', 'Cloud', 'Enabled', 'Flavor', 'Image', 'Keep Alive', 'Total', 'Unregistered', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Setting', 'RAM', 'Slots', 'Foreign', 'Idle', 'Used']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV'],
        list='Job status', columns=['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', 'Jobs/enabled']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status'],
        list='Cloud status', columns=['Defaults', 'Group', 'Cloud', 'Enabled']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status'],
        list='Job status', columns=['Group', 'Jobs']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r'],
        list='Cloud status', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r'],
        list='Job status', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', '']
    )

    #### UPDATE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'update', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'update', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud update".',
        ['cloudscheduler', 'cloud', 'update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'update', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'update', '-cn', 'invalid-unit-test', '-ca', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'cloud', 'update', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "ram_ctl" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vr', 'invalid-unit-test'
        ]
    )
    
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "cores_ctl" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vc', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ce', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "vm_keep_alive" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vka', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-ce', 'no',
            '-vka', '10',
            '-vi', 'command-line-cloud-update',
            '-vf', 'command-line-cloud-update'
        ]
    )

if __name__ == "__main__":
    main(None)

