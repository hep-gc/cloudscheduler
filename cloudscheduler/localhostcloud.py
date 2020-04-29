"""
LocalHost module - connector classes for local cloud simulation
inherits from BaseCloud
"""
import os
import tempfile
import subprocess
import logging
import gzip
import time

#from sqlalchemy import create_engine
#from sqlalchemy.ext.automap import automap_base
#from sqlalchemy.orm import Session

from email import message_from_file

import libvirt
import yaml

import basecloud
import config as csconfig

class LocalHostCloud(basecloud.BaseCloud):

    """
    Localhost Connector class for cloudscheduler
    """
    def __init__(self, config, resource=None, defaultimage=None,
                 defaultnetwork=None, extrayaml=None, imagerepo='', metadata=None):

        """
        Localhost constructor

        :param csmain's db_config
        :param resource: resource row from db
        :param defaultsecuritygroup:
        :param defaultimage:
        :param defaultflavor:
        :param defaultnetwork:
        :param extrayaml: The cloud specific yaml
        """
        basecloud.BaseCloud.__init__(self, config, name=resource.cloud_name,
                                                    extrayaml=extrayaml, metadata=metadata)
        self.log = logging.getLogger(__name__)
        self.default_image = defaultimage
        self.default_network = defaultnetwork
        self.default_imagerepo = imagerepo

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None, template_dict=None):
        """
        Try to boot VMs on LocalHost.
        :param group_yaml_list: yaml from the group owning cloud
        :param num: Number of VMs to try and boot
        :param job: job row from db
        :return: exit code indicating success or error
        """

        #Create connection
        conn = libvirt.open('qemu:///system')
        if conn is None:
            self.log.error("Failed to open connection to hypervisor")
            return -1

        # Deal with user data - combine and zip etc.
        template_dict['cs_cloud_type'] = self.__class__.__name__
        template_dict['cs_flavor'] = flavor
        user_data_list = job.user_data.split(',') if job.user_data else []
        userdata = self.prepare_userdata(group_yaml=group_yaml_list,
                                         yaml_list=user_data_list,
                                         template_dict=template_dict)

        hostname = self._generate_next_name()

        # Check image from job, else use cloud default, else global default
        image_dict = self._attr_list_to_dict(job.image)
        self.log.debug(image_dict)
        self.log.debug(self.name)
        try:
            if job.image and self.name in image_dict:
                image = image_dict[self.name]
            elif self.default_image:
                image = self.default_image
            elif 'default' in image_dict:
                image = image_dict['default']
            else:
                image = csconfig.config.default_image
        except Exception as error:
            self.log.error("Could no determine image: %s", error)
            return -1
        if not image:
            self.log.debug("Unable to find an image to use")
            return -1

        #Check the image exists and backing directory
        #imagerepo = self.default_imagerepo
        imagerepo = '/home/tahyaw/instances'
        if os.path.exists(imagerepo+'/base/'+image):
            path = imagerepo+'/base/'+image
        elif os.path.exists(imagerepo+'/'+image):
            path = imagerepo+'/'+image
        elif os.path.exists(image):
            path = image
            image = os.path.basename(path)
        else:
            self.log.error("Could not find image %s: Does not exists in image repository %s", image, imagerepo)
            return -1

        #Job request disk given in KiB, convert to GB for qemu
        disk_gb = (job.request_disk/1000000) + 1
        #Create image copies to use with backing files
        if image.endswith('.img'):
            image_copy = image.rstrip('.img')
            image_copy = image_copy+'-'+hostname+'.qcow2'
            subprocess.call('qemu-img create -f qcow2 -o size='+str(disk_gb)+'GB -b '+path+' '+imagerepo+'/'+image_copy, shell=True)
            image = image_copy
            path = imagerepo+'/'+image
        elif image.endswith('.qcow2'):
            image_copy = image.rstrip('.qcow2')
            base = image_copy+'.img'
            if not os.path.exists(imagerepo+'/base'+base):
                subprocess.call('qemu-img convert -f qcow2 -O raw '+path+' '+imagerepo+'/base/'+base, shell=True)
            image_copy = image_copy +'-'+hostname+'.qcow2'
            subprocess.call('qemu-img create -f qcow2 -o size='+str(disk_gb)+'GB -b '+imagerepo+'/base/'+base+' '+imagerepo+'/'+image_copy, shell=True)
            image = image_copy
            path = imagerepo+'/'+image
        else:
            self.log.error("Unrecognized image format, must be qcow2 or raw image")
            return -1

        # Deal with network if needed
        netid = []
        network = None
        network_dict = self._attr_list_to_dict(job.network)
        self.log.debug(network_dict)
        if network_dict and self.name in network_dict:
            if len(network_dict[self.name].split('-')) == 5:  # uuid
                netid = [{'net-id': network_dict[self.name]}]
            else:
                network = self._find_network(network_dict[self.name])
        elif network_dict and 'default' in network_dict:
            if len(network_dict['default'].split('-')) == 5: # uuid
                netid = [{'net-id': network_dict['default']}]
            else:
                network = self._find_network(network_dict['default'])
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
            netid = [{'net-id': network.UUIDString()}]

        #Setup metadata and userdata
        metapath = self._generate_meta(hostname)

        #config_tmp = tempfile.mkdtemp(suffix='-'+hostname, dir='/home/tahyaw/instances')
        config_tmp = tempfile.mkdtemp(suffix='-'+hostname)
        self.log.debug(config_tmp)

        subprocess.call('mv '+metapath+' '+config_tmp+'/meta-data', shell=True)
        subprocess.call('rm -f '+metapath, shell=True)


        rawdata = gzip.decompress(userdata)
        with open(config_tmp+'/raw-user', 'w') as raw:
            raw.write(rawdata.decode())
        with gzip.open(config_tmp+'/user-data', 'wb') as ufile:
            ufile.write(rawdata)

        try:
            subprocess.call('mkisofs -o '+config_tmp+'/config.iso -V cidata -r -J --quiet '
                            +config_tmp+'/meta-data '+config_tmp+'/user-data', shell=True)
        except Exception as error:
            self.log.error("Could not create configuration drive for metadata: %s", error)
            return -1

        #Check that host can run requested vm
        instance = None
        host_cap = self._check_host_capabilities(conn)
        self.log.debug(host_cap)
        if job.request_cpus > (host_cap['vcpus'] - host_cap['activeCpus']):
            self.log.error("Host doesn't have available vcpus to boot VM")
            return -1
        if job.request_ram > host_cap['freeMemory']:
            self.log.error("Host doesn't have available ram to boot VM")
            return -1
        mem = job.request_ram + 1000
        #create domain def and launch domain

        virt_call = "virt-install --name "+hostname+" --network="+network.name()+ \
                    " --print-xml --dry-run -r "+str(mem)+" --disk path="+path+ \
                    ",sparse=true --disk path="+config_tmp+\
                    "/config.iso,device=cdrom --import --serial file,path="+config_tmp+\
                    "/boot-log --vcpus "+str(job.request_cpus)
        self.log.debug(virt_call)

        image_xml = subprocess.check_output(virt_call, shell=True)
        self.log.debug(type(image_xml))

        instance = conn.createXML(image_xml.decode(), 0)
        if instance is None:
            self.log.error("Failed to create domain from xml definition")
            return -1
        else:
            self.log.debug("New Image request successful.")

        """
        if instance:
#           new_vm = VM(vmid=instance.ID(), hostname=hostname)
#           self.vms[instance.ID()] = new_vm
#           engine = self._get_db_engine()
#           Base = automap_base()
#           Base.prepare(engine, reflect=True)
#           db_session = Session(engine)
#           vmobj = Base.classes.csv2_vms
            VM = self.config.db_map.classes.csv2_vms
            vm_dict = {
                'vmid': instance.ID(),
                'hostname': hostname,
                'status': 'New',
                'last_updated': int(time.time())
            }
            new_vm = VM(**vm_dict)
            self.config.db_open()
            self.config.db_session.merge(new_vm)
            self.config.db_close(commit=True)
        """
        self.log.debug('vm create')
        conn.close()

    def vm_destroy(self, vm):
        """
        Destroy VM on cloud.
        :param vm: ID of VM to destroy.
        """
        self.log.debug('vm destroy')

        conn = libvirt.open('qemu:///system')
        if conn is None:
            self.log.error("Failed to open connection with hypervisor")
            return -1

        try:
            instance = conn.lookupByName(vm.hostname)
            instance.destroy()
            del self.vms[vm.vmid]
        except libvirt.libvirtError as error:
            self.log.exception("VM %s not found on %s: Removing from CS: %s",
                               vm.hostname, self.name, error)
            del self.vms[vm.vmid]
        except Exception as ex:
            self.log.exception("Unhandled Exception trying to destroy VM: %s: %s",
                               vm.hostname, ex)
        conn.close()

        #Cleanup tmp dir and image copy
        try:
            subprocess.call('rm -f '+self.default_imagerepo+'/'+vm.image, shell=True)
        except Exception as ex:
            self.log.exception("Exception is deleting VM %s image %s: %s", vm.name, vm.image, ex)

        try:
            pipe = subprocess.Popen(['ls', '/tmp'], stdout=subprocess.PIPE)
            tmp = pipe.communicate()[0]
            for tmp_file in tmp.split():
                tmp_file = tmp_file.rstrip()
                if tmp_file.enswith(vm.hostname):
                    tmp_dir = '/tmp/'+tmp_file
                    subprocess.call('rm -rf '+tmp_dir, shell=True)
        except Exception as ex:
            self.log.exception("Could not remove the tmp directory for VM %s: %s", vm.hostname, ex)

    def vm_update(self):
        """I don't think this will be needed at all."""
        self.log.debug('vm update')

        conn = libvirt.open('qemu:///system')
        if conn is None:
            self.log.error("Failed to open connection to hypervisor")
            return -1
        try:
            listvms = conn.listAllDomains()
            for ovm in listvms:
                if owm.ID() == -1:
                    #domain not running
                    pass
                try:
                    self.vms[ovm.name()].status = ovm.state()
                except KeyError:
                    pass  # Will need to deal with unexpected vm still there by
                    # checking hostname and rebuilding vm obj if its a CS booted
                    # vm - probably have this as a config option since we
                    # sometimes remove  VMs intentionally
        except Exception as ex:
            self.log.exception(ex)


    def _find_network(self, netname):
        """
        Find network on OpenStack given a network name.
        :param netname: name of network to look for.
        :return: network object.
        """
        conn = libvirt.open('qemu:///system')
        if conn is None:
            self.log.error("Failed to open connection with hypervisor")
            return -1
        network = None
        try:
            network = conn.networkLookupByName(netname)
        except Exception as ex:
            self.log.exception("Unable to list networks for %s: Exception: %s", self.name, ex)
        return network

#   def _get_db_engine(self):
#       """
#       Get a connection to the database.
#       :return: db connection object.
#       """
#       return create_engine("mysql://" + csconfig.config.db_user + ":" +
#                            csconfig.config.db_password + "@" +
#                            csconfig.config.db_host + ":" +
#                            str(csconfig.config.db_port) + "/" +
#                            csconfig.config.db_name)

    def _generate_meta(self, name):
        instance_id = name
        host = name
        (fd, file_path) = tempfile.mkstemp(text=True)

        meta_info = {'instance-id':instance_id, 'local-hostname':host}

        with open(file_path, 'w') as yaml_file:
            yaml.dump(meta_info, yaml_file, default_flow_style=False)
        return file_path

    def _check_host_capabilities(self, conn):
        vcpus = conn.getMaxVcpus(None)
        node_info = conn.getInfo()
        mem = conn.getFreeMemory()

        cap = {'vcpus': vcpus, 'activeCpus': node_info[2], 'memory': node_info[1], 'freeMemory': mem}
        return cap
