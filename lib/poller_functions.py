from dateutil import tz, parser
import hashlib
import logging
import time
import os

from cloudscheduler.lib.attribute_mapper import map_attributes

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

## Poller functions.

def start_cycle(new_poll_time, start_time):
    logging.debug("Beginning poller cycle")
    start_time = time.time()
    new_poll_time = int(start_time)
    return new_poll_time, start_time

# This function helps maintain a moving average of cycle time and if the cycle times are
# exceeding the configured sleep time it lengthens the sleep to the average cycle time
def wait_cycle(start_time, poll_time_history, config_sleep_time):
    cycle_length = time.time() - start_time
    poll_time_history.append(cycle_length)
    if len(poll_time_history) > 5:
        poll_time_history.pop(0)

    avg_cycle_length = 0
    for poll_time in poll_time_history:
        avg_cycle_length = avg_cycle_length + poll_time
    avg_cycle_length = avg_cycle_length/len(poll_time_history)

    if avg_cycle_length > config_sleep_time:
        logging.debug("Completed cycle - cycle length: %s, sleeping for %s" % (cycle_length, avg_cycle_length))
        time.sleep(avg_cycle_length)
    else:
        logging.debug("Completed cycle - cycle length: %s, sleeping for %s" % (cycle_length, config_sleep_time))
        time.sleep(config_sleep_time)
    return


def build_inventory_for_condor(inventory, db_session, group_resources_class):
    cloud_list = db_session.query(group_resources_class)
    for cloud in cloud_list:
        set_inventory_group_and_cloud(inventory, cloud.group_name, "-",)


def cleanup_inventory(inventory, base_class_key, poll_time=None):
    logging.debug("Starting Inventory Cleanup")
    items_to_clean = []
    for group_name in inventory:
        for cloud_name in inventory[group_name]:
            for item in inventory[group_name][cloud_name]:
                if base_class_key == '-':
                    if inventory[group_name][cloud_name]['-']['poll_time'] < poll_time:
                        items_to_clean.append((group_name, cloud_name))
                        #
                        #logging.debug("Cleaning up %s - %s" % (group_name, cloud_name))
                        #inventory[group_name].pop(cloud_name, None)
                else:
                    if inventory[group_name][cloud_name][item.__dict__[base_class_key]]['poll_time'] < poll_time:
                        items_to_clean.append((group_name, cloud_name, item.__dict__[base_class_key]))
                        #
                        #logging.debug("Cleaning up %s - %s - %s" % (group_name, cloud_name, item.__dict__[base_class_key]))
                        #inventory[group_name][cloud_name].pop(item.__dict__[base_class_key], None)

    for item in items_to_clean:
        if base_class_key == '-':
            logging.debug("Cleaning up %s - %s" % (item[0], item[1]))
            inventory[item[0]].pop(item[1], None)
        else:
            logging.debug("Cleaning up %s - %s - %s" % (item[0], item[1], item[2]))
            inventory[item[0]][item[1]].pop(item[2], None)



def delete_obsolete_database_items(type, inventory, db_session, base_class, base_class_key, poll_time=None, failure_dict=None, cloud_type=None):
    inventory_deletions = []
    logging.debug("Delete Cycle - checking database for consistency")
    for group_name in inventory:
        for cloud_name in inventory[group_name]:
            if failure_dict is not None:
                if cloud_name is not None and group_name+cloud_name in failure_dict: 
                    logging.info("Skipping deletes on %s::%s due to cloud polling failures" %  (group_name, cloud_name))
                    continue
                if group_name in failure_dict:
                    logging.info("Skipping deletes on %s due to condor polling failures" %  group_name)
                    continue
            if type == 'VM':
                if cloud_type is not None:
                    obsolete_items = db_session.query(base_class).filter(
                        base_class.group_name == group_name,
                        base_class.cloud_name == cloud_name,
                        base_class.last_updated < poll_time,
                        base_class.cloud_type == cloud_type
                        )

                else:
                    obsolete_items = db_session.query(base_class).filter(
                        base_class.group_name == group_name,
                        base_class.cloud_name == cloud_name,
                        base_class.last_updated < poll_time
                        )
            elif cloud_name == '-':
                if cloud_type is not None:
                    obsolete_items = db_session.query(base_class).filter(
                        base_class.group_name == group_name,
                        base_class.cloud_type == cloud_type
                        )
                else:
                    obsolete_items = db_session.query(base_class).filter(
                        base_class.group_name == group_name
                        )
            else:
                if cloud_type is not None:
                    obsolete_items = db_session.query(base_class).filter(
                        base_class.group_name == group_name,
                        base_class.cloud_name == cloud_name,
                        base_class.cloud_type == cloud_type
                        )
                else:
                    obsolete_items = db_session.query(base_class).filter(
                        base_class.group_name == group_name,
                        base_class.cloud_name == cloud_name
                        )

            uncommitted_updates = 0
            for item in obsolete_items:
                if type == 'VM' and cloud_type == "amazon":
                    if item.vmid[0:3].lower() == "sir" and (item.instance_id is None or item.instance_id == "") and item.terminate < 2:
                        #don't delete it since its a spot request that never got a vm
                        continue
                if base_class_key == '-' and poll_time:
                    if inventory[group_name][cloud_name]['-']['poll_time'] >= poll_time:
                        continue
                    else:
                        inventory_deletions.append([group_name, cloud_name, '-'])
                else:
                    if poll_time:
                        if item.__dict__[base_class_key] in inventory[group_name][cloud_name] and inventory[group_name][cloud_name][item.__dict__[base_class_key]]['poll_time'] >= poll_time:
                            continue
                        else:
                            inventory_deletions.append([group_name, cloud_name, item.__dict__[base_class_key]])
                    else:
                        if item.__dict__[base_class_key] in inventory[group_name][cloud_name]:
                            continue

                if base_class_key == '-':
                    logging.info("Cleaning up %s: from group:cloud - %s::%s" % (type, item.group_name, item.cloud_name))
                else:
                    logging.info("Cleaning up %s: %s from group:cloud - %s::%s" % (type, item.__dict__[base_class_key], item.group_name, cloud_name))

                try:
                    db_session.delete(item)
                    uncommitted_updates += 1
                except Exception as exc:
                    logging.exception("Failed to delete %s." % type)
                    logging.error(exc)

            if uncommitted_updates > 0:
                try:        
                    db_session.commit()
                    logging.info("%s deletions committed: %d" % (type, uncommitted_updates))
                except Exception as exc:
                    logging.exception("Failed to commit %s deletions (%d) for %s::%s." % (type, uncommitted_updates, group_name, cloud_name))
                    logging.error(exc)

    for item in inventory_deletions:
        try:
            del inventory[item[0]][item[1]][item[2]]
        except KeyError as exc:
            logging.error("Error attempting to delete obsolete enteries from inventory:")
            logging.error(exc)
            logging.error("Item: %s" % item)
            logging.error(inventory[item[0]][item[1]])

def foreign(vm):
    native_id = '%s--%s--' % (vm.group_name, vm.cloud_name)
    if vm.hostname[:len(native_id)] == native_id:
        return False
    else:
        return True

def get_inventory_item_hash_from_database(db_engine, base_class, base_class_key, debug_hash=False, cloud_type=None):
    inventory = {}
    try:
        db_session = Session(db_engine)
        if cloud_type is not None:
            rows =db_session.query(base_class).filter(base_class.cloud_type == cloud_type)
        else:
            rows = db_session.query(base_class)
        for row in rows:
            try:
                group_name = row.group_name
                cloud_name = row.cloud_name
            except AttributeError:
                # machines and jobs have no cloud name attribute
                group_name = row.group_name
                cloud_name = "-"

            if base_class_key == '-':
                hash_name = '-'
            else:
                hash_name = row.__dict__[base_class_key]

            if group_name not in inventory:
                inventory[group_name] = {}

            if cloud_name not in inventory[group_name]:
                inventory[group_name][cloud_name] = {}

            if hash_name not in inventory[group_name][cloud_name]:
                inventory[group_name][cloud_name][hash_name] = {'poll_time': 0}

            hash_list = []
            hash_object = hashlib.new('md5')
            for item in sorted(row.__dict__):
                if item == '_sa_instance_state' or item == 'group_name' or item == 'cloud_name' or item == 'last_updated':
                    continue
               
                hash_list.append('%s=%s' % (item, str(row.__dict__[item])))
                hash_object.update(hash_list[-1].encode('utf-8'))


            if debug_hash:
                inventory[group_name][cloud_name][hash_name]['hash'] = '%s,%s' % (hash_object.hexdigest(), ','.join(hash_list))
            else:
                inventory[group_name][cloud_name][hash_name]['hash'] = hash_object.hexdigest()

        logging.info("Retrieved inventory from the database.")
    except Exception as exc:
        logging.error("Unable to initialize inventory from the database, setting empty dictionary.")

    return inventory

def get_last_poll_time_from_database(db_engine, base_class_and_key):
    try:
        db_session = Session(db_engine)
        db_query = db_session.query(func.max(base_class_and_key).label("timestamp"))
        db_response = db_query.one()
        last_poll_time = db_response.timestamp
        del db_session
    except Exception as exc:
        logging.error("Failed to retrieve last poll time (%s, %s, %s), skipping this cloud..." % (db_engine, base_class, base_class_key))
        logging.error(exc)
        last_poll_time = 0

    logging.info("Setting last_poll_time: %s" % last_poll_time)
    return last_poll_time

def set_inventory_group_and_cloud(inventory, group_name, cloud_name):
    if group_name not in inventory:
        inventory[group_name] = {}

    if cloud_name not in inventory[group_name]:
        inventory[group_name][cloud_name] = {}

    return

def set_inventory_item(inventory, group_name, cloud_name, item, update_time):
    inventory[group_name][cloud_name][item] = True
    return int(parser.parse(update_time).astimezone(tz.tzlocal()).strftime('%s'))

def set_orange_count(logging, config, column, previous_count, current_count):
    if current_count < 1:
       orange_count = 0
    else:
       orange_count = current_count

    if orange_count != previous_count and (orange_count < 1 or orange_count >= config.categories["ProcessMonitor"]["orange_threshold"]):
        if not config.db_session:
            auto_close = True
            config.db_open()
        else:
            auto_close = False

        rc, msg = config.db_session_execute('update csv2_system_status set %s=%d;' % (column, orange_count))
        if rc == 0:
            config.db_session.commit()
        else:
            logging.error('Failed to update csv2_system_status, %s=%s' % (column, orange_count))

        if auto_close:
            config.db_close()

    return orange_count, orange_count

def test_and_set_inventory_item_hash(inventory, group_name, cloud_name, item, item_dict, poll_time, debug_hash=False):
    from cloudscheduler.lib.poller_functions import set_inventory_group_and_cloud

    set_inventory_group_and_cloud(inventory, group_name, cloud_name)

    if item not in inventory[group_name][cloud_name]:
        inventory[group_name][cloud_name][item] = {'hash': None}

    inventory[group_name][cloud_name][item]['poll_time'] = poll_time

    hash_list = []
    hash_object = hashlib.new('md5')
    for hash_item in sorted(item_dict):
        if hash_item == 'group_name' or hash_item == 'cloud_name' or hash_item == 'last_updated':
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

    if new_hash == inventory[group_name][cloud_name][item]['hash']:
        return True

    logging.debug("inventory_item_hash(old): %s" % inventory[group_name][cloud_name][item]['hash'])
    logging.debug("inventory_item_hash(new): %s" % new_hash)

    inventory[group_name][cloud_name][item]['hash'] = new_hash
    return False
