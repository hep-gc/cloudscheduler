#from cloudscheduler.vm import VM
import cloudscheduler.basecloud
import cloudscheduler.config as csconfig
import novaclient.exceptions
from novaclient import client as nvclient
from keystoneauth1 import session
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from neutronclient.v2_0 import client as neuclient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import time

class OpenStackCloud(cloudscheduler.basecloud.BaseCloud):
    def __init__(self, cloud_name, instances, authurl, username, password, region=None, keyname=None ,cacertificate=None,
                 userdomainname=None, projectdomainname=None, defaultsecuritygroup=[], defaultimage=None,
                 defaultflavor=None, defaultnetwork=None, extrayaml=None, tenantname=None):

        cloudscheduler.basecloud.BaseCloud.__init__(self, name=cloud_name, slots=instances, extrayaml=extrayaml)
        self.authurl = authurl
        self.username = username
        self.password = password
        self.region = region
        self.keyname = keyname
        self.cacertificate = cacertificate
        self.tenantname = tenantname
        self.userdomainname = userdomainname
        self.projectdomainname = projectdomainname
        self.session = self._get_auth_version(authurl)

        self.default_securitygroup = defaultsecuritygroup
        self.default_image = defaultimage
        self.default_flavor = defaultflavor
        self.default_network = defaultnetwork


    def vm_create(self, job=None):
        nova = self._get_creds_nova()
        #Check For valid security groups


        # Ensure keyname is valid
        if self.keyname:
            key_name = self.keyname if self.keyname else ""
            if not nova.keypairs.findall(name=self.keyname):
                key_name = ""
            elif not nova.keypairs.findall(name=csconfig.config.keyname):
                key_name = ""

        # Deal with user data - combine and zip etc.
        userdata = self.prepare_userdata(job.VMUserData)

        # Check image coming from job, otherwise use cloud default, otherwise global default
        imageobj = None
        try:
            if job.VMAMIConfig and self.name in job.VMAMIConfig.keys():
                imageobj = nova.glance.find_image(job.VMAMIConfig[self.name]) # update to glance?
            elif self.default_image:
                imageobj = nova.glance.find_image(self.default_image)
            else:
                imageobj = nova.glance.find_image(csconfig.config.default_image)
        except novaclient.exceptions.EndpointNotFound:
            print("Endpoint not found, region problem")
            return -1
        except Exception as e:
            print("Problem finding image. Error: %s" % (e))
        if not imageobj:
            print("Unable to find an image to use")
            return -1

        # check flavor from job, otherwise cloud default, otherwise global default
        flavor = None
        try:
            instancetype_dict = self._attr_list_to_dict(job.VMInstanceType)
            if instancetype_dict and self.name in instancetype_dict.keys():
                flavor = nova.flavors.find(name=instancetype_dict[self.name])
            elif 'default' in instancetype_dict.keys():
                flavor = nova.flavors.find(name=instancetype_dict['default'])
            elif self.default_flavor:
                flavor = nova.flavors.find(name=self.default_flavor)
            else:
                flavor = nova.flavors.find(name=csconfig.config.default_flavor)
        except Exception as e:
            print(e)
        # Deal with network if needed
        netid = []
        network = None
        network_dict = self._attr_list_to_dict(job.VMNetwork)
        if network_dict and self.name in network_dict.keys():
            if len(network_dict[self.name].split('-')) == 5: # uuid
                netid = [{'net-id': network_dict[self.name]}]
            else:
                network = self._find_network(network_dict[self.name])
        elif self.default_network:
            if len(self.default_network.split('-')) == 5: # uuid
                netid = [{'net-id': self.default_network}]
            else:
                network = self._find_network(self.default_network)
        elif csconfig.config.default_network:
            if len(csconfig.config.default_network.split('-')) == 5: # uuid
                netid = [{'net-id': csconfig.config.default_network}]
            else:
                network = self._find_network(csconfig.config.default_network)
        if network and not netid:
            netid = [{'net-id': network.id}]
        hostname = self._generate_next_name()
        instance = None
        try:
            instance = nova.servers.create(name=hostname, image=imageobj, flavor=flavor, key_name=self.keyname,
                                       availability_zone=None, nics=netid, userdata=userdata, security_groups=None)
        except novaclient.exceptions.OverLimit as e:
            print(e)
        except Exception as e:
            print(e)
        if instance:
            #new_vm = VM(vmid=instance.id, hostname=hostname)
            #self.vms[instance.id] = new_vm
            self.slots -= 1
            engine = self._get_db_engine()
            Base = automap_base()
            Base.prepare(engine, reflect=True)
            db_session = Session(engine)
            VM = Base.classes.csv2_vms
            vm_dict = {
                'auth_url': self.authurl,
                'project': self.tenantname,
                'vmid': instance.id,
                'hostname': hostname,
                'status': 'New',
                'last_updated': int(time.time()),
            }
            new_vm = VM(**vm_dict)
            db_session.merge(new_vm)
            db_session.commit()
            


        
        print('vm create')

    def vm_destroy(self, vm):
        print('vm destroy')
        nova = self._get_creds_nova()
        try:
            instance = nova.servers.get(vm.vmid)
            instance.delete()
            del self.vms[vm.vmid]
        except novaclient.exceptions.NotFound as e:
            print("VM %s not found on %s: Removing from CS" % (vm.hostname, self.name))
            del self.vms[vm.vmid]
            self.slots += 1
        except Exception as e:
            print("Unhandled Exception trying to destroy VM: %s: %s" % (vm.hostname, e))

    def vm_update(self):
        print('vm update')
        nova = self._get_creds_nova()
        try:
            listvms = nova.servers.list()
            for ovm in listvms:
                try:
                    self.vms[ovm.id].status = ovm.status
                except KeyError:
                    pass # Will need to deal with unexpected vm still there by checking hostname and rebuilding vm obj if its a CS booted vm - probably have this as a config option since we sometimes remove  VMs intentionally
        except Exception as e:
            print(e)

    def _get_keystone_session_v2(self):
        auth = v2.Password(auth_url=self.authurl, username=self.username, password=self.password, tenant_name=self.tenantname,)
        sess = session.Session(auth=auth, verify=self.cacertificate)
        return sess

    def _get_keystone_session_v3(self):
        auth = v3.Password(auth_url=self.authurl, username=self.username, password=self.password, project_name="", project_domain_name=self.projectdomainname,
                           user_domain_name=self.userdomainname,)
        sess = session.Session(auth=auth, verify=self.cacertificate)
        return sess

    def _get_creds_nova(self):
        client = nvclient.Client("2.0", session=self.session, region_name=self.region, timeout=10,)
        return client

    def _get_creds_neutron(self):
        return neuclient.Client(session=self.session)

    def _find_network(self, netname):
        nova = self._get_creds_nova()
        network = None
        try:
            network = nova.neutron.find_network(netname)
        except Exception as e:
            print("Unable to list networks for %s: Exception: %s" % (self.name, e))
        return network

    def _get_auth_version(self, authurl):
        session = None
        try:
            authsplit = authurl.split('/')
            version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            if version == 2:
                session = self._get_keystone_session_v2()
            elif version == 3:
                session = self._get_keystone_session_v3()
        except Exception as e:
            print("Error determining keystone version from auth url: %s" % e)
            return None
        return session

    def _get_db_engine(self):
        return create_engine("mysql://" + csconfig.config.db_user + ":" + csconfig.config.db_password + "@" +
                     csconfig.config.db_host + ":" + str(csconfig.config.db_port) + "/" + csconfig.config.db_name)
