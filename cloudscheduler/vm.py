"""
Virtual Machine object Module
"""
class VM:

    """
    Represents a Virtual Machine.
    """
    def __init__(self, vm):

        """
        VM Constructor.
        :param vmid: id of vm
        :param hostname: hostname of vm
        """
        self.hostname = vm.hostname
        self.vmid = vm.vmid
        self.group_name = vm.group_name
        self.cloud_name = vm.cloud_name
        self.status = vm.status
        self.flavor_id = vm.flavor_id
        self.terminate = vm.terminate
        self.last_updated = vm.last_updated


    def __repr__(self):
        return self.hostname
