from __future__ import absolute_import, unicode_literals
import os
import sys
import time
import multiprocessing
from multiprocessing import Process
import subprocess
import logging
import django
from django.conf import settings

from celery import Celery
from celery.utils.log import get_task_logger
from glintwebui.db_util import get_db_base_and_session
from cloudscheduler.lib.db_config import Config

from glintwebui.glint_api import repo_connector
from glintwebui.utils import  jsonify_image_list, update_pending_transactions, get_images_for_group,\
set_images_for_group, process_pending_transactions, process_state_changes, queue_state_change,\
find_image_by_name, check_delete_restrictions, decrement_transactions, get_num_transactions,\
repo_proccesed, check_for_repo_changes, check_for_image_conflicts, check_and_transfer_defaults,\
set_conflicts_for_group, check_cached_images, add_cached_image, do_cache_cleanup


def image_collection():
    multiprocessing.current_process().name = "Glint Image Collection"
    wait_period = 0
    term_signal = False
    num_tx = get_num_transactions()

    # setup database objects
    Group_Resources = config.db_map.classes.csv2_group_resources
    Group = config.db_map.classes.csv2_groups
    Group_Defaults = db_map.classes.csv2_group_defaults

    # perminant for loop to monitor image states and to queue up tasks
    while True:
        # First check for term signal
        logging.debug("Term signal: %s", term_signal)
        if term_signal is True:
            #term signal detected, break while loop
            logging.info("Term signal detected, shutting down")
            return
        logging.info("Start Image collection")

        config.db_open()
        session = config.db_session
        group_list = session.query(Group)

        #if there are no active transactions clean up the cache folders
        if num_tx == 0:
            do_cache_cleanup()

        for group in group_list:
            logging.info("Querying group: %s for cloud resources." % group.group_name)
            repo_list = session.query(Group_Resources).filter(Group_Resources.group_name == group.group_name)
            image_list = ()
            for repo in repo_list:
                logging.info("Querying cloud: %s for image data." % repo.cloud_name)
                try:
                    rcon = repo_connector(
                        auth_url=repo.authurl,
                        project=repo.project,
                        username=repo.username,
                        password=repo.password,
                        user_domain_name=repo.user_domain_name,
                        project_domain_name=repo.project_domain_name,
                        alias=repo.cloud_name)
                    image_list = image_list + rcon.image_list

                except Exception as exc:
                    logging.error(exc)
                    logging.error("Could not connect to repo: %s at %s",\
                        repo.project, repo.authurl)

            # take the new json and compare it to the previous one
            # and merge the differences, generally the new one will be used but if there
            # are any images awaiting transfer or deletion they must be added to the list
            updated_img_list = update_pending_transactions(
                get_images_for_group(group.group_name),
                jsonify_image_list(image_list=image_list, repo_list=repo_list))

            # now we have the most current version of the image matrix for this group the last
            # thing that needs to be done here is to proccess the PROJECTX_pending_transactions
            logging.info("Processing pending Transactions for group: %s", group.group_name)
            updated_img_list = process_pending_transactions(
                group_name=group.group_name,
                json_img_dict=updated_img_list)
            logging.info("Proccessing state changes for group: %s", group.group_name)
            updated_img_list = process_state_changes(
                group_name=group.group_name,
                json_img_dict=updated_img_list)
            set_images_for_group(group_name=group.group_name, json_img_dict=updated_img_list)

            # Need to build conflict dictionary to be displayed on matrix page. Check for
            # image conflicts function returns a dictionary of conflicts, keyed by the repos
            # THESE FUNCTIONS ARE NOT USED FOR CSV2 ANYWHERE SO I AM DISABLING THEM
            #conflict_dict = check_for_image_conflicts(json_img_dict=updated_img_list)
            #set_conflicts_for_group(group_name=group.group_name, conflict_dict=conflict_dict)

            logging.info("Checking resources for group default image...")
            check_and_transfer_defaults(session, updated_img_list, group.group_name)


        logging.info("Image collection complete, entering downtime")
        config.db_close()
        del session

        loop_counter = 0
        if num_tx == 0:
            wait_period = config.image_collection_interval
        else:
            wait_period = 0

        while loop_counter*5 < wait_period:
            time.sleep(5)
            num_tx = get_num_transactions()
            #check for new transactions
            if num_tx > 0:
                break
            #check if repos have been added or deleted
            if check_for_repo_changes():
                repo_proccesed()
                break

            #check if httpd is running
            output = subprocess.check_output(['ps', '-A'])
            if 'httpd' not in str(output):
                #apache has shut down, time for image collection to do the same
                logging.info("httpd offline, terminating")
                term_signal = True
                break
            loop_counter = loop_counter+1
        num_tx = get_num_transactions()





## Main.

if __name__ == '__main__':
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    logging.basicConfig(
        filename=config.log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-16s - %(levelname)s - %(message)s')

    logging.info("**************************** starting glint image collection *********************************")

    processes = {}
    process_ids = {
        'glint':     image_collection,
        }

    # Wait for keyboard input to exit
    try:
        while True:
            for process in process_ids:
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        logging.error("%s process died, restarting...", process)
                        del(processes[process])
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.sleep_interval_main_short)
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process)
