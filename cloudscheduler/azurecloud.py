"""
The Microsoft Azure cloud connection module.
It should have all the pieces specific to dealing with Azure clouds.
"""
import cloudscheduler.basecloud


class AzureCloud(cloudscheduler.basecloud.BaseCloud):

    """
    cloudscheduler connection object for Microsoft Azure Clouds.
    """

    def __init__(self, resource=None, extrayaml=None):
        """
        Create a new Microsoft Azure connection object
        :param resource: The row containing all the needed stuff from the database
        :param extrayaml: a tuple holding the cloud specific yaml
        """
        cloudscheduler.basecloud.BaseCloud.__init__(self,
                                                    name=resource.cloud_name, extrayaml=extrayaml)

    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        """
        Attempts to create a Virtual Machine on Microsoft Azure.
        :param group_yaml_list: The YAML for the group owning this cloud.
        :param num: The number of VMs to try booting.
        :param job: The job row to boot from.
        :param flavor: The flavor/instance type to boot.
        """
        print(group_yaml_list, num, job, flavor)

    def vm_destroy(self, vm):
        """
        Destroy a VM on Microsoft Azure cloud.
        """
        pass

    def vm_update(self):
        """
        Update the status of a VM on Microsoft Azure cloud.
        """
        pass
