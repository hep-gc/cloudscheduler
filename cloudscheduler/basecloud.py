"""
cloudscheduler basecloud module.
Defines the basic interface cloudscheduler expects to use across all types of clouds
and contains methods common to all clouds.
"""

import gzip
import uuid
import logging
from abc import ABC, abstractmethod

import cloudscheduler.cloud_init_util

import jinja2

class BaseCloud(ABC):

    """
    Abstract BaseCloud class, meant to be inherited by any specific cloud class for use
    by cloudscheduler.
    """
    def __init__(self, name, extrayaml=None):
        self.log = logging.getLogger(__name__)
        self.name = name
        self.enabled = False
        self.vms = {}
        self.extrayaml = extrayaml

    def __repr__(self):
        return ' : '.join([self.name, self.enabled])

    def num_vms(self):
        """Return the number of VMs on the cloud."""
        return len(self.vms)

    def get_vm(self, vmid):
        """
        Return the VM object of the given VM ID.
        :param vmid: ID of the VM you want to get
        :return: VM Object.
        """
        return self.vms[vmid]

    @abstractmethod
    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        """
        Abstract method for creating a VM on a cloud.
        :param group_yaml_list: The owning group's yaml
        :param num: Number of VMs to boot
        :param job: job row from the database
        :param flavor: the flavor value from database
        """
        assert 0, 'SubClass must implement vm_create()'

    @abstractmethod
    def vm_destroy(self, vm):
        """
        Destroy a VM on the cloud.
        """
        assert 0, 'SubClass must implement vm_destroy()'

    @abstractmethod
    def vm_update(self):
        """Probably not needed since the cloud/vm poller will be
         handling all the status updates in the db"""
        assert 0, 'SubClass must implement vm_update()'

    def _generate_next_name(self):
        """Generate hostnames and check they're not in use."""
        name = ''.join([self.name.replace('_', '-').lower(), '-',
                        str(uuid.uuid4())])
        for vm in self.vms.values():
            if name == vm.hostname:
                name = self._generate_next_name()
        return name

    def prepare_userdata(self, group_yaml, yaml_list, template_dict):
        """ yamllist is a list of strings of file:mimetype format
            group_yaml is a list of tuples with name, yaml content, mimetype format"""
        if yaml_list:
            raw_yaml_list = []
            for yam in yaml_list:
                (contents, mimetype) = cloudscheduler.cloud_init_util\
                    .read_file_type_pairs(yam)
                raw_yaml_list.append(('jobyaml', contents, mimetype))
            group_yaml.extend(raw_yaml_list)
        if self.extrayaml:
            group_yaml.extend(self.extrayaml)
        for yaml_tuple in group_yaml:
            # relies on name having 'template' in it. Alternative?
            if '.j2' in yaml_tuple[0]:
                template_dict['cs_cloud_name'] = self.name
                yaml_tuple[1] = jinja2.Environment()\
                    .from_string(yaml_tuple[1]).render(template_dict)
        userdata = cloudscheduler.cloud_init_util\
            .build_multi_mime_message(group_yaml)
        if not userdata:
            return ""
        compressed = ""
        try:
            compressed = gzip.compress(str.encode(userdata))
        except ValueError as ex:
            self.log.exception('zip failure bad value: %s', ex)
        except TypeError as ex:
            self.log.exception('zip failure bad type: %s', ex)
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
