from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: AV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'alias', 'list')

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['alias', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', columns=['Group', 'Alias', 'Clouds']
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'alias list, 1. Aliases: keys=group_name,alias_name, columns=clouds\nalias list, 2. Clouds (optional): keys=group_name,cloud_name, columns=',
        ['alias', 'list', '--view-columns', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # --comma-separated-values (-CSV), --comma-separated-values-separator (-CSEP), --no-view (-NV), --only-keys (-ok), --rotate (-r), --view (-V), and --with (-w) are only tested here (because they work the same way for other table-printing commands).
    # 17 --view.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        # Excludes `group_name` and `clouds`, but `group_name` will appear anyways because it is a key.
        ['alias', 'list', '--view', 'alias_name', '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', columns=['Group', 'Alias']
    )

    # 18 --no-view. Temporarily override the view.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--no-view', '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', columns=['Group', 'Alias', 'Clouds']
    )

    # 19 --rotate.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--rotate', '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', columns=['Key', 'Value']
    )

    # 20 --comma-separated-values[-separator]. The view defined above should still have effect here.
    execute_csv2_command(
        gvar, 0, None, '{}.{}\n'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla1')),
        ['alias', 'list', '--comma-separated-values', '', '--comma-separated-values-separator', '.', '-su', ut_id(gvar, 'clu3')]
    )

    # 21 Remove the view.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--view', '', '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', columns=['Group', 'Alias', 'Clouds']
    )

    # 22 --only-keys.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--only-keys', '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', columns=['Group', 'Alias']
    )

    # 23 --with using table name.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--with', 'Clouds', '-su', ut_id(gvar, 'clu3')],
        # `columns` includes the columns from both tables.
        expected_list='Clouds', columns=['Group', 'Alias', 'Clouds', 'Cloud']
    )

    # 24 --with using table index.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--with', '2', '--view', 'group_name,alias_name/group_name','-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds', columns=['Group', 'Alias', 'Cloud']
    )

    # 25 --with using 'ALL'.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['alias', 'list', '--with', 'ALL', '--view', '', '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds', columns=['Group', 'Alias', 'Clouds', 'Cloud']
    )

if __name__ == '__main__':
    main(None)
