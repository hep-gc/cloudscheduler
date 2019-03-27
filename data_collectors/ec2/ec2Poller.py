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

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
   # register_signal_receiver(config, "insert_csv2_clouds")
   # register_signal_receiver(config, "update_csv2_clouds")


    while True:
        try:
            #poll flavors
            logging.debug("Beginning flavor poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session
            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")
            region_dict = {}
            #TODO
            # BUILD REGION LIST from cloud_list
            # get json dump from amazon pricing url
            # parse json for entries from that region

            for cloud in cloud_list:
                if cloud.region not in region_dict:
                    region_dict[cloud.region] = {
                        'group-cloud': [(cloud.group_name, cloud.cloud_name)]
                    }
                else:
                    region_dict[cloud.region]['group-cloud'].append((cloud.group_name, cloud.cloud_name))

            #print(region_dict.items())

            for region in region_dict:
                # Skip China, info not available in aws offers file
                if region.split("-", 1)[0] == "cn":
                    continue
                logging.debug("Processing flavours from region - %s" % region)
                try:
                    url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.json".format(region)
                    resp = requests.get(url)
                    resp.raise_for_status()
                    flav_list = resp.json()
                except Exception as exc:
                    logging.error("Failed to retrieve flavours JSON for {} from amazon pricing url".format(region))
                    logging.debug(exc)
                    if exc is None or exc == "":
                        logging.debug(repr(exc))
                    continue

                if flav_list:
                    unique = set()
                    for product in flav_list["products"]:
                        if flav_list["products"][product]["productFamily"] != "Compute Instance" or flav_list["products"][product]["attributes"]["instanceType"] in unique:
                            continue
                        ram = flav_list["products"][product]["attributes"]["memory"].split(" ", 1)[0]
                        ram = ram.split(",")
                        if len(ram) == 1:
                            ram = int(float(ram[0])*1000)
                        else:
                            ram = int(float("".join(ram))*1000)
                          
                        disk = flav_list["products"][product]["attributes"]["storage"]
                        if disk == "EBS only":
                            ephemeral_disk = 0
                            disk = 0
                        else:
                            disk = disk.split(" ")
                            d = disk[2].split(",")
                            if len(d) == 1:
                                disk = int(disk[0])*int(disk[2])
                            else:
                                disk = int(disk[0])*int("".join(d))
                            ephemeral_disk = 0
                        
                        swap = 0
                        if flav_list["products"][product]["attributes"]["instanceType"] == "c1.medium" or flav_list["products"][product]["attributes"]["instanceType"] == "m1.small":
                            # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-swap-volumes.html
                            swap = 900

                        for (group,cloud) in region_dict[region]['group-cloud']:
                            flav_dict = {
                                'group_name': group,
                                'cloud_name': cloud,
                                'name': flav_list["products"][product]["attributes"]["instanceType"],
                                'ram': ram,
                                'vcpus': flav_list["products"][product]["attributes"]["vcpu"],
                                'id': flav_list["products"][product]["attributes"]["usagetype"],
                                'swap': swap,
                                'disk': disk,
                                'ephemeral_disk': ephemeral_disk,
                                #'is_public': ,
                                'last_updated': new_poll_time
                            }
                            
                            flav_dict, unmapped = map_attributes(src="os_flavors", dest="csv2", attr_dict=flav_dict)
                            if unmapped:
                                logging.error("Unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)                

                            #print(flav_dict)
                        unique.add(flav_list["products"][product]["attributes"]["instanceType"])
                    

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
