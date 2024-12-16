import multiprocessing
import logging
import socket
import time
import sys
import signal
import os
import shutil
import datetime
import yaml
import oci
from pytz import timezone
from dateutil import tz
import copy

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, terminate, check_pid
#from cloudscheduler.lib.signal_manager import register_signal_receiver
from cloudscheduler.lib.view_utils import kill_retire
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.signal_functions import event_signal_send
from cloudscheduler.lib.watchdog_utils import watchdog_send_heartbeat, watchdog_cleanup
from cloudscheduler.lib.oracle_functions import *

from cloudscheduler.lib.poller_functions import \
    inventory_cleanup, \
    inventory_obsolete_database_items_delete, \
    inventory_get_item_hash_from_db_query_rows, \
    inventory_test_and_set_item_hash, \
    start_cycle, \
    wait_cycle, \
    generate_unique_cloud_dict, \
    process_cloud_failure, \
    reset_cloud_error_dict, \
    expand_failure_dict

from cloudscheduler.lib.signal_functions import event_receiver_registration

# The purpose of this file is to get some information from the various registered
# oracle clouds and place it in a database for use by cloudscheduler
#
# Target data sets (should all be available from novaclient):
#       Flavor information
#       Quota Information
#       Image Information
#       Network Information
#
# This file also polls the oracle clouds for live VM information and inserts it into the database

CLOUD = "csv2_clouds"

## Poller sub-functions.

def poller_setup(): 
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor", "SQL"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    
    config.db_open()
    #event_receiver_registration(config, "insert_csv2_clouds_oracle")
    #event_receiver_registration(config, "update_csv2_clouds_oracle")
    return config, PID_FILE

## Poller functions.

def flavor_poller():
    multiprocessing.current_process().name = "Flavor Poller"

    FLAVOR = "cloud_flavors"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {} 

    config, PID_FILE = poller_setup()

    try: 
        where_clause = "cloud_type='oracle'"
        rc, msg, rows = config.db_query(FLAVOR, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning flavor poller cycle")
                config.db_open()
                config.refresh()
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
                if not os.path.exists(PID_FILE):
                    logging.info("Falied to get pid file, stop set, exiting...")
                    break
     
                signal.signal(signal.SIGINT, signal.SIG_IGN) 

                abort_cycle = False

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = generate_unique_cloud_dict(config, CLOUD, "oracle")
                if not unique_cloud_dict:
                    #failed to retrieve cloud list, it will return a dictionary or False
                    logging.debug("Unable to retrieve any clouds for polling... ending cycle")
                    unique_cloud_dict = {} 

     
                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj =  unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing flavours from cloud - %s" % cloud_name)

                    try:
                        with open('/var/local/cloudscheduler/oracle/flavors.yaml', 'r') as f:
                            flavors = yaml.load(f, Loader=yaml.SafeLoader)
                    except Exception as exc:
                        logging.error("Failed to load flavour yaml file, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    failure_dict = reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj)

                    # Process flavours for this cloud.
                    uncommitted_updates = 0
                    try:
                        for flavor in flavors:
                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]

                                flav_dict = {
                                    'group_name': group_n,
                                    'cloud_name': cloud_n,
                                    'name': flavor,
                                    'id': flavor,
                                    'cloud_type': "oracle",
                                    'ram': flavors[flavor]["ram"],
                                    'vcpus': flavors[flavor]["cores"],
                                    'swap': 0,
                                    'disk': flavors[flavor]["disk"],
                                    'last_updated': new_poll_time
                                    }

                                flav_dict, unmapped = map_attributes(src="os_flavors", dest="csv2", attr_dict=flav_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, flav_dict, inventory, new_poll_time, debug_hash=(config.categories["oraclePoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(FLAVOR, flav_dict)
                                    uncommitted_updates += 1 
                                except Exception as exc: 
                                    logging.exception("Failed to merge flavor entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, flavor.name))
                                    logging.error(exc)
                                    abort_cycle = True 
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc: 
                                    logging.exception("Failed to commit flavor updates for %s, aborting cycle..." % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True 
                                    break

                    except Exception as exc: 
                        logging.error("Error proccessing flavor_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Flavor updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    time.sleep(config.categories["oraclePoller.py"]["sleep_interval_flavor"])
                    continue


                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                rows = expand_failure_dict(config, CLOUD, "oracle", FLAVOR, failure_dict)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, FLAVOR)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["oraclePoller.py"]["sleep_interval_flavor"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Flavor poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def image_poller():
    # Temporary, do properly
    #oracleConfig = oci.config.from_file()
    compartment_id = "ocid1.compartment.oc1..aaaaaaaaig7yftcjqel6qeaxph7gcdmirjqumxczmnquctnqxim7w66mz6aa"

    multiprocessing.current_process().name = "Image Poller"

    IMAGE = "cloud_images"

    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='oracle'"
        rc, msg, rows = config.db_query(IMAGE, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                config.db_open()
                logging.debug("Beginning image poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.info("Falied to get pid file, stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='oracle'"
                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = generate_unique_cloud_dict(config, CLOUD, "oracle")
                if not unique_cloud_dict:
                    #failed to retrieve cloud list, it will return a dictionary or False
                    logging.debug("Unable to retrieve any clouds for polling... ending cycle")
                    unique_cloud_dict = {}

                for cloud in unique_cloud_dict:
                    oracleConfig = loadOracleConfig(unique_cloud_dict[cloud]['cloud_obj'])

                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    logging.info("Processing Images from cloud - %s" % cloud_name)
                    try:
                        imageclient = oci.core.ComputeClient(oracleConfig)
                    except Exception as exc:
                        logging.error("Failed to initialize compute client on cloud %s (check Oracle config), skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue
            
                    # Retrieve all images for this cloud.
                    pre_req_time = time.time() * 1000000 
                    image_list = []
                    try:
                        image_list = do_image_query(imageclient, compartment_id)
                        post_req_time = time.time() * 1000000
                    except Exception as exc:
                        logging.error("Failed to retrieve image data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    # we successfully contacted the cloud for data if we get here, reset cloud errors
                    failure_dict = reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj)

                    uncommitted_updates = 0

                    # This code updates the communication_rt for a particular cloud- previous cloud errors were handled in this loop which was refactored
                    # into reset_cloud_error_dict, this functionality may be optionally moved into that routine to be a little more efficient but a
                    # double loop is probably fine for now.
                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        try:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            where_clause = "group_name='%s' and cloud_name='%s'" % (grp_nm, cld_nm)
                            rc, msg, cloud_rows = config.db_query(CLOUD, where=where_clause)
                            cloud_row = cloud_rows[0]
                            cloud_row["communication_rt"] = int(post_req_time - pre_req_time)
                            logging.debug('cloud_tuple grp %s, cld %s, time diff %s' % (grp_nm, cld_nm, cloud_row["communication_rt"]))
                            cld_update_dict = {
                                "group_name": cloud_row["group_name"],
                                "cloud_name": cloud_row["cloud_name"],
                                "communication_rt": cloud_row["communication_rt"],
                            }
                            config.db_merge(CLOUD, cld_update_dict)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.warning("Failed merge and commit an update for communication_rt on cloud row : %s" % cloud_row)
                            logging.warning(exc)

                    try:
                        for image in image_list:
                            if image.size_in_mbs == "" or image.size_in_mbs is None:
                                size = 0
                            else:
                                size = image.size_in_mbs

                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]

                                created_datetime = image.time_created.strftime("%Y-%m-%d %H:%M:%S")
                                
                                img_dict = {
                                    'group_name': group_n,
                                    'cloud_name': cloud_n,
                                    'cloud_type': "oracle",
                                    'id': image.id,
                                    'size': size,
                                    'name': image.display_name,
                                    'created_at': created_datetime,
                                    'last_updated': new_poll_time
                                    }

                                img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=img_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, img_dict, inventory, new_poll_time, debug_hash=(config.categories["oraclePoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    logging.debug("Merging: %s" % img_dict)
                                    config.db_merge(IMAGE, img_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge image entry for %s::%s::%s:" % (group_n, cloud_n, image.name))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.exception("Failed to commit image updates for %s, aborting cycle..." % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing image_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue
                        

                    del imageclient
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Image updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    time.sleep(config.categories["oraclePoller.py"]["sleep_interval_image"])
                    continue
                config.db_commit()

                
                # this block of code used to expand the failure dict AND update the communication status
                # however, the failure dict expansion was refactored to be agnostic between poller processes
                # leaving this extra loop in here to deal with the communication. Again we've introduced a double
                # loop which could optionally be moved into the expand_failure_dict but since this code is unique
                # only to the image poller a double loop is probably fine
                where_clause = "cloud_type='oracle'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"] + cloud["password"]
                    if key in failure_dict:
                        cld_update_dict = {
                            "group_name": cloud["group_name"],
                            "cloud_name": cloud["cloud_name"],
                            "communication_up": 0
                        }
                        config.db_update(CLOUD, cld_update_dict)
                        config.db_commit()
                        logging.error("Communication down for %s:%s" % (grp_nm, cld_nm))

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                logging.debug("Proccessing failure, failure_dict: %s" % failure_dict)
                rows = expand_failure_dict(config, CLOUD, "oracle", IMAGE, failure_dict)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, IMAGE)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["oraclePoller.py"]["sleep_interval_image"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue


    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def limit_poller():
    # Temporary, do properly
    #oracleConfig = oci.config.from_file()
    compartment_id = "ocid1.compartment.oc1..aaaaaaaaig7yftcjqel6qeaxph7gcdmirjqumxczmnquctnqxim7w66mz6aa"

    multiprocessing.current_process().name = "Limit Poller"

    LIMIT = "cloud_limits"
    ikey_names = ["group_name", "cloud_name"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='oracle'"
        rc, msg, rows = config.db_query(LIMIT, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning limit poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.info("Falied to get pid file, stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
                config.refresh()

                abort_cycle = False
                unique_cloud_dict = generate_unique_cloud_dict(config, CLOUD, "oracle")
                logging.debug("Unique clouds dict: %s" % unique_cloud_dict.keys())

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing limits from cloud - %s" % cloud_name)
                    sess = get_oracle_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["oraclePoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    # Retrieve limit list for the current cloud.
                    nova = get_nova_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])

                    if nova is False:
                        logging.info("Openstack nova connection failed for %s, skipping this cloud..." % cloud_name)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    shared_limits_dict = {}
                    try:
                        limit_list = nova.get_limits().absolute
                        for limit in limit_list:
                            shared_limits_dict[limit] = limit_list[limit]
                    except Exception as exc:
                        logging.error("Failed to retrieve limits from nova, skipping %s" %  cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    if shared_limits_dict is False:
                        logging.info("No limits defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    failure_dict = reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj)

                    uncommitted_updates = 0
                    # Process limit list for the current cloud.
                    try:
                        for groups in unique_cloud_dict[cloud]['groups']:
                            limits_dict = copy.deepcopy(shared_limits_dict)
                            # remove unused attributes
                            limits_dict.pop('id')
                            limits_dict.pop('name')
                            limits_dict.pop('location')

                            group_n = groups[0]
                            cloud_n = groups[1]                        
                            # We need to make just a connection object to get information about volumes
                            os_conn = get_oracle_conn(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])
                            try:
                                vol_limits = os_conn.get_volume_limits().absolute
                                vol_dict = {key:vol_limits[key] for key in ['maxTotalVolumes', 'totalVolumesUsed', 'maxTotalVolumeGigabytes', 'totalGigabytesUsed']}
                                limits_dict = { **limits_dict, **vol_dict}
                            except:
                                #no volume info for this cloud
                                logging.debug("No volume limits for %s::%s" % (group_n, cloud_n))


                            limits_dict['group_name'] = group_n
                            limits_dict['cloud_name'] = cloud_n
                            limits_dict['last_updated'] = int(time.time())
                            limits_dict, unmapped = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict, config=config)
                            if unmapped:
                                logging.error("Unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)


                            if inventory_test_and_set_item_hash(ikey_names, limits_dict, inventory, new_poll_time, debug_hash=(config.categories["oraclePoller.py"]["log_level"] < 20)):
                                continue

                            for limit in limits_dict:
                                if "-1" in str(limits_dict[limit]):
                                    limits_dict[limit] = config.categories["oraclePoller.py"]["no_limit_default"]
                                # for the data colleced from clouds, it shouldn't have any negative values unless in some error cases, so set the negative value to 0
                                else:
                                    try:
                                        if int(limits_dict[limit]) < 0:
                                            limits_dict[limit] = 0
                                    except:
                                        continue
                            limits_dict["cloud_type"] = "oracle"

                            try:
                                logging.debug("Updating grp:cld - %s:%s" % (group_n, cloud_n))
                                config.db_merge(LIMIT, limits_dict)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge limits for %s::%s, aborting cycle..." % (group_n, cloud_n))
                                logging.error(exc)
                                abort_cycle = True
                                break

                            try:
                                config.db_commit()
                            except Exception as exc:
                                logging.error("Failed to commit new limits for %s, aborting cycle..."  % cloud_name)
                                logging.error(exc)
                                abort_cycle = True
                                break

                    except Exception as exc:
                        logging.error("Error proccessing limit_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del nova
                    if abort_cycle:
                        time.sleep(config.categories["oraclePoller.py"]["sleep_interval_limit"])
                        continue

                    if uncommitted_updates > 0:
                        logging.info("Limit updates committed: %d" % uncommitted_updates)

                rows = expand_failure_dict(config, CLOUD, "oracle", LIMIT, failure_dict)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, LIMIT)

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()
 
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["oraclePoller.py"]["sleep_interval_limit"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Limit poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def network_poller():
    # Temporary, do properly
    #oracleConfig = oci.config.from_file()
    compartment_id = "ocid1.compartment.oc1..aaaaaaaaig7yftcjqel6qeaxph7gcdmirjqumxczmnquctnqxim7w66mz6aa"

    multiprocessing.current_process().name = "Network Poller"

    NETWORK = "cloud_networks"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='oracle'"
        rc, msg, rows = config.db_query(NETWORK, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning network poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.info("Falied to get pid file, stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)

                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
                config.refresh()

                abort_cycle = False

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = generate_unique_cloud_dict(config, CLOUD, "oracle")

                for cloud in unique_cloud_dict:
                    oracleConfig = loadOracleConfig(unique_cloud_dict[cloud]['cloud_obj'])

                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing networks from cloud - %s" % cloud_name)
                    try:
                        netclient = oci.core.VirtualNetworkClient(oracleConfig)
                    except Exception as exc:
                        logging.debug("Failed to initialize network client (check Oracle config) with %s, skipping this cloud..." % cloud_name)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    try:
                        net_list = do_subnet_query(netclient, compartment_id)
                    except Exception as exc:
                        logging.error("Failed to retrieve network list, skipping %s" %  cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    if net_list is False:
                        logging.info("No networks defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    failure_dict = reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj)

                    uncommitted_updates = 0
                    try:
                        for network in net_list:
                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]
                                network_dict = {
                                    'group_name': group_n,
                                    'cloud_name': cloud_n,
                                    'name': network.display_name,
                                    'cloud_type': "oracle",
                                    'id': network.id,
                                    'last_updated': int(time.time()),
                                }

                                network_dict, unmapped = map_attributes(src="os_networks", dest="csv2", attr_dict=network_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, network_dict, inventory, new_poll_time, debug_hash=(config.categories["oraclePoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(NETWORK, network_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge network entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, network['name']))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.error("Failed to commit new networks for %s, aborting cycle..." %  cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing network_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del netclient
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Network updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    config.db_rollback()
                    time.sleep(config.categories["oraclePoller.py"]["sleep_interval_network"])
                    continue
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                rows = expand_failure_dict(config, CLOUD, "oracle", NETWORK, failure_dict)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, NETWORK)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)

                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["oraclePoller.py"]["sleep_interval_network"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                    config.db_close()
                    continue

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def vm_poller():
    # Temporary, do properly
    #oracleConfig = oci.config.from_file()
    compartment_id = "ocid1.compartment.oc1..aaaaaaaaig7yftcjqel6qeaxph7gcdmirjqumxczmnquctnqxim7w66mz6aa"

    multiprocessing.current_process().name = "VM Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "SQL", "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    VM = "csv2_vms"
    FVM = "csv2_vms_foreign"
    GROUP = "csv2_groups"
    CLOUD = "csv2_clouds"
    ikey_names = ["group_name", "cloud_name", "vmid"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config.db_open()
    event_receiver_registration(config, "insert_csv2_clouds_oracle")
    event_receiver_registration(config, "update_csv2_clouds_oracle")
    
    try:
        where_clause = "cloud_type='oracle'"
        rc, msg, rows = config.db_query(VM, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                # This cycle should be reasonably fast such that the scheduler will always have the most
                # up to date data during a given execution cycle.
                logging.debug("Beginning VM poller cycle")

                if not os.path.exists(PID_FILE):
                    logging.info("Falied to get pid file, stop set, exiting...")
                    break
                config.db_open()
                signal.signal(signal.SIGINT, signal.SIG_IGN)

                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
                config.refresh()

                # For each OpenStack cloud, retrieve and process VMs.
                abort_cycle = False
               
                try:
                    avg_cycle_length = 0
                    for poll_time in poll_time_history:
                        avg_cycle_length = avg_cycle_length + poll_time
                    avg_cycle_length = avg_cycle_length/len(poll_time_history)
                    if avg_cycle_length < config.categories["oraclePoller.py"]["sleep_interval_vm"]:
                        avg_cycle_length = config.categories["oraclePoller.py"]["sleep_interval_vm"]
                    where_clause="cloud_type='oracle' and start_time<='%s'" % (new_poll_time-2*avg_cycle_length)
                    rc, msg, unfiltered_rows = config.db_query(VM, where=where_clause)
                except Exception as exc:
                    logging.error("Failed to read configuration: %s" % exc)
                    where_clause = "cloud_type='oracle'"
                    rc, msg, unfiltered_rows = config.db_query(VM, where=where_clause)
                
                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = generate_unique_cloud_dict(config, CLOUD, "oracle")

                group_list = []
                for cloud in unique_cloud_dict:
                    group_list = group_list + unique_cloud_dict[cloud]['groups']

                for cloud in unique_cloud_dict:
                    oracleConfig = loadOracleConfig(unique_cloud_dict[cloud]['cloud_obj'])

                    auth_url = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']

                    where_clause = "authurl='%s' and region='%s' and project='%s'" % (cloud_obj["authurl"], cloud_obj["region"], cloud_obj["project"])
                    rc, msg, foreign_vm_list = config.db_query(FVM, where=where_clause)

                    #set foreign vm counts to zero as we will recalculate them as we go, any rows left at zero should be deleted
                    # dict[cloud+flavor]
                    for_vm_dict = {}
                    for for_vm in foreign_vm_list:
                        fvm_dict = {
                            "fvm_obj": for_vm,
                            "count": 0,
                            "region": cloud_obj["region"],
                            "authurl": cloud_obj["authurl"],
                            "project": cloud_obj["project"]
                        }
                        for_vm_dict[auth_url + "--" + for_vm["flavor_id"]] = fvm_dict

                    logging.debug("Polling VMs from cloud: %s" % auth_url)
                    try:
                        vmclient = oci.core.ComputeClient(oracleConfig)
                    except Exception as exc:
                        logging.debug("Failed to initialize network client (check Oracle config) with %s, skipping this cloud..." % cloud_name)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    try:
                        vm_list = do_instance_query(vmclient, compartment_id)
                    except Exception as exc:
                        logging.error("Failed to retrieve VM data for  %s::%s::%s, skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"]))
                        logging.error("Exception type: %s" % type(exc))
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    if vm_list == []:
                        logging.info("No VMs defined for %s::%s:%s, skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"]))
                        del vmclient
                        continue

                    # if we get here the connection to oracle has been succussful and we can remove the error status
                    failure_dict = reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj)
                    #update network status
                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        #where_clause = "group_name='%s' and cloud_name='%s'" % (grp_nm, cld_nm)
                        #rc, msg, cloud_rows = config.db_query(CLOUD, where=where_clause)
                        #cloud_row = cloud_rows[0]
                        cloud_row = {
                            "group_name": grp_nm,
                            "cloud_name": cld_nm,
                            "communication_up": 1
                        }
                        config.db_update(CLOUD, cloud_row)
                        config.db_commit()
                        

                    # Process VM list for this cloud.
                    # We've decided to remove the variable "status_changed_time" since it was holding the exact same value as "last_updated"
                    # This is because we are only pushing updates to the csv2 database when the state of a vm is changed and thus it would be logically equivalent
                    uncommitted_updates = 0
                    try:
                        for vm in vm_list:
                        #~~~~~~~~
                        # figure out if it is foreign to this group or not based on tokenized hostname:
                        # hostname example: testing--otter--2049--256153399971170-1
                        # tokenized:        group,   cloud, csv2_host_id, ?vm identifier?
                        #
                        # at the end some of the dictionary enteries might not have a previous database object
                        # due to emergent flavors and thus a new obj will need to be created
                        #~~~~~~~~
                            try:
                                host_tokens = vm.display_name.split("--")
                                vm_group_name = host_tokens[0]
                                vm_cloud_name = host_tokens[1]
                                found_flavor = translateFlavor(vm.shape_config)
                                vm_flavor_id = found_flavor
                        
                                if (host_tokens[0], host_tokens[1]) not in group_list:
                                    logging.debug("Group-Cloud combination doesn't match any in csv2, marking %s as foreign vm" % vm.display_name)
                                    logging.debug(group_list)
                                    if auth_url + "--" + vm_flavor_id in for_vm_dict:
                                        for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] = for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] + 1
                                    else:
                                        # no entry yet
                                        for_vm_dict[auth_url + "--" + vm_flavor_id]= {
                                            'count': 1,
                                            'region': cloud_obj["region"],
                                            'project': cloud_obj["project"],
                                            'authurl': cloud_obj["authurl"], 
                                            'flavor_id': vm_flavor_id
                                        }
                                    continue
                                elif int(host_tokens[2]) != int(config.categories["SQL"]["csv2_host_id"]):
                                    logging.debug("csv2 host id from host does not match (should be %s), marking %s as foreign vm" % (config.categories["SQL"]["csv2_host_id"], vm.display_name))
                                    if auth_url + "--" + vm_flavor_id in for_vm_dict:
                                        for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] = for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] + 1
                                    else:
                                        # no entry yet
                                        for_vm_dict[auth_url + "--" + vm_flavor_id]= {
                                            'count': 1,
                                            'region': cloud_obj["region"],
                                            'project': cloud_obj["project"],
                                            'authurl': cloud_obj["authurl"], 
                                            'flavor_id': vm_flavor_id
                                        }

                                    #foreign vm
                                    continue
                            except IndexError as exc:
                                #not enough tokens, bad hostname or foreign vm
                                logging.debug("Not enough tokens from hostname, bad hostname or foreign vm: %s" % vm.display_name)
                                found_flavor = translateFlavor(vm.shape_config)
                                if found_flavor is not None:
                                    vm_flavor_id = found_flavor
                                else:
                                    vm_flavor_id = vm.shape

                                if auth_url + "--" + vm_flavor_id in for_vm_dict:
                                    for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] = for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[auth_url + "--" + vm_flavor_id]= {
                                        'count': 1,
                                        'region': cloud_obj["region"],
                                        'project': cloud_obj["project"],
                                        'authurl': cloud_obj["authurl"], 
                                        'flavor_id': vm_flavor_id
                                    }

                                continue

                            ip_addrs = []
                            floating_ips = []
                            netclient = oci.core.VirtualNetworkClient(config)
                            private_IP_list, public_IP_list = do_IP_query(vmclient, netclient, compartment_id, vm.id)
                            for addr in private_IP_list:
                                ip_addrs.append(addr['addr'])
                            for addr in public_IP_list:
                                floating_ips.append(addr['addr'])
                            
                            additions = {}
                            where_clause="group_name='%s' and cloud_name='%s' and hostname='%s'" % (vm_group_name, vm_cloud_name, vm.display_name)
                            rc, msg, rows = config.db_query(VM, where=where_clause)
                            if (not rows) or len(rows) == 0:
                                where_clause = "group_name='%s'" % cloud_obj["group_name"]
                                rc, msg, found_group = config.db_query("csv2_groups", where=where_clause)
                                keep_alive = 0
                                if found_group and len(found_group) > 0:
                                    keep_alive = found_group[0].get("vm_keep_alive")
                                additions = {'start_time': int(time.time()), 'keep_alive': keep_alive}
                            
                            vm_dict = {
                                'group_name': vm_group_name,
                                'cloud_name': vm_cloud_name,
                                'region': cloud_obj["region"],
                                'auth_url': cloud_obj["authurl"],
                                'project': cloud_obj["project"],
                                'cloud_type': "oracle",
                                'hostname': vm.display_name,
                                'vmid': vm.id,
                                'image_id': vm.image_id,
                                'flavor_id': vm_flavor_id,
                                'vm_ips': str(ip_addrs),
                                'vm_floating_ips': str(floating_ips),
                                'last_updated': new_poll_time,
                                **additions
                            }

                            vm_dict, unmapped = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict, config=config)
                            if unmapped:
                                logging.error("unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)

                            if inventory_test_and_set_item_hash(ikey_names, vm_dict, inventory, new_poll_time, debug_hash=(config.categories["oraclePoller.py"]["log_level"] < 20)):
                                continue

                            try:
                                config.db_merge(VM, vm_dict)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge VM entry for %s::%s::%s, using group %s's credentials aborting cycle..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                                logging.error(exc)
                                abort_cycle = True
                                break

                            try:
                                config.db_commit()
                            except Exception as exc:
                                logging.exception("Failed to commit VM updates for %s::%s:%s, using group %s's credentials aborting cycle..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                                logging.error(exc)
                                abort_cycle = True
                                break

                    except Exception as exc:
                        logging.error("Error proccessing vm_list for cloud %s" % cloud_obj["cloud_name"])
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del nova
                    if abort_cycle:
                        break

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        where_clause = "group_name='%s' and cloud_name='%s'" % (grp_nm, cld_nm)
                        rc, msg, found_cloud_list = config.db_query(CLOUD, where=where_clause)
                        if found_cloud_list and len(found_cloud_list) > 0 and found_cloud_list[0].get('freeze') == 1:
                            cloud_row = { "freeze": 0 }
                            config.db_update("csv2_clouds", cloud_row, where=where_clause)
                            config.db_commit()
                            logging.info("reset freeze for cloud %s" % cld_nm)
                
                    if uncommitted_updates > 0:
                        logging.info("VM updates committed: %d for cloud %s" % (uncommitted_updates, cloud_obj["cloud_name"]))

                    # proccess FVM dict
                    # check if any rows have a zero count and delete them, otherwise update with new count
                    for key in for_vm_dict:
                        split_key = key.split("--")
                        if for_vm_dict[key]['count'] == 0:
                            # delete this row
                            config.db_delete(FVM, for_vm_dict[key]['fvm_obj'])
                        else:
                            try:
                                # if we get here there is at least 1 count of this flavor, though there may not be a database object yet
                                for_vm_dict[key]['fvm_obj']["count"] = for_vm_dict[key]['count']
                                config.db_merge(FVM, for_vm_dict[key]['fvm_obj'])
                            except KeyError:
                                # need to create new db obj for this entry
                                fvm_dict = {
                                    'authurl':    for_vm_dict[key]['authurl'],
                                    'project':    for_vm_dict[key]['project'],
                                    'region':     for_vm_dict[key]['region'],
                                    'flavor_id':  for_vm_dict[key]['flavor_id'],
                                    'count':      for_vm_dict[key]['count'],
                                    'cloud_type': "oracle"
                                }
                                config.db_merge(FVM, fvm_dict)
                        try:
                            config.db_commit()
                        except Exception as exc:
                            logging.exception("Failed to commit foreign VM updates, aborting cycle...")
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    config.db_rollback()
                    config.db_close()
                    time.sleep(config.categories["oraclePoller.py"]["sleep_interval_vm"])
                    continue

                # Scan the OpenStack VMs in the database, removing each one that is not in the inventory.
                # VMs have a different failure dict schema using group_name + auth_url instead of group_name + cloud_name
                #     failure_dict needs to be remapped before calling
                logging.debug("Expanding failure_dict: %s" % failure_dict)
                where_clause="cloud_type='oracle'"
                rc, qmsg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1
                        # update cloud network status
                        cloud_row = {
                            "group_name": cloud["group_name"],
                            "cloud_name": cloud["cloud_name"],
                            "communication_up": 0
                        }
                        config.db_update(CLOUD, cloud_row)
                        config.db_commit()
                        logging.error("Communication down for %s:%s" % (cloud["group_name"], cloud["cloud_name"]))

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                rows = []            
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, VM)


                # Check on the core limits to see if any clouds need to be scaled down.
                logging.debug("checking for over-quota clouds")
                where_clause = "cloud_type='oracle'"
                rc, msg, over_quota_clouds = config.db_query("view_vm_kill_retire_over_quota", where=where_clause) 
                for cloud in over_quota_clouds:
                    #logging.info("Remove overquota vms from %s::%s" % (cloud["group_name"], cloud["cloud_name"]))
                    kill_retire(config, cloud["group_name"], cloud["cloud_name"], "control", [cloud["cores"], cloud["ram"]], get_frame_info())
                    config.db_commit()
                #if len(over_quota_clouds) > 0: 
                #    event_signal_send(config, "update_csv2_clouds_oracle")

                logging.debug("Completed VM poller cycle")

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    config.db_close()
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)

                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["oraclePoller.py"]["sleep_interval_vm"], config)
                except KeyboardInterrupt:
                    # sigint received, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Received wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def compartment_poller():
    # Temporary, do properly
    #oracleConfig = oci.config.from_file()
    # Root compartment (tenancy) OCID
    compartment_id = "ocid1.tenancy.oc1..aaaaaaaauoyqb55c4rrod776vzlvvn7kucvab5t3xiqubfda6wirqllgtohq"

    multiprocessing.current_process().name = "Compartment Poller"

    COMPARTMENT = "cloud_compartments"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {} 

    config, PID_FILE = poller_setup()

    try: 
        where_clause = "cloud_type='oracle'"
        rc, msg, rows = config.db_query(COMPARTMENT, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning compartment poller cycle")
                config.db_open()
                config.refresh()
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
                if not os.path.exists(PID_FILE):
                    logging.info("Falied to get pid file, stop set, exiting...")
                    break
     
                signal.signal(signal.SIGINT, signal.SIG_IGN) 

                abort_cycle = False

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = generate_unique_cloud_dict(config, CLOUD, "oracle")
                if not unique_cloud_dict:
                    #failed to retrieve cloud list, it will return a dictionary or False
                    logging.debug("Unable to retrieve any clouds for polling... ending cycle")
                    unique_cloud_dict = {} 

     
                for cloud in unique_cloud_dict:
                    oracleConfig = loadOracleConfig(unique_cloud_dict[cloud]['cloud_obj'])

                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj =  unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing compartments from cloud - %s" % cloud_name)

                    try:
                        comp_client = oci.identity.IdentityClient(oracleConfig)
                    except Exception as exc:
                        logging.error("Failed to initialize identity client on cloud %s (check Oracle config), skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    # Retrieve all compartments
                    try:
                        comp_list = do_compartment_query(comp_client, compartment_id)
                    except Exception as exc:
                        logging.error("Failed to retrieve compartment data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        failure_dict = process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict)
                        continue

                    if comp_list == []:
                        logging.info("No compartments defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    failure_dict = reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj)

                    # Process compartments for this cloud.
                    uncommitted_updates = 0
                    try:
                        for comp in comp_list:
                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]

                                comp_dict = {
                                    'group_name': group_n,
                                    'cloud_name': cloud_n,
                                    'name': comp["name"],
                                    'cloud_type': "oracle",
                                    'id': comp["ocid"],
                                    'last_updated': new_poll_time
                                    }

                                if inventory_test_and_set_item_hash(ikey_names, comp_dict, inventory, new_poll_time, debug_hash=(config.categories["oraclePoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(COMPARTMENT, comp_dict)
                                    uncommitted_updates += 1 
                                except Exception as exc: 
                                    logging.exception("Failed to merge compartment entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, comp["name"]))
                                    logging.error(exc)
                                    abort_cycle = True 
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc: 
                                    logging.exception("Failed to commit compartment updates for %s, aborting cycle..." % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True 
                                    break

                    except Exception as exc: 
                        logging.error("Error proccessing comp_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del comp_client
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Compartment updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    time.sleep(config.categories["oraclePoller.py"]["sleep_interval_compartment"])
                    continue


                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                rows = expand_failure_dict(config, CLOUD, "oracle", COMPARTMENT, failure_dict)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, COMPARTMENT)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["oraclePoller.py"]["sleep_interval_compartment"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Compartment poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    process_ids = {
        'flavor':                flavor_poller,
        'image':                 image_poller,
        'limit':                 limit_poller,
        'network':               network_poller,
        'vm':                    vm_poller,
        'compartment':           compartment_poller
    }
    watchdog_exemptions = []
    db_categories = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]

    procMon = ProcessMonitor(config_params=db_categories, pool_size=3, process_ids=process_ids, watchdog_exemption_list=watchdog_exemptions)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting oracle VM poller - Running %s *********************************" % version)


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
