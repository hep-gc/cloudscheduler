from sys import argv
from cloudscheduler.unit_tests.unit_test_common import load_settings
from web_common import cleanup, set_setup_required

def main():
    for parameter in argv[1:]:
        if parameter == '--set-setup-required' or '-ssr':
            set_setup_required(True)
        elif parameter == '--cleanup' or '-c':
            cleanup(load_settings(web=True))

if __name__ == '__main__':
    main()
