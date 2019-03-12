import multiprocessing
from multiprocessing import Process
import logging
import socket
import time
import sys
import os
import datetime
import copy

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    foreign, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    set_orange_count, \
    start_cycle, \
    wait_cycle
#   get_last_poll_time_from_database, \
#   set_inventory_group_and_cloud, \
#   set_inventory_item, \

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import func

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


# The purpose of this file is to get some information from a registered
# openstack cloud (otter) using libcloud
#

otter = {
'username': 'csv2-test',
'pw': '**********',
'project_name': 'testing',
'auth_url': 'https://otter.heprc.uvic.ca:15000',
'region_name': 'Victoria',
'user_domain_name': 'Default',
'project_domain_name': 'default'
}

"""
driver = OpenStack(cloud['username'], cloud['pw'],
					ex_tenant_name=cloud['project_name'],
                    ex_force_auth_url=cloud['auth_url'],
                    ex_force_auth_version='2.0_password',
                    api_version='2.0',
                    ex_force_service_region=cloud['region_name']
                    )

# NOTE: also works with 3.x_password
"""

dairqc = {
'username': 'HEPnet',
'pw': '******',
'project_name': 'NEP_HEPnet',
'auth_url': 'https://nova-ab.dair-atir.canarie.ca:5000/v2.0/tokens',
'region_name': 'quebec',
'user_domain_name': 'Default',
'project_domain_name': 'default'
}

""" Malformed response error (w url 5000/)
driver = OpenStack(cloud['username'], cloud['pw'],
					ex_tenant_name=cloud['project_name'],
                    ex_force_auth_url=cloud['auth_url'],
                    ex_force_auth_version='2.0_password',
                    api_version='2.0',
                    #ex_force_service_region=cloud['region_name']
                    )
"""




def test(cloud):
	OpenStack = get_driver(Provider.OPENSTACK)
	driver = OpenStack(cloud['username'], cloud['pw'],
                    ex_force_auth_url=cloud['auth_url'],
                    ex_force_auth_version='2.0_password',
                    ex_force_service_region=cloud['region_name'],
                    ex_force_service_name='nova',
                    ex_tenant_name=cloud['project_name'],
                    #ex_force_service_region=cloud['region_name']
                    )

	images = driver.list_images()
	print("Images >>")
	for image in images:
		print(image)

	nodes = driver.list_nodes()
	print("Nodes >>")
	for node in nodes:
		print(node)

	key_pairs = driver.list_key_pairs()
	print("Key Pairs >>")
	for key_pair in key_pairs:
		print(key_pair)

	locations = driver.list_locations()
	print("Locations >>")
	for location in locations:
		print(location)

	networks = driver.ex_list_networks()
	print("Networks >>")
	for network in networks:
		print(network)

	flavours = driver.list_sizes()
	print("Flavours >>")
	for flavour in flavours:
		print(flavour)

	"""
	createNode(driver)

	instances = driver.list_nodes()
	print("Nodes >>")
	for instance in instances:
		print(instance)
	
	deleteNode(driver)

	instances = driver.list_nodes()
	print("Nodes >>")
	for instance in instances:
		print(instance)
	"""


	

def createNode(driver):
	image_id = 'cab9b4a2-8bf4-4778-aa05-08f0d253bf09'
	image = driver.get_image(image_id)
	print(image)

	flavor_id = '0d8a594f-95df-448c-83b3-6485a7001508'
	flavor = driver.ex_get_size(flavor_id)
	print(flavor)
	
	network_id='d2857cd5-c653-4006-9c96-85556e38e6ee'
	networks = driver.ex_list_networks()
	for network in networks:
		if network.id == network_id:
			instance_name = 'libcloud-testing'
			testing_instance = driver.create_node(name=instance_name, image=image, size=flavor, networks=networks)




def deleteNode(driver):
	nodes = driver.list_nodes()
	for node in nodes:
		if node.name == 'libcloud-testing':
			print(node)
			destroyed = driver.destroy_node(node)
			if destroyed == True:
				print("Node Deleted :)")
			else:
				print("Node not deleted :(")




if __name__ == '__main__':
	test(dairqc)
