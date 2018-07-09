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
        gvar, 1, None, 'No action specified for object "group"',
        ['cloudscheduler', 'group']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "group"',
        ['cloudscheduler', 'group', 'invalid-unit-test']
    )

    #### ADD ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'add', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'add', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', '', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "condor_central_manager" must not be an empty string.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test', '-gm', '']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'Invalid-Unit-Test', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test-', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid!unit?test', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV02', r'Data too long for column \'group_name\' at row 1',
        ['cloudscheduler', 'group', 'add', '-gn', 'thisisagroupnametoolongtobeinsertedintothedatabasethisisagroupnametoolongtobeinsertedintothedatabasethisisagroupnametoolongtobein', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg10')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg10'), '-gm', 'command-line-group-10']
    )

    execute_csv2_command(
        gvar, 1, 'GV97', 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test', '-gm', 'invalid-unit-test', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV03', r'Duplicate entry \'invalid-unit-test\' for key \'PRIMARY\'',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test', '-gm', 'invalid-unit-test', '-un', ut_id(gvar, 'clu3,clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg11')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg11'), '-gm', 'command-line-group-11', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {}'.format(ut_id(gvar, 'clg1,clg11')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    #### DEFAULTS ####
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, '')[:-1]),
        ['cloudscheduler', 'group', 'defaults']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'defaults', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'defaults', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'defaults', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'GV06', 'value specified for "job_cpus" must be a integer value.',
        ['cloudscheduler', 'group', 'defaults', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV06', 'value specified for "job_disk" must be a integer value.',
        ['cloudscheduler', 'group', 'defaults', '-jd', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-jed\', \'invalid-unit-test\']',
        ['cloudscheduler', 'group', 'defaults', '-jed', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV06', 'value specified for "job_ram" must be a integer value.',
        ['cloudscheduler', 'group', 'defaults', '-jr', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV06', 'value specified for "job_swap" must be a integer value.',
        ['cloudscheduler', 'group', 'defaults', '-js', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group defaults "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'defaults', '-jc', '1', '-jd', '1', '-jed', '1', '-jr', '1', '-js', '1']
    )

    #### DELETE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, r'cannot delete "", group doesn\'t exist.',
        ['cloudscheduler', 'group', 'delete', '-gn', '']
    )

    execute_csv2_command(
        gvar, 1, None, r'cannot delete "invalid-unit-test", group doesn\'t exist.',
        ['cloudscheduler', 'group', 'delete', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg3')),
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg4')),
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg4')]
    )

    #### LIST ####
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'group', 'list', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list', '-ok']
    )

    #### METADATA-DELETE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'metadata-delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-delete', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'GV33', 'the request did not match any rows.',
        ['cloudscheduler', 'group', 'metadata-delete', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group metadata file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        ['cloudscheduler', 'group', 'metadata-delete', '-mn', ut_id(gvar, 'clm1')]
    )

    #### METADATA-EDIT ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-edit']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'metadata-edit', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-edit', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-edit', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'no value, neither default nor command line, for the following required parameters',
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'file "{}::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test']
    )

    # The edit scripts in the next 4 tests will break easily as they rely on some system variables
    execute_csv2_command(
        gvar, 0, None, '"{}::{}" completed, no changes.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2'), '-te', './editscript1']
    )

    execute_csv2_command(
        gvar, 0, None, '"{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2'), '-te', './editscript2']
    )

    execute_csv2_command(
        gvar, 0, None, '"{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2.yaml')),
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript3']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript4']
    )

    #### METADATA-LIST ####
    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'group', 'metadata-list']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'metadata-list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-cn\', \'invalid-unit-test\']',
        ['cloudscheduler', 'group', 'metadata-list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-gn\', \'invalid-unit-test\']',
        ['cloudscheduler', 'group', 'metadata-list', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'group', 'metadata-list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'group', 'metadata-list', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'group', 'metadata-list', '-mn', ut_id(gvar, 'clm2')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'group', 'metadata-list', '-ok']
    )

    #### METADATA-LOAD ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-load']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'metadata-load', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-load', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-load', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The specified metadata file "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV27', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', 'invalid-unit-test', '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV27', r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', 'invalid-unit-test', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV27', 'value specified for "priority" must be a integer value.',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', 'invalid-unit-test', '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV27', 'value specified for "metadata (metadata_name)" is invalid - scanner error',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'notyamlfile.txt', '-mn', 'invalid-unit-test.yaml']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10')),
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'notyamlfile.txt', '-mn', ut_id(gvar, 'clm10')]
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10.yaml')),
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'clm10.yaml')]
    )

    #### METADATA-UPDATE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'metadata-update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'group', 'metadata-update', '-mn', 'invalid-unit-test', '-me', '0']
    )

    execute_csv2_command(
        gvar, 1, None, 'value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'group', 'metadata-update', '-mn', 'invalid-unit-test', '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'group', 'metadata-update', '-mn', 'invalid-unit-test', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'value specified for "priority" must be a integer value.',
        ['cloudscheduler', 'group', 'metadata-update', '-mn', 'invalid-unit-test', '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'group', 'metadata-update', '-mn', ut_id(gvar, 'clm2')]
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'group', 'metadata-update', '-mn', ut_id(gvar, 'clm2'), '-me', 'false']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'group', 'metadata-update', '-mn', ut_id(gvar, 'clm2'), '-mmt', 'ucernvm-config']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'group', 'metadata-update', '-mn', ut_id(gvar, 'clm2'), '-mp', '1']
    )

    #### UPDATE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to update.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV21', 'the request did not match any rows.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, r'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'duplicate entry',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-gm', 'unit-test-group-update.ca']
    )

    execute_csv2_command(
        gvar, 0, None, 'unit-test-group-update.ca',
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'delete']
    )

    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'delete']
    )

    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )
            
if __name__ == "__main__":
    main(None)

