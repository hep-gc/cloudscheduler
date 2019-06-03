import yaml

def dump(yaml_object):
    return yaml.dump(yaml_object)

def load(yaml_string):
    if hasattr(yaml, 'FullLoader'):
        return yaml.full_load(yaml_string)
    else:
        return yaml.load(yaml_string)

