import logging

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from libcloud.common.openstack_identity import OpenStackIdentity_3_0_Connection
from libcloud.common.openstack_identity import OpenStackIdentityTokenScope



def get_openstack_driver(cloud):
    Openstack = get_driver(Provider.OPENSTACK)

    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
    if version == 2:
        driver = Openstack(
            cloud.username, cloud.password,
            ex_force_base_url=cloud.authurl,
            ex_force_auth_version=version, 
            ex_tenant_name=cloud.project
        )
    else:
        version = '3.x_password'
        cls = get_driver(Provider.OPENSTACK)
        driver = cls(
            cloud.username, cloud.password,
            ex_force_auth_version=version,
            ex_force_auth_url=cloud.authurl,
            ex_force_service_type='compute',
            ex_force_service_region='Victoria',
            ex_tenant_name=cloud.project
        )
    return driver

class Cloud:
    def __init__(self, username, password, authurl, project, project_domain_name=None):
        self.username = username
        self.password = password
        self.authurl = authurl
        self.project = project
        self.project_domain_name = project_domain_name




test_cloud = Cloud("colsond", "", "https://otter.heprc.uvic.ca:15000/v3/", "testing")
os_drvr = get_openstack_driver(test_cloud)


os_drvr.list_images()