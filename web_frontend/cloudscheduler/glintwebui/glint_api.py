import logging
from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
import glanceclient
import glintwebui.config as config


logger = logging.getLogger('glintv2')


'''
The Glint API file contains any functionality that connects to cloud components
to gather data, upload or download images, or any other need to connect to a cloud.
Most compute or utility functions can be found in utils.py or for asynchronous and
periodic tasks in celery.py
'''

class repo_connector(object):
    def __init__(self, auth_url, project, username, password, user_domain_name="Default", project_domain_name="Default", alias=None):
        self.auth_url = auth_url
        self.alias = alias
        authsplit = self.auth_url.split('/')
        self.version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
        self.project = project
        self.username = username
        self.password = password
        self.project_domain_name = project_domain_name
        self.user_domain_name = user_domain_name
        self.token = None
        self.keystone = None
        self.cacert = config.cert_auth_bundle_path
        self.sess = self._get_keystone_session()
        self.image_list = self._get_images()

    # Borrowed from cloud schedular and modified to match this enviroment
    # This was a nightmare to get working behind apache but it turns out
    # all that was needed was to upgrade the python cryptography library
    def _get_keystone_session(self):
        if self.version == 2:
            try:
                auth = v2.Password(
                    auth_url=self.auth_url,
                    username=self.username,
                    password=self.password,
                    tenant_name=self.project)
                sess = session.Session(auth=auth, verify=self.cacert)
            except Exception as exc:
                print("Problem importing keystone modules, and getting session: %s" % exc)
            return sess
        elif self.version == 3:
            #connect using keystone v3
            try:
                auth = v3.Password(
                    auth_url=self.auth_url,
                    username=self.username,
                    password=self.password,
                    project_name=self.project,
                    user_domain_name=self.user_domain_name,
                    project_domain_name=self.project_domain_name)
                sess = session.Session(auth=auth, verify=self.cacert)
            except Exception as exc:
                print("Problem importing keystone modules, and getting session: %s" % exc)
            return sess

    def _get_images(self):
        glance = glanceclient.Client('2', session=self.sess)
        image_list = ()

        # Do things with images
        for image in glance.images.list():
            img_checksum = "No Checksum"
            img_id = image['id']
            img_name = image['name']
            img_disk_format = image['disk_format']
            img_containter_format = image['container_format']
            img_visibility = image['visibility']
            if image['checksum'] is not None:
                img_checksum = image['checksum']

            image_list += ((self.project, img_name, img_id, img_disk_format, \
            	img_containter_format, img_visibility, img_checksum, self.alias),)

        return image_list

    def create_placeholder_image(self, image_name, disk_format, container_format):
        glance = glanceclient.Client('2', session=self.sess)
        image = glance.images.create(
            name=image_name,
            disk_format=disk_format,
            container_format=container_format)
        return image.id

    # Upload an image to repo, returns image id if successful
    # if there is no image_id it is a direct upload and no placeholder exists
    def upload_image(self, image_id, image_name, scratch_dir, disk_format=None, container_format=None):
        if image_id is not None:
            #this is the 2nd part of a transfer not a direct upload
            glance = glanceclient.Client('2', session=self.sess)
            images = glance.images.list()
            file_path = scratch_dir + image_name
            glance.images.upload(image_id, open(file_path, 'rb'))
            return image_id
        else:
            #this is a straight upload not part of a transfer
            glance = glanceclient.Client('2', session=self.sess)
            image = glance.images.create(
                name=image_name,
                disk_format=disk_format,
                container_format=container_format)
            glance.images.upload(image.id, open(scratch_dir, 'rb'))
            logger.info("Upload complete")
            return image.id

    # Download an image from the repo, returns True if successful or False if not
    def download_image(self, image_name, image_id, scratch_dir):
        glance = glanceclient.Client('2', session=self.sess)

        #open file then write to it
        file_path = scratch_dir + image_name
        image_file = open(file_path, 'w+')
        for chunk in glance.images.data(image_id):
            image_file.write(chunk)

        return True

    def delete_image(self, image_id):
        try:
            glance = glanceclient.Client('2', session=self.sess)
            glance.images.delete(image_id)
        except Exception:
            logger.error("Unknown error, unable to delete image")
            return False
        return True

    def update_image_name(self, image_id, image_name):
        glance = glanceclient.Client('2', session=self.sess)
        glance.images.update(image_id, name=image_name)

    def get_checksum(self, image_id):
        glance = glanceclient.Client('2', session=self.sess)
        image = glance.images.get(image_id)
        return image['checksum']

def validate_repo(auth_url, username, password, tenant_name, user_domain_name="Default", project_domain_name="Default"):
    try:
        repo = repo_connector(
            auth_url=auth_url,
            project=tenant_name,
            username=username,
            password=password,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name)

    except exceptions.connection.ConnectFailure as exc:
        logger.error("Repo not valid: %s: %s", tenant_name, auth_url)
        logger.error(exc)
        return (False, "Unable to validate: Bad Auth URL")
    except exceptions.http.HTTPClientError as exc:
        logger.error(exc)
        return (False, "Unable to connect: Bad username, password, or tenant")
    except exceptions.connection.SSLError as exc:
        logger.error(exc)
        return (False, "SSL connection error")
    except Exception as exc:
        logger.error("Repo not valid: %s: %s", tenant_name, auth_url)
        logger.error(exc)
        return (False, "unable to validate: please check httpd error log for message")

    return (True, "Ok")


def change_image_name(repo_obj, img_id, old_img_name, new_img_name, user):
    try:
        logger.info("User %s attempting to rename image '%s' to '%s' in repo '%s'",\
            user, old_img_name, new_img_name, repo_obj.project)
        repo = repo_connector(
            auth_url=repo_obj.authurl,
            project=repo_obj.project,
            username=repo_obj.username,
            password=repo_obj.password)
        repo.update_image_name(image_id=img_id, image_name=new_img_name)
        logger.info("Image rename complete")
    except Exception as exc:
        logger.error('Unknown exception occured when attempting to change image name')
        logger.error(exc)
        return None
