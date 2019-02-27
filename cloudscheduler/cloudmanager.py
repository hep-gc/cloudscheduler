"""
Cloud Manager module - the CloudManager class holds all the cloud connectors
for a given group.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import openstackcloud
import localhostcloud
import config as csconfig

from cloudscheduler.lib.db_config import Config

class CloudManager():

    """
    CloudManager class for holding a groups resources and their group yaml
    """
    def __init__(self, name, group_resources, group_yamls, metadata):
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
        self.metadata = metadata
        self.config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [])

    def setup(self):
        """
        Setup the group cloud resources and fetch cloud specific
        yaml from the database.
        """
        self.config.db_open()

        for cloud in self.group_resources:
            try:
                if cloud.cloud_type == 'localhost':
                    newcloud = localhostcloud.LocalHostCloud(resource=cloud,
                                                                            metadata=self.metadata[cloud.cloud_name])
                else:
                    newcloud = openstackcloud.\
                        OpenStackCloud(resource=cloud, metadata=self.metadata[cloud.cloud_name] if cloud.cloud_name in self.metadata.keys() else None)
                if newcloud:
                    self.clouds[newcloud.name] = newcloud
            except Exception as ex:
                self.log.exception(ex)
        self.log.debug("Added all clouds for group: %s", self.name)
        try:
            self.config.db_close()
        except Exception as ex:
            self.log.exception(ex)
