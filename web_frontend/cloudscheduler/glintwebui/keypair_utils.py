from cloudscheduler.lib.openstack_functions import get_openstack_sess, get_nova_connection
from cloudscheduler.lib.db_config import Config

config = Config('/etc/cloudscheduler/cloudscheduler.yaml', 'web_frontend', pool_size=2, max_overflow=10)


def delete_keypair(key_name, cloud):
    sess = get_openstack_sess(cloud, config.categories["web_frontend"]["cert_auth_bundle_path"])
    nova = get_nova_connection(sess)

    keys = nova.keypairs()
    for key in keys:
        if key.name == key_name:
            nova.delete_keypair(key)
            return True

    return False

def get_keypair(keypair_key, cloud, key_name = None):
    sess = get_openstack_sess(cloud, config.categories["web_frontend"]["cert_auth_bundle_path"])
    nova = get_nova_connection(sess)

    found_key_name = None
    if key_name:
        found_key_name = key_name
    elif keypair_key:
        split_key = keypair_key.split(";")
        fingerprint = split_key[0]
        found_key_name = split_key[1]

    keys = nova.keypairs()
    for key in keys:
        if key.name == found_key_name:
            return key
    return None

def transfer_keypair(keypair, cloud):
    sess = get_openstack_sess(cloud, config.categories["web_frontend"]["cert_auth_bundle_path"])
    nova = get_nova_connection(sess)

    result = nova.create_keypair(name=keypair.name, public_key=keypair.public_key)
    return result

def create_keypair(key_name, key_string, cloud):
    sess = get_openstack_sess(cloud, config.categories["web_frontend"]["cert_auth_bundle_path"])
    nova = get_nova_connection(sess)

    try:
        new_key = nova.create_keypair(name=key_name, public_key=key_string)
    except Exception as exc:
        raise
    return new_key


def create_new_keypair(key_name, cloud):
    sess = get_openstack_sess(cloud, config.categories["web_frontend"]["cert_auth_bundle_path"])
    nova = get_nova_connection(sess)

    try:
        new_key = nova.create_keypair(name=key_name)
    except Exception as exc:
        raise
    return new_key

# database must be opened prior to calling these functions
#
def getUser(request, db_config):
    user = request.META.get('REMOTE_USER')
    Glint_User = "csv2_user"
    rc, qmsg, auth_user_list = db_config.db_query(Glint_User)
    for auth_user in auth_user_list:
        if user == auth_user["cert_cn"] or user == auth_user["username"]:
            return auth_user

def verifyUser(request, db_config):
    auth_user = getUser(request, db_config)
    return bool(auth_user)

