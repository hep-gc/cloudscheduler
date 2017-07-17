class VM:
    def __init__(self, vmid, hostname=""):
        self.hostname = hostname
        self.vmid = vmid

    def __repr__(self):
        return self.hostname
