import multiprocessing
import logging
import socket
import time
import sys
import os
import datetime
from dateutil import tz
import copy

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor
from cloudscheduler.lib.signal_manager import register_signal_receiver

from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    start_cycle, \
    wait_cycle
#   get_last_poll_time_from_database, \
#   set_inventory_group_and_cloud, \
#   set_inventory_item, \

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import func

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
from neutronclient.v2_0 import client as neuclient
from cinderclient import client as cinclient

import boto3


# The purpose of this file is to get some information from the various registered
# openstack clouds and place it in a database for use by cloudscheduler
#
# Target data sets (should all be available from novaclient):
#       Flavor information
#       Quota Information
#       Image Information
#       Network Information
#
# This file also polls the openstack clouds for live VM information and inserts it into the database

## Poller sub-functions.
def _get_ec2_session(cloud):
    return boto3.session.Session(region_name=cloud.region,
                                 aws_access_key_id=cloud.username,
                                 aws_secret_access_key=cloud.password)

def _get_ec2_client(session):
    return session.client('ec2')

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



## Poller functions.

def flavor_poller():
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
            The below code should be updated to populate the cloud_flavors table using the data
            from the ec2_instance_types table. The data should be filtered using a default + custom filters
            in the ec2_instance_type_filters table.
            '''


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

def image_poller():
    multiprocessing.current_process().name = "Amazon Image Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)

    IMAGE = config.db_map.classes.cloud_images
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0, 0, 0, 0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, IMAGE, 'id',
                                                          debug_hash=(config.log_level < 20), cloud_type='amazon')
        while True:
            try:
                logging.debug("Beginning image poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl + cloud.project + cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region]['groups'].append(
                            (cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing Images from cloud - %s" % cloud_name)
                    session = _get_ec2_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.error("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve all images for this cloud.
                    client = _get_ec2_client(session)
                    try:
                        '''
                        users2 = ['self','all']
                        filters = [ {'Name': 'owner-alias', 'Values':['amazon']},
                            #{'Name': 'root-device-type', 'Values':['instance-store']},
                            {'Name': 'image-type', 'Values':['machine']},
                            {'Name': 'architecture', 'Values':['x86_64']},
                            {'Name': 'state', 'Values':['available']},
                            {'Name': 'virtualization-type', 'Values':['hvm']},
                            #{'Name': 'name', 'Values':['amzn2-ami-hvm-2.0.????????-x86_64-gp2']}# <- Amazon Linux 2
                            #{'Name': 'name', 'Values':['amzn-ami-hvm-????.??.?.????????-x86_64-gp2']}# <- Amazon Linux
                            #{'Name': 'name', 'Values':['ubuntu-xenial-16.04-amd64-server-*']}# <- Ubuntu Server 16.04 LTS
                            #{'Name': 'name', 'Values':['RHEL-7.5_HVM_GA*']}# <- RHEL 7.5
                            #{'Name': 'name', 'Values':['suse-sles-15-v????????-hvm-ssd-x86_64']}# <- SUSE Linux Enterprise Server 15
                        ]
                        '''
                        image_list = client.describe_images() # Can pass in filters here: client.describe_images(ExecutableUsers=user_list, Filters=filters)
                    except Exception as ex:
                        logging.error("Failed to retrieve image data for %s, skipping this cloud..." % cloud_name)
                        logging.error(ex)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if image_list is False:
                        logging.info("No images defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm + cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    uncommitted_updates = 0
                    for image in image_list['Images']:
                        if image['BlockDeviceMappings']:
                            size = 0
                            for device in image['BlockDeviceMappings']:
                                if 'Ebs' in device.keys():
                                    size += device['Ebs']['VolumeSize']


                        for groups in unique_cloud_dict[cloud]['groups']:
                            group_n = groups[0]
                            cloud_n = groups[1]

                            img_dict = {
                                'group_name': group_n,
                                'cloud_name': cloud_n,
                                'container_format': None,
                                'disk_format': image['RootDeviceType'],
                                'min_ram': 0,
                                'id': image['ImageId'],
                                'size': size,
                                'visibility': image['Public'],
                                'min_disk': 0,
                                'name': image['Name'],
                                'last_updated': new_poll_time
                            }

                            img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=img_dict)
                            if unmapped:
                                logging.error("Unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, image.id, img_dict,
                                                                new_poll_time, debug_hash=(config.log_level < 20)):
                                continue

                            new_image = IMAGE(**img_dict)
                            try:
                                db_session.merge(new_image)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception(
                                    "Failed to merge image entry for %s::%s::%s:" % (group_n, cloud_n, image.name))
                                logging.error(exc)
                                abort_cycle = True
                                break

                    del client
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        try:
                            db_session.commit()
                            logging.info("Image updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.exception("Failed to commit image updates for %s, aborting cycle..." % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_image)
                    continue

                # Scan the OpenStack images in the database, removing each one that is not in the inventory.
                delete_obsolete_database_items('Image', inventory, db_session, IMAGE, 'id', failure_dict=failure_dict)

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_image)
                except KeyboardInterrupt:
                    # sigint received, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint received, cancel the sleep and start the loop
                logging.error("Received wake-up signal during regular execution, resetting and continuing")
                continue


    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


# Retrieve keypairs.
def keypair_poller():
    multiprocessing.current_process().name = "Keypair Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    KEYPAIR = config.db_map.classes.cloud_keypairs
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0, 0, 0, 0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, KEYPAIR, 'key_name',
                                                          debug_hash=(config.log_level < 20), cloud_type='amazon')
        while True:
            try:
                logging.debug("Beginning keypair poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")
                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl + cloud.project + cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region]['groups'].append(
                            (cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing Key pairs from group:cloud - %s" % cloud_name)
                    session = _get_ec2_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.error("Failed to establish session with %s" % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # setup openstack api objects
                    client = _get_ec2_client(session)

                    # setup fingerprint list
                    fingerprint_list = []

                    try:
                        # get keypairs and add them to database
                        cloud_keys = client.describe_key_pairs()
                    except Exception as exc:
                        logging.error("Failed to poll key pairs from nova, skipping %s" % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm + cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    uncommitted_updates = 0
                    for key in cloud_keys['KeyPairs']:
                        fingerprint_list.append(key['KeyFingerprint'])
                        for groups in unique_cloud_dict[cloud]['groups']:
                            group_n = groups[0]
                            cloud_n = groups[1]
                            key_dict = {
                                "cloud_name": cloud_n,
                                "group_name": group_n,
                                "key_name": key['KeyName'],
                                "fingerprint": key['KeyFingerprint'],
                                "cloud_type": 'amazon',
                            }

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, key['KeyName'], key_dict,
                                                                new_poll_time, debug_hash=(config.log_level < 20)):
                                continue

                            new_key = KEYPAIR(**key_dict)
                            try:
                                db_session.merge(new_key)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception(
                                    "Failed to merge keypair entry for %s::%s, aborting cycle..." % (cloud_n, key['KeyName']))
                                logging.error(exc)
                                abort_cycle = True
                                break

                    del client
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        try:
                            db_session.commit()
                            logging.info("Keypair updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.error("Failed to commit new keypairs for %s, aborting cycle..." % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_keypair)
                    continue

                # Scan the EC2 keypairs in the database, removing each one that was not updated in the inventory.
                delete_obsolete_database_items('Keypair', inventory, db_session, KEYPAIR, 'key_name',
                                               poll_time=new_poll_time, failure_dict=failure_dict)

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_keypair)
                except KeyboardInterrupt:
                    # sigint received, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint received, cancel the sleep and start the loop
                logging.error("Received wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("Keypair poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()


def limit_poller():
    multiprocessing.current_process().name = "Limit Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    LIMIT = config.db_map.classes.cloud_limits
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0, 0, 0, 0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, LIMIT, '-',
                                                          debug_hash=(config.log_level < 20), cloud_type='amazon')
        while True:
            try:
                logging.debug("Beginning limit poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")
                uncommitted_updates = 0

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl + cloud.project + cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region]['groups'].append(
                            (cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing limits from cloud - %s" % cloud_name)
                    session = _get_ec2_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.error("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve limit list for the current cloud.
                    nova = _get_ec2_client(session)

                    shared_limits_dict = {}
                    try:
                        limit_list = nova.describe_account_attributes()
                        for limit in limit_list['AccountAttributes']:
                            shared_limits_dict[limit['AttributeName']] = limit['AttributeValues'][0]['AttributeValue']
                    except Exception as exc:
                        logging.error("Failed to retrieve limits from nova, skipping %s" % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if shared_limits_dict is False:
                        logging.info("No limits defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm + cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process limit list for the current cloud.
                    for groups in unique_cloud_dict[cloud]['groups']:
                        limits_dict = copy.deepcopy(shared_limits_dict)
                        group_n = groups[0]
                        cloud_n = groups[1]

                        limits_dict['group_name'] = group_n
                        limits_dict['cloud_name'] = cloud_n
                        limits_dict['cloud_type'] = 'amazon'
                        limits_dict['last_updated'] = int(time.time())
                        limits_dict, unmapped = map_attributes(src="ec2_limits", dest="csv2", attr_dict=limits_dict)
                        # Limit dict has a lot of require not null - set them all to -1 for now
                        limits_dict['server_meta_max'] = -1
                        limits_dict['personality_max'] = -1
                        limits_dict['image_meta_max'] = -1
                        limits_dict['personality_size_max'] = -1
                        limits_dict['ram_max'] = -1
                        limits_dict['server_groups_max'] = -1
                        limits_dict['security_group_rules_max'] = -1
                        limits_dict['keypairs_max'] = -1
                        limits_dict['security_groups_max'] = -1
                        limits_dict['server_group_members_max'] = -1
                        limits_dict['cores_max'] = -1
                        limits_dict['server_groups_used'] = -1
                        limits_dict['instances_used'] = -1
                        limits_dict['ram_used'] = -1
                        limits_dict['security_groups_used'] = -1
                        limits_dict['floating_ips_used'] = -1
                        limits_dict['cores_used'] = -1

                        if unmapped:
                            logging.error("Unmapped attributes found during mapping, discarding:")
                            logging.error(unmapped)

                        if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, '-', limits_dict,
                                                            new_poll_time, debug_hash=(config.log_level < 20)):
                            continue

                        for limit in limits_dict:
                            if "-1" in str(limits_dict[limit]):
                                limits_dict[limit] = config.no_limit_default

                        new_limits = LIMIT(**limits_dict)
                        try:
                            db_session.merge(new_limits)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception(
                                "Failed to merge limits for %s::%s, aborting cycle..." % (group_n, cloud_n))
                            logging.error(exc)
                            abort_cycle = True
                            break

                    del nova
                    if abort_cycle:
                        config.db_close()
                        del db_session
                        time.sleep(config.sleep_interval_limit)
                        continue

                    if uncommitted_updates > 0:
                        try:
                            db_session.commit()
                            logging.info("Limit updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.error("Failed to commit new limits for %s, aborting cycle..." % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
                delete_obsolete_database_items('Limit', inventory, db_session, LIMIT, '-', poll_time=new_poll_time,
                                               failure_dict=failure_dict)

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_limit)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("Limit poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()


def network_poller():
    multiprocessing.current_process().name = "Network Poller"
    # Base = automap_base()
    # db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_user,
    #        config.db_password,
    #        config.db_host,
    #        str(config.db_port),
    #        config.db_name
    #        )
    #    )
    # Base.prepare(db_engine, reflect=True)
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    NETWORK = config.db_map.classes.cloud_networks
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0, 0, 0, 0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, NETWORK, 'name',
                                                          debug_hash=(config.log_level < 20), cloud_type='amazon')
        while True:
            try:
                logging.debug("Beginning network poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl + cloud.project + cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region]['groups'].append(
                            (cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing networks from cloud - %s" % cloud_name)
                    session = _get_ec2_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.error("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve network list.
                    neutron = _get_ec2_client(session)
                    try:
                        net_list = neutron.describe_network_interfaces()['NetworkInterfaces']
                    except Exception as exc:
                        logging.error("Failed to retrieve networks from neutron, skipping %s" % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if net_list is False:
                        logging.info("No networks defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm + cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    uncommitted_updates = 0
                    for network in net_list:
                        for groups in unique_cloud_dict[cloud]['groups']:
                            group_n = groups[0]
                            cloud_n = groups[1]
                            network_dict = {
                                'group_name': group_n,
                                'cloud_name': cloud_n,
                                'cloud_type': 'amazon',
                                'name': network['Description'],
                                'subnets': network['SubnetId'],
                                'tenant_id': network['OwnerId'],
                                'external_route': 1,
                                'shared': 0,#network['Status'],
                                'id': network['NetworkInterfaceId'],
                                'last_updated': int(time.time())
                            }

                            #network_dict, unmapped = map_attributes(src="ec2_networks", dest="csv2",
                            #                                        attr_dict=network_dict)
                            #if unmapped:
                            #    logging.error("Unmapped attributes found during mapping, discarding:")
                            #    logging.error(unmapped)

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, network['Description'],
                                                                network_dict, new_poll_time,
                                                                debug_hash=(config.log_level < 20)):
                                continue

                            new_network = NETWORK(**network_dict)
                            try:
                                db_session.merge(new_network)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge network entry for %s::%s::%s, aborting cycle..." % (
                                group_n, cloud_n, network['Description']))
                                logging.error(exc)
                                abort_cycle = True
                                break

                    del neutron
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        try:
                            db_session.commit()
                            logging.info("Network updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.error("Failed to commit new networks for %s, aborting cycle..." % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_network)
                    continue

                # Scan the OpenStack networks in the database, removing each one that was not updated in the inventory.
                delete_obsolete_database_items('Network', inventory, db_session, NETWORK, 'name',
                                               poll_time=new_poll_time, failure_dict=failure_dict)

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_network)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


def security_group_poller():
    multiprocessing.current_process().name = "Security Group Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)

    SECURITY_GROUP = config.db_map.classes.cloud_security_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0, 0, 0, 0]
    failure_dict = {}
    my_pid = os.getpid()

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, SECURITY_GROUP, 'id',
                                                          debug_hash=(config.log_level < 20), cloud_type='amazon')
        while True:
            try:
                logging.debug("Beginning security group poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl + cloud.project + cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl + cloud.project + cloud.region]['groups'].append(
                            (cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing security groups from cloud - %s" % cloud_name)
                    session = _get_ec2_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.error("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                            continue

                    # setup OpenStack api objects
                    neu = _get_ec2_client(session)

                    # Retrieve all flavours for this cloud.
                    try:
                        sec_grp_list = neu.describe_security_groups()
                    except Exception as exc:
                        logging.error("Failed to retrieve security groups for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm + cld_nm not in failure_dict:
                                failure_dict[grp_nm + cld_nm] = 1
                            else:
                                failure_dict[grp_nm + cld_nm] = failure_dict[grp_nm + cld_nm] + 1
                            if failure_dict[grp_nm + cld_nm] > 3:  # should be configurable
                                logging.error(
                                    "Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm + cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if sec_grp_list['SecurityGroups'] is False:
                        logging.info("No security groups defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm + cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process security groups for this cloud.
                    uncommitted_updates = 0
                    for sec_grp in sec_grp_list["SecurityGroups"]:
                        for groups in unique_cloud_dict[cloud]['groups']:
                            group_n = groups[0]
                            cloud_n = groups[1]

                            sec_grp_dict = {
                                'group_name': group_n,
                                'cloud_name': cloud_n,
                                'name': sec_grp["GroupName"],
                                'id': sec_grp["GroupId"],
                                'last_updated': new_poll_time
                            }

                            flav_dict, unmapped = map_attributes(src="os_sec_grps", dest="csv2", attr_dict=sec_grp_dict)
                            if unmapped:
                                logging.error("Unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, sec_grp["GroupId"],
                                                                sec_grp_dict, new_poll_time,
                                                                debug_hash=(config.log_level < 20)):
                                continue

                            new_sec_grp = SECURITY_GROUP(**sec_grp_dict)
                            try:
                                db_session.merge(new_sec_grp)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception(
                                    "Failed to merge security group entry for %s::%s::%s, aborting cycle..." % (
                                    group_n, cloud_n, sec_grp.name))
                                logging.error(exc)
                                abort_cycle = True
                                break

                    del neu
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        try:
                            db_session.commit()
                            logging.info("Security group updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.exception(
                                "Failed to commit security group updates for %s, aborting cycle..." % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    db_session.close()
                    time.sleep(config.sleep_interval_sec_grp)
                    continue

                # Scan the OpenStack sec_grps in the database, removing each one that was not iupdated in the inventory.
                delete_obsolete_database_items('sec_grp', inventory, db_session, SECURITY_GROUP, 'id',
                                               poll_time=new_poll_time, failure_dict=failure_dict)

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_sec_grp)

                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue

            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("sec_grp poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


def vm_poller():
    multiprocessing.current_process().name = "VM Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]), pool_size=8)
    VM = config.db_map.classes.csv2_vms
    FVM = config.db_map.classes.csv2_vms_foreign
    GROUP = config.db_map.classes.csv2_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0, 0, 0, 0]
    failure_dict = {}

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, VM, 'hostname',
                                                          debug_hash=(config.log_level < 20), cloud_type='amazon')
        while True:
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            logging.debug("Beginning EC2 VM poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            # For each OpenStack cloud, retrieve and process VMs.
            abort_cycle = False
            group_list = db_session.query(GROUP)
            for group in group_list:
                logging.debug("Polling Group: %s" % group.group_name)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon",
                                                            CLOUD.group_name == group.group_name)
                foreign_vm_list = db_session.query(FVM).filter(FVM.group_name == group.group_name)

                # set foreign vm counts to zero as we will recalculate them as we go, any rows left at zero should be deleted
                # dict[cloud+flavor]
                for_vm_dict = {}
                for for_vm in foreign_vm_list:
                    fvm_dict = {
                        "fvm_obj": for_vm,
                        "count": 0,
                    }
                    for_vm_dict[for_vm.cloud_name + "--" + for_vm.flavor_id] = fvm_dict

                for cloud in cloud_list:
                    group_name = group.group_name
                    cloud_name = cloud.cloud_name
                    logging.debug("Polling VMs from cloud: %s" % cloud_name)
                    session = _get_ec2_session(cloud)
                    if session is False:
                        logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (
                        group_name, cloud_name))
                        if group_name + cloud_name not in failure_dict:
                            failure_dict[group_name + cloud_name] = 1
                        else:
                            failure_dict[group_name + cloud_name] = failure_dict[group_name + cloud_name] + 1
                        if failure_dict[group_name + cloud_name] > 3:  # should be configurable
                            logging.error(
                                "Failure threshhold limit reached for %s:%s, manual action required, skipping" % (
                                group_name, cloud_name))
                        continue

                    # Retrieve VM list for this cloud.
                    nova = _get_ec2_client(session)
                    try:
                        vm_list = nova.describe_instances()
                    except Exception as exc:
                        logging.error(
                            "Failed to retrieve VM data for %s::%s, skipping this cloud..." % (group_name, cloud_name))
                        logging.error("Exception type: %s" % type(exc))
                        logging.error(exc)
                        if group_name + cloud_name not in failure_dict:
                            failure_dict[group_name + cloud_name] = 1
                        else:
                            failure_dict[group_name + cloud_name] = failure_dict[group_name + cloud_name] + 1
                        if failure_dict[group_name + cloud_name] > 3:  # should be configurable
                            logging.error(
                                "Failure threshold limit reached for %s::%s, manual action required, skipping" % (
                                group_name, cloud_name))
                        continue

                    if 'Reservations' in vm_list.keys() and len(vm_list['Reservations']) == 0:
                        logging.info("No VMs defined for %s::%s, skipping this cloud..." % (group_name, cloud_name))
                        del nova
                        continue

                    # if we get here the connection to openstack has been succussful and we can remove the error status
                    failure_dict.pop(group_name + cloud_name, None)

                    # Process VM list for this cloud.
                    # We've decided to remove the variable "status_changed_time" since it was holding the exact same value as "last_updated"
                    # This is because we are only pushing updates to the csv2 database when the state of a vm is changed and thus it would be logically equivalent
                    uncommitted_updates = 0
                    for vm in vm_list['Reservations']:
                        # ~~~~~~~~
                        # figure out if it is foreign to this group or not based on tokenized hostname:
                        # hostname example: testing--otter--2049--256153399971170-1
                        # tokenized:        group,   cloud, csv2_host_id, ?vm identifier?
                        #
                        # at the end some of the dictionary enteries might not have a previous database object
                        # due to emergent flavors and thus a new obj will need to be created
                        # ~~~~~~~~
                        try:
                            host_tokens = vm.name.split("--") # TODO Can't control hostname so this won't work
                            if host_tokens[0] != group_name:
                                logging.debug("group_name from host does not match, marking %s as foreign vm" % vm.name)
                                if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = \
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]] = {
                                        'count': 1
                                    }
                                # foreign vm
                                continue
                            elif host_tokens[1] != cloud_name:
                                logging.debug("cloud_name from host does not match, marking %s as foreign vm" % vm.name)
                                if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = \
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]] = {
                                        'count': 1
                                    }
                                # foreign vm
                                continue
                            elif int(host_tokens[2]) != int(config.csv2_host_id):
                                logging.debug(
                                    "csv2 host id from host does not match (should be %s), marking %s as foreign vm" % (
                                    config.csv2_host_id, vm.name))
                                if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = \
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]] = {
                                        'count': 1
                                    }

                                # foreign vm
                                continue
                        except IndexError as exc:
                            # not enough tokens, bad hostname or foreign vm
                            logging.error("Not enough tokens from hostname, bad hostname or foreign vm: %s" % vm.name)
                            if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = \
                                for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                            else:
                                # no entry yet
                                for_vm_dict[cloud_name + "--" + vm.flavor["id"]] = {
                                    'count': 1
                                }

                            continue

                        ip_addrs = []
                        floating_ips = []
                        for net in vm.addresses:
                            for addr in vm.addresses[net]:
                                if addr['OS-EXT-IPS:type'] == 'fixed':
                                    ip_addrs.append(addr['addr'])
                                elif addr['OS-EXT-IPS:type'] == 'floating':
                                    floating_ips.append(addr['addr'])
                        strt_time = vm.__dict__["OS-SRV-USG:launched_at"]
                        try:
                            from_zone = tz.gettz('UTC')
                            to_zone = tz.gettz('America/Vancouver')
                            dt_strt_time = datetime.datetime.strptime(strt_time, '%Y-%m-%dT%H:%M:%S.%f')
                            dt_strt_time = dt_strt_time.replace(tzinfo=from_zone)
                            local_strt_time = dt_strt_time.astimezone(to_zone)
                            vm_start_time = local_strt_time.strftime('%s')
                        except:
                            logging.info(
                                "No start time because VM still booting: %s, %s - setting start time equal to current time." % (
                                type(strt_time), strt_time))
                            vm_start_time = new_poll_time
                        vm_dict = {
                            'group_name': cloud.group_name,
                            'cloud_name': cloud.cloud_name,
                            'auth_url': cloud.authurl,
                            'project': cloud.project,
                            'hostname': vm.name,
                            'vmid': vm.id,
                            'status': vm.status,
                            'flavor_id': vm.flavor["id"],
                            'task': vm.__dict__.get("OS-EXT-STS:task_state"),
                            'power_state': vm.__dict__.get("OS-EXT-STS:power_state"),
                            'vm_ips': str(ip_addrs),
                            'vm_floating_ips': str(floating_ips),
                            'start_time': vm_start_time,
                            'last_updated': new_poll_time
                        }

                        vm_dict, unmapped = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict)
                        if unmapped:
                            logging.error("unmapped attributes found during mapping, discarding:")
                            logging.error(unmapped)

                        if test_and_set_inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, vm.name,
                                                            vm_dict, new_poll_time, debug_hash=(config.log_level < 20)):
                            continue

                        new_vm = VM(**vm_dict)
                        try:
                            db_session.merge(new_vm)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge VM entry for %s::%s::%s, aborting cycle..." % (
                            group_name, cloud_name, vm.name))
                            logging.error(exc)
                            abort_cycle = True
                            break
                        if uncommitted_updates >= config.batch_commit_size:
                            try:
                                db_session.commit()
                                logging.debug("Comitted %s VMs" % uncommitted_updates)
                                uncommitted_updates = 0
                            except Exception as exc:
                                logging.error("Error during batch commit of VMs:")
                                logging.error(exc)

                    del nova
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        try:
                            db_session.commit()
                            logging.info("VM updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.exception(
                                "Failed to commit VM updates for %s::%s, aborting cycle..." % (group_name, cloud_name))
                            logging.error(exc)
                            abort_cycle = True
                            break
                if abort_cycle:
                    break
                # proccess FVM dict
                # check if any rows have a zero count and delete them, otherwise update with new count
                for key in for_vm_dict:
                    split_key = key.split("--")
                    if for_vm_dict[key]['count'] == 0:
                        # delete this row
                        db_session.delete(for_vm_dict[key]['fvm_obj'])
                    else:
                        try:
                            # if we get here there is at least 1 count of this flavor, though there may not be a database object yet
                            for_vm_dict[key]['fvm_obj'].count = for_vm_dict[key]['count']
                            db_session.merge(for_vm_dict[key]['fvm_obj'])
                        except KeyError:
                            # need to create new db obj for this entry
                            fvm_dict = {
                                'group_name': group.group_name,
                                'cloud_name': split_key[0],
                                'flavor_id': split_key[1],
                                'count': for_vm_dict[key]['count']
                            }
                            new_fvm = FVM(**fvm_dict)
                            db_session.merge(new_fvm)
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit foreign VM updates, aborting cycle...")
                    logging.error(exc)
                    abort_cycle = True
                    break

            if abort_cycle:
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_vm)
                continue

            # Scan the OpenStack VMs in the database, removing each one that is not in the inventory.
            delete_obsolete_database_items('VM', inventory, db_session, VM, 'hostname', new_poll_time,
                                           failure_dict=failure_dict)

            logging.debug("Completed VM poller cycle")
            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_vm)

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


def service_registrar():
    multiprocessing.current_process().name = "Service Registrar"

    # database setup
    db_category_list = [os.path.basename(sys.argv[0]), "general"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    SERVICE_CATALOG = config.db_map.classes.csv2_service_catalog

    service_fqdn = socket.gethostname()
    service_name = "csv2-openstack"

    while True:
        config.db_open()

        service_dict = {
            "service": service_name,
            "fqdn": service_fqdn,
            "last_updated": None,
            "yaml_attribute_name": "cs_condor_remote_openstack_poller"
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
        #'flavor': flavor_poller,
        'image': image_poller,
        'keypair': keypair_poller,
        'limit': limit_poller,
        'network': network_poller,
        #'vm': vm_poller,
        #'registrar': service_registrar,
        'security_group_poller': security_group_poller
    }
    db_categories = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    procMon = ProcessMonitor(config_params=db_categories, pool_size=9,
                             orange_count_row='csv2_ec2_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    logging.info(
        "**************************** starting ec2 poller - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        # start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()