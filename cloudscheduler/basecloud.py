import gzip
import uuid
from abc import ABC, abstractmethod
import cloudscheduler.cloud_init_util


class BaseCloud(ABC):
    def __init__(self, name, extrayaml=None):
        self.name = name
        self.enabled = False
        self.vms = {}
        self.extrayaml = extrayaml

    def __repr__(self):
        return ' : '.join([self.name, self.enabled])

    def num_vms(self):
        return len(self.vms)

    def get_vm(self, vmid):
        return self.vms[vmid]

    @abstractmethod
    def vm_create(self):
        assert 0, 'SubClass must implement vm_create()'

    @abstractmethod
    def vm_destroy(self):
        assert 0, 'SubClass must implement vm_destroy()'

    @abstractmethod
    def vm_update(self):
        """Probably not needed since the cloud/vm poller will be
         handling all the status updates in the db"""
        assert 0, 'SubClass must implement vm_update()'

    def _generate_next_name(self):
        """Generate hostnames and check they're not in use."""
        name = ''.join([self.name.replace('_', '-').lower(), '-', str(uuid.uuid4())])
        for vm in self.vms.values():
            if name == vm.hostname:
                name = self._generate_next_name()
        return name

    def prepare_userdata(self, group_yaml, yaml_list):
        """ yamllist is a list of strings of file:mimetype format
            group_yaml is a list of tuples with name, yaml content, mimetype format"""
        if yaml_list:
            raw_yaml_list = []
            for yam in yaml_list:
                (contents, mimetype) = cloudscheduler.cloud_init_util.read_file_type_pairs(yam)
                raw_yaml_list.append(('jobyaml', contents, mimetype))
            group_yaml.extend(raw_yaml_list)
        if self.extrayaml:
            group_yaml.extend(self.extrayaml)
        userdata = cloudscheduler.cloud_init_util.build_multi_mime_message(group_yaml)
        if not userdata:
            return ""
        compressed = ""
        try:
            compressed = gzip.compress(str.encode(userdata))
        except ValueError as ex:
            print('zip failure bad value: ', ex)
        except TypeError as ex:
            print('zip failure bad type: ', ex)
        return compressed

    def _attr_list_to_dict(self, attr_list_str):
        """Convert string in form "key1:value1,key2:value2" into a dictionary"""
        if not attr_list_str:
            return {}
        attr_dict = {}
        for keyvaluestr in attr_list_str.split(','):
            keyvalue = keyvaluestr.split(':')
            if len(keyvalue) == 1:
                attr_dict['default'] = keyvalue[0].strip()
            elif len(keyvalue) == 2:
                attr_dict[keyvalue[0].strip().lower()] = keyvalue[1].strip()
            else:
                raise ValueError("Can't split '%s' into suitable host attribute pair: %s"
                                 % (keyvalue, self.name))
        return attr_dict
