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

sudo ln -s /home/centos/cloudscheduler/cli/bin/cloudscheduler cloudscheduler
echo 'Please save the following server settings as "unit-test":'
cloudscheduler defaults set

read -p 'Please enter the path to a private ssh key with no password that allows you to ssh onto the server (ex. /home/centos/.ssh/web_testing): ' keypath
read -p 'Please enter your server username (ex. sampleuser): ' server_username
read -p 'Please enter the server you wish to address (ex. csv2-dev.heprc.uvic.ca): ' server
read -p 'Please enter the port the server is on (ex. 2200): ' server_port

cd ~/cloudscheduler/unit_tests/web_tests/misc_files

cp job_sample.condor job.condor
cp job_sample.sh job.sh
sed -i "s/{user}/$username/" job.condor

sudo scp -i $keypath -P $server_port job.condor $server_username@$server:~
sudo scp -i $keypath -P $server_port job.sh $server_username@$server:~
