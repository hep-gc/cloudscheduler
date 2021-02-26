#!/usr/bin/env python3
from subprocess import Popen, PIPE
import os
import socket

# Change to firewall only
def configure_fw(config, logger=None, other_dns=[]):
    local_dir = '/var/local/cloudscheduler/etc/condor/config.d'

    def configure_fw_logger(logger, level, msg):
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
            print('configure_fw: %s - %s' % (level, msg))

    def decode(obj):
        if obj:
            if isinstance(obj, str):
                return obj
            else:
                return obj.decode('utf-8')
        else:
            return ''

    def sys_cmd(logger, cmd, comment=''):
        configure_fw_logger(logger, 'debug', 'sys_cmd: %s %s' % (cmd, comment))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            return True, decode(stdout)
        else:
            configure_fw_logger(logger, 'error', 'sys_cmd="%s", rc="%s", stderr="%s"' % (cmd, p.returncode, stderr))
            return False, None

    if config.csv2_host_id == config.local_host_id:
        if config.db_connection:
            db_close_on_exit = False
        else:
            config.db_open()
            db_close_on_exit = True

        # firewall-cmd rich-rules
        rr_xref = {}
        new_fw_set = set()
        where_clause = 'htcondor_fqdn is not null and htcondor_fqdn!="localhost"'
        rc, msg, rows = config.db_query("csv2_groups", select=["htcondor_fqdn"], where=where_clause, distinct=True)
        for fqdn in rows:
            try:
                ip_addr = socket.gethostbyname(fqdn['htcondor_fqdn'])
                rr = 'rule family="ipv4" source address="%s" port port="%s" protocol="tcp" accept' % (ip_addr, config.public_ports['amqp'])
                rr_xref[rr] = fqdn['htcondor_fqdn']
                new_fw_set.add(rr)

                rr = 'rule family="ipv4" source address="%s" port port="%s" protocol="tcp" accept' % (ip_addr, config.public_ports['database'])
                rr_xref[rr] = fqdn['htcondor_fqdn']
                new_fw_set.add(rr)
            except:
                configure_fw_logger(logger, 'warning', 'ignoring HTCondor hostname "%s", unable to resolve .' % fqdn)

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
        configure_fw_logger(logger, 'info', 'Non Csv2 host, skipping firewall configuration.')

