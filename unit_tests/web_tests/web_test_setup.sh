#! /usr/bin/bash

read -p 'Please enter your username on the server you wish to address: ' USERNAME

sudo yum -y install epel-release

PYTHON_PATH=`which python3`
if [ -z "$PYTHON_PATH" ]; then
    sudo yum -y install python3.x86_64
fi

PIP_PATH=`which pip3`
if [ -z "$PIP_PATH" ]; then
    sudo yum -y install pip3
fi

sudo pip3 install selenium

sudo pip3 install python-openstackclient
XDG_SESSION_TYPE=wayland

WGET_PATH=`which wget`
if [ -z "$WGET_PATH" ]; then
    sudo yum -y install wget
fi

wget http://cernvm.cern.ch/releases/production/cernvm4-micro-2020.07-1.hdd -O ~/cloudscheduler/unit_tests/web_tests/misc_files/$USERNAME-wii1.hdd
cd ~/cloudscheduler/unit_tests/web_tests/misc_files
cp $USERNAME-wii1.hdd $USERNAME-wii2.hdd
cp $USERNAME-wii1.hdd $USERNAME-wii3.hdd
cp $USERNAME-wii1.hdd $USERNAME-wii4.hdd

ssh-keygen -f ~/cloudscheduler/unit_tests/web_tests/misc_files/$USERNAME-wik3 -N ''

ssh-keygen -f ~/cloudscheduler/unit_tests/web_tests/misc_files/invalid-web-test -N ''

cd /usr/bin

read -p 'Install Firefox? [y/n]: ' FIREFOX
if [ "$FIREFOX" = "y" ]; then
    FIREFOX_PATH=`which firefox`
    if [ -z "$FIREFOX_PATH" ]; then
        sudo yum -y install firefox
    fi
    GECKODRIVER_PATH=`which geckodriver`
    if [ -z "$GECKODRIVER_PATH" ]; then
        GECKODRIVER_TAG=`curl https://github.com/mozilla/geckodriver/releases | grep "<a href=\"/mozilla/geckodriver/releases/tag/v[0-9]\.[0-9][0-9]\.[0-9]\">[0-9]\.[0-9][0-9]\.[0-9]</a>" | head -1`
        PATTERN='(<.*>)(.*)(<.*>)'
        [[ "$GECKODRIVER_TAG" =~ $PATTERN ]]
        GECKODRIVER_VERSION="${BASH_REMATCH[2]}"
        sudo wget https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz
        sudo tar xvzf /usr/bin/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz
    fi
fi

read -p 'Install Chromium? [y/n]: ' CHROMIUM
if [ "$CHROMIUM" = "y" ]; then
    CHROMIUM_PATH=`which chromium-browser`
    if [ -z $CHROMIUM_PATH ]; then
        sudo yum -y install chromium.x86_64
    fi
    CHROMEDRIVER_PATH=`which chromedriver`
    if [ -z "$CHROMEDRIVER_PATH" ]; then
        sudo yum -y install chromedriver
    fi
 fi

read -p 'Install Opera? [y/n]: ' OPERA
if [ "$OPERA" = "y" ]; then
    UNZIP_PATH=`which unzip`
    if [ -z "$UNZIP_PATH" ]; then
        sudo yum -y install unzip
    fi
    OPERA_PATH=`which opera`
    if [ -z "$OPERA_PATH" ]; then
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
    OPERACHROMIUMDRIVER_PATH=`which operadriver`
    if [ -z "$OPERACHROMIUMDRIVER_PATH" ]; then
        sudo wget https://github.com/operasoftware/operachromiumdriver/releases/latest/download/operadriver_linux64.zip 
       sudo unzip operadriver_linux64.zip
       cd operadriver_linux64
       sudo cp operadriver ..
       cd ..
       sudo chmod +x operadriver
    fi
fi

read -p 'Install Chrome? [y/n]: ' CHROME
if [ "$CHROME" = "y" ]; then
    CHROME_PATH=`which google-chrome`
    if [ -z "$CHROME_PATH" ]; then
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        sudo yum -y localinstall google-chrome-stable_current_x86_64.rpm
    fi
    CHROMEDRIVER_PATH=`which chromedriver`
    if [ -z "$CHROMEDRIVER_PATH" ]; then
        sudo yum install chromedriver
    fi
fi

OPENSTACK_PATH=`which openstack`
if [ -z "$OPENSTACK_PATH" ]; then
    sudo pip3 install python-openstackclient
fi
