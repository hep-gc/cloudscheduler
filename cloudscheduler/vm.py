"""
Virtual Machine object Module
"""
class VM:

    """
    Represents a Virtual Machine.
    """
    def __init__(self, vmid, hostname=""):

        """
        VM Constructor.
        :param vmid: id of vm
        :param hostname: hostname of vm
        """
        self.hostname = hostname
        self.vmid = vmid
        self.status = "Starting"

    def __repr__(self):
        return self.hostname
