#! /usr/bin/bash

read -p 'Please enter your username on the version of cloudscheduler you wish to address: ' username

sudo yum -y install epel-release

python_path=`which python3`
if [ -z "$python_path" ]; then
    sudo yum -y install python3.x86_64
fi

pip_path=`which pip3`
if [ -z "$pip_path" ]; then
    sudo yum -y install pip3
fi

sudo pip3 install --upgrade pip

sudo pip3 install selenium

sudo pip3 install python-openstackclient
XDG_SESSION_TYPE=wayland

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

cd /usr/bin

read -p 'Install Firefox? [y/n]: ' firefox
if [ "$firefox" = "y" ]; then
    firefox_path=`which firefox`
    if [ -z "$firefox_path" ]; then
        sudo yum -y install firefox
    fi
    geckodriver_path=`which geckodriver`
    if [ -z "$geckodriver_path" ]; then
        geckodriver_tag=`curl https://github.com/mozilla/geckodriver/releases | grep "<a href=\"/mozilla/geckodriver/releases/tag/v[0-9]\.[0-9][0-9]\.[0-9]\">[0-9]\.[0-9][0-9]\.[0-9]</a>" | head -1`
        pattern='(<.*>)(.*)(<.*>)'
        [[ "$geckodriver_tag" =~ $pattern ]]
        geckodriver_version="${BASH_REMATCH[2]}"
        sudo wget https://github.com/mozilla/geckodriver/releases/download/v$geckodriver_version/geckodriver-v$geckodriver_version-linux64.tar.gz
        sudo tar xvzf /usr/bin/geckodriver-v$geckodriver_version-linux64.tar.gz
    fi
fi

read -p 'Install Chromium? [y/n]: ' chromium
if [ "$chromium" = "y" ]; then
    chromium_path=`which chromium-browser`
    if [ -z $chromium_path ]; then
        sudo yum -y install chromium.x86_64
    fi
    chromedriver_path=`which chromedriver`
    if [ -z "$chromedriver_path" ]; then
        sudo yum -y install chromedriver
    fi
 fi

read -p 'Install Opera? [y/n]: ' opera
if [ "$opera" = "y" ]; then
    unzip_path=`which unzip`
    if [ -z "$unzip_path" ]; then
        sudo yum -y install unzip
    fi
    opera_path=`which opera`
    if [ -z "$opera_path" ]; then
        # source for Opera installation: https://linuxconfig.org/how-to-install-opera-web-browser-on-linux
        sudo rpm --import https://rpm.opera.com/rpmrepo.key
        sudo tee /etc/yum.repos.d/opera.repo <<RPMREPO
[opera]
name=Opera packages
type=rpm-md
baseurl=https://rpm.opera.com/rpm
gpgcheck=1
gpgkey=https://rpm.opera.com/rpmrepo.key
enabled=1
RPMREPO
        sudo yum -y install opera-stable
    fi
    operachromiumdriver_path=`which operadriver`
    if [ -z "$operachromiumdriver_path" ]; then
        sudo wget https://github.com/operasoftware/operachromiumdriver/releases/latest/download/operadriver_linux64.zip 
       sudo unzip operadriver_linux64.zip
       cd operadriver_linux64
       sudo cp operadriver ..
       cd ..
       sudo chmod +x operadriver
    fi
fi

read -p 'Install Chrome? [y/n]: ' chrome
if [ "$chrome" = "y" ]; then
    chrome_path=`which google-chrome`
    if [ -z "$chrome_path" ]; then
        sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        sudo yum -y localinstall google-chrome-stable_current_x86_64.rpm
    fi
    chromedriver_path=`which chromedriver`
    if [ -z "$chromedriver_path" ]; then
        sudo yum install chromedriver
    fi
fi

openstack_path=`which openstack`
if [ -z "$openstack_path" ]; then
    sudo pip3 install python-openstackclient
fi

sudo ln -s /home/centos/cloudscheduler/cli/bin/cloudscheduler cloudscheduler
cloudscheduler defaults set

read -p 'Please enter the path to a private ssh key with no password that allows you to ssh onto the server: ' keypath
read -p 'Please enter your server username: ' server_username

sudo ssh -oStrictHostKeyChecking=no $server_username@csv2-dev.heprc.uvic.ca -p 3121 -i $keypath "cat > job.condor <<EOF1
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

sudo ssh $server_username@csv2-dev.heprc.uvic.ca -p 3121 -i $keypath "cat > job.sh <<EOF2
o $HOSTNAME
date
cat /var/lib/cloud_type
cat /var/lib/cloud_name
sleep 780
EOF2
"