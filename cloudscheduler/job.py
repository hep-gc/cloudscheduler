"""
Job related stuff
"""

class Job:

    """
    Job class for mapping condor jobs.
    """
    STATES = ("Unscheduled", "Scheduled")

    def __init__(self, GlobalJobId, JobStatus=0, RequestMemory=0,
                 RequestDisk=0, Requirements="", JobPrio=0, Cmd="",
                 ClusterId=0, User="", VMInstanceType="", Iwd="", VMType="",
                 VMNetwork="", VMLoc="", VMAMI="", VMKeepAlive=0,
                 VMMaximumPrice=0, VMUserData="", VMAMIConfig="",
                 CSMyProxyCredsName="", CSMyProxyServer="",
                 x509userproxysubject="", x509userproxy="",
                 SUBMIT_x509userproxy="", VMJobPerCore=False, MyType="",
                 ServerTime=0, TargetType=""):
        """
        Create job object from condor classad.
        :param GlobalJobId:
        :param JobStatus:
        :param RequestMemory:
        :param RequestDisk:
        :param Requirements:
        :param JobPrio:
        :param Cmd:
        :param ClusterId:
        :param User:
        :param VMInstanceType:
        :param Iwd:
        :param VMType:
        :param VMNetwork:
        :param VMLoc:
        :param VMAMI:
        :param VMKeepAlive:
        :param VMMaximumPrice:
        :param VMUserData:
        :param VMAMIConfig:
        :param CSMyProxyCredsName:
        :param CSMyProxyServer:
        :param x509userproxysubject:
        :param x509userproxy:
        :param SUBMIT_x509userproxy:
        :param VMJobPerCore:
        :param MyType:
        :param ServerTime:
        :param TargetType:
        """
        self.globaljobid = GlobalJobId
        self.job_status = JobStatus
        self.request_memory = RequestMemory
        self.request_disk = RequestDisk
        self.requirements = Requirements
        self.job_prio = JobPrio
        self.cmd = Cmd
        self.cluster_id = ClusterId
        self.user = User
        self.vm_instance_type = VMInstanceType
        self.iwd = Iwd
        self.vm_type = VMType
        self.vm_network = VMNetwork
        self.vm_loc = VMLoc
        self.vm_ami = VMAMI
        self.vm_keep_alive = VMKeepAlive
        self.vm_maximum_price = VMMaximumPrice
        self.vm_userdata = VMUserData
        self.vm_ami_config = VMAMIConfig
        self.cs_myproxy_creds_name = CSMyProxyCredsName
        self.cs_myproxy_server = CSMyProxyServer
        self.x509userproxysubject = x509userproxysubject
        self.x509userproxy = x509userproxy
        self.submit_x509userproxy = SUBMIT_x509userproxy
        self.vm_job_per_core = VMJobPerCore
        self.my_type = MyType
        self.server_time = ServerTime
        self.target_type = TargetType
        self.state = self.STATES[0]

    def __repr__(self):
        return "JobID: " + str(self.globaljobid) + " status: "\
               + str(self.globaljobid)\
               + " user: " + str(self.user) + " state: " + str(self.state)

    def set_state(self, state):
        """Set the job as scheduled or unscheduled."""
        self.state = self.STATES[state]
