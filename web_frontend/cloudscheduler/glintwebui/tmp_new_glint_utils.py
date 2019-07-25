# glint utils

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
import glanceclient


def get_nova_client(session, region=None):
    nova = novaclient.Client("2", session=session, region_name=region, timeout=10)
    return nova


def get_glance_client(session, region=None):
    glance = glanceclient.Client("2", session=session, region_name=region)
    return glance


def get_openstack_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.debug("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
    if version == 2:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project)
    else:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project,
            user_domain=cloud.user_domain_name,
            project_domain_name=cloud.project_domain_name,
            project_domain_id=cloud.project_domain_id,)
    if session is False:
        logging.error("Failed to setup session, skipping %s", cloud.cloud_name)
        if version == 2:
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s",
                          (cloud.authurl, cloud.username, cloud.project))
        else:
            logging.error(
                "Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s",
                (cloud.authurl, cloud.username, cloud.project, cloud.user_domain, cloud.project_domain_name))
    return session

def _get_openstack_session_v1_v2(auth_url, username, password, project, user_domain="Default", project_domain_name="Default",
                                 project_domain_id=None):
    authsplit = auth_url.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.debug("Bad openstack URL: %s, could not determine version, aborting session", auth_url)
        return False
    if version == 2:
        try:
            auth = v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project)
            sess = session.Session(auth=auth, verify=config.cacerts)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s::%s" % (auth_url, exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
            return False
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project,
                user_domain_name=user_domain,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,)
            sess = session.Session(auth=auth, verify=config.cacerts)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess




# new glint api, maybe make this part of glint utils?

def create_placeholder_image(glance, image_name, disk_format, container_format):
    image = glance.images.create(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format)
    return image.id


# Upload an image to repo, returns image id if successful
# if there is no image_id it is a direct upload and no placeholder exists
def upload_image(glance, image_id, image_name, scratch_dir, disk_format=None, container_format=None):
    if image_id is not None:
        #this is the 2nd part of a transfer not a direct upload
        file_path = scratch_dir + image_name
        glance.images.upload(image_id, open(file_path, 'rb'))
        return image_id

    else:
        #this is a straight upload not part of a transfer
        image = glance.images.create(
            name=image_name,
            disk_format=disk_format,
            container_format=container_format)
        glance.images.upload(image.id, open(scratch_dir, 'rb'))
        logger.info("Upload complete")
        return image.id


# Download an image from the repo, returns True if successful or False if not
def download_image(glance, image_name, image_id, scratch_dir):
    #open file then write to it
    try:
        file_path = scratch_dir + image_name
        image_file = open(file_path, 'wb')
        for chunk in glance.images.data(image_id):
            image_file.write(bytes(chunk))
        img = glance.images.get(image_id)

        return (True, "Success", img.disk_format)
    except Exception as exc:
        return (False, exc, "")

def delete_image(glance, image_id):
    try:
        glance.images.delete(image_id)
    except Exception:
        logger.error("Unknown error, unable to delete image")
        return False
    return True


def update_image_name(glance, image_id, image_name):
    glance.images.update(image_id, name=image_name)


def get_checksum(glance, image_id):
    image = glance.images.get(image_id)
    return image['checksum']