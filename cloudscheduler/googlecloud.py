"""
Google Compute Engine Connector Module.
"""
import cloudscheduler.basecloud

class GoogleCloud(cloudscheduler.basecloud):
    """
    Cloud Connector class for Google Compute Engine.
    """

    def __init__(self, resource, extrayaml):
        """Constructor for GCE."""
        cloudscheduler.basecloud.BaseCloud.__init__(self, name=resource.cloud_name,
                                                    extrayaml=extrayaml)

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        pass

    def vm_destroy(self, vm):
        pass

    def vm_update(self):
        pass