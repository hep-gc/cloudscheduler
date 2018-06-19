from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 1, 'UV13', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/list/', form_data={'group': 'invalid-unit-test'},
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={}
        )

if __name__ == "__main__":
    main(None)