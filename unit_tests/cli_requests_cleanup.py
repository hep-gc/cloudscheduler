from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'clg1')}
    )

    # 02
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'clg2')}
    )

    # 03
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'clg3')}
    )

    # 04
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'clg4')}
    )

    # 05
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'clg10')}
    )

    # 06
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu1')}
    )

    # 07
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu2')}
    )

    # 08
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu3')}
    )

    # 09
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu4')}
    )

    # 10
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu5')}
    )

    # 11
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu6')}
    )

    # 12
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu7')}
    )

    # 13
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu10')}
    )

    # 14
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'clu11')}
    )

if __name__ == "__main__":
    main(None)
