#! /usr/bin/bash

read -p 'Please enter your username on the version of cloudscheduler you wish to address: ' username

wget_path=`which wget`
if [ -z "$wget_path" ]; then
    sudo yum -y install wget
fi

wget http://cernvm.cern.ch/releases/production/cernvm4-micro-2020.07-1.hdd -O ~/cloudscheduler/unit_tests/web_tests/misc_files/$username-wii1.hdd
cd ~/cloudscheduler/unit_tests/web_tests/misc_files
cp $username-wii1.hdd $username-wii2.hdd
cp $username-wii1.hdd $username-wii3.hdd
cp $username-wii1.hdd $username-wii4.hdd

ssh-keygen -f ~/cloudscheduler/unit_tests/web_tests/misc_files/$username-wik3 -N ''

ssh-keygen -f ~/cloudscheduler/unit_tests/web_tests/misc_files/invalid-web-test -N ''

read -p 'Please enter the path to a private ssh key with no password that allows you to ssh onto the server: ' keypath
read -p 'Please enter your server username: ' server_username
read -p 'Please enter the server you wish to address: ' server
read -p 'Please enter the port the server is on: ' server_port

sudo ssh -oStrictHostKeyChecking=no $server_username@$server -p $server_port -i $keypath "cat > job.condor <<EOF1
Universe   = vanilla
Executable = job.sh
dir           = \$ENV(HOME)/logs
# dir           = /var/tmp/apf-logs
output        = \$\(dir\)/\$\(Cluster\).\$\(Process\).out
error         = \$\(dir\)/\$\(Cluster\).\$\(Process\).err
log           = \$\(dir\)/\$\(Cluster\).\$\(Process\).log
priority       = 10
Requirements = group_name =?= \"$username-wig0\" && TARGET.Arch == \"x86_64\"
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
request_cpus = 1
request_memory = 1500
request_disk = 20G
RunAsOwner = False
getenv = False
queue 4
EOF1
"

sudo ssh $server_username@$server -p $server_port -i $keypath "cat > job.sh <<EOF2
o $HOSTNAME
date
cat /var/lib/cloud_type
cat /var/lib/cloud_name
sleep 780
EOF2
"
