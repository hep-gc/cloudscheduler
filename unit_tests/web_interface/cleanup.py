from cloudscheduler.unit_tests.unit_test_common import load_settings
from web_common import cleanup

def main():
    cleanup(load_settings())

if __name__ == '__main__':
    main()
