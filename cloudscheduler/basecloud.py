import gzip
import uuid
import cloudscheduler.config as csconfig
import cloudscheduler.cloud_init_util
import io.StringIO

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
        yamllist.extend(self.extrayaml)
        userdata = cloudscheduler.cloud_init_util.build_multi_mime_message(yamllist)
        if not userdata:
            return ""
        udbuf = io.StringIO()
        udf = gzip.GzipFile(mode='wb', fileobj=udbuf)
        try:
            udf.write(userdata)
        finally:
            udf.close()
        return udbuf.getvalue()
