"""
Google Compute Engine Connector Module.
"""
import time
import googleapiclient.discovery

import cloudscheduler.basecloud

class GoogleCloud(cloudscheduler.basecloud.BaseCloud):
    """
    Cloud Connector class for Google Compute Engine.
    """

    def __init__(self, resource, extrayaml):
        """Constructor for GCE."""
        cloudscheduler.basecloud.BaseCloud.__init__(self, name=resource.cloud_name,
                                                    extrayaml=extrayaml)

        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.project = resource.project
        self.bucket = resource.bucket
        self.zone = resource.zone
        # looks like we'll need the following to talk to GCE.
        # a project_id
        # a bucket name - storage bucket - will this created before or CS take care of it?
        # a zone value - ie region equiv
        # a hostname - this will auto generate from the base cloud function.

        # To Create a VM:
        # image project and family? two values to get an image?
        # there's also the instance type / flavor ie n1-standard-1
        # there's a startup script option, does it support cloud-init out of the box?
        # there might be additonal setting for a specific network - path, type, and name.
        # service account email & scopes
        # metadata might have a different format - check v1 code to see what's similar.

        # not seeing anything about auth in the example.

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None, template_dict=None):
        self.log.debug("vm_create from gce.")
        # Deal with user data - combine and zip etc.
        template_dict['cs_cloud_type'] = self.__class__.__name__
        template_dict['cs_flavor'] = flavor
        user_data_list = job.user_data.split(',') if job.user_data else []
        userdata = self.prepare_userdata(group_yaml=group_yaml_list,
                                         yaml_list=user_data_list,
                                         template_dict=template_dict)
        # Check image from job, else use cloud default, else global default
        source_image = None
        image_dict = self._attr_list_to_dict(job.image)
        try:
            if job.image and self.name in image_dict.keys():
                source_image = 1 # TODO how to get the image url from service or line in db
        except ValueError:
            pass
        machine_type = "zones/{}/machineTypes/{}".format(self.zone, flavor)

        config = {
            'name': self._generate_next_name(),
            'machineType': machine_type,
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_image,
                    }
                }
            ],
            'networkInterfaces': [{
                'network': 'global/networks/default/',  # this may need to be configurable later
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External_NAT'}
                ]
            }],
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'
                ]
            }],
            'metadata': {
                'items': [{
                    'key': 'user-data',
                    'value': userdata,
                }]
            }
        }
        operation = self.compute.instances().insert(project=self.project,
                                                    zone=self.zone,
                                                    body=config).execute()
        self.log.debug(operation)


    def vm_destroy(self, vm):
        self.log.debug("vm_destroy from gce: %s", vm)

    def vm_update(self):
        self.log.debug("vm_update from gce.")

    def wait_gce_operation(self, compute, project, zone, operation):
        """Wait for Async Operation on GCE to finish before continuing.
        Since I'm less concerned about the VM states here this may not be as important."""
        self.log.debug("Waiting for gce operation to complete.")
        max_wait = 5
        while max_wait:
            result = compute.zoneOperations().get(project=project,
                                                  zone=zone,
                                                  operation=operation).execute()
            if result['status'] == 'DONE':
                self.log.debug("Operation Done.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result
            time.sleep(1)
            max_wait -= 1
