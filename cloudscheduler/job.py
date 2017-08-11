class Job:
    STATES=("Unscheduled", "Scheduled")

    def __init__(self, GlobalJobId, JobStatus=0, RequestMemory=0, RequestDisk=0, Requirements="", JobPrio=0,
                 Cmd="", ClusterId=0, User="", VMInstanceType="", Iwd="", VMType="", VMNetwork="", VMName="",
                 VMLoc="", VMAMI="", VMKeepAlive=0, VMMaximumPrice=0, VMUserData="", VMAMIConfig="",
                 CSMyProxyCredsName="", CSMyProxyServer="", x509userproxysubject="", x509userproxy="",
                 SUBMIT_x509userproxy="", VMJobPerCore=False, MyType="", ServerTime=0, TargetType=""):
        self.GlobalJobId = GlobalJobId
        self.JobStatus = JobStatus
        self.RequestMemory = RequestMemory
        self.RequestDisk = RequestDisk
        self.Requirements = Requirements
        self.JobPrio = JobPrio
        self.Cmd = Cmd
        self.ClusterId = ClusterId
        self.User = User
        self.VMInstanceType = VMInstanceType
        self.Iwd = Iwd
        self.VMType = VMType
        self.VMNetwork = VMNetwork
        self.VMName = VMName
        self.VMLoc = VMLoc
        self.VMAMI = VMAMI
        self.VMKeepAlive = VMKeepAlive
        self.VMMaximumPrice = VMMaximumPrice
        self.VMUserData = VMUserData
        self.VMAMIConfig = VMAMIConfig
        self.CSMyProxyCredsName = CSMyProxyCredsName
        self.CSMyProxyServer = CSMyProxyServer
        self.x509userproxysubject = x509userproxysubject
        self.x509userproxy = x509userproxy
        self.SUBMIT_x509userproxy = SUBMIT_x509userproxy
        self.VMJobPerCore = VMJobPerCore
        self.MyType = MyType
        self.ServerTime = ServerTime
        self.TargetType = TargetType
        self.state = self.STATES[0]

    def __repr__(self):
        return "JobID: " + str(self.GlobalJobId) + " status: " + str(self.JobStatus) + " user: " + str(self.User) + " state: " + str(self.state)
    
    def set_state(self, state):
        self.state = self.STATES[state]