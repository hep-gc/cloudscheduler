#!/usr/bin/env python

import time
import sys
import os
import requests
import json

from cloudscheduler.lib.db_config import Config

# The purpose of this file is to collect region offer files from amazon pricing urls to store in
# /var/local/ec2/regions/<region>/instance_types for a more efficient performance of the Flavor Poller - ec2FlavorPoller.py



def getAmazonOffersJSON():
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    REGION = config.db_map.classes.ec2_regions
    CONFIG = config.db_map.classes.csv2_configuration

    config.db_open()
    db_session = config.db_session

    region_list = db_session.query(REGION)
    config_list = db_session.query(CONFIG).filter(CONFIG.category == "ec2FlavorPoller.py", CONFIG.config_key == "region_instance_type_file")
            
    # Get region instance type file location
    save_at = False
    for con in config_list:
        save_at = con.config_value
        break
    if not save_at:
        print("Could not get region instance type file location... exiting")
    else:
        for region in region_list:
            region = region.region
            print("Getting flavors for region - {}".format(region))
            # Skip China, info not available in AWS offers file
            if region.split("-", 1)[0] == "cn":
                print("Skipping China - {}. No available flavor information".format(region))
                continue
            try:
                flav_list = False
                url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.json".format(region)
                resp = requests.get(url)
                resp.raise_for_status()
                flav_list = resp.json()
            except Exception as exc:
                print("Failed to retrieve flavors JSON for region - {} from Amazon pricing url, skipping this region".format(region))
                print(exc)

            if flav_list:
                # Save offer file in /var/local/ec2/regions
                try:
                    os.makedirs(save_at+"/{}".format(region))
                except FileExistsError:
                    pass
                try:
                    with open(save_at+"/{}/instance_types.json".format(region), 'w') as f:
                        f.write(json.dumps(flav_list))
                except Exception as exc:
                    print("Error saving json file")
                    print(exc)
        
    config.db_close()
    del db_session
    print("done")
    return -1


# main

if __name__ == '__main__':
    getAmazonOffersJSON()

