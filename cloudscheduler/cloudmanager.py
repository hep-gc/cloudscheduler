"""
Cloud Manager module - the CloudManager class holds all the cloud connectors
for a given group.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import cloudscheduler.openstackcloud
import cloudscheduler.config as csconfig



class CloudManager():

    """
    CloudManager class for holding a groups resources and their group yaml
    """
    def __init__(self, name, group_resources, group_yamls):
        """
        Create a new CloudManager.
        :param name: The name of the group
        :param group_resources: sqlalchemy result of this groups resources
        :param group_yamls: the group's yaml from the database.
        """
        self.log = logging.getLogger(__name__)
        self.name = name
        self.clouds = {}
        self.group_resources = group_resources
        self.group_yamls = group_yamls

    def setup(self):
        """
        Setup the group cloud resources and fetch cloud specific
        yaml from the database.
        """
        base = automap_base()
        engine = create_engine("mysql://" + csconfig.config.db_user + ":" +
                               csconfig.config.db_password + "@" +
                               csconfig.config.db_host + ":" +
                               str(csconfig.config.db_port) +
                               "/" + csconfig.config.db_name)
        base.prepare(engine, reflect=True)
        session = Session(engine)
        cloud_yaml = base.classes.csv2_group_resource_yaml

        for cloud in self.group_resources:
            cloud_yamls = session.query(cloud_yaml).\
                filter(cloud_yaml.group_name == self.name,
                       cloud_yaml.cloud_name == cloud.cloud_name)
            cloud_yaml_list = []
            for yam in cloud_yamls:
                cloud_yaml_list.append((yam.yaml_name, yam.yaml, yam.mime_type))
            newcloud = cloudscheduler.openstackcloud.\
                OpenStackCloud(extrayaml=cloud_yaml_list, resource=cloud)
            self.clouds[newcloud.name] = newcloud
        self.log.debug("Added all clouds for group: %s", self.name)
