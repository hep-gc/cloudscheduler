"""
EC2 API Cloud Connector Module. Using Boto
"""
import time
import base64
import logging

import boto3
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

try:
    import basecloud
except ImportError:
    import cloudscheduler.basecloud as basecloud

class EC2Cloud(basecloud.BaseCloud):

    """
    Cloud Connector class for EC2 API based clouds like AmazonEC2, or OpenNebula.
    """

    def __init__(self, resource=None, metadata=None, extrayaml=None):
        """Constructor for ec2 based clouds."""
        basecloud.BaseCloud.__init__(self, name=resource.cloud_name, group = resource.group_name,
                                     extrayaml=extrayaml, metadata=metadata)
        self.log = logging.getLogger(__name__)
        self.username = resource.username  # Access ID
        self.password = resource.password  # Secret key
        self.region = resource.region
        self.authurl = resource.authurl  # endpoint_url
        self.keyname = resource.default_keyname if resource.default_keyname else ""
        self.project = resource.project
        self.spot_price = resource.spot_price
        self.default_security_groups = resource.default_security_groups
        self.keep_alive = resource.default_keep_alive
        try:
            self.default_security_groups = self.default_security_groups.split(
                ',') if self.default_security_groups else ['default']
        except:
            raise Exception


    def _get_client(self):
        client = None
        try:
            session = boto3.session.Session(region_name=self.region,
                                            aws_access_key_id=self.username,
                                            aws_secret_access_key=self.password)
            client = session.client('ec2')
        except Exception as ex:
            self.log.exception(ex)
        return client

# base64.b64encode(user_data.encode("ascii")).decode('ascii')
    def vm_create(self, num=1, job=None, flavor=None, template_dict=None, image=None):
        self.log.debug("vm_create from ec2 cloud.")
        template_dict['cs_cloud_type'] = self.__class__.__name__
        template_dict['cs_flavor'] = flavor
        self.log.debug(template_dict)
        user_data_list = job.user_data.split(',') if job.user_data else []
        userdata = self.prepare_userdata(yaml_list=user_data_list,
                                         template_dict=template_dict)
        instancetype_dict = self._attr_list_to_dict(job.instance_type)
        tags = [{'ResourceType':'instance', 'Tags':[{'Key':'csv2', 'Value':'--'.join(
            [self.group, self.name, str(self.config.csv2_host_id)])}]}]
        client = self._get_client()
        if not client:
            self.log.error("Failed to get client for ec2. Check Configuration.")
            return -1


        # need to check on instance type, if one isn't specified by the job itself
        # we inherit from the cloud (aka the 'flavor' parameter)
        if self.name not in instancetype_dict.keys():
            instancetype_dict = self._attr_list_to_dict(flavor)
        if self.spot_price <= 0:
            flag_spot_instance = 0
            if self.keyname:
                new_vm = client.run_instances(ImageId=image, MinCount=1, MaxCount=num,
                                              InstanceType=instancetype_dict[self.name],
                                              UserData=userdata, KeyName=self.keyname,
                                              SecurityGroups=self.default_security_groups,
                                              TagSpecifications=tags)
            else:
                new_vm = client.run_instances(ImageId=image, MinCount=1, MaxCount=num,
                                              InstanceType=instancetype_dict[self.name],
                                              UserData=userdata,
                                              SecurityGroups=self.default_security_groups,
                                              TagSpecifications=tags)
        else:
            flag_spot_instance = 1
            specs = {'ImageId': image,
                     'InstanceType': instancetype_dict[self.name],
                     # Dumb encoding hack required for spot instances
                     # since boto behaves different on request_spot vs run_instance
                     'UserData': base64.b64encode(userdata).decode(),
                     'SecurityGroups': self.default_security_groups}
            if self.keyname:
                specs['KeyName'] = self.keyname
            new_vm = client.request_spot_instances(SpotPrice=str(self.spot_price),
                                                   Type='one-time', InstanceCount=num,
                                                   LaunchSpecification=specs)
        if 'Instances' in new_vm.keys():
            engine = self._get_db_engine()
            base = automap_base()
            base.prepare(engine, reflect=True)
            db_session = Session(engine)
            vms = base.classes.csv2_vms
            EC2_STATUS = base.classes.ec2_instance_status_codes
            ec2_status_dict = {}
            ec2_status = db_session.query(EC2_STATUS)
            for row in ec2_status:
                ec2_status_dict[row.ec2_state] = row.csv2_state

            for vm in new_vm['Instances']:
                self.log.debug(vm)
                hostname = vm['PublicDnsName'] if 'PublicDnsName' in vm.keys() \
                                                  and vm['PublicDnsName'] else vm['PrivateDnsName']
                vm_dict = {
                    'group_name': self.group,
                    'cloud_name': self.name,
                    'cloud_type': 'amazon',
                    'region': self.region,
                    'auth_url': self.authurl,
                    'project': self.project,
                    'hostname': hostname,
                    'vmid': vm['InstanceId'],
                    'spot_instance': flag_spot_instance,
                    'status': ec2_status_dict[vm['State']['Name']],
                    'flavor_id': vm['InstanceType'],
                    'last_updated': int(time.time()),
                    'keep_alive': self.keep_alive,
                    'start_time': int(time.time()),
                }
                new_vm = vms(**vm_dict)
                db_session.merge(new_vm)
            db_session.commit()
        elif 'SpotInstanceRequests' in new_vm.keys():
            # TODO Need to attach the tags to the spot instances

            engine = self._get_db_engine()
            base = automap_base()
            base.prepare(engine, reflect=True)
            db_session = Session(engine)
            vms = base.classes.csv2_vms
            EC2_STATUS = base.classes.ec2_instance_status_codes
            ec2_status_dict = {}
            ec2_status = db_session.query(EC2_STATUS)
            for row in ec2_status:
                ec2_status_dict[row.ec2_state] = row.csv2_state

            for vm in new_vm['SpotInstanceRequests']:
                self.log.debug(vm)
                client.create_tags(Resources=[vm['SpotInstanceRequestId']], Tags=tags[0]['Tags'])
                self.log.debug("STATE: %s", vm['State'])
                vm_dict = {
                    'group_name': self.group,
                    'cloud_name': self.name,
                    'region': self.region,
                    'cloud_type': 'amazon',
                    'auth_url': self.authurl,
                    'project': self.project,
                    'vmid': vm['SpotInstanceRequestId'],
                    'hostname': '',
                    'instance_id': '',
                    'status': ec2_status_dict[vm['State']['Name']],
                    'flavor_id': vm['LaunchSpecification']['InstanceType'],
                    'last_updated': int(time.time()),
                    'keep_alive': self.keep_alive,
                    'start_time': int(time.time()),
                }
                new_vm = vms(**vm_dict)
                db_session.merge(new_vm)
            db_session.commit()
        self.log.debug('ec2 vm_create')
