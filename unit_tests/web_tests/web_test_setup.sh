#! /usr/bin/bash

PYTHON_PATH=`which python3`
if [ $PYTHON_PATH = "\n" ]; then
    yum install python3.x86_64
fi

PIP_PATH=`which pip3`
if [ $PIP_PATH = "\n" ]; then
    yum install pip3
fi

pip3 install selenium

pip3 install python-openstackclient
XDG_SESSION_TYPE=wayland

wget http://cernvm.cern.ch/releases/production/cernvm4-micro-2020.07-1.hdd -O ~/cloudscheduler/unit_tests/web_tests/misc_files/$USER-wii1.hdd
cd ~/cloudscheduler/unit_tests/web_tests/misc_files
cp $USER-wii1.hdd $USER-wii2.hdd
cp $USER-wii1.hdd $USER-wii3.hdd
cp $USER-wii1.hdd $USER-wii4.hdd

printf("~/cloudscheduler/unit_tests/web_tests/misc_files/$USER-wik3\n\n\n")
ssh-keygen

printf("~/cloudscheduler/unit_tests/web_tests/misc_files/invalid-web-test\n\n\n")
ssh-keygen

read -p 'Install Firefox? [y/n]: ' firefox
if [ $firefox = 'y' ]; then
    FIREFOX_PATH=`which firefox`
    if [ $FIREFOX_PATH = "\n" ]; then
        sudo yum -y install firefox
    fi
    GECKODRIVER_PATH=`which geckodriver`
    if [ $GECKODRIVER_PATH = "\n" ]; then
        #install geckodriver
    fi
fi

read -p 'Install Chromium? [y/n]: ' chromium
if [ $chromium = 'y' ]; then
    CHROMIUM_PATH=`which chromium-browser`
    if [ $CHROMIUM_PATH = "\n" ]; then
        sudo yum -y install chromium-browser
    fi
    CHROMEDRIVER_PATH=`which chromedriver`
    if [ $CHROMEDRIVER_PATH = "\n" ]; then
        sudo yum -y install chromedriver
    fi
 fi

read -p 'Install Opera? [y/n]: ' opera
if [ $opera = 'y' ]; then
    OPERA_PATH=`which opera`
    if [ $OPERA_PATH = "\n" ]; then
        sudo rpm --import https://rpm.opera.com/rpmrepo.key
        sudo yum -y install opera-stable
    fi
    OPERACHROMIUMDRIVER_PATH=`which operadriver`
    if [ $OPERACHROMIUMDRIVER_PATH = "\n"]; then
        #install operadriver
    fi
fi

read -p 'Install Chrome? [y/n]: ' chrome
if [ $chrome = 'y' ]; then
    CHROME_PATH=`which google-chrome`
    if [ $CHROME_PATH = "\n" ]; then
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        sudo yum localinstall google-chrome-stable_current_x86_64.rpm
    fi
    CHROMEDRIVER_PATH=`which chromedriver`
    if [ $CHROMEDRIVER_PATH = "\n" ]; then
        sudo yum install chromedriver
    fi
fi
