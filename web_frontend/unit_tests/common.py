import os
import yaml

CONFIG_FILE = 'config.yaml'

def setup():
    config = _get_config()
    if config['setup_required']:
        # TODO: Tear down old test objects and recreate them.
        pass

    return config['server_address']

def _get_config():
    try:
        with open(CONFIG_FILE) as config_file:
            config = yaml.safe_load(config_file)
    except FileNotFoundError:
        # Create the config file with appropriate permissions.
        print('Creating configuration file at {}.'.format(CONFIG_FILE))
        config = {'server_address': input('Enter the address of the server to test: '), 'setup_required': True}
        os.umask(0)
        os.makedirs(os.path.dirname(CONFIG_FILE), mode=0o700, exist_ok=True)
        with open(os.open(CONFIG_FILE, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as credentials_file:
            config_file.write(yaml.dump(config))
    except yaml.YAMLError as err:
        print('YAML encountered an error while parsing {}: {}'.format(CREDENTIALS_PATH, err))

    return config
