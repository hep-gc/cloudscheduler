"""
Oracle module - connector classes for Oracle Clouds
inherits from BaseCloud
"""
import time
from time import sleep
import logging
import oci
import base64

#import cloudscheduler.basecloud
#import cloudscheduler.config as csconfig
import json
import basecloud
import config as csconfig
from cloudscheduler.lib.oracle_functions import *

class OracleCloud(basecloud.BaseCloud):

    """
    Oracle Connector class for cloudscheduler
    """
    def __init__(self, config, resource=None, extrayaml=None, metadata=None):

        """
        Oracle constructor

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
        self.user_ocid = resource.get("user_ocid")
        self.api_private_key = resource.get("api_private_key")
        self.user_fingerprint = resource.get("user_fingerprint")
        self.tenancy_ocid = resource.get("tenancy_ocid")
        self.region = resource.get("region")
        self.default_image = resource.get("default_image")
        self.default_flavor = resource.get("default_flavor")
        self.flavor = resource.get("flavor")
        self.flavor_cores = resource.get("flavor_cores")
        self.flavor_ram = resource.get("flavor_ram")
        self.flavor_disk = resource.get("flavor_disk")
        self.default_network = resource.get("default_network")
        self.keep_alive = resource.get("default_keep_alive")
        self.oci_compartment = resource.get("oci_compartment")
        self.oci_availability_domain = resource.get("oci_availability_domain")
        
    def vm_create(self, num=1, job=None, flavor=None, template_dict=None, image=None):
        """
        Try to boot VMs on Oracle.
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


        # as a note the group level configuration comes from the resource and the cloud/job level configuration comes from the job
        # so when you are trying to find the proper config you check the job and if theres nothing there then check the defaults
        
        #collect oracle boot components
        self.config.db_open()
        where_clause = "group_name='%s' and cloud_name='%s'" % (self.group, self.name)
        rc, msg, compartment_list_raw = self.config.db_query("oracle_compartments", where=where_clause + " and name='%s'" % self.oci_compartment)
        if rc != 0 or len(compartment_list_raw) == 0:
            #problem getting the oracle compartment, likey there isn't one configured or for some reason the configured one doesn't exist
            logging.error("Unable to retrieve oci compartment entry for %s:" % self.oci_compartment)
            logging.error(msg)
            logging.error("Cancelling boot request")
            self.config.db_close()
            return 0
        else:
            compartment = compartment_list_raw[0]

        rc, msg, av_domains_raw = self.config.db_query("oracle_availability_domains", where=where_clause + " and name='%s'" % self.oci_availability_domain)
        if rc != 0 or len(compartment_list_raw) == 0:
            #problem getting the oracle compartment, likey there isn't one configured or for some reason the configured one doesn't exist
            logging.error("Unable to retrieve availability domain entry for %s:" % self.oci_compartment)
            logging.error(msg)
            logging.error("Cancelling boot request")
            self.config.db_close()
            return 0
        else:
            availability_domain = av_domains_raw[0]

        rc, msg, networks_raw = self.config.db_query("cloud_networks", where=where_clause + " and name='%s'" % job.get("network"))
        if rc != 0 or len(networks_raw) == 0:
            #if we don't find anything here we should check to see if we can find anything by the default name
            logging.debug("Got a bad return code or zero networks when querying for network name %s" % job.get("network"))
            logging.debug(msg)
            # we should check if we got more than one by this name too tho ideally names should be unique
            logging.debug("checking for a default network:")
            rc, msg, networks_raw = self.config.db_query("cloud_networks", where=where_clause + " and name='%s'" % self.default_network)
            if rc !=0 or len(networks_raw) == 0:
                #we still found nothing so we're giving up
                logging.error("Unable to determine network entry for either: %s or the default: %s" % (job.get("network"), self.default_network))
            else:
                #we found one or more networks by the default name
                if len(networks_raw) > 1:
                    logging.error("Found multiple networks on this cloud using the name %s, please ensure they are unique") # we could also just take the first one and hope for the best but i'm going to fail for now
                    logging.error("Cancelling boot request")
                    self.config.db_close()
                    return 0
                network = networks_raw[0]
        else:
            if len(networks_raw) > 1:
                logging.error("Found multiple networks on this cloud using the name %s, please ensure they are unique") # we could also just take the first one and hope for the best but i'm going to fail for now
                logging.error("Cancelling boot request")
                self.config.db_close()
                return 0
            network = networks_raw[0]
             
        rc, msg, images_raw = self.config.db_query("cloud_images", where=where_clause + " and name='%s'" % job.get("image"))
        if rc != 0 or len(images_raw) == 0:
            #if we don't find anything here we should check to see if we can find anything by the default name
            logging.debug("Got a bad return code or zero images when querying for image name %s" % job.get("image"))
            logging.debug(msg)
            # we should check if we got more than one by this name too tho ideally names should be unique
            logging.debug("checking for a default image:")
            rc, msg, images_raw = self.config.db_query("cloud_images", where=where_clause + " and name='%s'" % self.default_image)
            if rc !=0 or len(images_raw) == 0:
                #we still found nothing so we're giving up
                logging.error("Unable to determine image entry for either: %s or the default: %s" % (job.get("image"), self.default_image))
            else:
                #we found one or more images by the default name
                if len(images_raw) > 1:
                    logging.error("Found multiple images on this cloud using the name %s, please ensure they are unique") # we could also just take the first one and hope for the best but i'm going to fail for now
                    logging.error("Cancelling boot request")
                    self.config.db_close()
                    return 0
                image = images_raw[0]
        else:
            if len(images_raw) > 1:
                logging.error("Found multiple images on this cloud using the name %s, please ensure they are unique") # we could also just take the first one and hope for the best but i'm going to fail for now
                logging.error("Cancelling boot request")
                self.config.db_close()
                return 0
            image = images_raw[0]

        hostname = self._generate_next_name()

        # we should be smarter about handling this here, right now if we fail earlier and return zero the database connection isn't closed
        self.config.db_close()
             
        try:
            # boot without a volume
            self.log.debug("Booting on Oracle")
            based_userdata = base64.b64encode(userdata)
            format_userdata = based_userdata.decode('utf-8')
            
            client = self._get_client()

            try:
                if "amd" in flavor:
                    shape = "VM.Standard.E5.Flex"
                elif "intel" in flavor:
                    shape = "VM.Standard3.Flex"
                elif "arm" in flavor:
                    shape = "VM.Standard.A1.Flex"
                else:
                    logging.error("No CPU type (e.g. intel) included in flavour name, can't figure out flavour")
                    return 0
                
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus = self.flavor_cores, memory_in_gbs = self.flavor_ram)
                source_details=oci.core.models.InstanceSourceViaImageDetails(source_type = "image", image_id = image.get("id"), boot_volume_size_in_gbs = self.flavor_disk)
                launch_instance_details=oci.core.models.LaunchInstanceDetails(
                                        availability_domain = availability_domain.get("name"), 
                                        compartment_id = compartment.get("id"), shape = shape, 
                                        subnet_id = network.get("id"), source_details = source_details, 
                                        shape_config = shape_config, display_name = hostname,
                                        metadata = {"user_data": format_userdata})

                self.log.debug("Instance metadata")
                self.log.debug(launch_instance_details.metadata)

                new_vm = client.launch_instance(launch_instance_details)
            except Exception as exc:
                self.log.error(exc)
                self.log.error("Failed to create new vms: %s" % exc)

            vm_updated = self._update_vm_list(client, compartment.get("id"), hostname, job, num)
            if vm_updated:
                return num
            else:
                self.config.db_open()
                where_clause = "group_name='%s' and cloud_name='%s'" % (self.group, self.name)
                cloud_row = { "freeze": 1 }
                self.config.db_update("csv2_clouds", cloud_row, where=where_clause)
                self.config.db_close(commit=True)
                return 0

        except Exception as ex:
            self.config.update_service_catalog(provider='csmain', error='Error booting VM for group: %s, cloud: %s - %s' % (self.group, self.name, ex), logger=self.log)
            raise

    def _get_client(self):
        configdict = {}
        configdict["user_ocid"] = self.user_ocid
        configdict["api_private_key"] = self.api_private_key
        configdict["user_fingerprint"] = self.user_fingerprint
        configdict["tenancy_ocid"] = self.tenancy_ocid
        configdict["region"] = self.region

        oracleConfig = loadOracleConfig(configdict)
        client = oci.core.ComputeClient(oracleConfig)

        return client

    def _update_vm_list(self, client, compartment, hostname, job, num):
        self.log.debug("Try to fetch with filter of hostname used")
        list_vms = None
        for _ in range(0, 3):
            try:
                list_vms = client.list_instances(compartment_id = compartment, display_name = hostname).data
                break
            except Exception as ex:
                self.log.warning("Bad Request caught, Oracle db may not be updated yet, retrying %s" % ex)
                time.sleep(1)

        try:
            self.config.db_open()
            count = 0
            for vm in list_vms:
                self.log.debug(vm)
                vm_flavor_id = vm.shape

                vm_dict = {
                    'group_name': self.group,
                    'cloud_name': self.name,
                    'region': self.region,
                    'cloud_type': "oracle",
                    'hostname': vm.display_name,
                    'vmid': vm.id,
                    'status': translateStatus(vm.lifecycle_state),
                    'flavor_id': vm_flavor_id,
                    'image_id': vm.image_id,
                    'target_alias': job.get("target_alias"),
                    'last_updated': int(time.time()),
                    'keep_alive': self.keep_alive,
                    'start_time': int(time.time())
                }
                rc, msg = self.config.db_merge('csv2_vms', vm_dict)
                if rc == 0:
                    count = count + 1
            self.config.db_close(commit=True)
            if count != num:
                self.log.error("Error finding VM for group: %s, cloud: %s, found %s hostname %s" % (self.group, self.name, count, hostname))
                return False
        except Exception as exc:
            self.log.error("Error update VM for group: %s, cloud: %s : %s" % (self.group, self.name, exc))
            return False
        return True

