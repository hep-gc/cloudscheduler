# The purpose of this file is to get some information from the
# local cloud and place it in a database for use by cloudscheduler
#
# Target data sets:
#       Flavor information
#       Quota Information
#       Image Information
#       Network Information
#
# This file also polls the openstack clouds for live VM information and inserts it into the database
import multiprocessing
from multiprocessing import Process
import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from attribute_mapper.attribute_mapper import map_attributes

import libvirt
import config

## UTILITY FUNCTIONS
#

def get_limit_data(conn):
#Get memory and cpu limits for current node
    try:
        limits = []
        limits['maxVcpu'] = [conn.getMaxVcpus(None)]
        nodeinfo = conn.getInfo()
        limits['memory'] = [nodeinfo[1]]
        return limits
    except Exception as err:
        logging.error("Unable to retrieve limit data")
        logging.error(err)
        return False

def get_network_data(conn):
#List virtual networks
    return conn.listNetworks()

def get_vm_list(conn):
#Get current domains, active and inactive
    return conn.listAllDomains(0)

def terminate_vm(conn, vm):
#Kill vm
    try:
        dom = conn.lookupByName(vm.name)
        dom.destroy()
        return True
    except Exception as exc:
        logging.error("Unable to terminate vm: %s", vm.hostname)
        logging.error(exc)
        return False


## PROCESS FUNCTIONS
#

# This process thread will be responsible for polling the list of VMs from each registered
# openstack cloud and reporting their state back to the database for use by cloud scheduler
#

def vm_poller():
    print("In VM poller")
    multiprocessing.current_process().name = "VM Poller"
    while True:
        logging.debug("Begining poll cycle")
        Base = automap_base()
        engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Vm = Base.classes.csv2_vms
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "localhost")

        # Itterate over cloud list
        for cloud in cloud_list:
            conn = libvirt.open('qemu:///system')
            if conn is None:
                logging.debug("Can't connect to hypervisor")
                continue

            # get server list
            vm_list = get_vm_list(conn)
            if vm_list:
                for vm in vm_list:
                    logging.debug("Found VM %s", vm)
                    if not vm.isActive():
                        continue
                     #Need to get readable state imformation
                    vm_dict = {
                        'group_name': cloud.group_name,
                        'cloud_name': cloud.cloud_name,
                        'hostname': vm.name(),
                        'vmid': vm.ID(),
                        'status': vm.state(),
                        #'task': vm.__dict__.get("OS-EXT-STS:task_state"),
                        #'power_state': vm.__dict__.get("OS-EXT-STS:power_state"),
                        'last_updated': int(time.time())
                    }

                    vm_dict = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict)
                    new_vm = Vm(**vm_dict)
                    logging.debug(new_vm)
                    #db_session.merge(new_vm)
            #db_session.commit()
        logging.debug("Poll cycle complete, sleeping...")
        # This cycle should be reasonably fast such that the scheduler will always have the most
        # up to date data during a given execution cycle.
        time.sleep(config.vm_sleep_interval)

    return None


def limitPoller():
    print("In limit poller")
    multiprocessing.current_process().name = "Limit Poller"

    while True:
        #thingdo
        Base = automap_base()
        engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Limit = Base.classes.cloud_limits
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")

        current_cycle = int(time.time())
        for cloud in cloud_list:
            conn = libvirt.open('qemu:///system')

            logging.debug("Polling limits")
            limits_dict = get_limit_data(conn)
            limits_dict['group_name'] = cloud.group_name
            limits_dict['cloud_name'] = cloud.cloud_name
            limits_dict['last_updated'] = int(time.time())
            limits_dict = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict)
            new_limits = Limit(**limits_dict)
            #db_session.merge(new_limits)

            #now remove any that were not updated
            limit_to_delete = db_session.query(Limit).filter(
                Limit.last_updated < current_cycle,
                Limit.group_name == cloud.group_name,
                Limit.cloud_name == cloud.cloud_name)
            for limit in limit_to_delete:
                logging.info("Cleaning up limit %s", limit)
                #db_session.delete(limit)

        #db_session.commit()
        logging.debug("End of cycle, sleeping...")
        time.sleep(config.limit_sleep_interval)

    return None

def networkPoller():
    print("In network poller")
    multiprocessing.current_process().name = "Network Poller"
    last_cycle = 0

    while True:
        #thingdo
        Base = automap_base()
        engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        db_session.autoflush = False
        Network = Base.classes.cloud_networks
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "localhost")

        current_cycle = int(time.time())
        for cloud in cloud_list:
            conn = libvirt.open(None)
            if conn is None:
                logging.debug("Failed to open connection to hypervisor")
                continue
            net_list = get_network_data(conn)
            for network in net_list:
                network_dict = {
                    'group_name': cloud.group_name,
                    'cloud_name': cloud.cloud_name,
                    'name': network.name(),
                    'bridge_name': network.bridgeName(),
                    'id': network.UUIDString(),
                    'last_updated': int(time.time())
                }
                network_dict = map_attributes(
                    src="os_networks",
                    dest="csv2",
                    attr_dict=network_dict)
                new_network = Network(**network_dict)
                #db_session.merge(new_network)

            #now remove any that were not updated
            net_to_delete = db_session.query(Network).filter(
                Network.last_updated <= last_cycle,
                Network.group_name == cloud.group_name,
                Network.cloud_name == cloud.cloud_name)
            for net in net_to_delete:
                logging.info("Cleaning up network: %s", net)
                #db_session.delete(net)

        #db_session.commit()
        last_cycle = current_cycle
        logging.debug("End of cycle, sleeping...")
        time.sleep(config.network_sleep_interval)

    return None

def vmCleanUp():
    print("In VM cleanup")
    multiprocessing.current_process().name = "VM Cleanup"
    last_cycle = 0
    while True:
        current_cycle_time = time.time()
        #set up database objects
        logging.debug("Begining cleanup cycle")
        Base = automap_base()
        engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Vm = Base.classes.csv2_vms
        Cloud = Base.classes.csv2_group_resources


        if last_cycle == 0:
            logging.info("First cycle, sleeping for now...")
            #first cycle- just sleep for the first while waiting for db updates.
            last_cycle = current_cycle_time
            time.sleep(config.vm_cleanup_interval)
            continue

        # check for vms that have dissapeared since the last cycle
        vm_to_delete = db_session.query(Vm).filter(Vm.last_updated <= last_cycle)
        for vm in vm_to_delete:
            logging.info("Cleaning up VM: %s", vm)
            #db_session.delete(vm)

        # check for vms that have been marked for termination
        vm_to_destroy = db_session.query(Vm).filter(Vm.terminate == 1)
        for vm in vm_to_destroy:
            logging.info("VM marked for termination... terminating: %s", vm.hostname)
            # terminate vm
            # need to get cloud data from csv2_group_resources using group_name + cloud_name from vm
            cloud = db_session.query(Cloud).filter(
                Cloud.cloud_type == "localhost",
                Cloud.group_name == vm.group_name,
                Cloud.cloud_name == vm.cloud_name)
            conn = libvirt.open(None)
            if conn is None:
                logging.debug("Failed to open connection to hypervisor")
                continue
            # returns true if vm terminated, false if an error occured
            # probably wont need to use this result outside debugging as
            # deleted VMs should be removed on the next cycle
            result = terminate_vm(conn, vm)

        #db_session.commit()

        last_cycle = current_cycle_time
        time.sleep(config.vm_cleanup_interval)
    return None


## MAIN
#
if __name__ == '__main__':

    print("In main")
    logging.basicConfig(
        filename=config.poller_log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-12s - %(levelname)s - %(message)s')
    processes = []

    p_vm_poller = Process(target=vm_poller)
    processes.append(p_vm_poller)
    p_vm_cleanup = Process(target=vmCleanUp)
    processes.append(p_vm_cleanup)
    #p_limit_poller = Process(target=limitPoller)
    #processes.append(p_limit_poller)
    p_network_poller = Process(target=networkPoller)
    processes.append(p_network_poller)

    # Wait for keyboard input to exit
    try:
        for process in processes:
            logging.debug(process)
            process.start()
        while True:
            for process in processes:
                if not process.is_alive():
                    logging.error("%s process died!", process.name)
                    logging.error("Restarting %s process...", process.name)
                    process.start()
                time.sleep(1)
            time.sleep(10)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
