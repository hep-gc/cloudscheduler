#!/bin/bash
###
### This utility must be run as root. It performs the following:
###
### 1. creates an HTCondor auth token
### 2. sets directory permissions on /etc, /etc/condor, and /etc/condor/tokens.d 
### 3. sets token file permissions and ownership 

IDENTITY="condor@$(hostname)"

cd /etc/condor/tokens.d
condor_token_create -identity "$IDENTITY" -token "$IDENTITY"

chmod 755 /etc /etc/condor /etc/condor/tokens.d
chmod 640 /etc/condor/tokens.d/"$IDENTITY"
chown root:condor /etc/condor/tokens.d/"$IDENTITY"
