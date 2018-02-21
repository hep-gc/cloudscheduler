"""
Google Compute Engine Connector Module.
"""
import googleapiclient.discovery

import cloudscheduler.basecloud

class GoogleCloud(cloudscheduler.basecloud):
    """
    Cloud Connector class for Google Compute Engine.
    """

    def __init__(self, resource, extrayaml):
        """Constructor for GCE."""
        cloudscheduler.basecloud.BaseCloud.__init__(self, name=resource.cloud_name,
                                                    extrayaml=extrayaml)
        # looks like we'll need the following to talk to GCE.
        # a project_id
        # a bucket name - storage bucket - will this have to be created before or should CS take care of it?
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

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        self.log.debug("vm_create from gce.")


    def vm_destroy(self, vm):
        self.log.debug("vm_destroy from gce.")

    def vm_update(self):
        self.log.debug("vm_update from gce.")
