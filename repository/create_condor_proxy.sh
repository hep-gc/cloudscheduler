#!/bin/bash
    condor_cert=$(condor_config_val gsi_daemon_cert)
    if [ "$?" == "0" ]; then
        condor_key=$(condor_config_val gsi_daemon_key)
        M=$(/usr/bin/grid-proxy-init  -cert $condor_cert -key $condor_key -valid 720:00 2>&1)
        if [ "$?" -eq "0" ]; then
            /bin/cp -f /tmp/x509up_u0 /tmp/x509up_u$(id -u condor) && chown __condor_uid__.__condor_uid__ /tmp/x509up_u__condor_uid__
        else
            /usr/bin/echo "$M" | /usr/bin/mail -s "grid-proxy-init problem on $(hostname)" root@localhost
        fi
    fi
