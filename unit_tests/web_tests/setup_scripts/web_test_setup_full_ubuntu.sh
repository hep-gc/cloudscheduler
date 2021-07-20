#! /bin/bash

read -p 'Please enter your username on the server you wish to address: ' username

sudo apt-get -y install epel-release
sudo apt-get -y install software-properties-common 

python_path=`which python3`
if [ -z "$python_path" ]; then
    sudo apt-get -y install python3
fi

pip_path=`which pip3`
if [ -z "$pip_path" ]; then
    sudo apt-get -y install python3-pip
fi

pip3 install --upgrade pip
pip3 install selenium

pip3 install python-openstackclient
XDG_SESSION_TYPE=wayland

wget_path=`which wget`
if [ -z "$wget_path" ]; then
    sudo apt-get -y install wget
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
        sudo apt-get -y install firefox
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
        sudo apt-get -y install chromium-browser
    fi
    chromedriver_path=`which chromedriver`
    if [ -z "$chromedriver_path" ]; then
        sudo apt-get -y install chromium-chromedriver
    fi
 fi

read -p 'Install Opera? [y/n]: ' opera
if [ "$opera" = "y" ]; then
    unzip_path=`which unzip`
    if [ -z "$unzip_path" ]; then
        sudo apt-get -y install unzip
    fi
    opera_path=`which opera`
    if [ -z "$opera_path" ]; then
        # source for Opera installation: https://vitux.com/ubuntu_opera_browser
        sudo wget -qO- https://deb.opera.com/archive.key | sudo apt-key add -
	sudo apt-get update
	sudo add-apt-repository "deb [arch=i386,amd64] https://deb.opera.com/opera-stable stable non-free #Opera Browser (final releases)"
	sudo apt-get update
        sudo apt-get --yes --force-yes install opera-stable
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
        sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	sudo apt-get update
        sudo apt-get -y install ./google-chrome-stable_current_amd64.deb
    fi
    chromedriver_path=`which chromedriver`
    if [ -z "$chromedriver_path" ]; then
        sudo apt-get -y install chromium-chromedriver
    fi
fi

openstack_path=`which openstack`
if [ -z "$openstack_path" ]; then
    pip3 install python-openstackclient
fi

sudo ln -s /home/ubuntu/cloudscheduler/cli/bin/cloudscheduler cloudscheduler
echo 'Please save the following server settings as "unit-test":'
cloudscheduler defaults set

cd /etc

sudo sed -i '/^PATH="/ s/"$/:\/home\/ubuntu\/.local\/bin"/' environment
sudo sed -i '/^PATH="/ s/"\n/:\/home\/ubuntu\/.local\/bin"/' environment

read -p 'Please enter the path to a private ssh key with no password that allows you to ssh onto the server (ex. /home/ubuntu/.ssh/web_testing): ' keypath
read -p 'Please enter your server username (ex. sampleuser): ' server_username
read -p 'Please enter the server you wish to address (ex. csv2-dev.heprc.uvic.ca): ' server
read -p 'Please enter the port the server is on (ex. 2200): ' server_port

cd ~/cloudscheduler/unit_tests/web_tests/misc_files

cp job_sample.condor job.condor
cp job_sample.sh job.sh
sed -i "s/{user}/$username/" job.condor

sudo scp -i $keypath -P $server_port job.condor $server_username@$server:~
sudo scp -i $keypath -P $server_port job.sh $server_username@$server:~
