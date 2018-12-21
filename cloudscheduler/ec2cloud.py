"""
EC2 API Cloud Connector Module. Using Apache Libcloud
"""

#import boto3
#import botocore
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


import cloudscheduler.basecloud

class EC2Cloud(cloudscheduler.basecloud):

    """
    Cloud Connector class for EC2 API based clouds like AmazonEC2, or OpenNebula.
    """

    def __init__(self, resource, vms=None, extrayaml=None):
        """Constructor for ec2 based clouds."""
        cloudscheduler.basecloud.BaseCloud.__init__(self, name=resource.cloud_name, group = resource.group_name,
                                                    extrayaml=extrayaml, vms=vms)
        self.log = logging.getLogger(__name__)
        self.username = resource.username  # Access ID?
        self.password = resource.password  # Secret key?
        self.region = resource.region
        self.keyname = resource.keyname


        self.driver = get_driver(Provider.EC2)
        self.conn = self.driver(self.username, self.password, region=self.region)

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        self.log.debug("vm_create from ec2 cloud.")
        new_vm = self.conn.create_node(name=self.generate_name(), image=None, size=None)

    def vm_destroy(self, vm):
        self.log.debug("vm_destroy from ec2 cloud.")

    def vm_update(self):
        self.log.debug("vm_update from ec2 cloud.")
