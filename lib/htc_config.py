#!/usr/bin/env python3
from subprocess import Popen, PIPE
import os
import socket

def configure_htc(config, logger=None):
    local_dir = '/var/local/cloudscheduler/etc/condor/config.d'

    def configure_htc_logger(logger, level, msg):
        if logger:
            if level == 'debug':
                logger.debug(msg)
            elif level == 'error':
                logger.error(msg)
            elif level == 'warning':
                logger.warning(msg)
            else:
                logger.info(msg)

        else:
            print('configure_htc: %s - %s' % (level, msg))

    def decode(obj):
        if obj:
            if isinstance(obj, str):
                return obj
            else:
                return obj.decode('utf-8')
        else:
            return ''

    def sys_cmd(logger, cmd, comment=''):
        configure_htc_logger(logger, 'debug', 'sys_cmd: %s %s' % (cmd, comment))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            return True, decode(stdout)
        else:
            configure_htc_logger(logger, 'error', 'sys_cmd="%s", rc="%s", stderr="%s"' % (cmd, p.returncode, stderr))
            return False, None
            
    if query_htc_gsi():
        if config.db_connection:
            db_close_on_exit = False
        else:
            config.db_open()
            db_close_on_exit = True

        # GSI_DAEMON_NAME
        fd = open('%s/htcondor_distinguished_names' % local_dir)
        new_daemon_set = set(fd.read().split('=')[1].strip().split(','))
        fd.close()

        new_daemon_set = set()
        for daemon in config.db_connection.execute('select distinct htcondor_gsi_dn from csv2_groups where htcondor_gsi_dn is not null'):
            new_daemon_set.add(daemon['htcondor_gsi_dn'])

        fd = open('%s/gsi_daemon_name' % local_dir)
        old_daemon_set = set(fd.read().split('=')[1].strip().split(','))
        fd.close()

        if new_daemon_set != old_daemon_set:
            fd = open('%s/gsi_daemon_name' % local_dir, 'w')
            fd.write('GSI_DAEMON_NAME = %s' % ','.join(list(new_daemon_set)))
            fd.close()
            
            success, stdout = sys_cmd(logger, ['/usr/sbin/condor_reconfig'])

        # firewall-cmd rich-rules
        rr_xref = {}
        new_fw_set = set()
        for fqdn in config.db_connection.execute('select distinct htcondor_fqdn from csv2_groups where htcondor_fqdn is not null'):
            try:
                ip_addr = socket.gethostbyname(fqdn['htcondor_fqdn'])
                rr = 'rule family="ipv4" source address="%s" port port="5672" protocol="tcp" accept' % ip_addr
                rr_xref[rr] = fqdn['htcondor_fqdn']
                new_fw_set.add(rr)
            except:
                configure_htc_logger(logger, 'warning', 'ignoring HTCondor hostname "%s", unable to resolve .' % fqdn)

        success, stdout = sys_cmd(logger, ['/usr/bin/sudo', '/bin/firewall-cmd', '--zone', 'public', '--list-rich-rules'])
        if success:
            old_fw_set = set(stdout[:-1].split('\n'))
        else:
            old_fw_set = set()

        if new_fw_set != old_fw_set:
            for fw_rule in old_fw_set - new_fw_set:
                success, stdout = sys_cmd(logger, ['/usr/bin/sudo', '/bin/firewall-cmd', '--permanent', '--zone', 'public', '--remove-rich-rule', fw_rule])
            
            for fw_rule in new_fw_set - old_fw_set:
                success, stdout = sys_cmd(logger, ['/usr/bin/sudo', '/bin/firewall-cmd', '--permanent', '--zone', 'public', '--add-rich-rule', fw_rule], comment='(%s)' % rr_xref[fw_rule])
            
            success, stdout = sys_cmd(logger, ['/usr/bin/sudo', '/bin/firewall-cmd', '--reload'])

        if db_close_on_exit:
            config.db_close()

    else:
        configure_htc_logger(logger, 'info', 'HTCondor is not configured for GSI, ignoring reconfiguration request.')

def query_htc_gsi():
    if os.path.isfile('/etc/condor/config.d/gsi') and os.path.islink('/etc/condor/config.d/gsi_daemon_name'):
        return True
    return False

