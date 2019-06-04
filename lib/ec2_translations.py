"""
Translate EC2 Image Name to ami.
"""

from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.schema import *
from cloudscheduler.lib.view_utils import qt

def get_ami_dictionary():
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [])
    config.db_open()

    image_xref = {}
    for row in qt(config.db_connection.execute('select group_name,cloud_name,name,id from cloud_images where cloud_type="amazon"')):
        if row['group_name'] not in  image_xref:
            image_xref[row['group_name']] = {}

        if row['cloud_name'] not in  image_xref[row['group_name']]:
            image_xref[row['group_name']][row['cloud_name']] = {}

        if row['name'] not in  image_xref[row['group_name']][row['cloud_name']]:
            image_xref[row['group_name']][row['cloud_name']][row['name']] = row['id']

    config.db_close()
    return image_xref

