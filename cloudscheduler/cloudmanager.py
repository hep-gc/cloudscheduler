import yaml
import cloudscheduler.openstackcloud

class CloudManager():
    def __init__(self, name, resource_file):
        self.name = name
        self.clouds = {}
        self.resource_file = resource_file

    def setup(self):
        try:
            pass
            # Have to connect to db and get cloud info from there instead

            with open(self.resource_file) as f:
                cloudresources = yaml.load(f)
        except Exception as e:
            print(e)
        
        #print(type(cloudresources))
        #print(cloudresources)
        for cloud in cloudresources:
            # determine type of cloud (would be nice if this could be done from the config keys?
            newcloud = cloudscheduler.openstackcloud.OpenStackCloud(**cloud)
            self.clouds[newcloud.name] = newcloud

