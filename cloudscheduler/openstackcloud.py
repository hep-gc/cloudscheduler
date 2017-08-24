import cloudscheduler.vm
import cloudscheduler.basecloud
import novaclient.v2.client as nvclient
import novaclient.exceptions
from keystoneauth1 import session
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3

class OpenStackCloud(cloudscheduler.basecloud.BaseCloud):
    def __init__(self, name, slots, authurl, username, password, region=None, keyname=None ,cacert=None,
                 userdomainname=None, projectdomainname=None, defaultsecuritygroup=[], defaultimage=None,
                 defaultflavor=None, defaultnetwork=None, extrayaml=None, ):

        cloudscheduler.basecloud.BaseCloud.__init__(self, name=name, slots=slots)
        self.authurl = authurl
        self.username = username
        self.password = password
        self.region = region
        self.keyname = keyname
        self.cacert = cacert
        self.userdomainname = userdomainname
        self.projectdomainname = projectdomainname
        self.session = self._get_auth_version(authurl)

        self.default_securitygroup = defaultsecuritygroup
        self.default_image = defaultimage
        self.default_flavor = defaultflavor
        self.default_network = defaultnetwork

        self.extrayaml = extrayaml

    def vm_create(self, job=None):
        nova = self._get_creds_nova()
        #Check For valid security groups

        # Ensure keyname is valid
        if self.keyname:
            key_name = self.keyname if self.keyname else ""
            if not nova.keypairs.findall(name=keyname):
                key_name = ""
            elif not nova.keypairs.findall(name=config.keyname):
                key_name = ""

        # Deal with user data - combine and zip etc.

        # Check image coming from job, otherwise use cloud default, otherwise global default
        try:
            if self.name in job.image.keys():
                imageobj = nova.images.find(name=job.image[self.name])
            elif self.default_image:
                imageobj = nova.images.find(name=self.default_image)
            else:
                pass # global default image
        except novaclient.exceptions.EndpointNotFound:
            print("Endpoint not found, region problem")
            return -1
        except Exception as e:
            print("Problem finding image %s. Error: %s" % (job.image, e))

        # check flavor from job, otherwise cloud default, otherwise global default
        try:
            if self.name in job.VMInstanceType.keys():
                flavor = nova.flavors.find(name=job.VMInstanceType[self.name])
            elif self.default_flavor:
                flavor = nova.flavors.find(name=self.default_flavor)
            #else:
                #flavor = nova.flavors.find(name=config.default_flavor)
        except Exception as e:
            print(e)

        # Deal with network if needed
        if self.name in job.VMNetwork.keys():
            pass
        elif self.default_network:
            pass
        #elif config.default_network:
            #pass
        #else:
            #pass

        hostname = self._generate_next_name()
        instance = None
        try:
            instance = nova.servers.create(name=hostname, image=imageobj, flavor=flavor, key_name=self.keyname,
                                       availability_zone=None, nics=[], userdata=None, security_groups=None)
        except novaclient.exceptions.OverLimit as e:
            print(e)
        except Exception as e:
            print(e)
        if instance:
            new_vm = VM(vmid=instance.id, hostname=hostname)
            self.vms[instance.id] = new_vm
            self.slots -= 1


        
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
        auth = v2.Password(auth_url="", username="", password="", tenant_name="", )
        sess = session.Session(auth=auth, verify="")
        return sess

    def _get_keystone_session_v3(self):
        auth = v3.Password(auth_url="", username="", password="", project_name="", project_domain_name="",
                           user_domain_name="",)
        sess = session.Session(auth=auth, verify="")
        return sess

    def _get_creds_nova(self):
        client = nvclient.Client("2.0", session=self.session, region_name="", timeout=10,)
        return client

    def _find_network(self, netname):
        nova = self._get_creds_nova()
        network = None
        try:
            networks = nova.networks.list()
            for net in networks:
                if net.label == netname:
                    network = net
        except Exception as e:
            print("Unable to list networks for %s: Exception: %s" % (self.name, e))

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
