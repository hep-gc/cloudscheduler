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
                    {'Name': 'name', 'Values':['suse-sles-15-v????????-hvm-ssd-x86_64']}# <- SUSE Linux Enterprise Server 15
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
        elasticbeanstak_dict = {}
        with open('output_suse.txt', 'w') as f:
            most_recent = 0
            cnt = 0
            for image in image_list['Images']:
                try: 
                    image['Platform']
                    continue
                except KeyError:
                    pass
                curr_recent = datetime.strptime(image_list['Images'][most_recent]['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z") 
                this_recent = datetime.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z")
                if this_recent > curr_recent:
                    most_recent = cnt
                cnt += 1
            image = image_list['Images'][most_recent]
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
            print(most_recent)
            print(cnt)

    except Exception as exc:
        print("Failure during processing...")
        print(exc)
        traceback.print_exc()
            
    return None


# main
if __name__ == '__main__':
    image_poller()


