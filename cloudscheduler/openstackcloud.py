"""
OpenStack module - connector classes for OpenStack Clouds
inherits from BaseCloud
"""
import time
import logging
import novaclient.exceptions
from novaclient import client as nvclient
from keystoneauth1 import session
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1.exceptions.connection import ConnectFailure
from keystoneauth1.exceptions.catalog import EmptyCatalog
from neutronclient.v2_0 import client as neuclient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#import cloudscheduler.basecloud
#import cloudscheduler.config as csconfig
import basecloud
import config as csconfig

class OpenStackCloud(basecloud.BaseCloud):

    """
    OpenStack Connector class for cloudscheduler
    """
    def __init__(self, resource=None, vms=None, defaultsecuritygroup=None,
                 extrayaml=None, metadata=None):

        """
        OpenStack constructor

        :param resource: resource row from db
        :param defaultsecuritygroup:
        :param defaultnetwork:
        :param extrayaml: The cloud specific yaml
        """
        basecloud.BaseCloud.__init__(self, group=resource.group_name,
                                     name=resource.cloud_name,
                                     extrayaml=extrayaml, metadata=metadata)
        self.log = logging.getLogger(__name__)
        self.authurl = resource.authurl
        self.username = resource.username
        self.password = resource.password
        self.region = resource.region
        self.keyname = resource.default_keyname
        self.cacertificate = resource.cacertificate
        self.project = resource.project
        self.userdomainname = resource.user_domain_name
        self.projectdomainname = resource.project_domain_name
        self.session = self._get_auth_version(self.authurl)
        if not self.session:
            raise Exception

        self.default_security_groups = resource.default_security_groups
        try:
            self.default_security_groups = self.default_security_groups.split(',')
        except:
            raise Exception
        self.default_image = resource.default_image
        self.default_flavor = resource.default_flavor
        self.default_network = resource.default_network
        self.keep_alive = resource.default_keep_alive

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
        user_data_list = job.user_data.split(',') if job.user_data else []
        userdata = self.prepare_userdata(yaml_list=user_data_list,
                                         template_dict=template_dict)

        nova = self._get_creds_nova()
        # Check For valid security groups


        # Ensure keyname is valid
        if self.keyname:
            key_name = ""
            try:
                if nova.keypairs.findall(name=self.keyname):
                    key_name = self.keyname
                elif nova.keypairs.findall(name=csconfig.config.keyname):
                    key_name = csconfig.config.keyname
            except ConnectFailure as ex:
                self.log.exception("Failed to connect to openstack cloud: %s", ex)
                raise Exception
            except EmptyCatalog as ex:
                self.log.exception("Unable to find key %s ?", self.keyname)
                raise Exception
        else:
            key_name = ""

        # Check image from job, else use cloud default, else global default
        imageobj = None
        image_dict = self._attr_list_to_dict(job.image)
        try:
            if job.image and self.name in image_dict.keys():
                imageobj = nova.glance.find_image(image_dict[self.name])
            elif self.default_image:
                imageobj = nova.glance.find_image(self.default_image)
            elif image:
                imageobj = nova.glance.find_image(image)
            else:
                imageobj = nova.glance.find_image(csconfig.config.default_image)
        except novaclient.exceptions.EndpointNotFound:
            self.log.exception("Endpoint not found, region problem")
            return -1
        except novaclient.exceptions.NotFound as ex:
            self.log.exception("Problem finding image. Error: %s", ex)
        if not imageobj:
            self.log.debug("Unable to find an image to use")
            return -1

        # check flavor from job, else cloud default, else global default
        #flavor = flavor
        instancetype_dict = self._attr_list_to_dict(job.instance_type)
        try:
            #flavor = nova.flavors.find(name=flavor)
            if instancetype_dict and self.name in instancetype_dict.keys():
                flavorl = nova.flavors.find(name=instancetype_dict[self.name])
            elif 'default' in instancetype_dict.keys():
                flavorl = nova.flavors.find(name=instancetype_dict['default'])
            elif flavor:
                flavorl = nova.flavors.find(name=flavor.split(':')[1])
            elif self.default_flavor:
                flavorl = nova.flavors.find(name=self.default_flavor)
            else:
                flavorl = nova.flavors.find(name=csconfig.config.default_instancetype)
        except novaclient.exceptions.NotFound as ex:
            self.log.exception(ex)
        # Deal with network if needed
        netid = []
        network = None
        network_dict = self._attr_list_to_dict(job.network)
        if network_dict and self.name in network_dict.keys():
            if len(network_dict[self.name].split('-')) == 5:  # uuid
                netid = [{'net-id': network_dict[self.name]}]
            else:
                network = self._find_network(network_dict[self.name])
        elif self.default_network:
            if len(self.default_network.split('-')) == 5:  # uuid
                netid = [{'net-id': self.default_network}]
            else:
                network = self._find_network(self.default_network)
        elif csconfig.config.default_network:
            if len(csconfig.config.default_network.split('-')) == 5:  # uuid
                netid = [{'net-id': csconfig.config.default_network}]
            else:
                network = self._find_network(csconfig.config.default_network)
        if network and not netid:
            netid = [{'net-id': network.id}]
        hostname = self._generate_next_name()
        instance = None
        try:
            instance = nova.servers.create(name=hostname, image=imageobj,
                                           flavor=flavorl, key_name=key_name,
                                           availability_zone=None, nics=netid,
                                           userdata=userdata,
                                           security_groups=self.default_security_groups, max_count=num)
        except novaclient.exceptions.OverLimit as ex:
            self.log.exception(ex)
            raise novaclient.exceptions.OverLimit
        except Exception as ex:
            self.log.exception(ex)
            raise Exception
        if instance:
            self.log.debug("Try to fetch with filter of hostname used")
            engine = self._get_db_engine()
            base = automap_base()
            base.prepare(engine, reflect=True)
            db_session = Session(engine)
            vms = base.classes.csv2_vms
            for _ in range(0, 3):
                try:
                    list_vms = nova.servers.list(search_opts={'name':hostname})
                    break
                except novaclient.exceptions.BadRequest as ex:
                    self.log.warning("Bad Request caught, OpenStack db may not be updated yet, "
                                     "retrying")
                    time.sleep(1)

            for vm in list_vms:
                self.log.debug(vm)

                vm_dict = {
                    'group_name': self.group,
                    'cloud_name': self.name,
                    'auth_url': self.authurl,
                    'project': self.project,
                    'hostname': vm.name,
                    'vmid': vm.id,
                    'status': vm.status,
                    'flavor_id': vm.flavor["id"],
                    'task': vm.__dict__.get("OS-EXT-STS:task_state"),
                    'power_status': vm.__dict__.get("OS-EXT-STS:power_state"),
                    'last_updated': int(time.time()),
                    'keep_alive': self.keep_alive,
                    'start_time': int(time.time()),
                }
                new_vm = vms(**vm_dict)
                db_session.merge(new_vm)
            db_session.commit()

        self.log.debug('vm create')

    def _get_keystone_session_v2(self):
        """
        Gets a keystone session for version 2 keystone auth url.
        :return: session object for keystone
        """
        auth = v2.Password(auth_url=self.authurl, username=self.username,
                           password=self.password,
                           tenant_name=self.project, )
        sess = session.Session(auth=auth, verify=self.cacertificate)
        return sess

    def _get_keystone_session_v3(self):
        """
        Gets a keystone session for version 3 keystone auth url.
        :return: keystone session object.
        """
        auth = v3.Password(auth_url=self.authurl, username=self.username,
                           password=self.password, project_name=self.project,
                           project_domain_name=self.projectdomainname,
                           user_domain_name=self.userdomainname, )
        sess = session.Session(auth=auth, verify=self.cacertificate)
        return sess

    def _get_creds_nova(self):
        """
        Get a novaclient client object.
        :return: novaclient client.
        """
        client = nvclient.Client("2.0", session=self.session, region_name=self.region, timeout=10,)
        return client

    def _get_creds_neutron(self):
        """
        Get a neutron client.
        :return: neutron client.
        """
        return neuclient.Client(session=self.session)

    def _find_network(self, netname):
        """
        Find network on OpenStack given a network name.
        :param netname: name of network to look for.
        :return: network object.
        """
        nova = self._get_creds_nova()
        network = None
        try:
            network = nova.neutron.find_network(netname)
        except Exception as ex:
            self.log.exception("Unable to list networks for %s: Exception: %s", self.name, ex)
        return network

    def _get_auth_version(self, authurl):
        """
        Determine if we're using a v2 or v3 keystone auth url
        :param authurl: url for the keystone service
        :return: a valid keystone session of correct version.
        """
        keystone_session = None
        try:
            authsplit = authurl.split('/')
            version = int(float(authsplit[-1][1:])) if authsplit[-1]\
                else int(float(authsplit[-2][1:]))
            if version == 2:
                keystone_session = self._get_keystone_session_v2()
                self.log.debug("Using a v2 session for %s", self.name)
            elif version == 3:
                keystone_session = self._get_keystone_session_v3()
                self.log.debug("Using a v3 session for %s", self.name)
        except ValueError as ex:
            self.log.exception("Error determining keystone version from auth url: %s", ex)
            keystone_session = None
        return keystone_session

    def _get_db_engine(self):
        """
        Get a connection to the database.
        :return: db connection object.
        """
        return create_engine("mysql://" + csconfig.config.db_user + ":" +
                             csconfig.config.db_password + "@" +
                             csconfig.config.db_host + ":" +
                             str(csconfig.config.db_port) + "/" +
                             csconfig.config.db_name)
