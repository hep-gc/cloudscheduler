import logging

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
import glintwebui.config as config

from .__version__ import version
from .db_util import get_db_base_and_session
from .utils import get_keypair, delete_keypair, transfer_keypair, create_keypair, create_new_keypair

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

logger = logging.getLogger('glintv2')

def getUser(request):
    user = request.META.get('REMOTE_USER')
    Base, session = get_db_base_and_session()
    Glint_User = Base.classes.csv2_user
    auth_user_list = session.query(Glint_User)
    for auth_user in auth_user_list:
        if user == auth_user.cert_cn or user == auth_user.username:
            return auth_user

def verifyUser(request):
    auth_user = getUser(request)
    return bool(auth_user)

def getSuperUserStatus(request):
    auth_user = getUser(request)
    if auth_user is None:
        return False
    else:
        return auth_user.is_superuser


# WEB VIEWS

def manage_keys(request, group_name=None, message=None):
    print("MANAGE KEYS VIEW ENTRY")
    if not verifyUser(request):
        raise PermissionDenied
    user_obj = getUser(request)
    if group_name is None:
        group_name = user_obj.active_group

    Base, session = get_db_base_and_session()
    Group_Resources = Base.classes.csv2_group_resources
    Keypairs = Base.classes.csv2_keypairs
    User_Group = Base.classes.csv2_user_groups
    user_groups = session.query(User_Group).filter(User_Group.username == user_obj.username)
    group_list = []
    for grp in user_groups:
        grp_name = grp.group_name
        group_list.append(grp_name)

    grp_resources = session.query(Group_Resources).filter(Group_Resources.group_name == group_name)
    key_dict = {}

    num_clouds=0
    for cloud in grp_resources:
        num_clouds=num_clouds+1
        for key in key_dict:
            key_dict[key][cloud.cloud_name] = False
        cloud_keys = session.query(Keypairs).filter(Keypairs.cloud_name == cloud.cloud_name, Keypairs.group_name == cloud.group_name)
        for key in cloud_keys:
            # issue of renaming here if keys have different names on different clouds
            # the keys will have a unique fingerprint and that is what is used as an identifier
            if (key.fingerprint + ";" + key.key_name) in key_dict:
                dict_key = key.fingerprint + ";" + key.key_name
                key_dict[dict_key][key.cloud_name] = True
            else:
                dict_key = key.fingerprint + ";" + key.key_name
                key_dict[dict_key] = {}
                key_dict[dict_key]["name"] = key.key_name
                key_dict[dict_key][key.cloud_name] = True

    context = {
        "group_resources": grp_resources,
        "key_dict": key_dict,
        "active_group": group_name,
        "message": message,
        "enable_glint": True,
        "user_groups": group_list,
        "num_clouds": num_clouds
    }
    # need to create template
    return render(request, 'glintwebui/manage_keys.html', context)


def upload_keypair(request, group_name=None):
    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
         # set up database objects
        Base, session = get_db_base_and_session()
        Group_Resources = Base.classes.csv2_group_resources
        Keypairs = Base.classes.csv2_keypairs
        user = getUser(request)

        # get list of target clouds to upload key to
        cloud_name_list = request.POST.getlist('clouds')
        key_name = request.POST.get("key_name")
        key_string = request.POST.get("key_string")
        grp = request.POST.get("group_name")

        for cloud in cloud_name_list:
            db_cloud = session.query(Group_Resources).filter(Group_Resources.group_name == grp, Group_Resources.cloud_name == cloud).first()
            try:
                new_key = create_keypair(key_name=key_name, key_string=key_string, cloud=db_cloud)
            except Exception as exc:
                logger.error("Failed openstack request to make keypair")
                logger.error(exc)
                logger.error("%s is likely an invalid keystring" % key_string)
                message = "unable to upload key: '%s' is likely an invalid keystring" % key_string
                return manage_keys(request=request, group_name=grp, message=message)

            keypair_dict = {
                "group_name": grp,
                "cloud_name": cloud,
                "fingerprint": new_key.fingerprint,
                "key_name": key_name
            }
            new_keypair = Keypairs(**keypair_dict)
            session.merge(new_keypair)

            try:
                session.commit()
            except Exception as exc:
                logger.error(exc)
                logger.error("Error committing database session after creating new key")
                logger.error("openstack and the database may be out of sync until next keypair poll cycle")

        return redirect("manage_keys")
    else:
        #not a post do nothing
        return None

    return None


def new_keypair(request, group_name=None,):
    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
         # set up database objects
        Base, session = get_db_base_and_session()
        Group_Resources = Base.classes.csv2_group_resources
        Keypairs = Base.classes.csv2_keypairs
        user = getUser(request)

        # get list of target clouds to upload key to
        cloud_name_list = request.POST.getlist('clouds')
        key_name = request.POST.get("key_name")
        grp = request.POST.get("group_name")

        # Only check that needs to be made is if the key name is used on any of the target clouds
        for cloud in cloud_name_list:
            db_keypair = session.query(Keypairs).filter(Keypairs.group_name == grp, Keypairs.cloud_name == cloud, Keypairs.key_name == key_name).one_or_none()
            if db_keypair is None:
                #no entry exists, its safe to create this keypair
                logging.info("creating new keypair %s on cloud %s" % (key_name, cloud))

                #get grp resources obj
                cloud_obj =  session.query(Group_Resources).filter(Group_Resources.group_name == grp, Group_Resources.cloud_name == cloud).one()
                new_key = create_new_keypair(key_name=key_name, cloud=cloud_obj)

                keypair_dict = {
                "group_name": grp,
                "cloud_name": cloud,
                "fingerprint": new_key.fingerprint,
                "key_name": key_name
                }
                new_keypair = Keypairs(**keypair_dict)
                session.merge(new_keypair)

                try:
                    session.commit()
                except Exception as exc:
                    logger.error(exc)
                    logger.error("Error committing database session after creating new key")
                    logger.error("openstack and the database may be out of sync until next keypair poll cycle")
            else:
                #keypair name exists on this cloud
                message = "Keypair name %s in use on cloud: %s. Aborting transation, keypair may have been created on some clouds" % (key_name, cloud)
                logger.error(message)
                return manage_keys(request=request, group_name=grp, message=message)

        return redirect("manage_keys")
 
    else:
        #not a post do nothing
        return None


def save_keypairs(request, group_name=None, message=None):
    print("SAVE KEYS VIEW ENTRY")
    if not verifyUser(request):
        raise PermissionDenied

    user_obj = getUser(request)
    if group_name is None:
        group_name = user_obj.active_group
    if group_name is None:
        return None


    if request.method == 'POST':
        try:
            #set up database objects
            Base, session = get_db_base_and_session()
            Group_Resources = Base.classes.csv2_group_resources
            Keypairs = Base.classes.csv2_keypairs
            # get list of clouds for this group
            # for each cloud: check_list = request.POST.getlist(cloud.cloud_name)
            # check the checklist for diffs (add/remove keys)
            grp_resources = session.query(Group_Resources).filter(Group_Resources.group_name == group_name)
            logger.info("Checking for keys to transfer")
            for cloud in grp_resources:
                #check_list will only have the names of keys checked for that cloud
                check_list = request.POST.getlist(cloud.cloud_name)

                #cross reference check list against what is in database:
                cloud_keys = session.query(Keypairs).filter(Keypairs.group_name == group_name, Keypairs.cloud_name == cloud.cloud_name)
                cloud_fingerprints = []

                for keypair in cloud_keys:
                    cloud_fingerprints.append(keypair.fingerprint + ";" + keypair.key_name)

                # check for new key transfers
                for keypair_key in check_list:
                    if keypair_key not in cloud_fingerprints:
                        # transfer key to this cloud
                        logger.info("%s not found in %s" % (keypair_key, cloud_fingerprints))
                        logger.info("Found key: %s to transfer to %s" % (keypair_key, cloud.cloud_name))
                        split_key = keypair_key.split(";")
                        fingerprint = split_key[0]
                        key_name = split_key[1]
                        # get existing keypair: need name, public_key, key_type and ?user?
                        logger.info("getting source keypair database object...")
                        src_keypair = session.query(Keypairs).filter(Keypairs.fingerprint == fingerprint, Keypairs.key_name == key_name).first()
                        # get group resources corresponding to that keypair
                        logger.info("getting source cloud...")
                        src_cloud = session.query(Group_Resources).filter(Group_Resources.group_name == src_keypair.group_name, Group_Resources.cloud_name == src_keypair.cloud_name).first()
                        # download key from that group resources
                        logger.info("getting source keypair openstack object...")
                        os_keypair = get_keypair(keypair_key, src_cloud)
                        # upload key to current "cloud"
                        logger.info("transferring keypair...")
                        transfer_keypair(os_keypair, cloud)
                        keypair_dict = {
                            "group_name": group_name,
                            "cloud_name": cloud.cloud_name,
                            "fingerprint": fingerprint,
                            "key_name": key_name
                        }
                        new_keypair = Keypairs(**keypair_dict)
                        session.merge(new_keypair)
                try:
                    session.commit()
                except Exception as exc:
                    logger.error(exc)
                    logger.error("Error committing database session after proccessing key transfers")
                    logger.error("openstack and the database may be out of sync until next keypair poll cycle")

            # we need to do the entire loop of the clouds twice so we can do all the transfers, then all the deletes
            logger.info("Checking for keys to delete")
            for cloud in grp_resources:
                #check_list will only have the names of keys checked for that cloud
                check_list = request.POST.getlist(cloud.cloud_name)

                #cross reference check list against what is in database:
                cloud_keys = session.query(Keypairs).filter(Keypairs.group_name == group_name, Keypairs.cloud_name == cloud.cloud_name)
                for keypair in cloud_keys:
                    if (keypair.fingerprint + ";" + keypair.key_name) not in check_list:
                        # key has been deleted from this cloud:
                        logger.info("Found key to delete: %s" % keypair.key_name)
                        delete_keypair(keypair.key_name, cloud)
                        # delete from database
                        session.delete(keypair)
                try:
                    session.commit()
                except Exception as exc:
                    logger.error(exc)
                    logger.error("Error committing database session after proccessing key transfers")
                    logger.error("openstack and the database may be out of sync until next keypair poll cycle")

            
        except Exception as exc:
            logger.error(exc)
            logger.error("Error setting up database objects or during general execution of save_keypairs")

        
        return redirect("manage_keys")


    # not a post, do nothing
    return None

