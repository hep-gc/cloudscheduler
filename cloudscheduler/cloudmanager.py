import cloudscheduler.openstackcloud
import cloudscheduler.config as csconfig

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

class CloudManager():
    def __init__(self, name, group_resources, group_yamls):
        self.name = name
        self.clouds = {}
        self.group_resources = group_resources
        self.group_yamls = group_yamls

    def setup(self):
        Base = automap_base()
        engine = create_engine("mysql://" + csconfig.config.db_user + ":" + csconfig.config.db_password + "@" +
                               csconfig.config.db_host + ":" + str(csconfig.config.db_port) +
                               "/" + csconfig.config.db_name)
        Base.prepare(engine, reflect=True)
        session = Session(engine)
        Cloud_Yaml = Base.classes.csv2_group_resource_yaml

        for cloud in self.group_resources:
            cloud_yamls = session.query(Cloud_Yaml).filter(Cloud_Yaml.group_name == self.name, Cloud_Yaml.cloud_name == cloud.cloud_name)
            cloud_yaml_list = []
            for yam in cloud_yamls:
                cloud_yaml_list.append((yam.yaml_name, yam.yaml, yam.mime_type))

            newcloud = cloudscheduler.openstackcloud.OpenStackCloud(extrayaml=cloud_yaml_list, **cloud)
            self.clouds[newcloud.name] = newcloud
