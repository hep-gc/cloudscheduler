import gzip
import uuid
import cloudscheduler.config as csconfig
import cloudscheduler.cloud_init_util
#import io.StringIO
from io import StringIO

class BaseCloud():
    def __init__(self, name, slots=0, extrayaml=""):
        self.name = name
        self.enabled = False
        self.vms = {}
        self.slots = slots
        self.max_slots = slots
        self.extrayaml = extrayaml.split(',') if extrayaml else []

    def __repr__(self):
        return ' : '.join([self.name, self.slots, self.enabled])

    def num_vms(self):
        return len(self.vms)

    def get_vm(self, vmid):
        return self.vms[vmid]

    def vm_create(self, **args):
        assert 0, 'SubClass must implement vm_create()'

    def vm_destroy(self, **args):
        assert 0, 'SubClass must implement vm_destroy()'

    def vm_update(self, **args):
        assert 0, 'SubClass must implement vm_update()'

    def _generate_next_name(self):
        name = ''.join([self.name.replace('_', '-').lower(), '-', str(uuid.uuid4())])
        for vm in self.vms.values():
            if name == vm.hostname:
                name = self._generate_next_name()
        return name

    def prepare_userdata(self, yamllist):
        if yamllist:
            yamllist.extend(self.extrayaml)
        userdata = cloudscheduler.cloud_init_util.build_multi_mime_message(yamllist)
        if not userdata:
            return ""
        udbuf = StringIO()
        udf = gzip.GzipFile(mode='wb', fileobj=udbuf)
        try:
            udf.write(userdata)
        finally:
            udf.close()
        return udbuf.getvalue()

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
                raise ValueError("Can't split '%s' into suitable host attribute pair" % keyvalue)
        return attr_dict

