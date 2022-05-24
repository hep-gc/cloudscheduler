#!/usr/bin/env bash

OLD_CFG=/opt/cloudscheduler/etc/cloudscheduler/condor_poller.yaml
NEW_CFG=/tmp/cloudscheduler/etc/cloudscheduler/condor_poller.yaml

cd /tmp
wget --no-check-certificate https://csv2.heprc.uvic.ca/repo/condor_poller.tar.gz
tar -xzvf /tmp/condor_poller.tar.gz

if [ -f "$OLD_CFG" ]; then

    cp $OLD_CFG "$OLD_CFG.old"

    OLD_CERT=$(sed -n 's/\s*condor_worker_cert: //p' $OLD_CFG)
    NEW_CERT=$(sed -n 's/\s*condor_worker_cert: //p' $NEW_CFG)

    if [ ! -z "$OLD_CERT" -a "$OLD_CERT" != "$NEW_CERT" ] ; then
        read -p "Keep previous certificate location ($OLD_CERT) (y/n)? " choice
        case "$choice" in 
          y|Y ) sed -i "s#$NEW_CERT#$OLD_CERT#g" $NEW_CFG;;
        esac
    fi

    OLD_KEY=$(sed -n 's/\s*condor_worker_key: //p' $OLD_CFG)
    NEW_KEY=$(sed -n 's/\s*condor_worker_key: //p' $NEW_CFG)

    if [ ! -z "$OLD_KEY" -a "$OLD_KEY" != "$NEW_KEY" ] ; then
        read -p "Keep previous key location ($OLD_KEY) (y/n)? " choice
        case "$choice" in 
          y|Y ) sed -i "s#$NEW_KEY#$OLD_KEY#g" $NEW_CFG;;
        esac
    fi
fi

rsync -av /tmp/cloudscheduler /opt
