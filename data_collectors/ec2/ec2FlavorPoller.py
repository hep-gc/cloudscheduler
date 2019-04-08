import multiprocessing
import logging
import socket
import time
import sys
import os
import requests
import json

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor
from cloudscheduler.lib.signal_manager import register_signal_receiver


from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    foreign, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    start_cycle, \
    wait_cycle


def flavor_poller():
    #setup
    multiprocessing.current_process().name = "Flavor Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)

    FLAVOR = config.db_map.classes.cloud_flavors
    CLOUD = config.db_map.classes.csv2_clouds
    FILTERS = config.db_map.classes.ec2_instance_type_filters

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
   
   # register_signal_receiver(config, "insert_csv2_clouds")
   # register_signal_receiver(config, "update_csv2_clouds")


    while True:
        inventory = get_inventory_item_hash_from_database(config.db_engine, FLAVOR, 'name', debug_hash=(config.log_level<20), cloud_type='amazon')
        try:
            #poll flavors
            logging.debug("Beginning flavor poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session
            
            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")
            region_failure_dict = {}
            grp_flav_filter_dict = {}

            # Build unique region dict
            unique_region_dict = {}
            for cloud in cloud_list:
                if cloud.region not in unique_region_dict:
                    unique_region_dict[cloud.region] = {
                        "group-cloud": [(cloud.group_name, cloud.cloud_name)]
                    }
                else:
                    unique_region_dict[cloud.region]["group-cloud"].append((cloud.group_name, cloud.cloud_name))

            for region in unique_region_dict:
                # Skip China, info not available in AWS offers file
                if region.split("-", 1)[0] == "cn":
                    logging.debug("Skipping flavors in China - {}".format(region))
                    continue
                logging.debug("Processing flavors from region - {}".format(region))
                try:
                    flav_list = False
                    url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.json".format(region)
                    resp = requests.get(url)
                    logging.debug("Got response")
                    resp.raise_for_status()
                    flav_list = resp.json()
                except Exception as exc:
                    logging.error("Failed to retrieve flavors JSON for region - {} from Amazon pricing url, skipping this region".format(region))
                    logging.exception(exc)
                    if exc is None or exc == "":
                        logging.debug(repr(exc))
                    for region in unique_region_dict:
                        if region not in region_failure_dict:
                            region_failure_dict[region] = 1
                        else:
                            region_failure_dict[region] += 1
                        if region_failure_dict[region] > 3:
                            logging.error("Failure threshold limit reached for region - {}, manual action required, reporting error for all clouds in region".format(region))
                            for (group,cloud) in unique_region_dict[region]["group-cloud"]:
                                config.incr_cloud_error(group, cloud)
                    continue

                if not flav_list:
                    logging.info("No flavors defined for region - {}, skipping this region...".format(region))
                    continue
                for region in unique_region_dict:
                    region_failure_dict.pop(region, None)
                    for (group,cloud) in unique_region_dict[region]["group-cloud"]:
                        config.reset_cloud_error(group, cloud)
                
                # Get flavor filters from db for each group
                for (group,cloud) in unique_region_dict[region]["group-cloud"]:
                    flav_filter_list = db_session.query(FILTERS).filter(FILTERS.group_name == group)
                    if flav_filter_list != None:
                        for filter_entry in flav_filter_list:
                            #flav_filter = filter_entry
                            grp_flav_filter_dict[group] = filter_entry
                            break

                
                # Process flavors for clouds in this region
                unique = set()
                uncommitted_updates = 0
                for product in flav_list["products"]:
                    if flav_list["products"][product]["productFamily"] != "Compute Instance" or flav_list["products"][product]["attributes"]["instanceType"] in unique or \
                            flav_list["products"][product]["attributes"]["operatingSystem"] == "Windows":
                        continue
                    flavor_name = flav_list["products"][product]["attributes"]["instanceType"]
                    
                    for (group,cloud) in unique_region_dict[region]["group-cloud"]:
                        try:
                            flav_filter = grp_flav_filter_dict[group]
                        except KeyError:
                            flav_filter = None
                            logging.debug("No flavor filters found for group {}".format(group))

                        # JSON format: "memory" : "1,952 GiB"
                        ram = flav_list["products"][product]["attributes"]["memory"].split(" ", 1)[0].split(",")
                        if len(ram) == 1:
                            ram = ram[0]
                        else:
                            ram = "".join(ram)
                        ram = float(ram)
                        
                        # Filter flavors based on the specified attribute values
                        if flav_filter:
                            if not (flav_filter.families == None or flav_list["products"][product]["attributes"]["instanceFamily"].lower() in flav_filter.families.lower().split(',')) or \
                                    not (flav_filter.processor_types == None or \
                                        any([True if x in flav_filter.processor_types.lower().split(',') else False for x in flav_list["products"][product]["attributes"]["physicalProcessor"].lower().split(' ')])) or \
                                    not (flav_filter.cores == None or flav_list["products"][product]["attributes"]["vcpu"] in flav_filter.cores.split(',')) or \
                                    not (flav_filter.min_memory_gigabytes_per_core == None or (ram/float(flav_list["products"][product]["attributes"]["vcpu"])) >= float(flav_filter.min_memory_gigabytes_per_core)) or \
                                    not (flav_filter.max_memory_gigabytes_per_core == None or (ram/float(flav_list["products"][product]["attributes"]["vcpu"])) <= float(flav_filter.max_memory_gigabytes_per_core)):
                                continue
                   
                        # Ram in db is MB
                        ram = int(ram*1000)
                    
                        # JSON format: "storage" : "2 x 1,920 SSD"
                        # or           "storage" : "EBS only"
                        disk = flav_list["products"][product]["attributes"]["storage"]
                        if disk == "EBS only":
                            disk = 0
                        else:
                            try:
                                disk = disk.split(" ")
                                d = disk[2].split(",")
                                if len(d) == 1:
                                    disk = int(disk[0])*int(disk[2])
                                else:
                                    disk = int(disk[0])*int("".join(d))
                            except Exception as exc:
                                logging.error("Could not parse disk info for region: {0}, flavor: {1}. Format: \"storage\" : \"{2}\" was not as expected. Skipping flavor...".format(
                                    region, flavor_name, disk
                                ))
                                logging.error(exc)
                                continue
                    
                        swap = 0
                        vcpus = flav_list["products"][product]["attributes"]["vcpu"]
                        usagetype = flav_list["products"][product]["attributes"]["usagetype"]
                        
                        flav_dict = {
                            'group_name': group,
                            'cloud_name': cloud,
                            'cloud_type': 'amazon',
                            'name': flavor_name,
                            'ram': ram,
                            'cores': vcpus,
                            'id': flavor_name,
                            'swap': swap,
                            'disk': disk,
                            'last_updated': new_poll_time
                        }
                        
                        flav_dict, unmapped = map_attributes(src="ec2_flavors", dest="csv2", attr_dict=flav_dict)
                        if unmapped:
                            logging.error("Unmapped attributes found during mapping, discarding:")
                            logging.error(unmapped)                

                        if test_and_set_inventory_item_hash(inventory, group, cloud, flavor_name, flav_dict, new_poll_time, debug_hash=(config.log_level<20)):
                            continue
                          
                        new_flav = FLAVOR(**flav_dict)
                        try:
                            db_session.merge(new_flav)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge flavor entry for {0}::{1}::{2}, aborting cycle...".format(group, cloud, flavor_name))
                            logging.error(exc)
                            abort_cycle = True
                            break

                    unique.add(flavor_name)
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:
                        db_session.commit()
                        logging.info("Flavor updates comitted: {}".format(uncommitted_updates))
                    except Exception as exc:
                        logging.exception("Failed to commit flavor updates for region {}, aborting cycle...".format(region))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                db_session.close()
                time.sleep(config.sleep_interval_flavor)
                continue
            

            # Scan the EC2 flavors in the database, removing each one that was not updated in the inventory.
            for region in region_failure_dict:
                for (group, cloud) in unique_region_dict[region]["group-cloud"]:
                    failure_dict[group+cloud] = region_failure_dict[region]

            delete_obsolete_database_items('Flavor', inventory, db_session, FLAVOR, 'name', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type='amazon')

            config.db_close()
            del db_session


        except Exception as exc:
            logging.error("Unhandled exception during regular flavor polling:")
            logging.exception(exc)


    return -1


def service_registrar():
    multiprocessing.current_process().name = "Service Registrar"

    # database setup
    db_category_list = [os.path.basename(sys.argv[0]), "general"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=4)
    SERVICE_CATALOG = config.db_map.classes.csv2_service_catalog

    service_fqdn = socket.gethostname()
    service_name = "csv2-ec2"

    while True:
        config.db_open()

        service_dict = {
            "service":             service_name,
            "fqdn":                service_fqdn,
            "last_updated":        None,
            "yaml_attribute_name": "cs_condor_remote_ec2_poller"
        }
        service = SERVICE_CATALOG(**service_dict)
        try:
            config.db_session.merge(service)
            config.db_close(commit=True)
        except Exception as exc:
            logging.exception("Failed to merge service catalog entry, aborting...")
            logging.error(exc)
            return -1

        time.sleep(config.sleep_interval_registrar)

    return -1

## Main.

if __name__ == '__main__':
    process_ids = {
        'flavor':                flavor_poller,
        'registrar':             service_registrar
    }

    procMon = ProcessMonitor(os.path.basename(sys.argv[0]), pool_size=9, orange_count_row='csv2_ec2_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    logging.info("**************************** starting ec2 poller - Running %s *********************************" % version)


    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
