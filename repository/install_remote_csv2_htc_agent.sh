#!/bin/bash
    echo 'This script will initiate a csv2_htc_agent serving the csv2 host "csv2-dev2.heprc.uvic.ca" by'
    echo 'installing the following files:'
    echo ''
    echo '   o /usr/local/sbin/csv2_htc_agent'
    echo '   o /usr/local/etc/csv2_htc_agent.conf'
    echo ''
    echo 'and either:'
    echo ''
    echo '   o /etc/systemd/system/csv2-htc-agent.service'
    echo ''
    echo 'or:'
    echo ''
    echo '   o /etc/init.d/csv2-htc-agent'
    echo ''
    echo 'then running a couple of systemd/service commands.'

    if [ $EUID != 0 ]; then
        echo ''
        echo 'Unfortunately, you need to be running as root in order to use it.'
        exit 1
    fi
    
    curl -o /usr/local/sbin/create_condor_proxy   https://csv2-dev2.heprc.uvic.ca/repo/create_condor_proxy.sh
    curl -o /etc/cron.d/create_condor_proxy       https://csv2-dev2.heprc.uvic.ca/repo/create_condor_proxy.cron
    curl -o /usr/local/sbin/csv2_htc_agent        https://csv2-dev2.heprc.uvic.ca/repo/csv2_htc_agent
    curl -o /usr/local/etc/csv2_htc_agent.conf    https://csv2-dev2.heprc.uvic.ca/repo/csv2_htc_agent.conf

    mkdir -p /var/log/cloudscheduler
    chown cloudscheduler.condor /var/log/cloudscheduler
    chmod 0664 cloudscheduler.condor /var/log/cloudscheduler

    which systemctl
    if [ $? == 0 ]; then
	curl -o /etc/systemd/system/csv2-htc-agent.service https://csv2-dev2.heprc.uvic.ca/repo/csv2-htc-agent.service
        systemctl enable csv2-htc-agent
        systemctl start csv2-htc-agent
        systemctl status csv2-htc-agent

    else
	curl -o /etc/init.d/csv2-htc-agent https://csv2-dev2.heprc.uvic.ca/repo/csv2-htc-agent.initd
        chkconfig --add csv2-htc-agent
        service csv2-htc-agent start
        ps -ef | grep htc_a | grep -v grep

    fi
