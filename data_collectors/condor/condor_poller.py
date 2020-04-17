import multiprocessing
import time
import logging
import signal
import socket
from subprocess import Popen, PIPE
from multiprocessing import Process
import os
import re
import sys
import yaml

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, check_pid, terminate
from cloudscheduler.lib.schema import view_condor_host
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.fw_config import configure_fw
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    build_inventory_for_condor, \
    start_cycle, \
    wait_cycle

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient

import htcondor
import classad
import boto3
import sqlalchemy.exc
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session


MASTER_TYPE = htcondor.AdTypes.Master
STARTD_TYPE = htcondor.AdTypes.Startd

# mysql_privileges cloud_table csv2_clouds

def _get_nova_client(session, region=None):
    nova = novaclient.Client("2", session=session, region_name=region, timeout=10)
    return nova

def _get_openstack_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
    if version == 2:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project)
    else:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project,
            user_domain=cloud.user_domain_name,
            project_domain_name=cloud.project_domain_name)
    if session is False:
        logging.error("Failed to setup session, skipping %s", cloud.cloud_name)
        if version == 2:
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s" %
                          (cloud.authurl, cloud.username, cloud.project))
        else:
            logging.error(
                "Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s" %
                (cloud.authurl, cloud.username, cloud.project, cloud.user_domain_name, cloud.project_domain_name))
    return session


def _get_openstack_session_v1_v2(auth_url, username, password, project, user_domain="Default", project_domain_name="Default"):
    authsplit = auth_url.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad openstack URL: %s, could not determine version, aborting session", auth_url)
        return False
    if version == 2:
        try:
            auth = v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project)
            sess = session.Session(auth=auth, verify=config.categories["condor_poller.py"]["cacerts"])
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s::%s" % (auth_url, exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
            return False
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project,
                user_domain_name=user_domain,
                project_domain_name=project_domain_name)
            sess = session.Session(auth=auth, verify=config.categories["condor_poller.py"]["cacerts"])
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess



def _get_ec2_session(cloud):
    return boto3.session.Session(region_name=cloud.region,
                                 aws_access_key_id=cloud.username,
                                 aws_secret_access_key=cloud.password)

def _get_ec2_client(session):
    return session.client('ec2')

# condor likes to return extra keys not defined in the projection
# this function will trim the extra ones so that we can use kwargs
# to initiate a valid table row based on the data returned
def trim_keys(dict_to_trim, key_list):
    keys_to_trim = ["Owner"]
    for key in dict_to_trim:
        if key == "group_name" or key == "target_alias":
            continue
        if key not in key_list or isinstance(dict_to_trim[key], classad.Value):
            keys_to_trim.append(key)
    for key in keys_to_trim:
        dict_to_trim.pop(key, None)
    return dict_to_trim


def get_condor_dict(config, logging):
    condor_dict = {}
    group_list = config.db_connection.execute('select group_name,htcondor_fqdn from csv2_groups;')
    for group in group_list:
        try:
            condor_ip = socket.gethostbyname(group['htcondor_fqdn'])
            if group['htcondor_fqdn'] not in condor_dict:
                condor_dict[group['htcondor_fqdn']] = []

            condor_dict[group['htcondor_fqdn']].append(group['group_name'])

        except:
            logging.debug('Ignoring invalid condor host "%s".' % group['htcondor_fqdn'])

    return condor_dict

def if_null(val, col=None):
    if col:
        if val:
            return '%s="%s"' % (col, val)
        else:
            return '%s=NULL' % col

    else:
        if val:
            return val
        else:
            return 'NULL'



def condor_off(condor_classad):
    try:
        logging.debug("Sending condor_off to %s" % condor_classad)
        master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)
        if master_result is None:
            # None is good in this case it means it was a success
            master_result = "Success"
        logging.info("Condor_off result: %s" % master_result)
        return master_result
    except Exception as exc:
        logging.error("Condor off failed:")
        logging.error(exc)
        return False

def decode(obj):
    if not obj:
        return ''
    elif isinstance(obj, str):
        return obj
    else:
        return obj.decode('utf-8')

def get_condor_session(hostname=None):
    try:
        condor_session = htcondor.Collector(hostname)
        return condor_session
    except Exception as exc:
        logging.exception("Failed to get condor session for %s:" % hostname)
        logging.error(exc)
        return False

def get_gsi_cert_subject_and_eol(cert):
    if not os.access(cert, os.R_OK):
        logging.warning('function: get_gsi_cert_subject_and_eol, pem: %s is unreadable.' % cert)
        return 'unreadable', -999999

    if os.path.isfile(cert):
        p1 = Popen([
            'openssl',
            'x509',
            '-noout',
            '-subject',
            '-in',
            cert
            ], stdout=PIPE, stderr=PIPE)
        stdout, stderr = p1.communicate()

        stdout = decode(stdout)
        if p1.returncode == 0 and stdout != '':
            words = decode(stdout).split()
            subject = words[1]

            p1 = Popen([
                'openssl',
                'x509',
                '-noout',
                '-dates',
                '-in',
                cert
                ], stdout=PIPE, stderr=PIPE)

            p2 = Popen([
                'awk',
                '/notAfter=/ {print substr($0,10)}'
                ], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p2.communicate()

            if p2.returncode == 0:
                eol = int(time.mktime(time.strptime(decode(stdout[:-1]), '%b %d %H:%M:%S %Y %Z')))
                return subject, eol
            else:
                logging.error('function: get_gsi_cert_subject_and_eol(openssl x509 -dates), cert: %s, rc: %s, stdout: %s, stderr: %s' % (cert, p2.returncode, decode(stdout), decode(stderr)))
        else:
            logging.error('function: get_gsi_cert_subject_and_eol(openssl x509 -subject), cert: %s, rc: %s, stdout: %s, stderr: %s' % (cert, p1.returncode, decode(stdout), decode(stderr)))
    else:
        logging.error('function: get_gsi_cert_subject_and_eol(openssl x509 -subject), cert: "%s" does not exist.' % cert)

    return None, None


def get_master_classad(session, machine, hostname):
    try:
        if machine is not "":
            condor_classad = session.query(MASTER_TYPE, 'Name=="%s"' % machine)[0]
        else:
            condor_classad = session.query(MASTER_TYPE, 'regexp("%s", Name, "i")' % hostname)[0]
        return condor_classad
    except IndexError:
        logging.error("Failed to retrieve classad from condor. No matching classad")
    except Exception as exc:
        logging.error("Failed to retrieve classad from condor. Communication error :")
        logging.error(exc)
        return -1
    return False


def get_startd_classads(session, machine):
    startd_list = []
    try:
        condor_classads = session.query(STARTD_TYPE, 'Machine=="%s"' % machine)
        for classad in condor_classads:
            startd_list.append(classad)
        return startd_list
    except Exception as exc:
        logging.error("Failed to retrieve machine classads, aborting...")
        logging.error(exc)
        return False


def invalidate_master_classad(session, classad):
    return session.advertise([classad], "INVALIDATE_MASTER_ADS")

def invalidate_startd_classads(session, classad_list):
    return session.advertise(classad_list, "INVALIDATE_STARTD_ADS")
       
def yaml_full_load(yaml_string):
    if hasattr(yaml, 'full_load'):
        return yaml.full_load(yaml_string)
    else:
        return yaml.load(yaml_string)

def zip_base64(path):
    if not os.access(path, os.R_OK):
        logging.warning('function: zip_base64, pem: %s is unreadable.' % path)
        return 'unreadable'

    if os.path.isfile(path):
        p1 = Popen([
            'gzip',
            '-c',
            path
            ], stdout=PIPE, stderr=PIPE)

        p2 = Popen([
            'base64'
            ], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p2.communicate()

        if p2.returncode == 0:
            return decode(stdout)
        else:
            logging.error('function: zip_base64, pem: %s, rc: %s, stdout: %s, stderr: %s' % (path, p2.returncode, decode(stdout), decode(stderr)))

    return None

def check_pair_pid(pair, config, cloud_table):
    cloud = config.db_session.query(cloud_table).get((pair.group_name, pair.cloud_name))
    pid = cloud.machine_subprocess_pid
    if pid is None or pid == -1:
        # No subprocess ever started
        return False
    # Sending signal 0 to a pid will raise an OSError exception if the pid is not running, and do nothing otherwise
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True



def process_group_cloud_commands(pair, condor_host):
    group_name = pair.group_name
    cloud_name = pair.cloud_name

    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]),  "ProcessMonitor"], pool_size=3, signals=True)
    config.db_open()

    VM = config.db_map.classes.csv2_vms
    CLOUD = config.db_map.classes.csv2_clouds

    terminate_off = config.categories["condor_poller.py"]["terminate_off"]
    retire_off = config.categories["condor_poller.py"]["terminate_off"]
    retire_interval = config.categories["condor_poller.py"]["retire_interval"]

    master_type = htcondor.AdTypes.Master
    startd_type = htcondor.AdTypes.Startd

    pid = os.getpid()
    sql = 'update csv2_clouds set machine_subprocess_pid=%s where group_name="%s" and cloud_name="%s";' % (pid, group_name, cloud_name)
    config.db_connection.execute(sql)

    logging.info("Processing commands for group:%s, cloud:%s" % (group_name, cloud_name))


    # RETIRE CODE:
    # Query database for machines to be retired.
    for resource in config.db_session.query(view_condor_host).filter(view_condor_host.c.htcondor_fqdn==condor_host, view_condor_host.c.cloud_name==cloud_name, view_condor_host.c.group_name==group_name, or_(view_condor_host.c.retire>=1, view_condor_host.c.terminate>=1)):
        # Since we are querying a view we dont get an automapped object and instead get a 'result' tuple of the following format
        #index=attribute
        #0=group
        #1=cloud
        #2=htcondor_fqdn
        #3=vmid
        #4=hostname
        ##5primary_slots
        ##6dynamic_slots
        #7=retireflag
        #8=terminate flag
        #9=machine
        #10=updater
        #logging.debug("%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (resource.group_name, resource.cloud_name, resource.htcondor_fqdn, resource.vmid, resource.hostname, resource[5], resource[6], resource.retire, resource.updater, resource.terminate, resource.machine))
        # First check the slots to see if its time to terminate this machine

        #check if retire flag set & a successful retire has happened  and  (htcondor_dynamic_slots<1 || NULL) and htcondor_partitionable_slots>0, issue condor_off and increment retire by 1.
        if resource.retire >= 1:
            if (resource[6] is None or resource[6]<1) and (resource[5] is None or resource[5]<1):
                #check if terminate has already been set
                if not resource[8] >= 1:
                  # set terminate=1
                  # need to get vm classad because we can't update via the view.
                  try:
                      logging.info("slots are zero or null on %s, setting terminate, last updater: %s" % (resource.hostname, resource.updater))
                      logging.debug("group_name:%s\ncloud_name:%s\nhtcondor_fqdn:%s\nvmid:%s\nhostname%s\nPrimary Slots:%s\nDynamic Slots:%s\nretire:%s\nupdater:%s\nterminate:%s\nmachine:%s" % (resource.group_name, resource.cloud_name, resource.htcondor_fqdn, resource.vmid, resource.hostname, resource[5], resource[6], resource.retire, resource.updater, resource.terminate, resource.machine))
                      vm_row = config.db_session.query(VM).filter(VM.group_name==resource.group_name, VM.cloud_name==resource.cloud_name, VM.vmid==resource.vmid)[0]
                      vm_row.terminate = 1
                      vm_row.updater = str(get_frame_info() + ":t1")
                      config.db_session.merge(vm_row)
                      config.db_session.commit()

                  except Exception as exc:
                      # unable to get VM row error
                      logging.exception(exc)
                      logging.error("%s ready to be terminated but unable to locate vm_row" % resource.vmid)
                      continue
            if resource.retire >= 10:
                continue


        if retire_off:
            logging.critical("Retires disabled, normal operation would retire %s" % resource.hostname)
            continue


        # check the retire time to see if it has been enough time since the last retire was issued
        # if it's none we haven't issued a retire yet and can skip the check
        if resource.retire_time is not None:
            if int(time.time()) - resource.retire_time < retire_interval:
                # if the time since last retire is less than the configured retire interval, continue
                logging.debug("Resource has been retired recently... skipping for now.")
                continue


        logging.info("Retiring (%s) machine %s primary slots: %s dynamic slots: %s, last updater: %s" % (resource.retire, resource.machine, resource[5], resource[6], resource.updater))
        try:
            condor_session = get_condor_session()
            if resource.machine is not "":
                condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.machine)[0]
            else:
                condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource.hostname)[0]

            if not condor_classad or condor_classad == -1:
                #there was a condor error
                logging.error("Unable to retrieve condor classad, skipping %s ..." % resource.machine)

            logging.info("Issuing DaemonsOffPeaceful to %s" % condor_classad)
            master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)
            logging.debug("Result: %s " % master_result)
            
                
            #get vm entry and update retire = 2
            vm_row = config.db_session.query(VM).filter(VM.group_name==resource.group_name, VM.cloud_name==resource.cloud_name, VM.vmid==resource.vmid)[0]
            vm_row.retire = vm_row.retire + 1
            vm_row.updater = str(get_frame_info() + ":r+")
            vm_row.retire_time = int(time.time())
            config.db_session.merge(vm_row)
            try:
                config.db_session.commit()
            except Exception as exc:
                logging.exception("Failed to commit batch of retired machines, aborting cycle...")
                logging.error(exc)
                break

        except Exception as exc:
            logging.exception(exc)
            logging.error("Failed to issue DaemonsOffPeacefull to machine: %s, hostname: %s missing classad or condor miscomunication." % (resource.machine, resource.hostname))
            logging.debug(condor_host)
            continue


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Terminate code:
    master_list = []
    startd_list = []
    #get list of vm/machines from this condor host
    redundant_machine_list = config.db_session.query(view_condor_host).filter(view_condor_host.c.htcondor_fqdn == condor_host, view_condor_host.c.cloud_name==cloud_name, view_condor_host.c.group_name==group_name, view_condor_host.c.terminate >= 1)
    for resource in redundant_machine_list:
        if resource[6] is not None:
            if resource[5] is not None:
                if resource.terminate == 1 and resource[6] >= 1 and resource[5] >=1:
                    logging.info("VM still has active slots, skipping terminate on %s" % resource.vmid)
                    continue


        # we need the relevent vm row to check if its in manual mode and if not, terminate and update termination status
        try:
            vm_row = config.db_session.query(VM).filter(VM.group_name == resource.group_name, VM.cloud_name == resource.cloud_name, VM.vmid == resource.vmid)[0]
        except Exception as exc:
            logging.error("Unable to retrieve VM row for vmid: %s, skipping terminate..." % resource.vmid)
            continue
        if vm_row.manual_control == 1:
            logging.info("VM %s under manual control, skipping terminate..." % resource.vmid)
            continue


        # Get session with hosting cloud.
        cloud = config.db_session.query(CLOUD).filter(
            CLOUD.group_name == vm_row.group_name,
            CLOUD.cloud_name == vm_row.cloud_name).first()

        if cloud.cloud_type == "openstack":
            session = _get_openstack_session(cloud)
            if session is False:
                continue
         
            if terminate_off:
                logging.critical("Terminates disabled, normal operation would terminate %s" % vm_row.hostname)
                continue

            # terminate the vm
            nova = _get_nova_client(session, region=cloud.region)
            try:
                # may want to check for result here Returns: An instance of novaclient.base.TupleWithMeta so probably not that useful
                vm_row.terminate = vm_row.terminate + 1
                old_updater = vm_row.updater
                vm_row.updater = str(get_frame_info() + ":t+")

                try:
                    nova.servers.delete(vm_row.vmid)
                except novaclient.exceptions.NotFound:
                    logging.error("VM not found on cloud, deleting vm entry %s" % vm_row.vmid)
                    config.db_session.delete(vm_row)
                    try:
                        config.db_session.commit()
                    except Exception as exc:
                        logging.exception("Failed to commit vm delete, aborting cycle...")
                        logging.error(exc)
                        break
                    continue #skip rest of logic since this vm is gone anywheres 
                        

                except Exception as exc:
                    logging.error("Unable to delete vm, vm doesnt exist or openstack failure:")
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logging.error(exc_type)
                    logging.error(exc)
                    continue
                logging.info("VM Terminated(%s): %s primary slots: %s dynamic slots: %s, last updater: %s" % (vm_row.terminate, vm_row.hostname, vm_row.htcondor_partitionable_slots, vm_row.htcondor_dynamic_slots, old_updater))
                config.db_session.merge(vm_row)
                # log here if terminate # /10 = remainder zero
                if vm_row.terminate %10 == 0:
                    logging.critical("%s failed terminates on %s user action required" % (vm_row.terminate - 1, vm_row.hostname))
            except Exception as exc:
                logging.error("Failed to terminate VM: %s, terminates issued: %s" % (vm_row.hostname, vm_row.terminate - 1))
                logging.error(exc)

            # Now that the machine is terminated, we can speed up operations by invalidating the related classads
            # double check that a condor_session exists
            if 'condor_session' not in locals():
                condor_session = get_condor_session()
            if resource.machine is not None:
                logging.info("Removing classads for machine %s" % resource.machine)
            else:
                logging.info("Removing classads for machine %s" % resource.hostname)
            try:
                master_classad = get_master_classad(condor_session, resource.machine, resource.hostname)
                if not master_classad:
                    # there was no matching classad
                    logging.error("Classad not found for %s//%s" % (resource.machine, resource.hostname))

                master_result = invalidate_master_classad(condor_session, master_classad)
                logging.debug("Invalidate master result: %s" % master_result)
                startd_classads = get_startd_classads(condor_session, resource.hostname)
                startd_result = invalidate_startd_classads(condor_session, startd_classads)
                logging.debug("Invalidate startd result: %s" % startd_result)


                #if resource.machine is not None and resource.machine is not "":
                #    condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.machine)[0]
                #else:
                #    condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource.hostname)[0]
                #master_list.append(condor_classad)

                # this could be a list of adds if a machine has many slots
                #condor_classads = condor_session.query(startd_type, 'Machine=="%s"' % resource.hostname)
                #for classad in condor_classads:
                #    startd_list.append(classad)
            #except IndexError as exc:
            #    pass
            except Exception as exc:
                logging.error("Failed to get condor classads or issue invalidate:")
                logging.error(exc)
                break

        elif cloud.cloud_type == "amazon":
            if terminate_off:
                logging.critical("Terminates disabled, normal operation would terminate %s" % vm_row.hostname)
                continue
            #terminate the vm
            amz_session = _get_ec2_session(cloud)
            amz_client = _get_ec2_client(amz_session)
            try:
                vm_row.terminate = vm_row.terminate + 1
                old_updater = vm_row.updater
                vm_row.updater = str(get_frame_info() + ":t+")
                #destroy amazon vm, first we'll need to check if its a reservation
                if vm_row.vmid[0:3].lower() == "sir":
                    #its a reservation just delete it and destroy the vm
                    # not sure what the difference between a client and connection from csv1 is but there is more work to be done here
                    #
                    # need the command to remove reservation:
                    # cancel_spot_instance_requests(list_of_request_ids)
                    #
                    # need to terminate request, and possible image if instance_id isn't empty
                    try:
                        logging.info("Canceling amazon spot price request: %s" % vm_row.vmid)
                        amz_client.cancel_spot_instance_requests(SpotInstanceRequestIds=[vm_row.vmid])
                        if vm_row.instance_id is not None:
                            #spot price vm running need to terminate it:
                            logging.info("Terminating amazon vm: %s" % vm_row.instance_id)
                            amz_client.terminate_instances(InstanceIds=[vm_row.instance_id])
                    except Exception as exc:
                        logging.error("Unable to terminate %s due to:" % vm_row.vmid)
                        logging.error(exc)
                else:
                    #its a regular instance and just terminate it
                    logging.info("Terminating amazon vm: %s" % vm_row.vmid)
                    amz_client.terminate_instances(InstanceIds=[vm_row.vmid])
            except Exception as exc:
                logging.error("Unable to terminate %s due to:" % vm_row.vmid)
                logging.error(exc)


        else:
            # Other cloud types will need to be implemented here to terminate any vms not from openstack
            logging.info("Vm not from openstack, or amazon cloud, skipping...")
            continue
    try:
        config.db_session.commit()
    except Exception as exc:
        logging.exception("Failed to commit retire machine, aborting cycle...")
        logging.error(exc)
        config.db_session.rollback()
        sql = "update csv2_clouds set machine_subprocess_pid=%s where group_name='%s' and cloud_name='%s';" % (-1, group_name, cloud_name)
        return

    logging.info("Commands complete, closing subprocess")
    sql = "update csv2_clouds set machine_subprocess_pid=%s where group_name='%s' and cloud_name='%s';" % (-1, group_name, cloud_name)
    config.db_connection.execute(sql) 
    config.db_close()
    return



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def job_poller():
    multiprocessing.current_process().name = "Job Poller"
    job_attributes = ["TargetClouds", "JobStatus", "RequestMemory", "GlobalJobId", "HoldReason",
                      "RequestDisk", "RequestCpus", "RequestScratch", "RequestSwap", "Requirements",
                      "JobPrio", "ClusterId", "ProcId", "User", "VMInstanceType", "VMNetwork",
                      "VMImage", "VMKeepAlive", "VMMaximumPrice", "VMUserData", "VMJobPerCore", "Owner",
                      "EnteredCurrentStatus", "QDate", "HoldReasonCode", "HoldReasonSubCode", 
                      "LastRemoteHost", "TargetAlias"]
    # Not in the list that seem to be always returned:
    # FileSystemDomian, MyType, ServerTime, TargetType
    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    fail_count = 0
    inventory = {}
    delete_cycle = True
    cycle_count = 0
    condor_inventory_built = False
    uncommitted_updates = 0
    failure_dict = {}

    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]), "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])


    JOB = config.db_map.classes.condor_jobs
    CLOUDS = config.db_map.classes.csv2_clouds
    GROUPS = config.db_map.classes.csv2_groups
    USERS = config.db_map.classes.csv2_user_groups


    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, JOB, 'global_job_id', debug_hash=(config.categories["condor_poller.py"]["log_level"]<20), condor_host=config.local_host_id)
        config.db_open()
        while True:
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.refresh()

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            db_session = config.db_session
            groups = db_session.query(GROUPS).filter(GROUPS.htcondor_host_id == config.local_host_id)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            condor_host_groups = {}
            group_users = {}
            for group in groups:
                if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                    condor_central_manager = group.htcondor_container_hostname
                    condor_hosts_set.add(group.htcondor_container_hostname)
                elif group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                    condor_central_manager = group.htcondor_fqdn
                    condor_hosts_set.add(group.htcondor_fqdn)   
                else:
                    # no condor location set
                    logging.debug("No condor location set")
                    continue                

                if condor_central_manager not in condor_host_groups:
                    condor_host_groups[condor_central_manager] = [group.group_name]
                else:
                    condor_host_groups[condor_central_manager].append(group.group_name)

                # build group_users dict
                users = config.db_session.query(USERS).filter(USERS.group_name == group.group_name)
                htcondor_other_submitters = group.htcondor_other_submitters
                if htcondor_other_submitters is not None:
                    user_list = group.htcondor_other_submitters.split(',')
                else:
                    user_list = []
                # need to append users from group defaultts (htcondor_supplementary_submitters) here
                # alternatively we can just have 2 lists and check both wich would save on memory if there was a ton of users but cost cycles
                for usr in users:
                    user_list.append(usr.username)

                group_users[group.group_name] = user_list

            uncommitted_updates = 0
            foreign_jobs = 0
            for condor_host in condor_hosts_set:
                foreign_jobs = 0
                held_jobs = 0
                held_job_ids = []
                logging.debug("Polling condor host: %s" % condor_host)
                try:
                    coll = htcondor.Collector(condor_host)
                    scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, condor_host)
                    condor_session = htcondor.Schedd(scheddAd)

                except Exception as exc:
                    # if we fail we need to mark all these groups as failed so we don't delete the entrys later
                    fail_count = 0
                    for group in groups:
                        if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                            if group.htcondor_fqdn == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]
                        else:
                            if group.htcondor_container_hostname == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]
                    logging.error("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.debug(exc)

                    if fail_count > 3 and fail_count < 1500:
                        logging.critical("%s failed polls on host: %s, Configuration error or condor issues" % (fail_count, condor_host))
                    elif fail_count > 1500:
                        logging.critical("Over 1500 failed polls on host: %s, Configuration error or condor issues" % (fail_count, condor_host))
                    continue


                if not condor_inventory_built:
                    # Initializes the cloud field to "-" since a job has no concept of a cloud
                    build_inventory_for_condor(inventory, db_session, CLOUDS)
                    condor_inventory_built = True

                # Retrieve jobs.
                
                logging.debug("getting job list from condor")
                try:
                    job_list = condor_session.xquery(
                        projection=job_attributes
                        )
                except Exception as exc:
                    # if we fail we need to mark all these groups as failed so we don't delete the entrys later
                    fail_count = 0
                    for group in groups:
                        if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                            if group.htcondor_fqdn == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]
                        else:
                            if group.htcondor_container_hostname == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]
                    logging.error("Failed to get jobs from condor scheddd object, aborting poll on host: %s" % condor_host)
                    logging.error(exc)
                    if fail_count > 3:
                        logging.critical("%s failed polls on host: %s, Configuration error or condor issues" % (fail_count, condor_host))
                    continue

                # Process job data & insert/update jobs in Database
                abort_cycle = False
                job_errors = {}
                for job_ad in job_list:
                    job_dict = dict(job_ad)
                    if "Requirements" in job_dict:
                        ca1=classad.ClassAd(job_dict)
                        et2 = ca1.flatten(job_dict).eval()
                        job_dict['Requirements'] = str(et2['Requirements'])
                        # Parse group_name out of requirements
                        try:
                            #pattern = '(group_name is ")(.*?)(")'
                            pattern = '(group_name is "|group_name == "|group_name =\?= "|group_name =\?= toLower\("|group_name is toLower\("|group_name == toLower\(")(.*?)(")'
                            grp_name = re.search(pattern, job_dict['Requirements'])
                            job_dict['group_name'] = grp_name.group(2).lower()
                        except Exception as exc:
                            logging.debug("No group name found in requirements expression... ignoring foreign job.")
                            foreign_jobs = foreign_jobs+1
                            if "nogrp" not in job_errors:
                                job_errors["nogrp"] = 1
                                job_errors["nogrpinfo"] = {"Submitter: %s" % job_dict['Owner']}
                            else:
                                job_errors["nogrp"] = job_errors["nogrp"] + 1
                                job_errors["nogrpinfo"].add("Submitter: %s" % job_dict['Owner'])
                            continue
                        # Look for a target_alias in requirements string
                        try:
                            pattern = '(target_alias is "|target_alias == "|target_alias =\?= "|target_alias =\?= toLower\("|target_alias is toLower\("|target_alias == toLower\(")(.*?)(")'
                            target_alias = re.search(pattern, job_dict['Requirements'])
                            job_dict['target_alias'] = target_alias.group(2).lower()
                        except Exception as exc:
                            logging.debug("No alias found in requirements expression")
                    else:
                        logging.debug("No requirements attribute found, not a csv2 job... ignoring foreign job.")
                        foreign_jobs = foreign_jobs+1
                        if "noreq" not in job_errors:
                            job_errors["noreq"] = 1
                            job_errors["noreqinfo"] = {"Submitter: %s" % job_dict['Owner']}
                        else:
                            job_errors["noreq"] = job_errors["noreq"] + 1
                            job_errors["noreqinfo"].add("Submitter: %s" % job_dict['Owner'])
                        continue

                    #check group_name is valid for this host
                    if job_dict['group_name'] not in condor_host_groups[condor_host]:
                        # not a valid group for this host
                        logging.debug("%s is not a valid group for %s, ignoring foreign job." % (job_dict['group_name'], condor_host))
                        foreign_jobs = foreign_jobs+1
                        held_jobs = held_jobs + 1
                        #check if job is already held
                        if job_dict["JobStatus"] != 5:
                            held_job_ids.append(str(job_dict["ClusterId"]) +"."+ str(job_dict["ProcId"]))
                        if "invalidgrp" not in job_errors:
                            job_errors["invalidgrp"] = 1
                            job_errors["invalidgrpinfo"] = {"Invalid group: %s" % job_dict['group_name']}
                        else:
                            job_errors["invalidgrp"] = job_errors["invalidgrp"] + 1
                            job_errors["invalidgrpinfo"].add("Invalid group: %s" % job_dict['group_name'])

                        continue

                    # check if user is valid for this group
                    if job_dict['Owner'] not in group_users[job_dict['group_name']]:
                        # this user isn''t registered with this group and thus cannot submit jobs to it
                        logging.debug("User '%s' is not registered to submit jobs to %s, excluding as foreign job." % (job_dict['Owner'], job_dict['group_name']))
                        foreign_jobs = foreign_jobs+1
                        held_jobs = held_jobs + 1
                        if job_dict["JobStatus"] != 5:
                            held_job_ids.append(str(job_dict["ClusterId"]) +"."+ str(job_dict["ProcId"]))
                        if "invalidusr" not in job_errors:
                            job_errors["invalidusr"] = 1
                            job_errors["invalidusrinfo"] = {"Invalid user: %s for group: %s" % (job_dict['Owner'], job_dict['group_name'])}
                        else:
                            job_errors["invalidusr"] = job_errors["invalidusr"] + 1
                            job_errors["invalidusrinfo"].add("Invalid user: %s for group: %s" % (job_dict['Owner'], job_dict['group_name']))
                        continue

                    # Some jobs have an expression for the request disk causing us to store a string
                    # this should resolve the expression or us an alternative if unable
                    try:
                        job_dict["RequestDisk"] = int(job_dict["RequestDisk"])
                    except Exception as exc:
                        job_dict["RequestDisk"] = int(job_dict["DiskUsage"])
                    try:
                        job_dict["RequestCpus"] = int(job_dict["RequestCpus"])
                    except Exception as exc:
                        logging.debug("Request Cpus not set, setting minimum (1)")
                        job_dict["RequestCpus"] = 1


                    job_dict = trim_keys(job_dict, job_attributes)
                    job_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=job_dict)
                    logging.debug(job_dict)
                    if unmapped:
                        logging.error("attribute mapper found unmapped variables:")
                        logging.error(unmapped)

                    # Check if this item has changed relative to the local cache, skip it if it's unchanged
                    if test_and_set_inventory_item_hash(inventory, job_dict["group_name"], "-", job_dict["global_job_id"], job_dict, new_poll_time, debug_hash=(config.categories["condor_poller.py"]["log_level"]<20)):
                        continue

                    logging.debug("Adding job %s", job_dict["global_job_id"])
                    job_dict["htcondor_host_id"] = config.local_host_id
                    new_job = JOB(**job_dict)
                    try:
                        db_session.merge(new_job)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.error("Failed to merge job entry, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

                if held_jobs > 0:
                    #hold all the jobs
                    logging.info("%s jobs held or to be held due to invalid user or group specifications." % held_jobs)
                    logging.debug("Holding: %s" % held_job_ids)
                    try:
                        logging.debug("Executing job action hold on %s" % condor_host)
                        logging.critical("<< SKIPPING HOLDS, AUTHENTICATION NOT SET UP FOR REMOTE HOLDS >>")
                        #hold_result = condor_session.act(htcondor.JobAction.Hold, held_job_ids)
                        #logging.debug("Hold result: %s" % hold_result)
                        #condor_session.edit(held_job_ids, "HoldReason", '"Invalid user or group name for htondor host %s, held by job poller"' % condor_host)
                    except Exception as exc:
                        logging.error("Failure holding jobs: %s" % exc)
                        logging.error("Aborting cycle...")
                        abort_cycle = True
                        break


                config.update_service_catalog(counter=foreign_jobs)

                        
                if foreign_jobs > 0:
                    logging.info("Ignored total of: %s jobs on %s. Summary:" % (foreign_jobs, condor_host))
                    if "nogrp" in job_errors:
                        logging.info("    %s jobs ignored for missing group name" % job_errors["nogrp"])
                        for item in job_errors["nogrpinfo"]:
                            logging.info("        %s" % item)
                    if "noreq" in job_errors:
                        logging.info("    %s jobs ignored for missing requirements string" % job_errors["noreq"])
                        for item in job_errors["noreqinfo"]:
                            logging.info("        %s" % item)
                    if "invalidgrp" in job_errors:
                        logging.info("    %s jobs ignored & held for submitting to invalid group for host" % job_errors["invalidgrp"])
                        for item in job_errors["invalidgrpinfo"]:
                            logging.info("        %s" % item)
                    if "invalidusr" in job_errors:
                        logging.info("    %s ignored & held for submitting to a group without permission" % job_errors["invalidusr"])
                        for item in job_errors["invalidusrinfo"]:
                            logging.info("        %s" % item)

                # Poll successful, update failure_dict accordingly
                for group in groups:
                    if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                        if group.htcondor_fqdn == condor_host:
                             failure_dict.pop(group.group_name, None)
                    else:
                        if group.htcondor_container_hostname == condor_host:
                            failure_dict.pop(group.group_name, None)


                if abort_cycle:
                    del condor_session
                    config.db_session.rollback()
                    break

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Job updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.error("Failed to commit new jobs, aborting cycle...")
                    logging.error(exc)
                    config.db_session.rollback()
                    signal.signal(signal.SIGINT, config.signals['SIGINT'])
                    time.sleep(config.categories["condor_poller.py"]["sleep_interval_job"])
                    continue

            if delete_cycle:
                # Check for deletes
                delete_obsolete_database_items('Jobs', inventory, db_session, JOB, 'global_job_id', poll_time=new_poll_time, failure_dict=failure_dict, condor_host=config.local_host_id)

                delete_cycle = False

            cycle_count = cycle_count + 1
            if cycle_count >= config.categories["condor_poller.py"]["delete_cycle_interval"]:
                delete_cycle = True
                cycle_count = 0

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])    
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_job"], config)

    except Exception as exc:
        logging.exception("Job Poller while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def job_command_poller():
    multiprocessing.current_process().name = "Job Command Poller"

    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]), "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    Job = config.db_map.classes.condor_jobs
    GROUPS = config.db_map.classes.csv2_groups

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        config.db_open()
        while True:
            logging.debug("Beginning command consumer cycle")
            config.refresh()

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)

            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            db_session = config.db_session
            groups = db_session.query(GROUPS).filter(GROUPS.htcondor_host_id == config.local_host_id)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                # for containers we will have to issue the commands directly to the container and not the condor fqdn so here it takes precedence 
                if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                    condor_hosts_set.add(group.htcondor_container_hostname)
                else:
                    condor_hosts_set.add(group.htcondor_fqdn)

            uncommitted_updates = 0
            for condor_host in condor_hosts_set: 
                try:
                    coll = htcondor.Collector(condor_host)
                    scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, condor_host)
                    condor_session = htcondor.Schedd(scheddAd)
                except Exception as exc:
                    logging.warning("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.debug(exc)
                    continue

                #Query database for any entries that have a command flag
                abort_cycle = False
                for job in db_session.query(Job).filter(Job.hold_job_reason != None):
                    logging.info("Holding job %s, reason=%s" % (job.global_job_id, job.hold_job_reason))
                    local_job_id = job.global_job_id.split('#')[1]
                    try:
                        condor_session.edit([local_job_id,], "JobStatus", "5")
                        condor_session.edit([local_job_id,], "HoldReason", '"%s"' % job.hold_job_reason)

                        job.job_status = 5
                        job.hold_job_reason = None
                        db_session.merge(job)
                        uncommitted_updates = uncommitted_updates + 1

                        if uncommitted_updates >= config.categories['condor_poller.py']['batch_commit_size']:
                            try:
                                db_session.commit()
                                uncommitted_updates = 0
                            except Exception as exc:
                                logging.error("Failed to commit batch of job changes, aborting cycle...")
                                logging.error(exc)
                                abort_cycle = True
                                break

                    except Exception as exc:
                        logging.error("Failed to hold job, rebooting command poller...")
                        logging.error(exc)
                        exit(1)

                if abort_cycle:
                    del condor_session
                    config.db_session.rollback()
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_command"], config)
                    continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.error("Failed to commit job changes, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    config.db_session.rollback()
                    time.sleep(config.categories["condor_poller.py"]["sleep_interval_command"])
                    continue

            logging.debug("Completed command consumer cycle")
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_command"], config)

    except Exception as exc:
        logging.exception("Job poller while loop exception, process terminating...")
        logging.error(exc)
        del condor_session

def machine_poller():
    multiprocessing.current_process().name = "Machine Poller"
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", \
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", "Cpus", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", \
                           "cloud_name", "cs_host_id", "condor_host", "flavor", "TotalDisk"]

    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]), "SQL", "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])


    RESOURCE = config.db_map.classes.condor_machines
    CLOUDS = config.db_map.classes.csv2_clouds
    GROUPS = config.db_map.classes.csv2_groups

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    inventory = {}
    #delete_interval = config.delete_interval
    delete_cycle = False
    #condor_inventory_built = False
    cycle_count = 0
    uncommitted_updates = 0
    failure_dict = {}

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, RESOURCE, 'name', debug_hash=(config.categories["condor_poller.py"]["log_level"]<20), condor_host=config.local_host_id)
        configure_fw(config, logging)
        config.db_open()
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)


            db_session = config.db_session
            groups = db_session.query(GROUPS).filter(GROUPS.htcondor_host_id == config.local_host_id)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                    condor_hosts_set.add(group.htcondor_container_hostname)
                else:
                    condor_hosts_set.add(group.htcondor_fqdn)

            # need to make a data structure so that we can verify the the polled machines actually fit into a valid grp-cloud
            # need to check:
            #       - group_name (in both group_name and machine)
            #       - cloud_name (only in machine?)
            host_groups = {}
            groups = db_session.query(GROUPS).filter(GROUPS.htcondor_host_id == config.local_host_id)
            for group in groups:
                cloud_list = []
                clouds = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group.group_name)
                for cloud in clouds:
                    cloud_list.append(cloud.cloud_name)
                host_groups[group.group_name] = cloud_list

            for condor_host in condor_hosts_set:
                logging.debug("Polling condor host: %s" % condor_host)
                forgein_machines = 0
                try:
                    condor_session = htcondor.Collector(condor_host)
                except Exception as exc:
                    logging.exception("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.error(exc)
                    continue

                #if not condor_inventory_built:
                #    build_inventory_for_condor(inventory, db_session, CLOUDS)
                #    condor_inventory_built = True

                # Retrieve machines.
                try:
                    condor_resources = condor_session.query(
                        ad_type=htcondor.AdTypes.Startd,
                        projection=resource_attributes
                         )
                except Exception as exc:
                    # if we fail we need to mark all these groups as failed so we don't delete the entrys later
                    fail_count = 0
                    for group in groups:
                        if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                            if group.htcondor_fqdn == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]
                        else:
                            if group.htcondor_container_hostname == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]

                    logging.error("Failed to get machines from condor collector object, aborting poll on host %s" % condor_host)
                    logging.error(exc)
                    if fail_count > 3:
                        logging.critical("More than 3 consecutive failed polls on host: %s, Configuration error or condor issues" % condor_host)
                    continue

                abort_cycle = False
                machine_errors = {}
                uncommitted_updates = 0
                for resource in condor_resources:
                    r_dict = dict(resource)
                    if 'group_name' not in r_dict:
                        logging.debug("Skipping resource with no group_name.")
                        forgein_machines = forgein_machines + 1
                        if "nogrp" not in machine_errors:
                            machine_errors["nogrp"] = 1
                        else:
                            machine_errors["nogrp"] = machine_errors["nogrp"] + 1
                        continue
                    if 'cloud_name' not in r_dict:
                        logging.debug("Skipping resource with no cloud_name.")
                        forgein_machines = forgein_machines + 1
                        if "nocld" not in machine_errors:
                            machine_errors["nocld"] = 1
                        else:
                            machine_errors["nocld"] = machine_errors["nocld"] + 1
                        continue
                    if 'cs_host_id' not in r_dict:
                        logging.debug("Skipping resource with no host id.")
                        forgein_machines = forgein_machines + 1
                        if "nohost" not in machine_errors:
                            machine_errors["nohost"] = 1
                        else:
                            machine_errors["nohost"] = machine_errors["nohost"] + 1
                        continue
                        # check group name
                    if r_dict['group_name'] not in host_groups:
                        logging.debug("Skipping resource, group did not match any valid groups for this host: %s" % r_dict['group_name'])
                        forgein_machines = forgein_machines + 1
                        if "badgrp" not in machine_errors:
                            machine_errors["badgrp"] = 1
                        else:
                            machine_errors["badgrp"] = machine_errors["badgrp"] + 1
                        continue
                    # check cs host
                    if str(r_dict['cs_host_id']) != str(config.categories["SQL"]["csv2_host_id"]):
                        logging.debug("Skipping resource with bad cs_host_id: %s, should be %s" % (r_dict['cs_host_id'], config.categories["SQL"]["csv2_host_id"]))
                        forgein_machines = forgein_machines + 1
                        if "badgrp" not in machine_errors:
                            machine_errors["badgrp"] = 1
                        else:
                            machine_errors["badgrp"] = machine_errors["badgrp"] + 1
                        continue
                    # check cloud name
                    if r_dict['cloud_name'] not in host_groups[r_dict['group_name']]:
                        logging.debug("Skipping resource with cloud name that is invalid for group")
                        forgein_machines = forgein_machines + 1
                        if "badcld" not in machine_errors:
                            machine_errors["badcld"] = 1
                        else:
                            machine_errors["badcld"] = machine_errors["badcld"] + 1
                        continue


                    if "Start" in r_dict:
                        r_dict["Start"] = str(r_dict["Start"])
                    r_dict = trim_keys(r_dict, resource_attributes)
                    r_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=r_dict)
                    if unmapped:
                        logging.error("attribute mapper found unmapped variables:")
                        logging.error(unmapped)

                    # Check if this item has changed relative to the local cache, skip it if it's unchanged
                    if test_and_set_inventory_item_hash(inventory, r_dict["group_name"], r_dict["cloud_name"], r_dict["name"], r_dict, new_poll_time, debug_hash=(config.categories["condor_poller.py"]["log_level"]<20)):
                        continue

                    logging.info("Adding/updating machine %s", r_dict["name"])
                    r_dict["htcondor_host_id"] = config.local_host_id
                    new_resource = RESOURCE(**r_dict)
                    try:
                        db_session.merge(new_resource)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge machine entry, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break
                if forgein_machines > 0:
                    logging.info("Ignored %s total forgein machines" % forgein_machines)
                    if "nogrp" in machine_errors:
                        logging.info("    %s ignored for missing group name" % machine_errors["nogrp"])
                    if "badgrp" in machine_errors:
                        logging.info("    %s ignored for bad group name" % machine_errors["badgrp"])
                    if "badcld" in machine_errors:
                        logging.info("    %s ignored for invalid cloud name" % machine_errors["badcld"])
                    if "nocld" in machine_errors:
                        logging.info("    %s ignored for missing cloud name" % machine_errors["nocld"])
                    if "nohost" in machine_errors:
                        logging.info("    %s ignored for missing host id" % machine_errors["nohost"])
                    if "badhost" in machine_errors:
                        logging.info("    %s ignored for missing host id" % machine_errors["badhost"])

                # Poll successful, update failure_dict accordingly
                for group in groups:
                    if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                        if group.htcondor_container_hostname == condor_host:
                             failure_dict.pop(group.group_name, None)
                    else:
                        if group.htcondor_fqdn == condor_host:
                            failure_dict.pop(group.group_name, None)

                           
                if abort_cycle:
                    del condor_session
                    config.db_session.rollback()
                    break

            if 'db_session'in locals() and uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Machine updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.exception("Failed to commit machine updates, aborting cycle...")
                    logging.error(exc)
                    config.db_session.rollback()
                    time.sleep(config.categories["condor_poller.py"]["sleep_interval_machine"])
                    continue

            if delete_cycle:
                # Check for deletes
                delete_obsolete_database_items('Machines', inventory, db_session, RESOURCE, 'name', poll_time=new_poll_time, failure_dict=failure_dict, condor_host=config.local_host_id)
                delete_cycle = False
            config.db_session.commit()
            cycle_count = cycle_count + 1
            if cycle_count > config.categories["condor_poller.py"]["delete_cycle_interval"]:
                delete_cycle = True
                cycle_count = 0
            
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_machine"], config)

    except Exception as exc:
        logging.exception("Machine poller while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def machine_command_poller():
    multiprocessing.current_process().name = "Machine Command Poller"

    # database setup
    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]),  "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    Resource = config.db_map.classes.condor_machines
    GROUPS = config.db_map.classes.csv2_groups
    VM = config.db_map.classes.csv2_vms
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]


    cycle_count = 0


    try:
        config.db_open()
        while True:
            logging.debug("Beginning command consumer cycle")
            config.refresh()

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            db_session = config.db_session
            groups = db_session.query(GROUPS).filter(GROUPS.htcondor_host_id == config.local_host_id)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                    condor_hosts_set.add(group.htcondor_container_hostname)
                else:
                    condor_hosts_set.add(group.htcondor_fqdn)

            uncommitted_updates = 0
            logging.debug(condor_hosts_set)
            
            for condor_host in condor_hosts_set:

                # Get unique group,cloud pairs
                grp_cld_pairs = config.db_connection.execute('select distinct group_name, cloud_name from view_condor_host')

                for pair in grp_cld_pairs:
                    # First check pid of cloud entry
                    logging.info("Checking child pid for pair: %s, %s" % (pair.group_name, pair.cloud_name))
                    pid_active = check_pair_pid(pair, config, CLOUD)
                    if pid_active:
                        logging.info("Child pid still active...")
                    if not pid_active:
                        #subprocess this eventually
                        logging.info("No pid active, starting commands")
                        #process_group_cloud_commands(pair, condor_host)
                        p = Process(target=process_group_cloud_commands, args=(pair, condor_host))
                        p.start()
                    
            
            try:
                config.db_session.commit()
            except Exception as exc:
                logging.error("Error during final commit, likely that a vm was removed from database before final terminate update was comitted..")
                logging.exception(exc)

            
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_command"], config)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)

def worker_gsi_poller():
    multiprocessing.current_process().name = "Worker GSI Poller"

    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]), 'ProcessMonitor'], pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)

            config.db_open()

            condor_dict = get_condor_dict(config, logging)

            deleted = []
            condor = socket.gethostname()
            worker_cert = {}
            if 'GSI_DAEMON_CERT' in htcondor.param:
                try:
                    worker_cert['subject'], worker_cert['eol'] = get_gsi_cert_subject_and_eol(config.condor_poller['condor_worker_cert'])
                    worker_cert['cert'] = zip_base64(config.condor_poller['condor_worker_cert'])
                except:
                    logging.info("Unable to find condor_worker_cert from local configuration.")

                try:
                    worker_cert['key'] = zip_base64(config.condor_poller['condor_worker_key'])
                    if worker_cert['key'] == 'unreadable':
                        worker_cert['eol'] = -999999
                except Exception as ex:
                    logging.info("Unable to find condor_worker_key from local configuration")
                    logging.info(ex)
            if worker_cert:
                try:
                    config.db_session.execute('insert into condor_worker_gsi (htcondor_fqdn, htcondor_host_id, worker_dn, worker_eol, worker_cert, worker_key) values("%s",%d "%s", %d, "%s", "%s");' % (condor, config.local_host_id, if_null(worker_cert['subject']), worker_cert['eol'], if_null(worker_cert['cert']), if_null(worker_cert['key'])))
                    config.db_session.commit()

                    if worker_cert['subject']:
                        logging.info('Condor host: "%s", condor_worker_gsi inserted.' % condor)
                    else:
                        logging.info('Condor host: "%s", condor_worker_gsi (not configured) inserted.' % condor)

                except Exception as ex:
                    if not (isinstance(ex, sqlalchemy.exc.IntegrityError) and str(ex.orig)[1:-1].split(',')[0] == '1062'):
                        logging.warning('Condor host: "%s", condor_worker_gsi insert failed, exception: %s' % (condor, ex))

                    try:
                        config.db_session.execute('update condor_worker_gsi set %s, htcondor_host_id=%d,worker_eol=%d,%s,%s where htcondor_fqdn="%s";' % (
                            if_null(worker_cert['subject'], col='worker_dn'),
                            config.local_host_id,
                            worker_cert['eol'],
                            if_null(worker_cert['cert'], col='worker_cert'),
                            if_null(worker_cert['key'], col='worker_key'),
                            condor))
                        config.db_session.commit()

                        if worker_cert['subject']:
                            logging.info('Condor host: "%s", condor_worker_gsi updated.' % condor)
                        else:
                            logging.info('Condor host: "%s", condor_worker_gsi (not configured) updated.' % condor)

                    except Exception as ex:
                        config.db_session.rollback()

                        if worker_cert['subject']:
                            logging.error('Condor host: "%s", condor_worker_gsi update failed, exception: %s' % (condor, ex))
                        else:
                            logging.error('Condor host: "%s", condor_worker_gsi (not configured) update failed, exception: %s' % (condor, ex))

            else:
                logging.warning('Condor host: "%s", GSI not enabled, nothing to do...' % condor)

            config.db_close()
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            wait_cycle(cycle_start_time, poll_time_history, config.categories['condor_poller.py']['sleep_interval_worker_gsi'], config)

    except Exception as exc:
        logging.exception("Worker GSI while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()



def condor_gsi_poller():
    multiprocessing.current_process().name = "Condor GSI Poller"

    config = Config(sys.argv[1], [os.path.basename(sys.argv[0]), 'ProcessMonitor'], pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    config.db_open()

    try:
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)


            condor = socket.gethostname()
            condor_cert = {}
            if 'GSI_DAEMON_CERT' in htcondor.param:
                condor_hostcert = htcondor.param['GSI_DAEMON_CERT']
            else:
                try:
                    condor_hostcert = config.condor_poller.get("condor_hostcert")
                except:
                    condor_hostcert = None

            if condor_hostcert:
                condor_cert['subject'], condor_cert['eol'] = get_gsi_cert_subject_and_eol(condor_hostcert)
            
            if condor_cert:
                try:
                    config.db_session.execute('update csv2_groups set %s,htcondor_gsi_eol=%d where htcondor_fqdn="%s";' % (if_null(condor_cert['subject'], col='htcondor_gsi_dn'), condor_cert['eol'], condor))
                    config.db_session.commit()

                    if condor_cert['subject']:
                        logging.info('Condor host: "%s" GSI updated.' % condor)
                    else:
                        logging.info('Condor host: "%s" GSI (not configured) updated.' % condor)

                except Exception as ex:
                    config.db_session.rollback()

                    if condor_cert['subject']:
                        logging.error('Condor host: "%s" GSI update failed, exception: %s' % (condor, ex))
                    else:
                        logging.error('Condor host: "%s",  GSI (not configured) update failed, exception: %s' % (condor, ex))

            else:
                logging.warning('Unable to retrieve certificate')

            config.db_session.rollback()

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            wait_cycle(cycle_start_time, poll_time_history, config.categories['condor_poller.py']['sleep_interval_condor_gsi'], config)

    except Exception as exc:
        logging.exception("Condor GSI while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

if __name__ == '__main__':

    process_ids = {
        'job_command':      job_command_poller,
        'job':              job_poller,
        'machine_command':  machine_command_poller,
        'machine':          machine_poller,
        'condor_gsi':       condor_gsi_poller,
        'worker_gsi':       worker_gsi_poller,
    }

    db_category_list = [os.path.basename(sys.argv[0]), "ProcessMonitor", "general", "signal_manager"]

    procMon = ProcessMonitor(config_params=db_category_list, pool_size=3, process_ids=process_ids, config_file=sys.argv[1])
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting cscollector - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            config.update_service_catalog()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")
    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
