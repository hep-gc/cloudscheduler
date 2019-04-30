#!/usr/bin/env python3

import time
from datetime import datetime
import sys
import os
import json
import traceback

import boto3

from cloudscheduler.lib.db_config import Config
    

def image_poller():
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    
    CLOUD = config.db_map.classes.csv2_clouds
    
    try:
        config.db_open()
        cloud_list = config.db_session.query(CLOUD).filter(CLOUD.cloud_type == "amazon")
        
        # Build unique region dict
        unique_region_dict = {}
        for cloud in cloud_list:
            if cloud.region not in unique_region_dict:
                unique_region_dict[cloud.region] = {
                    "cloud_obj": cloud,
                    "group-cloud": [(cloud.group_name, cloud.cloud_name)]
                }
            else:
                unique_region_dict[cloud.region]["group-cloud"].append((cloud.group_name, cloud.cloud_name))
        
        for region in unique_region_dict:
            # Retrieve all images for this region
            session = boto3.session.Session(region_name=region,
                                            aws_access_key_id=unique_region_dict[region]["cloud_obj"].username,
                                            aws_secret_access_key=unique_region_dict[region]["cloud_obj"].password)
            client = session.client('ec2')
            users2 = ['self','all']
            users1 = ['self']
            """
            filters = [
                        {'Name': 'image-type', 'Values': ['machine']},
                        {'Name': 'state', 'Values': ['available']},
                        {'Name': 'virtualization-type', 'Values': ['hvm']}
                      ]

            image_filters = 
            if image_filters.owner != None:
                values = []
                for fil in image_filters.owner.lower().split(','):
                    values.append(str(fil))
                filters.append({'Name': 'owner-alias', 'Values': values})
            
            if image_filters.architecture != None:
                values = []
                for fil in image_filters.architecture.lower().split(','):
                    values.append(str(fil))
                filters.append({'Name': 'architecture', 'Values': values})

            if image_filters.root_device_type != None:
                values = []
                ebs = False
                for fil in image_filters.root_device_type.lower().split(','):
                    if str(fil == 'ebs'):
                        ebs = True
                    values.append(str(fil))
                filters.append({'Name': 'root-device-type', 'Values': values})

            if ebs:
                if image_filters.ebs_size != None:
                    values = []
                    for fil in image_filters.ebs_size.lower().split(','):
                        values.append(str(fil))
                    filters.append({'Name': 'block-device-mapping.volume-size', 'Values': values})
            
            """


            filters = [ {'Name': 'owner-alias', 'Values':['amazon', 'self']},
                        {'Name': 'image-type', 'Values':['machine']},
                        {'Name': 'state', 'Values':['available']},
                        {'Name': 'virtualization-type', 'Values':['hvm']},
                        #{'Name': 'name', 'Values':['amzn2-ami-hvm-2.0.????????-x86_64-gp2']}# <- Amazon Linux 2
                        #{'Name': 'name', 'Values':['amzn-ami-hvm-????.??.?.????????-x86_64-gp2']}# <- Amazon Linux
                        #{'Name': 'name', 'Values':['ubuntu-xenial-16.04-amd64-server-*']}# <- Ubuntu Server 16.04 LTS
                        #{'Name': 'name', 'Values':['RHEL-7.5_HVM_GA*']}# <- RHEL 7.5
                        #{'Name': 'name', 'Values':['suse-sles-15-v????????-hvm-ssd-x86_64']}# <- SUSE Linux Enterprise Server 15
                      ]
            try:
                image_list = client.describe_images(ExecutableUsers=users2, Filters=filters)
                print("Got response data")
            except Exception as exc:
                print("Failed to retrieve image data, skipping...")
                print(exc)
                return
            if image_list is False or image_list['Images'] == []:
                print("No images defined, skipping...")
                return
          
            eb_dict = {}
            amzn_dict = {}
            suse_dict = {}
            most_recent = 0
            cnt = 0
            for image in image_list['Images']:
                try:
                    # Skip Windows
                    image['Platform']
                    cnt += 1 
                    continue
                except KeyError:
                    pass
                if 'Deep Learning' in image['Name']:
                    cnt +=1
                    continue

                # Filtering for getting only the most recent version
                elif 'elasticbeanstalk' in image['Name']:
                    try:
                        curr = eb_dict[image['Name'].split('-')[-3]]
                        curr_time = datetime.strptime(curr['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                        this_time = datetime.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                        if this_time > curr_time:
                            eb_dict[image['Name'].split('-')[-3]] = image_list['Images'][cnt]
                    except KeyError:
                        eb_dict[image['Name'].split('-')[-3]] = image_list['Images'][cnt]
                elif 'amzn-ami' in image['Name'] or 'amzn2-ami' in image['Name']:
                    try:
                        curr = amzn_dict["-".join(image['Name'].split('.')[0].split('-')[:-1])+"-"+"".join(image['Name'].split('-')[-1])]
                        curr_time = datetime.strptime(curr['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                        this_time = datetime.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                        if this_time > curr_time:
                            amzn_dict["-".join(image['Name'].split('.')[0].split('-')[:-1])+"-"+"".join(image['Name'].split('-')[-1])] = image_list['Images'][cnt]
                    except KeyError:
                        amzn_dict["-".join(image['Name'].split('.')[0].split('-')[:-1])+"-"+"".join(image['Name'].split('-')[-1])] = image_list['Images'][cnt]
                
                elif 'suse-sles' in image['Name']:
                    try:
                        name = image['Name'].split('-')
                        count = 0
                        for word in name:
                            if word[0] == 'v':
                                del name[count]
                            count += 1
                        name = "-".join(name)
                        curr = suse_dict[name]
                        curr_time = datetime.strptime(curr['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                        this_time = datetime.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                        if this_time > curr_time:
                            suse_dict[name] = image_list['Images'][cnt]
                    except KeyError:
                        suse_dict[name] = image_list['Images'][cnt]
                
                else:
                    with open('output3.txt', 'a') as f:
                        for attr in image:
                            tab = ':\t'
                            if len(attr) <= 6:
                               tab = ':\t\t\t'
                            elif len(attr) <= 14:
                                tab = ':\t\t'
                            try:
                                f.write(
                                    attr+tab+str(image[attr])+'\n'
                                )
                            except Exception as exc:
                                print(exc)
                        f.write('\n')
                cnt += 1
            
            #print(eb_dict.items())
            with open('output3.txt', 'a') as f:
                for dictt in [eb_dict,amzn_dict,suse_dict]:
                    for image in dictt:
                        for attr in dictt[image]:
                            tab = ':\t'
                            if len(attr) <= 6:
                               tab = ':\t\t\t'
                            elif len(attr) <= 14:
                                tab = ':\t\t'
                            try:
                                f.write(
                                    attr+tab+str(dictt[image][attr])+'\n'
                                )
                            except Exception as exc:
                                print(exc)
                        f.write('\n')
            print(cnt)

    except Exception as exc:
        print("Failure during processing...")
        print(exc)
        traceback.print_exc()
            
    return None


# main
if __name__ == '__main__':
    image_poller()


