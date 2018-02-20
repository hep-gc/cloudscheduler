"""
EC2 API Cloud Connector Module.
"""

import boto3
import botocore

import cloudscheduler.basecloud

class EC2Cloud(cloudscheduler.basecloud):

    """
    Cloud Connector class for EC2 API based clouds like AmazonEC2, or OpenNebula.
    """

    def __init__(self, resource, extrayaml):
        """Constructor for ec2 based clouds."""
        cloudscheduler.basecloud.BaseCloud.__init__(self, name=resource.cloud_name,
                                                    extrayaml=extrayaml)

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        pass

    def vm_destroy(self, vm):
        pass

    def vm_update(self):
        pass
