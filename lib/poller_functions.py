from dateutil import tz, parser
import hashlib
import logging
import json
import os
import time

from cloudscheduler.lib.attribute_mapper import map_attributes

## Poller functions.

def start_cycle(new_poll_time, start_time):
    logging.debug("Beginning poller cycle")
    start_time = time.time()
    new_poll_time = int(start_time)
    return new_poll_time, start_time

# This function helps maintain a moving average of cycle time and if the cycle times are
# exceeding the configured sleep time it lengthens the sleep to the average cycle time
def wait_cycle(start_time, poll_time_history, config_sleep_time, config):
    cycle_length = time.time() - start_time
    poll_time_history.append(cycle_length)
    if len(poll_time_history) > 5:
        poll_time_history.pop(0)

    avg_cycle_length = 0
    for poll_time in poll_time_history:
        avg_cycle_length = avg_cycle_length + poll_time
    avg_cycle_length = avg_cycle_length/len(poll_time_history)

    config.refresh()
    if config.categories["ProcessMonitor"]["pause"]:
        while(config.categories["ProcessMonitor"]["pause"]):
            logging.debug("Pause flag set sleeping...")
            time.sleep(10)
            config.refresh()

    if avg_cycle_length > config_sleep_time:
        logging.debug("Completed cycle - cycle length: %s, sleeping for %s" % (cycle_length, avg_cycle_length))
        time.sleep(avg_cycle_length)
    else:
        logging.debug("Completed cycle - cycle length: %s, sleeping for %s" % (cycle_length, config_sleep_time))
        time.sleep(config_sleep_time)
    return

def foreign(vm):
    native_id = '%s--%s--' % (vm.group_name, vm.cloud_name)
    if vm.hostname[:len(native_id)] == native_id:
        return False
    else:
        return True

def __inventory_get_hash__(ikey_names, item_dict, debug_hash=False): 
    hash_list = []
    hash_object = hashlib.new('md5')
    new_hash=0 # If all attributes are primary keys, return a hash of zero
    for hash_item in sorted(item_dict):
        if hash_item in ikey_names:
            continue
       
        if isinstance(item_dict[hash_item], bool):
            hash_list.append('%s=%s' % (hash_item, str(int(item_dict[hash_item]))))
        elif isinstance(item_dict[hash_item], list):
            hash_list.append('%s=%s' % (hash_item, str(item_dict[hash_item][0])))
        else:
            hash_list.append('%s=%s' % (hash_item, str(item_dict[hash_item])))
        hash_object.update(hash_list[-1].encode('utf-8'))

        if debug_hash:
            new_hash = '%s,%s' % (hash_object.hexdigest(), ','.join(hash_list))
        else:
            new_hash = hash_object.hexdigest()

    return new_hash

def __inventory_set_key__(ikey_names, item_dict, inventory): 
    ikey_list = []
    for column in ikey_names:
        if column not in item_dict:
            raise Exception('Invalid ikey name "%s" in ikey name list.' % column)

        ikey_list.append(item_dict[column])

    ikey = json.dumps(ikey_list)

    if ikey not in inventory:
        inventory[ikey] = {'hash': None, 'poll_time': 0}

    return ikey

def inventory_cleanup(ikey_names, rows, inventory):
    """
    Cleans up any inventory items whose group/cloud have been deleted. An
    exception will be raised if iley_names does not contain the columns
    "group_name" and "cloud_name".
    """

    logging.debug("Starting Inventory Cleanup")
    
    gix = ikey_names.index("group_name")
    cix = ikey_names.index("cloud_name")

    group_clouds = {}
    for row in rows:
        group_cloud = '%s::%s' % (row['group_name'], row['cloud_name'])
        group_clouds[group_cloud] = 1

    keys_to_delete = []
    for ikey in inventory:
        ikey_list = json.loads(ikey)
        group_cloud = '%s::%s' % (ikey_list[gix], ikey_list[cix])
        if group_cloud not in group_clouds:
            keys_to_delete.append(ikey)
    for ikey in keys_to_delete:
        del inventory[ikey]
        logging.debug('inventory_cleanup: delete item "%s" from inventory, no matching group_name/cloud_name.' % json.loads(ikey))


def inventory_get_item_hash_from_db_query_rows(ikey_names, rows, inventory={}):
    for row in rows:
        ikey = __inventory_set_key__(ikey_names, row, inventory)
        inventory[ikey]['hash'] =  __inventory_get_hash__(ikey_names, row)

    return inventory

def inventory_obsolete_database_items_delete(ikey_names, rows, inventory, poll_time, config, table):
    for row in rows:
        ikey = __inventory_set_key__(ikey_names, row, inventory)

        if poll_time != None and inventory[ikey]['poll_time'] < poll_time:
            rc, msg = config.db_delete(table, row)
            if rc == 0:
                config.db_commit()
                del inventory[ikey]
            else:
                logging.warning('inventory_delete_obsolete_database_items: failed to delete item "%s" from table "%s" - %s' % (json.loads(ikey), table, msg))

def inventory_test_and_set_item_hash(ikey_names, item_dict, inventory, poll_time, debug_hash=False):
    ikey = __inventory_set_key__(inventory=inventory, ikey_names=ikey_names, item_dict=item_dict)
    inventory[ikey]['poll_time'] = poll_time

    new_hash = __inventory_get_hash__(ikey_names, item_dict)

    if new_hash == inventory[ikey]['hash']:
        return True

    logging.debug("inventory_item_hash(old): %s" % inventory[ikey]['hash'])
    logging.debug("inventory_item_hash(new): %s" % new_hash)

    inventory[ikey]['hash'] = new_hash
    return False

def log_heartbeat_message(last_statement_time, poller_name):
    cur_time = time.time()
    if cur_time - last_statement_time > 300:
        logging.info ("-- %s HEARTBEAT --" % poller_name)
        return cur_time
    else:
        return last_statement_time


def generate_unique_cloud_dict(config, cloud_table, cloud_type):
    rc, msg, cloud_list = config.db_query(cloud_table, where="cloud_type='%s'" % cloud_type)

    # build unique cloud list to only query a given cloud once per cycle
    unique_cloud_dict = {}
    try:
        for cloud in cloud_list:
            if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]+cloud["password"] not in unique_cloud_dict:
                unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]+cloud["password"]] = {
                    'cloud_obj': cloud,
                    'groups': [(cloud["group_name"], cloud["cloud_name"])]
                }
            else:
                unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]+cloud["password"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))
    except Exception as exc:
        logging.error("Failed to read cloud list: %s" % exc)
        return False
    
    return unique_cloud_dict


def process_cloud_failure(config, unique_cloud_dict, cloud, cloud_obj, failure_dict):
    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
        grp_nm = cloud_tuple[0]
        cld_nm = cloud_tuple[1]
        if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] + cloud_obj["password"] not in failure_dict:
            failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] + cloud_obj["password"]] = 1
        else:
            failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] + cloud_obj["password"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] + cloud_obj["password"]] + 1
        if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] + cloud_obj["password"]] > 3: #should be configurable
            logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
            config.incr_cloud_error(grp_nm, cld_nm)
    return failure_dict


def reset_cloud_error_dict(config, unique_cloud_dict, failure_dict, cloud, cloud_obj):
    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
        grp_nm = cloud_tuple[0]
        cld_nm = cloud_tuple[1]
        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] + cloud_obj["password"], None)
        config.reset_cloud_error(grp_nm, cld_nm)
    return failure_dict



def expand_failure_dict(config, cloud_table, cloud_type, data_type, failure_dict):
    rc, msg, cloud_list = config.db_query(cloud_table, where="cloud_type='%s'" % cloud_type)
    new_f_dict = {}
    for cloud in cloud_list:
        key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
        if key in failure_dict:
            new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1

    # since the new inventory function doesn't accept a failure dict we need to screen the rows ourselfs
    if cloud_type is not None:
        rc, msg, unfiltered_rows = config.db_query(data_type, where="cloud_type='%s'" % cloud_type)
    else:
        rc, msg, unfiltered_rows = config.db_query(data_type)
    rows = []
    for row in unfiltered_rows:
        if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
            continue
        else:
            rows.append(row)
    return rows
