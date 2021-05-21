"""
OpenStack module - connector classes for OpenStack Clouds
inherits from BaseCloud
"""
import time
from time import sleep
import logging
import openstack
import novaclient.exceptions
from novaclient import client as nvclient
import base64

#import cloudscheduler.basecloud
#import cloudscheduler.config as csconfig
import json
import basecloud
import config as csconfig
from cloudscheduler.lib.openstack_functions import MyServer, get_openstack_sess, get_nova_connection, get_glance_connection, get_neutron_connection, get_cinder_connection

class OpenStackCloud(basecloud.BaseCloud):

    """
    OpenStack Connector class for cloudscheduler
    """
    def __init__(self, config, resource=None, extrayaml=None, metadata=None):

        """
        OpenStack constructor

        :param csmain's db_config
        :param resource: resource row from db
        :param defaultsecuritygroup:
        :param defaultnetwork:
        :param extrayaml: The cloud specific yaml
        """
        basecloud.BaseCloud.__init__(self, config, group=resource.get("group_name"),
                                     name=resource.get("cloud_name"),
                                     extrayaml=extrayaml, metadata=metadata)
        self.log = logging.getLogger(__name__)
        self.authurl = resource.get("authurl")
        self.username = resource.get("username")
        self.password = resource.get("password")
        self.region = resource.get("region")
        self.keyname = resource.get("default_keyname")
        self.cacertificate = resource.get("cacertificate")
        self.project = resource.get("project")
        self.userdomainname = resource.get("user_domain_name")
        self.projectdomainname = resource.get("project_domain_name")
        self.projectdomainid = resource.get("project_domain_id")
        self.authtype = resource.get("auth_type")
        self.appcredentials = resource.get("app_credentials")
        self.appcredentialssecret = resource.get("app_credentials_secret")
        self.session = self._get_auth_version(self.authurl)
        if not self.session:
            raise Exception

        self.default_security_groups = resource.get("default_security_groups")
        try:
            self.default_security_groups = self.default_security_groups.split(',') if self.default_security_groups else ['default']
        except:
            raise Exception
        self.default_image = resource.get("default_image")
        self.default_flavor = resource.get("default_flavor")
        self.default_network = resource.get("default_network")
        self.keep_alive = resource.get("default_keep_alive")
        self.volume_info = resource.get("vm_boot_volume")
        self.flavor_cores = resource.get("flavor_cores")

    def vm_create(self, num=1, job=None, flavor=None, template_dict=None, image=None):
        """
        Try to boot VMs on OpenStack.
        :param group_yaml_list: yaml from the group owning cloud
        :param num: Number of VMs to try and boot
        :param job: job row from db
        :param flavor: flavor value from db
        :return: exit code indicating success or error
        """

        # Deal with user data - combine and zip etc.
        template_dict['cs_cloud_type'] = self.__class__.__name__
        template_dict['cs_flavor'] = flavor
        self.log.debug(template_dict)
        user_data_list = job.get("user_data").split(',') if job.get("user_data") else []
        userdata = self.prepare_userdata(yaml_list=user_data_list,
                                         template_dict=template_dict)
        self.log.debug("~!~!~Userdata~!~!~")
        self.log.debug(userdata)
        
        nova = self._get_creds_nova()
        # Check For valid security groups

        # Ensure keyname is valid
        if self.keyname:
            key_name = ""
            try:
                self_keyname = self.keyname or ''
                config_keyname = csconfig.config.keyname or ''
                if nova.find_keypair(name_or_id=self_keyname):
                    key_name = self.keyname
                elif nova.find_keypair(name_or_id=config_keyname):
                    key_name = csconfig.config.keyname
            except Exception as ex:
                self.config.update_service_catalog(provider='csmain', error='Error finding keypair for group: %s, cloud: %s - %s' % (self.group, self.name, ex), logger=self.log)
                raise Exception
        else:
            key_name = ""

        # Check image from job, else use cloud default, else global default
        imageobj = None
        image_dict = self._attr_list_to_dict(job.get("image"))
        try:
            ex = 'no image found'
            glance = self._get_creds_glance()
            if job.get("image") and self.name in image_dict:
                imageobj = self._find_image(glance, image_dict[self.name])
            elif image:
                imageobj = self._find_image(glance, image)
            elif self.default_image:
                imageobj = self._find_image(glance, self.default_image)
            else:
                imageobj = self._find_image(glance, csconfig.config.default_image)
        except Exceptions as ex:
            imageobj = None
        
        if not imageobj:
            self.config.update_service_catalog(provider='csmain', error='Error finding image for group: %s, cloud: %s - %s' % (self.group, self.name, ex), logger=self.log)
            return -1

        # check flavor from job, else cloud default, else global default
        #flavor = flavor
        instancetype_dict = self._attr_list_to_dict(job.get("instance_type"))
        try:
            if instancetype_dict and self.name in instancetype_dict:
                flavorl = nova.find_flavor(name_or_id=instancetype_dict[self.name])
            elif 'default' in instancetype_dict:
                flavorl = nova.find_flavor(name_or_id=instancetype_dict['default'])
            elif flavor:
                flavorl = nova.find_flavor(name_or_id=flavor.split(':')[1])
            elif self.default_flavor:
                flavorl = nova.find_flavor(name_or_id=self.default_flavor)
            else:
                flavorl = nova.find_flavor(name_or_id=csconfig.config.default_instancetype)
        except openstack.exceptions.ResourceNotFound as ex:
            self.config.update_service_catalog(provider='csmain', error='Error finding flavor for group: %s, cloud: %s - %s' % (self.group, self.name, ex), logger=self.log)

        # Deal with network if needed
        netid = []
        network = None
        network_dict = self._attr_list_to_dict(job.get("network"))
        if network_dict and self.name in network_dict:
            if len(network_dict[self.name].split('-')) == 5:  # uuid
                netid = [{'uuid': network_dict[self.name]}]
            else:
                network = self._find_network(network_dict[self.name])
        elif self.default_network:
            if len(self.default_network.split('-')) == 5:  # uuid
                netid = [{'uuid': self.default_network}]
            else:
                network = self._find_network(self.default_network)
        elif csconfig.config.default_network:
            if len(csconfig.config.default_network.split('-')) == 5:  # uuid
                netid = [{'uuid': csconfig.config.default_network}]
            else:
                network = self._find_network(csconfig.config.default_network)
        if network and not netid:
            netid = [{'uuid': network.id}]
        hostname = self._generate_next_name()
        instance = None
        
        self.log.debug("netid %s" % netid)

        try:
            self.log.debug("Getting volume info..")
            self.log.debug("#################")
            self.log.debug(self.volume_info)
            vol_info = json.loads(self.volume_info)
        except Exception as ex:
            self.log.debug('Invalid or null volume for group: %s, cloud: %s - %s' % (self.group, self.name, ex))
            vol_info = None

        instance = None
        instances = None
        try:
            if vol_info is None:
                # boot without a volume
                self.log.debug("Booting without volume")
                based_userdata = base64.b64encode(userdata)
                format_userdata = based_userdata.decode('utf-8')
                sec_groups = []
                if self.default_security_groups:
                    sec_groups = list(map(lambda x: {"name": x}, self.default_security_groups))
                if key_name == '':
                    instance = nova._create(MyServer, name=hostname, image_id=imageobj.id, flavor_id=flavorl.id, user_data=format_userdata, networks=netid, security_groups=sec_groups, max_count=num)
                else:
                    instance = nova._create(MyServer, name=hostname, image_id=imageobj.id, flavor_id=flavorl.id, key_name=key_name, user_data=format_userdata, networks=netid, security_groups=sec_groups, max_count=num)
            else:
                instances = []
                self.log.debug("Booting with volume")
                for i in range(num):
                    # boot with a volume
                    size_per_core = vol_info.get("GBs_per_core")
                    base_size = vol_info.get("GBs", 0)
                    if size_per_core:
                        size = base_size + (size_per_core * self.flavor_cores)
                    else:
                        size = base_size
                    volume_type = vol_info.get("volume_type")
                    self.log.debug("Size: %s Base: %s GBpC: %s Core count: %s Def Flavor: %s flavorl: %s" % (size, base_size, size_per_core, self.flavor_cores, self.default_flavor, flavorl))
                    bdm = None
                    self.log.debug("creating boot volume")
                    cinder = self._get_creds_cinder()
                    bv_name = "vol-" + hostname
                    cv = cinder.create_volume(name=bv_name, size=size, image_id=imageobj.id, volume_type=volume_type, is_bootable=True)
                    while (cv.status != 'available'):
                        time.sleep(1)
                        cv = cinder.get_volume(cv.id)
                    bdm = [{'uuid': cv.id, 'source_type': 'volume', 'destination_type': 'volume', 'delete_on_termination': True, 'boot_index': i}]
                    #append tuple with nova responce and hostname used
                    based_userdata = base64.b64encode(userdata)
                    format_userdata = based_userdata.decode()
                    sec_groups = []
                    if self.default_security_groups:
                        sec_groups = list(map(lambda x: {"name": x}, self.default_security_groups))
                    if key_name == '':
                        instances.append((nova.create_server(name=hostname, image_id=imageobj.id, flavor_id=flavorl.id, block_device_mapping=bdm, user_data=format_userdata, networks=netid, security_groups=sec_groups), hostname))
                    else:
                        instances.append((nova.create_server(name=hostname, image_id=imageobj.id, flavor_id=flavorl.id, key_name=key_name, block_device_mapping=bdm, user_data=format_userdata, networks=netid, security_groups=sec_groups), hostname))
                    hostname = self._generate_next_name()


        except Exception as ex:
            self.config.update_service_catalog(provider='csmain', error='Error booting VM for group: %s, cloud: %s - %s' % (self.group, self.name, ex), logger=self.log)
            instance = None
            instances = None
            raise

        if instance:
            self.log.debug("Try to fetch with filter of hostname used")
            vms = "csv2_vms"
            for _ in range(0, 3):
                try:
                    list_vms = nova.servers(name=hostname)
                    break
                except Exception as ex:
                    self.log.warning("Bad Request caught, OpenStack db may not be updated yet, "
                                     "retrying %s" % ex)
                    time.sleep(1)

            self.config.db_open()
            for vm in list_vms:
                self.log.debug(vm)
                found_flavor = nova.find_flavor(name_or_id=vm.flavor['original_name'])
                vm_flavor_id = found_flavor.id

                vm_dict = {
                    'group_name': self.group,
                    'cloud_name': self.name,
                    'region': self.region,
                    'cloud_type': "openstack",
                    'auth_url': self.authurl,
                    'project': self.project,
                    'hostname': vm.name,
                    'vmid': vm.id,
                    'status': vm.status,
                    'flavor_id': vm_flavor_id,
                    'image_id': vm.image["id"],
                    'target_alias': job.get("target_alias"),
                    'task': vm.to_dict().get('task_state'),
                    'power_status': vm.to_dict().get('power_state'),
                    'last_updated': int(time.time()),
                    'keep_alive': self.keep_alive,
                    'start_time': int(time.time()),
                }
                self.config.db_merge(vms, vm_dict)
            self.config.db_close(commit=True)
        elif instances:
            self.log.debug("Parse instances using block storage")
            self.config.db_open()
            for instance, i_hostname in instances:
                vms = "csv2_vms"
                for _ in range(0, 3):
                    try:
                        list_vms = nova.servers(name=i_hostname)
                        break
                    except Exception as ex:
                        self.log.warning("Bad Request caught, OpenStack db may not be updated yet, "
                                         "retrying %s" % ex)
                        time.sleep(1)

                for vm in list_vms:
                    self.log.debug(vm)
                    found_flavor = nova.find_flavor(name_or_id=vm.flavor['original_name'])
                    vm_flavor_id = found_flavor.id

                    vm_dict = {
                        'group_name': self.group,
                        'cloud_name': self.name,
                        'region': self.region,
                        'cloud_type': "openstack",
                        'auth_url': self.authurl,
                        'project': self.project,
                        'hostname': vm.name,
                        'vmid': vm.id,
                        'status': vm.status,
                        'flavor_id': vm_flavor_id,
                        'image_id': vm.image["id"],
                        'target_alias': job.get("target_alias"),
                        'task': vm.to_dict().get('task_state'),
                        'power_status': vm.to_dict().get('power_state'),
                        'last_updated': int(time.time()),
                        'keep_alive': self.keep_alive,
                        'start_time': int(time.time()),
                    }
                    self.config.db_merge(vms, vm_dict)
                self.config.db_commit()

            self.config.db_close()
    

    def _get_keystone_data_v2(self):
        """
        Format the data for keystone session for version 2
        """
        return {"authurl": self.authurl, "username": self.username, "password": self.password, "project": self.project}

    def  _get_keystone_data_v3(self):
        """
        Format the data for keystone session for version 3
        """
        return {"authurl": self.authurl, "username": self.username, "password": self.password, "project": self.project, "project_domain_name": self.projectdomainname, "user_domain_name": self.userdomainname, "project_domain_id": self.projectdomainid}

    def _get_keystone_app_cred_data(self):
        """
        Format the data for keystone session using application credential
        """
        return {"authurl": self.authurl, "app_credentials": self.appcredentials, "app_credentials_secret": self.appcredentialssecret}

    def _get_creds_nova(self):
        """
        Get a novaclient client object by openstacksdk.
        :return: novaclient client.
        """
        try:
            nova = get_nova_connection(self.session, self.region)
        except Exception as e:
            self.log.error("Cannot use nova on %s:%s" % (self.name, e))
            raise e
        return nova

    def _get_creds_neutron(self):
        """
        Get a neutron client.
        :return: neutron client.
        """
        try:
            neutron = get_neutron_connection(self.session, self.region)
        except Exception as e:
            self.log.error("Cannot use neutron on %s:%s" % (self.name, e))
            raise e
        return neutron

    def _get_creds_cinder(self):
        try:
            cinder = get_cinder_connection(self.session, self.region)
        except Exception as e:
            self.log.error("Cannot use cinder on %s:%s" % (self.name, e))
            raise e
        return cinder

    def _get_creds_glance(self):
        try:
            glance = get_glance_connection(self.session, self.region)
        except Exception as e:
            self.log.error("Cannot use glance on %s:%s" % (self.name, e))
            raise e
        return glance

    def _find_image(self, glance, image_name):
        try:
            images = glance.images()
            for image in images:
                if image.name == image_name:
                    return image
        except Exception as e:
            self.log.error("Error retrieving image for %s:%s" % (self.name, e))
            return
        return

    def _find_network(self, netname):
        """
        Find network on OpenStack given a network name.
        :param netname: name of network to look for.
        :return: network object.
        """
        neutron = self._get_creds_neutron()
        network = None
        try:
            network = neutron.find_network(netname)
        except Exception as ex:
            self.config.update_service_catalog(provider='csmain', error='Error finding network for group: %s, cloud: %s - %s' % (self.group, self.name, ex), logger=self.log)
        return network

    def _get_auth_version(self, authurl):
        """
        Determine if we're using a v2 or v3 keystone auth url
        :param authurl: url for the keystone service
        :return: a valid keystone session of correct version.
        """
        keystone_session = None
        cloud_data = {}
        try:
            if self.authtype and self.authtype == 'app_creds':
               cloud_data = self._get_keystone_app_cred_data()
            else:
                authsplit = authurl.split('/')
                version = int(float(authsplit[-1][1:])) if authsplit[-1] else int(float(authsplit[-2][1:]))
                if version == 2:
                    #self.log.debug("Using a v2 session for %s", self.name)
                    cloud_data = self._get_keystone_data_v2()
                elif version == 3:
                    #self.log.debug("Using a v3 session for %s", self.name)
                    cloud_data = self._get_keystone_data_v3()
            keystone_session = get_openstack_sess(cloud_data, self.cacertificate)
        except ValueError as ex:
            self.log.exception("Error determining keystone version from auth url: %s", ex)
            keystone_session = None
        return keystone_session
