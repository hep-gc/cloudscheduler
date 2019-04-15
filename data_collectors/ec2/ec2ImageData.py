#!/usr/bin/env python3

import time
from datetime import datetime
import sys
import os
import json
import traceback

import boto3
    

def image_poller():
    try:
        # Retrieve all images for this cloud.
        session = boto3.session.Session(region_name='us-west-2',
                                        aws_access_key_id='AKIAJILAEESQLCA6HXDA',
                                        aws_secret_access_key='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')
        client = session.client('ec2')
        users2 = ['self','all']
        users1 = ['self']

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
        most_recent = 0
        cnt = 0
        for image in image_list['Images']:
            try: 
                image['Platform']
                cnt += 1 
                continue
            except KeyError:
                pass
            if 'Deep Learning' in image['Name']:
                cnt +=1
                continue
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
        
        print(eb_dict.items())
        with open('output3.txt', 'a') as f:
            for bean in eb_dict:
                for attr in eb_dict[bean]:
                    tab = ':\t'
                    if len(attr) <= 6:
                       tab = ':\t\t\t'
                    elif len(attr) <= 14:
                        tab = ':\t\t'
                    try:
                        f.write(
                            attr+tab+str(eb_dict[bean][attr])+'\n'
                        )
                    except Exception as exc:
                        print(exc)
                f.write('\n')
            for bean in amzn_dict:
                for attr in amzn_dict[bean]:
                    tab = ':\t'
                    if len(attr) <= 6:
                       tab = ':\t\t\t'
                    elif len(attr) <= 14:
                        tab = ':\t\t'
                    try:
                        f.write(
                            attr+tab+str(amzn_dict[bean][attr])+'\n'
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


