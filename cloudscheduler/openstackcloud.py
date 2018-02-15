"""
OpenStack module - connector classes for OpenStack Clouds
inherits from BaseCloud
"""
import logging
import novaclient.exceptions
from novaclient import client as nvclient
from keystoneauth1 import session
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from neutronclient.v2_0 import client as neuclient
from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# from sqlalchemy.ext.automap import automap_base

import cloudscheduler.basecloud
import cloudscheduler.config as csconfig

class OpenStackCloud(cloudscheduler.basecloud.BaseCloud):

    """
    OpenStack Connector class for cloudscheduler
    """
    def __init__(self, resource=None, defaultsecuritygroup=None,
                 defaultimage=None, defaultflavor=None,
                 defaultnetwork=None, extrayaml=None,):

        """
        OpenStack constructor

        :param resource: resource row from db
        :param defaultsecuritygroup:
        :param defaultimage:
        :param defaultflavor:
        :param defaultnetwork:
        :param extrayaml: The cloud specific yaml
        """
        cloudscheduler.basecloud.BaseCloud.__init__(self, name=resource.cloud_name,
                                                    extrayaml=extrayaml)
        self.log = logging.getLogger(__name__)
        self.authurl = resource.authurl
        self.username = resource.username
        self.password = resource.password
        self.region = resource.region
        self.keyname = resource.keyname
        self.cacertificate = resource.cacertificate
        self.project = resource.project
        self.userdomainname = resource.userdomainname
        self.projectdomainname = resource.projectdomainname
        self.session = self._get_auth_version(self.authurl)

        self.default_securitygroup = defaultsecuritygroup
        self.default_image = defaultimage
        self.default_flavor = defaultflavor
        self.default_network = defaultnetwork

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None, template_dict=None):
        """
        Try to boot VMs on OpenStack.
        :param group_yaml_list: yaml from the group owning cloud
        :param num: Number of VMs to try and boot
        :param job: job row from db
        :param flavor: flavor value from db
        :return: exit code indicating success or error
        """
        nova = self._get_creds_nova()
        # Check For valid security groups


        # Ensure keyname is valid
        if self.keyname:
            key_name = self.keyname if self.keyname else ""
            if not nova.keypairs.findall(name=self.keyname):
                key_name = ""
            elif not nova.keypairs.findall(name=csconfig.config.keyname):
                key_name = ""

        # Deal with user data - combine and zip etc.
        template_dict['cs_cloud_type'] = self.__class__.__name__
        template_dict['cs_flavor'] = flavor
        user_data_list = job.user_data.split(',') if job.user_data else []
        userdata = self.prepare_userdata(group_yaml=group_yaml_list,
                                         yaml_list=user_data_list,
                                         template_dict=template_dict)

        # Check image from job, else use cloud default, else global default
        imageobj = None
        image_dict = self._attr_list_to_dict(job.image)
        try:
            if job.image and self.name in image_dict.keys():
                imageobj = nova.glance.find_image(image_dict[self.name])
            elif self.default_image:
                imageobj = nova.glance.find_image(self.default_image)
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
        flavor = flavor
        try:
            flavor = nova.flavors.find(name=flavor)

        #    instancetype_dict = self._attr_list_to_dict(job.VMInstanceType)
       #     if instancetype_dict and self.name in instancetype_dict.keys():
      #          flavor = nova.flavors.find(name=instancetype_dict[self.name])
     #       elif 'default' in instancetype_dict.keys():
    #            flavor = nova.flavors.find(name=instancetype_dict['default'])
   #         elif self.default_flavor:
  #              flavor = nova.flavors.find(name=self.default_flavor)
 #           else:
#                flavor = nova.flavors.find(name=csconfig.config.default_flavor)
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
                                           flavor=flavor, key_name=key_name,
                                           availability_zone=None, nics=netid,
                                           userdata=userdata,
                                           security_groups=None, max_count=num)
        except novaclient.exceptions.OverLimit as ex:
            self.log.exception(ex)
        except Exception as ex:
            self.log.exception(ex)
        if instance:
            self.log.debug("New Image request successful.")
            # new_vm = VM(vmid=instance.id, hostname=hostname)
            # self.vms[instance.id] = new_vm
            # Do I actually want to bother putting in the new VM or
            # let the poller handle it?
            #engine = self._get_db_engine()
            #Base = automap_base()
            #Base.prepare(engine, reflect=True)
            #db_session = Session(engine)
            #VM = Base.classes.csv2_vms
            #vm_dict = {
            #    'auth_url': self.authurl,
            #    'project': self.project,
            #    'vmid': instance.id,
            #    'hostname': hostname,
            #    'status': 'New',
            #    'last_updated': int(time.time()),
            #}
            #new_vm = VM(**vm_dict)
            #db_session.merge(new_vm)
            #db_session.commit()

        self.log.debug('vm create')

    def vm_destroy(self, vm):
        """
        Destroy VM on cloud.
        :param vm: ID of VM to destroy.
        """
        self.log.debug('vm destroy')
        nova = self._get_creds_nova()
        try:
            instance = nova.servers.get(vm.vmid)
            instance.delete()
            del self.vms[vm.vmid]
        except novaclient.exceptions.NotFound as ex:
            self.log.exception("VM %s not found on %s: Removing from CS: %s",
                               vm.hostname, self.name, ex)
            del self.vms[vm.vmid]
        except Exception as ex:
            self.log.exception("Unhandled Exception trying to destroy VM: %s: %s",
                               vm.hostname, ex)

    def vm_update(self):
        """I don't think this will be needed at all."""
        self.log.debug('vm update')
        nova = self._get_creds_nova()
        try:
            listvms = nova.servers.list()
            for ovm in listvms:
                try:
                    self.vms[ovm.id].status = ovm.status
                except KeyError:
                    pass  # Will need to deal with unexpected vm still there by
                    # checking hostname and rebuilding vm obj if its a CS booted
                    # vm - probably have this as a config option since we
                    # sometimes remove  VMs intentionally
        except Exception as ex:
            self.log.exception(ex)

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
                           password=self.password, project_name="",
                           project_domain_name=self.projectdomainname,
                           user_domain_name=self.userdomainname, )
        sess = session.Session(auth=auth, verify=self.cacertificate)
        return sess

    def _get_creds_nova(self):
        """
        Get a novaclient client object.
        :return: novaclient client.
        """
        client = nvclient.Client("2.0", session=self.session, region_name=self.region, timeout=10, )
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
            elif version == 3:
                keystone_session = self._get_keystone_session_v3()
        except ValueError as ex:
            self.log.exception("Error determining keystone version from auth url: %s", ex)
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
