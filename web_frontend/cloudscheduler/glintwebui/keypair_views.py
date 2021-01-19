import logging

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .__version__ import version
from django.conf import settings
db_config = settings.CSV2_CONFIG
from .keypair_utils import get_keypair, delete_keypair, transfer_keypair, \
                         create_keypair, create_new_keypair, getUser, verifyUser

from cloudscheduler.lib.web_profiler import silk_profile as silkp
from cloudscheduler.lib.view_utils_na import set_user_groups

logger = logging.getLogger('glintv2')

# WEB VIEWS
@silkp(name='Manage Keys')
def manage_keys(request, group_name=None, message=None):
    db_config.db_open()
    if not verifyUser(request, db_config):
        raise PermissionDenied
    rc, msg, user_obj = set_user_groups(db_config, request, False)
    user_groups = user_obj.user_groups
    if group_name is None:
        group_name = user_obj.active_group

    Group_Resources = "csv2_clouds"
    Keypairs = "cloud_keypairs"

    where_clause = "group_name='%s'" % group_name
    rc, qmsg, grp_resources = db_config.db_query(Group_Resources, where=where_clause)
    key_dict = {}

    num_clouds=0
    for cloud in grp_resources:
        num_clouds=num_clouds+1
        for key in key_dict:
            key_dict[key][cloud["cloud_name"]] = False
        where_clause = "cloud_name='%s' and group_name='%s'" % (cloud["cloud_name"], cloud["group_name"])
        rc, qmsg, cloud_keys = db_config.db_query(Keypairs, where=where_clause)
        for key in cloud_keys:
            # issue of renaming here if keys have different names on different clouds
            # the keys will have a unique fingerprint and that is what is used as an identifier
            if (key["fingerprint"] + ";" + key["key_name"]) in key_dict:
                dict_key = key["fingerprint"] + ";" + key["key_name"]
                key_dict[dict_key][key["cloud_name"]] = True
            else:
                dict_key = key["fingerprint"] + ";" + key["key_name"]
                key_dict[dict_key] = {}
                key_dict[dict_key]["name"] = key["key_name"]
                key_dict[dict_key][key["cloud_name"]] = True

    context = {
        "group_resources": grp_resources,
        "key_dict": key_dict,
        "active_group": group_name,
        "message": message,
        "user_groups": user_groups,
        "num_clouds": num_clouds
    }
    # need to create template
    db_config.db_close()
    return render(request, 'glintwebui/manage_keys.html', context)

@silkp(name='Upload Keypair')
def upload_keypair(request, group_name=None):
    db_config.db_open()
    if not verifyUser(request, db_config):
        raise PermissionDenied

    if request.method == 'POST':
         # set up database objects
        user = getUser(request, db_config)
        Group_Resources = "csv2_clouds"
        Keypairs = "cloud_keypairs"


        # get list of target clouds to upload key to
        cloud_name_list = request.POST.getlist('clouds')
        key_name = request.POST.get("key_name")
        key_string = request.POST.get("key_string")
        grp = request.POST.get("group_name")

        for cloud in cloud_name_list:
            where_clause = "group_name='%s' and cloud_name='%s'" % (grp, cloud)
            rc, qmsg, db_cloud_list = db_config.query(Group_Resources, where=where_clause)
            db_cloud = db_cloud_list[0]
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
            db_config.db_merge(Keypairs, keypair_dict)

            try:
                db_config.db_commit()
            except Exception as exc:
                logger.error(exc)
                logger.error("Error committing database session after creating new key")
                logger.error("openstack and the database may be out of sync until next keypair poll cycle")

        db_config.db_close()
        return redirect("manage_keys")
    else:
        #not a post do nothing
        return None

    return None

@silkp(name='New Keypair')
def new_keypair(request, group_name=None,):
    db_config.db_open()
    if not verifyUser(request, db_config):
        raise PermissionDenied
    if request.method == 'POST':
        # set up database objects
        user = getUser(request, db_config)
        Group_Resources = "csv2_clouds"
        Keypairs = "cloud_keypairs"
        

        # get list of target clouds to upload key to
        cloud_name_list = request.POST.getlist('clouds')
        key_name = request.POST.get("key_name")
        grp = request.POST.get("group_name")

        # Only check that needs to be made is if the key name is used on any of the target clouds
        for cloud in cloud_name_list:
            where_clause = "group_name='%s' and cloud_name='%s' and key_name='%s'" % (grp, cloud, key_name)
            rc, qmsg, db_keypair_list = db_config.db_query(Keypairs, where=where_clause)
            if len(db_keypair_list)==0:
                #no entry exists, its safe to create this keypair
                logging.info("creating new keypair %s on cloud %s" % (key_name, cloud))

                #get grp resources obj
                where_clause = "group_name='%s' and cloud_name='%s'" % (grp, cloud)
                rc, msg, cloud_obj_list =  db_config.db_query(Group_Resources, where=where_clause)
                cloud_obj = cloud_obj_list[0]
                new_key = create_new_keypair(key_name=key_name, cloud=cloud_obj)

                keypair_dict = {
                "group_name": grp,
                "cloud_name": cloud,
                "fingerprint": new_key.fingerprint,
                "key_name": key_name
                }
                db_config.db_merge(Keypairs, keypair_dict)

                try:
                    db_config.db_commit()
                except Exception as exc:
                    logger.error(exc)
                    logger.error("Error committing database session after creating new key")
                    logger.error("openstack and the database may be out of sync until next keypair poll cycle")
            else:
                #keypair name exists on this cloud
                message = "Keypair name %s in use on cloud: %s. Aborting transation, keypair may have been created on some clouds" % (key_name, cloud)
                logger.error(message)
                db_config.db_close()
                return manage_keys(request=request, group_name=grp, message=message)
        db_config.db_close()
        return redirect("manage_keys")
 
    else:
        #not a post do nothing
        return None

@silkp(name='Save Keypairs')
def save_keypairs(request, group_name=None, message=None):
    db_config.db_open()
    rc, msg, user_obj = set_user_groups(db_config, request, False)
    if group_name is None:
        group_name = user_obj.active_group
    if group_name is None:
        return None


    if request.method == 'POST':
        try:
            #set up database objects
            Group_Resources = "csv2_clouds"
            Keypairs = "cloud_keypairs"
            # get list of clouds for this group
            # for each cloud: check_list = request.POST.getlist(cloud.cloud_name)
            # check the checklist for diffs (add/remove keys)
            where_clause = "group_name='%s'" % (group_name)
            rc, qmsg, grp_resources = db_config.db_query(Group_Resources, where=where_clause)
            logger.info("Checking for keys to transfer")
            for cloud in grp_resources:
                #check_list will only have the names of keys checked for that cloud
                check_list = request.POST.getlist(cloud["cloud_name"])

                #cross reference check list against what is in database:
                where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, cloud["cloud_name"])
                rc, qmsg, cloud_keys = db_config.db_query(Keypairs, where=where_clause)
                cloud_fingerprints = []

                for keypair in cloud_keys:
                    cloud_fingerprints.append(keypair["fingerprint"] + ";" + keypair["key_name"])

                # check for new key transfers
                for keypair_key in check_list:
                    if keypair_key not in cloud_fingerprints:
                        # transfer key to this cloud
                        logger.info("%s not found in %s" % (keypair_key, cloud_fingerprints))
                        logger.info("Found key: %s to transfer to %s" % (keypair_key, cloud["cloud_name"]))
                        split_key = keypair_key.split(";")
                        fingerprint = split_key[0]
                        key_name = split_key[1]
                        # get existing keypair: need name, public_key, key_type and ?user?
                        logger.info("getting source keypair database object...")
                        # get list of keypairs to try and try each one
                        where_clause = "fingerprint='%s' and key_name='%s'" % (fingerprint, key_name)
                        rc, qmsg, src_keypairs = db_config.db_query(Keypairs, where=where_clause)
                        transfer_success = False
                        for src_keypair in src_keypairs:
                            try:
                                # get group resources corresponding to that keypair
                                logger.info("getting source cloud...")
                                where_clause = "group_name='%s' and cloud_name='%s'" % (src_keypair["group_name"], src_keypair["cloud_name"])
                                rc, qmsg, src_clouds = db_config.db_query(Group_Resources, where=where_clause)
                                src_cloud = src_clouds[0]
                                # download key from that group resources
                                logger.info("getting source keypair openstack object...")
                                os_keypair = get_keypair(keypair_key, src_cloud)
                                # upload key to current "cloud"
                                logger.info("transferring keypair...")
                                result = transfer_keypair(os_keypair, cloud)
                                logger.info(result)
                                keypair_dict = {
                                    "group_name": group_name,
                                    "cloud_name": cloud.cloud_name,
                                    "fingerprint": fingerprint,
                                    "key_name": key_name
                                }
                                db_config.db_merge(Keypairs, keypair_dict)
                                # Transfer successful, break
                                transfer_success = True
                                break
                            except Exception as exc:
                                logger.error("Failed to get src keypair from %s:%s, trying next src key" % (src_keypair["group_name"], src_keypair["cloud_name"]))
                                logger.exception(exc)
                                continue
                        if not transfer_success:
                            logger.error("Failed to transfer %s" %  keypair_key)
                try:
                    db_config.db_commit()
                except Exception as exc:
                    logger.error(exc)
                    logger.error("Error committing database session after proccessing key transfers")
                    logger.error("openstack and the database may be out of sync until next keypair poll cycle")

            # we need to do the entire loop of the clouds twice so we can do all the transfers, then all the deletes
            logger.info("Checking for keys to delete")
            for cloud in grp_resources:
                #check_list will only have the names of keys checked for that cloud
                check_list = request.POST.getlist(cloud["cloud_name"])

                #cross reference check list against what is in database:
                where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, cloud["cloud_name"])
                rc, qmsg, cloud_keys = db_config.db_query(Keypairs, where=where_clause)
                for keypair in cloud_keys:
                    if (keypair["fingerprint"] + ";" + keypair["key_name"]) not in check_list:
                        # key has been deleted from this cloud:
                        logger.info("Found key to delete: %s" % keypair["key_name"])
                        delete_keypair(keypair["key_name"], cloud)
                        # delete from database
                        db_config.db_delete(Keypairs, keypair)
                try:
                    db_config.db_commit()
                except Exception as exc:
                    logger.error(exc)
                    logger.error("Error committing database session after proccessing key transfers")
                    logger.error("openstack and the database may be out of sync until next keypair poll cycle")

            
        except Exception as exc:
            logger.error(exc)
            logger.error("Error setting up database objects or during general execution of save_keypairs")

        db_config.db_close()
        return redirect("/keypairs/?%s" % group_name)


    # not a post, do nothing
    return None

