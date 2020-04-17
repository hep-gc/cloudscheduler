Universe   = vanilla
Executable = db_job.exec
Arguments  = 7 25
dir        = $ENV(HOME)/logs
output     = $(dir)/$(Cluster).$(Process).out
error      = $(dir)/$(Cluster).$(Process).err
log        = $(dir)/$(Cluster).$(Process).log
priority   = 10
Requirements = group_name =?= "<group placeholder>" && TARGET.Arch == "x86_64"
should_transfer_files = YES
when_to_transfer_output = ON_EXIT

request_cpus = 1
request_memory = 1
request_disk = 1M

RunAsOwner = False
getenv = False

queue 1
