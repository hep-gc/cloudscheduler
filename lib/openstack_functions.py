import logging
from openstack import connection
from openstack import resource
from openstack.compute.v2 import server as _server
#from keystoneclient.auth.identity import v2
from keystoneauth1.identity import v2, v3
from keystoneauth1 import session
from pytz import timezone
import pytz

class MyServer(_server.Server):
    min_count = resource.Body('min_count')
    max_count = resource.Body('max_count')

def get_openstack_appcredential_auth(cloud):
    try:
        auth = v3.ApplicationCredential(
            auth_url=cloud["authurl"],
            application_credential_secret=cloud["app_credentials_secret"],
            application_credential_id=cloud["app_credentials"]
        )
        return auth
    except Exception as exc:
        if cloud.get("cloud_name"):
            logging.error("Failed to setup auth, skipping %s", cloud["cloud_name"])
        logging.error("Problem importing keystone modules for application credential identity, and getting auth for grp:cloud - %s: %s", (cloud["authurl"] ,exc))
        logging.error("Connection parameters: \n authurl: %s \n application_credential_secret: %s \n application_credential_id: %s", (cloud["authurl"], cloud["app_credentials_secret"], cloud["app_credentials"]))
        return False

def get_openstack_conn(sess, region=None):
    try:
        conn = connection.Connection(
            region_name=region,
            session=sess,
            compute_api_version='2',
            image_api_version='2', 
            block_storage_api_version='3',
            identity_api_version='3'
        )
        return conn
    except Exception as exc:
        logging.error("Problem getting openstacksdk connection - %s" % exc)
        return False

def get_neutron_connection(sess, region=None):
    try:
        conn = get_openstack_conn(sess, region)
        neutron = conn.network
        return neutron
    except Exception as exc:
        logging.error("Problem getting openstacksdk neutron connection - %s" % exc)
        return False

def get_nova_connection(sess, region=None):
    try:
        conn = get_openstack_conn(sess, region)
        nova = conn.compute
        return nova
    except Exception as exc:
        logging.error("Problem getting openstacksdk nova connection - %s" % exc)
        return False

def get_glance_connection(sess, region=None):
    try:
        conn = get_openstack_conn(sess, region)
        glance = conn.image
        return glance
    except Exception as exc:
        logging.error("Problem getting openstacksdk glance connection - %s" % exc)
        return False

def get_cinder_connection(sess, region=None):
    try:
        conn = get_openstack_conn(sess, region)
        cinder = conn.block_storage
        return cinder
    except Exception as exc:
        logging.error("Problem getting openstacksdk cinder connection - %s" % exc)
        return False

def get_keystone_connection(sess, region=None):
    try:
        conn = get_openstack_conn(sess, region)
        keystone = conn.identity
        return keystone
    except Exception as exc:
        logging.error("Problem getting openstacksdk keystone connection - %s" % exc)
        return False

def get_openstack_sess(cloud, verify=None):
    try:
        auth = None
        if cloud.get("app_credentials_secret") and cloud.get("app_credentials"):
            auth = get_openstack_appcredential_auth(cloud)
        else:
            auth = get_openstack_auth(cloud)
        sess = session.Session(auth=auth, verify=verify, split_loggers=False)
    except Exception as exc:
        sess = False
        logging.error("Problem getting session for grp: cloud - %s::%s" % (cloud["authurl"], exc))
        if cloud.get("cloud_name"):
            logging.error("Failed to setup session, skipping %s", cloud["cloud_name"])
    return sess

def get_openstack_api_version(authurl):
    authsplit = authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
        return 0, None, version
    except:
        return 1, 'Bad openstack URL: %s, could not determine version, skipping' % authurl, None

def get_openstack_auth(cloud):
    rc, msg, version = get_openstack_api_version(cloud["authurl"])
    if rc != 0:
        logging.debug(msg)
        return False
    if version == 2:
        try:
            auth = v2.Password(
                auth_url=cloud["authurl"],
                username=cloud["username"],
                password=cloud["password"],
                tenant_name=cloud["project"]
            )
        except Exception as exc:
            auth = False
            logging.error("Problem importing keystone modules, and getting auth for grp:cloud - %s::%s" % (cloud["authurl"], exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (cloud["authurl"], cloud["username"], cloud["project"]))
    else:
        try:
            try:
                user_domain_name=cloud["user_domain_name"]
            except:
                user_domain_name="Default"
            try:
                project_domain_name=cloud["project_domain_name"]
            except:
                project_domain_name="Default"
            try:
                project_domain_id=cloud["project_domain_id"]
            except:
                project_domain_id=None
            auth = v3.Password(
                auth_url=cloud["authurl"],
                username=cloud["username"],
                password=cloud["password"],
                project_name=cloud["project"],
                user_domain_name=user_domain_name,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id
            )
        except Exception as exc:
            auth = False
            logging.error("Problem importing keystone modules, and getting auth for grp:cloud - %s: %s", (cloud["authurl"], exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (cloud["authurl"], cloud["username"], cloud["project"], user_domain_name, project_domain_name))
    return auth

def convert_openstack_date_timezone(origin_date):
    try:
        localized_timestamp = pytz.timezone("UTC").localize(origin_date)
        pstdatetime = localized_timestamp.astimezone(timezone('Canada/Pacific'))
        return pstdatetime.timestamp()
    except Exception as exc:
        logging.error("Unable to conver the timestamp to pacific timezone: %s" % exc)
        return origin_date.timestamp()


