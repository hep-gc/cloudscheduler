from dateutil import tz, parser
import hashlib
import logging
import json
import os
import time

from cloudscheduler.lib.attribute_mapper_na import map_attributes

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


def inventory_get_item_hash_from_db_query_rows(ikey_names, rows):
    inventory = {}
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

