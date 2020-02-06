from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import group_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    # 01
    execute_csv2_request(
        gvar, 0, None, None,
        '/accounting/apel', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu2')
    )

if __name__ == '__main__':
    main(None)
