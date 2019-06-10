#!/usr/bin/env python3
import time
import sys
import os
import logging
import requests
import json

from cloudscheduler.lib.db_config import Config

# The purpose of this file is to collect region offer files from amazon pricing urls to store in
# a configurable local location for a more efficient performance of the Flavor Poller - ec2FlavorPoller.py



def getAmazonOffersJSON():
    # Set up
    logging.info("**************************** starting to collect ec2 region offer files ****************************")
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    REGION = config.db_map.classes.ec2_regions

    config.db_open()
    db_session = config.db_session

    # List of all ec2 regions from db
    region_list = db_session.query(REGION)
            
    # Get region instance type file location
    save_at = config.region_flavor_file_location
    
    logging.info("Getting flavors for ec2 regions")
    for region in region_list:
        region = region.region
        logging.debug("Getting flavors for region - {}".format(region))
        # Skip China, info not available in AWS offers file
        if region.split("-", 1)[0] == "cn":
            logging.info("Skipping China - {}. No available flavor information".format(region))
            continue
        try:
            flav_list = False
            url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.json".format(region)
            resp = requests.get(url)
            resp.raise_for_status()
            flav_list = resp.json()
        except Exception as exc:
            logging.error("Failed to retrieve flavors JSON for region - {} from Amazon pricing url, skipping this region".format(region))
            logging.error(exc)

        if flav_list:
            # Save offer file in location configured in db
            try:
                os.makedirs(save_at+"/{}".format(region))
            except FileExistsError:
                pass
            try:
                with open(save_at+"/{}/instance_types.json".format(region), 'w') as f:
                    f.write(json.dumps(flav_list))
            except Exception as exc:
                logging.error("Error saving json file")
                logging.error(exc)
        
    config.db_close()
    del db_session
    logging.info("**************************** completed ****************************")
    return None


# main

if __name__ == '__main__':
    
    # Set up logging file
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    logging.basicConfig(filename=config.log_file, level=config.log_level, format='%(asctime)s - Retrieve EC2 Flavor Files - %(levelname)s - %(message)s')
    
    #
    getAmazonOffersJSON()



