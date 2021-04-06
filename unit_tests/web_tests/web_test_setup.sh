#! /usr/bin/bash

read -p 'Please enter your username on the server you wish to address: ' USER

PYTHON_PATH=`which python3`
if [ -z "$PYTHON_PATH" ]; then
    sudo yum -y install python3.x86_64
fi

PIP_PATH=`which pip3`
if [ -z "$PIP_PATH" ]; then
    sudo yum -y install pip3
fi

pip3 install selenium

pip3 install python-openstackclient
XDG_SESSION_TYPE=wayland

WGET_PATH=`which wget`
if [ -z "$WGET_PATH" ]; then
    sudo yum -y install wget
fi

wget http://cernvm.cern.ch/releases/production/cernvm4-micro-2020.07-1.hdd -O ~/cloudscheduler/unit_tests/web_tests/misc_files/$USER-wii1.hdd
cd ~/cloudscheduler/unit_tests/web_tests/misc_files
cp $USER-wii1.hdd $USER-wii2.hdd
cp $USER-wii1.hdd $USER-wii3.hdd
cp $USER-wii1.hdd $USER-wii4.hdd

ssh-keygen -f ~/cloudscheduler/unit_tests/web_tests/misc_files/$USER-wik3 -N ''

ssh-keygen -f ~/cloudscheduler/unit_tests/web_tests/misc_files/invalid-web-test -N ''

read -p 'Install Firefox? [y/n]: ' FIREFOX
if [ "$FIREFOX" ="y" ]; then
    FIREFOX_PATH=`which firefox`
    if [ $FIREFOX_PATH ="\n" ]; then
        sudo yum -y install firefox
    fi
    GECKODRIVER_PATH=`which geckodriver`
    if [ $GECKODRIVER_PATH ="\n" ]; then
        GECKODRIVER_TAG=`curl https://github.com/mozilla/geckodriver/releases | grep "<a href=\"/mozilla/geckodriver/releases/tag/v[0-9]\.[0-9][0-9]\.[0-9]\">[0-9]\.[0-9][0-9]\.[0-9]</a>" | head -1`
        [[ "$GECKODRIVER_TAG" =~ '(<.*>)(.*)(<.*>)' ]]
        GECKODRIVER_VERSION="${BASH_REMATCH[2]}"
        wget https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz
        tar xvzf ~/Downloads/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz
    fi
fi

read -p 'Install Chromium? [y/n]: ' CHROMIUM
if [ "$CHROMIUM" ="y" ]; then
    CHROMIUM_PATH=`which chromium-browser`
    if [ $CHROMIUM_PATH ="\n" ]; then
        sudo yum -y install chromium-browser
    fi
    CHROMEDRIVER_PATH=`which chromedriver`
    if [ $CHROMEDRIVER_PATH ="\n" ]; then
        sudo yum -y install chromedriver
    fi
 fi

read -p 'Install Opera? [y/n]: ' OPERA
if [ "$OPERA" ="y" ]; then
    UNZIP_PATH=`which unzip`
    if [ $UNZIP_PATH ="\n" ]; then
        sudo yum -y install unzip
    fi
    OPERA_PATH=`which opera`
    if [ $OPERA_PATH ="\n" ]; then
        sudo rpm --import https://rpm.opera.com/rpmrepo.key
        sudo yum -y install opera-stable
    fi
    OPERACHROMIUMDRIVER_PATH=`which operadriver`
    if [ $OPERACHROMIUMDRIVER_PATH ="\n" ]; then
        wget https://github.com/operasoftware/operachromiumdriver/releases/latest/download/operadriver_linux64.zip 
    fi
fi

read -p 'Install Chrome? [y/n]: ' CHROME
if [ "$CHROME" ="y" ]; then
    CHROME_PATH=`which google-chrome`
    if [ $CHROME_PATH ="\n" ]; then
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        sudo yum localinstall google-chrome-stable_current_x86_64.rpm
    fi
    CHROMEDRIVER_PATH=`which chromedriver`
    if [ $CHROMEDRIVER_PATH ="\n" ]; then
        sudo yum install chromedriver
    fi
fi
