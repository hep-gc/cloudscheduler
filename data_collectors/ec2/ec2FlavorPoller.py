#!/usr/bin/env python3
import multiprocessing
import logging
import socket
import time
import sys
import os
import json
import urllib.request

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


# Support Functions

# This function checks that the local files exist, and that they are not older than a week
def check_instance_types(config):
    REGIONS = config.db_map.classes.ec2_regions

    db_session = config.db_session
    seven_days_ago = time.time() - 60*60*24*7

    json_path = config.region_flavor_file_location
    region_list = db_session.query(REGIONS)

    for region in region_list:
        region_path = json_path + "/" + region.region + "/instance_types.json"
        no_file = False
        if not os.path.exists(json_path + "/" + region.region):
            os.mkdir(json_path + "/" + region.region)
        if not os.path.exists(region_path):
            open(region_path, 'a').close()
            no_file = True
        if os.path.getctime(region_path) < seven_days_ago or no_file:
            logging.info("%s out of date, downloading new version" % region_path)
            # Download new version
            try:
                refresh_instance_types(config, region_path, region.region)
            except Exception as exc:
                logging.error("Unable to refresh instance types for region %s error:" % region.region)
                logging.error(exc)

#This function downloads the new regional instance types file and parses them into the ec2_instance_types table
def refresh_instance_types(config, file_path, region):
    EC2_INSTANCE_TYPES = config.db_map.classes.ec2_instance_types
    url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/" + region + "/index.json"
    try:
        urllib.request.urlretrieve(url, file_path)
    except Exception as exc:
        logging.error("unable to download %s:" % url)
        logging.error(exc)
        logging.error("Skipping region %s" % region)

    #ok we've got the new file, lets parse it into our trusty database
    fd = open(file_path)
    itxsku = json.loads(fd.read())
    fd.close()

    ifs = {}
    its = {}
    pps = {}
    for sku in itxsku['products']:
        if itxsku['products'][sku]['productFamily'] == 'Compute Instance':
            iff = itxsku['products'][sku]['attributes']['instanceFamily'] 
            if iff not in ifs:
                ifs[iff] = True

            pp = itxsku['products'][sku]['attributes']['physicalProcessor'] 
            if pp not in pps:
                pps[pp] = True

            it = itxsku['products'][sku]['attributes']['instanceType'] 
            if it not in its:
                if sku in itxsku['terms']['OnDemand']:
                    cost = 0.0
                    for offer in itxsku['terms']['OnDemand'][sku]:
                        for rate in itxsku['terms']['OnDemand'][sku][offer]['priceDimensions']:
                            cost = max(cost, float(itxsku['terms']['OnDemand'][sku][offer]['priceDimensions'][rate]['pricePerUnit']['USD']))

                try:

                    its[it] = {
                        'region': region,
                        'instance_type': it,
                        'operating_system': itxsku['products'][sku]['attributes']['operatingSystem'],
                        'instance_family': itxsku['products'][sku]['attributes']['instanceFamily'],
                        'processor': itxsku['products'][sku]['attributes']['physicalProcessor'],
                        'storage': itxsku['products'][sku]['attributes']['storage'],
                        'cores': int(itxsku['products'][sku]['attributes']['vcpu']),
                        'memory': float(itxsku['products'][sku]['attributes']['memory'].replace(',', '').split()[0]),
                        'mem_per_core': float(itxsku['products'][sku]['attributes']['memory'].replace(',', '').split()[0]) / int(itxsku['products'][sku]['attributes']['vcpu']),
                        'cost_per_hour': cost
                    }
                except Exception as exc:
                    logging.error("unable to create instance type dictionary:")
                    logging.error(exc)
                    logging.error("Attributes: %s" % itxsku['products'][sku]['attributes'])

    # delete old entries then load the its dict into the table
    old_its = config.db_session.query(EC2_INSTANCE_TYPES).filter(EC2_INSTANCE_TYPES.region == region)
    for it in old_its:
        config.db_session.delete(it)
    config.db_session.commit()
    # now add the updated list
    for it in its:
        new_it = EC2_INSTANCE_TYPES(**its[it])
        try:
            config.db_session.merge(new_it)
        except Exception as exc:
            logging.exception("Failed to merge instance type entry %s cancelling:" % it)
            logging.error(exc)
            break
    config.db_session.commit()

    return False


# Poller Functions

def flavor_poller():
    #setup
    multiprocessing.current_process().name = "Flavor Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ec2_retrieve_flavor_files.py"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=20)

    FLAVOR = config.db_map.classes.cloud_flavors
    CLOUD = config.db_map.classes.csv2_clouds
    FILTERS = config.db_map.classes.ec2_instance_type_filters
    CONFIG = config.db_map.classes.csv2_configuration

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

            # First check that our ec2 instance types table is up to date:
            check_instance_types(config)
            '''
            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")
            region_failure_dict = {}
            grp_flav_filter_dict = {}
            
            save_at = config.region_flavor_file_location
            if save_at == "False":
                logging.error("Could not get region instance type file location...")

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
                    with open(save_at+"/{}/instance_types.json".format(region), 'r') as f:
                        flav_list = json.load(f)
                    logging.debug("Got local copy of flavor info for region - {}".format(region))
                except Exception as exc:
                    logging.error("Failed to retrieve flavors JSON for region - {0} from local copy at {1}/{0}/instance_types, skipping this region".format(region,save_at))
                    logging.exception(exc)
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

            '''
            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_status)


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
