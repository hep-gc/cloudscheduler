import yaml
import cloudscheduler.openstackcloud

class CloudManager():
    def __init__(self, name, group_resources):
        self.name = name
        self.clouds = {}
        self.group_resources = group_resources

    def setup(self):

        for cloud in self.group_resources:
            newcloud = cloudscheduler.openstackcloud.OpenStackCloud(**cloud)
            self.clouds[newcloud.name] = newcloud
