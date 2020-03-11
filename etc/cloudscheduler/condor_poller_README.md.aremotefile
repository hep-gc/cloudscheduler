The remote condor_poller uses the command "condor_config_val GSI_DAEMON_CERT" to determine
whether GSI is enable. If it is enabled, the poller will need to be able to read:

- The condor server certificate file, and 
- The condor worker certificate and key files.

Having obtained the location of the server certificate, the file should be readable by the
"condor" user. The location of the worker certificate files is specified in the configuration
file "condor_poller.yaml" and defaults to a location in the condor user's home directory.
Wherever you place the worker certificate files, you should make sure the condor_poller.yaml
correctly points to them and that they are readable by the condor user.

