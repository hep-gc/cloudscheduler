class BaseCloud():
    def __init__(self, name, enabled=False, slots=0):
        self.name = name
        self.enabled = enabled
        self.vms = {}
        self.slots = slots

    def __repr__(self):
        return ' : '.join([self.name, self.slots, self.enabled])

    def num_vms(self):
        return len(vms.keys())

    def get_vm(self, vmid):
        return self.vms[vmid]

    def vm_create(self, **args):
        assert 0, 'SubClass must implement vm_create()'

    def vm_destroy(self, **args):
        assert 0, 'SubClass must implement vm_destroy()'

    def vm_update(self, **args):
        assert 0, 'Sublass must implement vm_update()'

    def generate_next_name(self):
        name = ''.join([self.name.replace('_', '-').lower(), '-', str(uuid.uuid4())])
        for vm in self.vms.values():
            if name == vm.hostname:
                name = self._generate_next_name()
        return name