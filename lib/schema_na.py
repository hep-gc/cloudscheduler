schema = {
    "archived_condor_jobs": {
        "keys": [
            "global_job_id"
            ],
        "columns": {
            "global_job_id": ["str", 128],
            "group_name": ["str", 128],
            "target_clouds": ["str"],
            "cloud_name": ["str"],
            "job_status": ["int"],
            "request_cpus": ["int"],
            "request_ram": ["int"],
            "request_disk": ["int"],
            "request_swap": ["int"],
            "request_scratch": ["int"],
            "requirements": ["str", 512],
            "job_priority": ["int"],
            "cluster_id": ["int"],
            "proc_id": ["int"],
            "user": ["str", 512],
            "image": ["str"],
            "instance_type": ["str", 512],
            "network": ["str", 512],
            "keep_alive": ["str", 512],
            "max_price": ["str", 512],
            "user_data": ["str", 512],
            "job_per_core": ["int"],
            "entered_current_status": ["int"],
            "q_date": ["int"],
            "hold_job_reason": ["str", 64],
            "held_reason": ["str", 64]
            }
        },
    "archived_condor_machines": {
        "keys": [
            "name"
            ],
        "columns": {
            "name": ["str", 128],
            "machine": ["str", 256],
            "group_name": ["str", 32],
            "condor_host": ["str", 64],
            "flavor": ["str", 32],
            "job_id": ["str", 128],
            "global_job_id": ["str", 128],
            "address": ["str", 512],
            "state": ["str", 128],
            "activity": ["str", 128],
            "vm_type": ["str", 128],
            "my_current_time": ["int"],
            "entered_current_state": ["int"],
            "start": ["str", 128],
            "remote_owner": ["str", 128],
            "slot_type": ["str", 128],
            "total_slots": ["int"],
            "idle_time": ["int"],
            "retire_request_time": ["int"],
            "retired_time": ["int"]
            }
        },
    "auth_group": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "name": ["str", 80]
            }
        },
    "auth_group_permissions": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "group_id": ["int"],
            "permission_id": ["int"]
            }
        },
    "auth_permission": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "name": ["str", 255],
            "content_type_id": ["int"],
            "codename": ["str", 100]
            }
        },
    "auth_user": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "password": ["str", 128],
            "last_login": ["int"],
            "is_superuser": ["int"],
            "username": ["str", 150],
            "first_name": ["str", 30],
            "last_name": ["str", 150],
            "email": ["str", 254],
            "is_staff": ["int"],
            "is_active": ["int"],
            "date_joined": ["int"]
            }
        },
    "auth_user_groups": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "user_id": ["int"],
            "group_id": ["int"]
            }
        },
    "auth_user_user_permissions": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "user_id": ["int"],
            "permission_id": ["int"]
            }
        },
    "cloud_flavors": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "id": ["str", 128],
            "name": ["str", 128],
            "cloud_type": ["str", 64],
            "ram": ["int"],
            "cores": ["int"],
            "swap": ["int"],
            "disk": ["int"],
            "ephemeral_disk": ["int"],
            "is_public": ["int"],
            "last_updated": ["int"]
            }
        },
    "cloud_images": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "id": ["str", 128],
            "cloud_type": ["str", 64],
            "container_format": ["str", 128],
            "disk_format": ["str", 128],
            "name": ["str", 256],
            "size": ["int"],
            "visibility": ["str", 128],
            "min_disk": ["int"],
            "min_ram": ["int"],
            "checksum": ["str", 64],
            "last_updated": ["int"]
            }
        },
    "cloud_keypairs": {
        "keys": [
            "group_name",
            "cloud_name",
            "fingerprint",
            "key_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "fingerprint": ["str", 64],
            "key_name": ["str", 64],
            "cloud_type": ["str", 64]
            }
        },
    "cloud_limits": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "cloud_type": ["str", 64],
            "server_meta_max": ["int"],
            "instances_max": ["int"],
            "personality_max": ["int"],
            "image_meta_max": ["int"],
            "personality_size_max": ["int"],
            "ram_max": ["int"],
            "server_groups_max": ["int"],
            "security_group_rules_max": ["int"],
            "keypairs_max": ["int"],
            "security_groups_max": ["int"],
            "server_group_members_max": ["int"],
            "floating_ips_max": ["int"],
            "cores_max": ["int"],
            "server_groups_used": ["int"],
            "instances_used": ["int"],
            "ram_used": ["int"],
            "security_groups_used": ["int"],
            "floating_ips_used": ["int"],
            "cores_used": ["int"],
            "last_updated": ["int"]
            }
        },
    "cloud_networks": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "id": ["str", 128],
            "name": ["str", 256],
            "cloud_type": ["str", 64],
            "subnets": ["str", 256],
            "tenant_id": ["str", 128],
            "external_route": ["int"],
            "shared": ["int"],
            "last_updated": ["int"]
            }
        },
    "cloud_security_groups": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "id": ["str", 64],
            "name": ["str", 128],
            "cloud_type": ["str", 64],
            "last_updated": ["int"]
            }
        },
    "condor_jobs": {
        "keys": [
            "global_job_id"
            ],
        "columns": {
            "global_job_id": ["str", 128],
            "htcondor_host_id": ["int"],
            "group_name": ["str", 32],
            "target_clouds": ["str"],
            "target_alias": ["str", 32],
            "job_status": ["int"],
            "request_cpus": ["int"],
            "request_ram": ["int"],
            "request_disk": ["int"],
            "request_swap": ["int"],
            "request_scratch": ["int"],
            "requirements": ["str", 512],
            "job_priority": ["int"],
            "cluster_id": ["int"],
            "proc_id": ["int"],
            "user": ["str", 512],
            "image": ["str"],
            "instance_type": ["str", 512],
            "network": ["str", 512],
            "keep_alive": ["str", 512],
            "max_price": ["str", 512],
            "user_data": ["str", 512],
            "job_per_core": ["int"],
            "entered_current_status": ["int"],
            "q_date": ["int"],
            "hold_reason_code": ["int"],
            "hold_reason_subcode": ["int"],
            "last_remote_host": ["str", 64],
            "held_reason": ["str", 128],
            "hold_job_reason": ["str", 64]
            }
        },
    "condor_machines": {
        "keys": [
            "name"
            ],
        "columns": {
            "name": ["str", 128],
            "htcondor_host_id": ["int"],
            "machine": ["str", 256],
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "condor_host": ["str", 64],
            "flavor": ["str", 32],
            "job_id": ["str", 128],
            "global_job_id": ["str", 128],
            "address": ["str", 512],
            "state": ["str", 128],
            "activity": ["str", 128],
            "vm_type": ["str", 128],
            "my_current_time": ["int"],
            "entered_current_state": ["int"],
            "start": ["str", 128],
            "remote_owner": ["str", 128],
            "total_disk": ["int"],
            "slot_type": ["str", 128],
            "slot_cpus": ["int"],
            "total_slots": ["int"],
            "idle_time": ["int"],
            "deprecated-retire_request_time": ["int"],
            "deprecated-retired_time": ["int"]
            }
        },
    "condor_worker_gsi": {
        "keys": [
            "htcondor_fqdn"
            ],
        "columns": {
            "htcondor_fqdn": ["str", 128],
            "htcondor_host_id": ["int"],
            "worker_dn": ["str", 128],
            "worker_eol": ["int"],
            "worker_cert": ["str"],
            "worker_key": ["str"]
            }
        },
    "csv2_attribute_mapping": {
        "keys": [
            "csv2"
            ],
        "columns": {
            "csv2": ["str", 64],
            "os_limits": ["str", 64],
            "os_flavors": ["str", 64],
            "os_images": ["str", 64],
            "os_networks": ["str", 64],
            "os_vms": ["str", 64],
            "os_sec_grps": ["str", 64],
            "condor": ["str", 64],
            "ec2_flavors": ["str", 64],
            "ec2_limits": ["str", 64],
            "ec2_regions": ["str", 64],
            "ec2_images": ["str", 64],
            "ec2_vms": ["str", 20]
            }
        },
    "csv2_cloud_aliases": {
        "keys": [
            "group_name",
            "cloud_name",
            "alias_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "alias_name": ["str", 32]
            }
        },
    "csv2_cloud_flavor_exclusions": {
        "keys": [
            "group_name",
            "cloud_name",
            "flavor_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "flavor_name": ["str", 128]
            }
        },
    "csv2_cloud_metadata": {
        "keys": [
            "group_name",
            "cloud_name",
            "metadata_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "metadata_name": ["str", 64],
            "enabled": ["int"],
            "priority": ["int"],
            "metadata": ["str"],
            "mime_type": ["str", 128]
            }
        },
    "csv2_cloud_types": {
        "keys": [
            "cloud_type"
            ],
        "columns": {
            "cloud_type": ["str", 32]
            }
        },
    "csv2_clouds": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "enabled": ["int"],
            "priority": ["int"],
            "authurl": ["str", 128],
            "project": ["str", 128],
            "username": ["str", 20],
            "password": ["str"],
            "obsolete_keyname": ["str", 20],
            "cacertificate": ["str"],
            "region": ["str", 32],
            "user_domain_name": ["str", 20],
            "user_domain_id": ["str", 64],
            "project_domain_name": ["str", 20],
            "project_domain_id": ["str", 64],
            "cloud_type": ["str", 64],
            "ec2_owner_id": ["str", 32],
            "communication_up": ["int"],
            "communication_rt": ["int"],
            "server_meta_ctl": ["int"],
            "instances_ctl": ["int"],
            "personality_ctl": ["int"],
            "image_meta_ctl": ["int"],
            "personality_size_ctl": ["int"],
            "ram_ctl": ["int"],
            "server_groups_ctl": ["int"],
            "security_group_rules_ctl": ["int"],
            "keypairs_ctl": ["int"],
            "security_groups_ctl": ["int"],
            "server_group_members_ctl": ["int"],
            "floating_ips_ctl": ["int"],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "spot_price": ["float"],
            "vm_boot_volume": ["str", 64],
            "vm_flavor": ["str", 64],
            "vm_image": ["str", 64],
            "vm_keep_alive": ["int"],
            "vm_keyname": ["str", 64],
            "vm_network": ["str", 64],
            "vm_security_groups": ["str", 128],
            "error_count": ["int"],
            "error_time": ["int"],
            "machine_subprocess_pid": ["int"]
            }
        },
    "csv2_configuration": {
        "keys": [
            "category",
            "config_key"
            ],
        "columns": {
            "category": ["str", 32],
            "config_key": ["str", 32],
            "config_type": ["str", 16],
            "config_value": ["str", 128]
            }
        },
    "csv2_group_metadata": {
        "keys": [
            "group_name",
            "metadata_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "metadata_name": ["str", 64],
            "enabled": ["int"],
            "priority": ["int"],
            "metadata": ["str"],
            "mime_type": ["str", 128]
            }
        },
    "csv2_group_metadata_exclusions": {
        "keys": [
            "group_name",
            "metadata_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "metadata_name": ["str", 64],
            "cloud_name": ["str", 32]
            }
        },
    "csv2_groups": {
        "keys": [
            "group_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "htcondor_fqdn": ["str", 128],
            "htcondor_host_id": ["int"],
            "htcondor_gsi_dn": ["str", 128],
            "htcondor_gsi_eol": ["int"],
            "htcondor_container_hostname": ["str", 128],
            "htcondor_other_submitters": ["str", 128],
            "job_cpus": ["int"],
            "job_ram": ["int"],
            "job_disk": ["int"],
            "job_scratch": ["int"],
            "job_swap": ["int"],
            "vm_flavor": ["str", 64],
            "vm_image": ["str", 64],
            "vm_keep_alive": ["int"],
            "vm_keyname": ["str", 64],
            "vm_network": ["str", 64],
            "vm_security_groups": ["str", 128]
            }
        },
    "csv2_image_cache": {
        "keys": [
            "image_name",
            "checksum"
            ],
        "columns": {
            "image_name": ["str", 256],
            "checksum": ["str", 64],
            "container_format": ["str", 128],
            "disk_format": ["str", 128],
            "downloaded": ["int"]
            }
        },
    "csv2_image_pull_requests": {
        "keys": [
            "tx_id"
            ],
        "columns": {
            "tx_id": ["str", 16],
            "target_group_name": ["str", 128],
            "target_cloud_name": ["str", 128],
            "image_name": ["str", 128],
            "image_id": ["str", 128],
            "checksum": ["str", 64],
            "status": ["str", 32],
            "message": ["str", 512],
            "request_time": ["int"],
            "requester": ["str", 64]
            }
        },
    "csv2_image_transactions": {
        "keys": [
            "tx_id"
            ],
        "columns": {
            "tx_id": ["str", 16],
            "status": ["str", 128],
            "message": ["str", 128],
            "target_group_name": ["str", 128],
            "target_cloud_name": ["str", 128],
            "image_name": ["str", 128],
            "image_id": ["str", 128],
            "checksum": ["str", 64],
            "request_time": ["int"],
            "requester": ["str", 64]
            }
        },
    "csv2_mime_types": {
        "keys": [
            "mime_type"
            ],
        "columns": {
            "mime_type": ["str", 32]
            }
        },
    "csv2_service_catalog": {
        "keys": [
            "provider",
            "host_id"
            ],
        "columns": {
            "provider": ["str", 64],
            "host_id": ["int"],
            "last_updated": ["float"],
            "last_error": ["float"],
            "error_message": ["str", 256],
            "counter": ["int"]
            }
        },
    "csv2_service_providers": {
        "keys": [
            "provider"
            ],
        "columns": {
            "provider": ["str", 64],
            "service": ["str", 64],
            "alias": ["str", 16],
            "alias_priority": ["int"]
            }
        },
    "csv2_signal_log": {
        "keys": [
            "timestamp",
            "fqdn",
            "pid",
            "event",
            "action"
            ],
        "columns": {
            "timestamp": ["float"],
            "fqdn": ["str", 128],
            "pid": ["int"],
            "event": ["str", 64],
            "action": ["str", 64],
            "signame": ["str", 16],
            "caller": ["str", 256]
            }
        },
    "csv2_user": {
        "keys": [
            "username"
            ],
        "columns": {
            "username": ["str", 32],
            "cert_cn": ["str", 128],
            "password": ["str", 128],
            "is_superuser": ["int"],
            "join_date": ["int"],
            "default_group": ["str", 32],
            "flag_global_status": ["int"],
            "flag_jobs_by_target_alias": ["int"],
            "flag_show_foreign_global_vms": ["int"],
            "flag_show_slot_detail": ["int"],
            "flag_show_slot_flavors": ["int"],
            "status_refresh_interval": ["int"]
            }
        },
    "csv2_user_groups": {
        "keys": [
            "username",
            "group_name"
            ],
        "columns": {
            "username": ["str", 32],
            "group_name": ["str", 32]
            }
        },
    "csv2_vms": {
        "keys": [
            "group_name",
            "cloud_name",
            "vmid"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "target_alias": ["str", 32],
            "region": ["str", 32],
            "vmid": ["str", 128],
            "spot_instance": ["int"],
            "instance_id": ["str", 64],
            "cloud_type": ["str", 64],
            "vm_ips": ["str", 128],
            "vm_floating_ips": ["str", 128],
            "auth_url": ["str", 128],
            "project": ["str", 128],
            "hostname": ["str", 128],
            "keep_alive": ["int"],
            "start_time": ["int"],
            "status": ["str", 32],
            "flavor_id": ["str", 128],
            "image_id": ["str", 128],
            "task": ["str", 32],
            "power_status": ["int"],
            "manual_control": ["int"],
            "htcondor_startd_errors": ["str", 256],
            "htcondor_startd_time": ["int"],
            "htcondor_partitionable_slots": ["int"],
            "htcondor_dynamic_slots": ["int"],
            "htcondor_slots_timestamp": ["int"],
            "retire": ["int"],
            "retire_time": ["int"],
            "terminate": ["int"],
            "terminate_time": ["int"],
            "status_changed_time": ["int"],
            "last_updated": ["int"],
            "updater": ["str", 128]
            }
        },
    "csv2_vms_foreign": {
        "keys": [
            "authurl",
            "region",
            "project",
            "flavor_id"
            ],
        "columns": {
            "authurl": ["str", 128],
            "region": ["str", 32],
            "project": ["str", 32],
            "flavor_id": ["str", 128],
            "count": ["int"],
            "cloud_type": ["str", 32]
            }
        },
    "django_admin_log": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "action_time": ["int"],
            "object_id": ["str"],
            "object_repr": ["str", 200],
            "action_flag": ["int"],
            "change_message": ["str"],
            "content_type_id": ["int"],
            "user_id": ["int"]
            }
        },
    "django_content_type": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "app_label": ["str", 100],
            "model": ["str", 100]
            }
        },
    "django_migrations": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": ["int"],
            "app": ["str", 255],
            "name": ["str", 255],
            "applied": ["int"]
            }
        },
    "django_session": {
        "keys": [
            "session_key"
            ],
        "columns": {
            "session_key": ["str", 40],
            "session_data": ["str"],
            "expire_date": ["int"]
            }
        },
    "ec2_image_filters": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "owner_aliases": ["str", 128],
            "owner_ids": ["str", 128],
            "like": ["str", 128],
            "not_like": ["str", 128],
            "operating_systems": ["str", 128],
            "architectures": ["str", 128]
            }
        },
    "ec2_image_well_known_owner_aliases": {
        "keys": [
            "alias"
            ],
        "columns": {
            "alias": ["str", 32]
            }
        },
    "ec2_images": {
        "keys": [
            "region",
            "id",
            "borrower_id"
            ],
        "columns": {
            "region": ["str", 32],
            "id": ["str", 128],
            "borrower_id": ["str", 32],
            "owner_id": ["str", 32],
            "owner_alias": ["str", 64],
            "disk_format": ["str", 128],
            "size": ["int"],
            "image_location": ["str", 512],
            "visibility": ["str", 128],
            "name": ["str", 256],
            "description": ["str", 256],
            "last_updated": ["int"]
            }
        },
    "ec2_instance_status_codes": {
        "keys": [
            "ec2_state"
            ],
        "columns": {
            "ec2_state": ["str", 32],
            "csv2_state": ["str", 32]
            }
        },
    "ec2_instance_type_filters": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "families": ["str", 128],
            "operating_systems": ["str", 128],
            "processors": ["str", 128],
            "processor_manufacturers": ["str", 128],
            "cores": ["str", 32],
            "memory_min_gigabytes_per_core": ["int"],
            "memory_max_gigabytes_per_core": ["int"]
            }
        },
    "ec2_instance_types": {
        "keys": [
            "region",
            "instance_type",
            "operating_system"
            ],
        "columns": {
            "region": ["str", 32],
            "instance_type": ["str", 32],
            "operating_system": ["str", 32],
            "instance_family": ["str", 32],
            "processor": ["str", 64],
            "storage": ["str", 32],
            "cores": ["int"],
            "memory": ["float"],
            "cost_per_hour": ["float"]
            }
        },
    "ec2_regions": {
        "keys": [
            "region"
            ],
        "columns": {
            "region": ["str", 64],
            "location": ["str", 64],
            "endpoint": ["str", 128]
            }
        },
    "testing": {
        "keys": [
            "test_key"
            ],
        "columns": {
            "test_key": ["str", 16],
            "test_value": ["int"]
            }
        },
    "view_active_resource_shortfall": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "target_alias": ["str", 32],
            "request_cores": ["int"],
            "active_cores": ["int"],
            "shortfall_cores": ["int"],
            "request_disk": ["int"],
            "active_disk": ["int"],
            "shortfall_disk": ["int"],
            "request_ram": ["int"],
            "active_ram": ["int"],
            "shortfall_ram": ["int"],
            "starting": ["int"],
            "unregistered": ["int"],
            "idle": ["int"],
            "running": ["int"]
            }
        },
    "view_available_resources": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "cloud_priority": ["int"],
            "region": ["str", 32],
            "cloud_type": ["str", 64],
            "htcondor_fqdn": ["str", 128],
            "htcondor_container_hostname": ["str", 128],
            "htcondor_other_submitters": ["str", 128],
            "vm_boot_volume": ["str", 64],
            "spot_price": ["float"],
            "authurl": ["str", 128],
            "cacertificate": ["str"],
            "project_domain_name": ["str", 20],
            "project_domain_id": ["str", 64],
            "project": ["str", 128],
            "user_domain_name": ["str", 20],
            "user_domain_id": ["str", 64],
            "username": ["str", 20],
            "password": ["str"],
            "default_flavor": ["str", 97],
            "default_image": ["str", 64],
            "default_keep_alive": ["int"],
            "default_keyname": ["str", 64],
            "default_network": ["str", 64],
            "default_security_groups": ["str", 128],
            "VMs": ["int"],
            "VMs_max": ["int"],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "cores_limit": ["int"],
            "cores_max": ["int"],
            "cores_used": ["int"],
            "cores_foreign": ["int"],
            "disk_used": ["int"],
            "ram_ctl": ["int"],
            "ram_max": ["int"],
            "ram_limit": ["float"],
            "ram_used": ["int"],
            "ram_foreign": ["float"],
            "swap_used": ["int"],
            "flavor": ["str", 161],
            "flavor_id": ["str", 128],
            "flavor_slots": ["int"],
            "flavor_cores": ["int"],
            "flavor_disk": ["int"],
            "flavor_ram": ["int"],
            "flavor_swap": ["int"],
            "flavor_VMs": ["int"],
            "flavor_starting": ["int"],
            "flavor_unregistered": ["int"],
            "flavor_idle": ["int"],
            "flavor_running": ["int"],
            "flavor_retiring": ["int"],
            "flavor_error": ["int"],
            "flavor_manual": ["int"],
            "updater": ["str"],
            "worker_cert": ["str"],
            "worker_key": ["str"]
            }
        },
    "view_cloud_aliases": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "alias_name": ["str", 32],
            "clouds": ["str"]
            }
        },
    "view_cloud_status": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "VMs": ["int"],
            "VMs_manual": ["int"],
            "VMs_in_error": ["int"],
            "VMs_starting": ["int"],
            "VMs_retiring": ["int"],
            "VMs_unregistered": ["int"],
            "VMs_idle": ["int"],
            "VMs_running": ["int"],
            "cores_native": ["int"],
            "ram_native": ["float"],
            "slot_count": ["int"],
            "slot_core_count": ["int"],
            "slot_idle_core_count": ["int"],
            "Foreign_VMs": ["int"],
            "enabled": ["int"],
            "communication_up": ["int"],
            "communication_rt": ["int"],
            "cores_ctl": ["int"],
            "cores_limit": ["int"],
            "VMs_quota": ["int"],
            "VMs_native_foreign": ["int"],
            "cores_quota": ["int"],
            "cores_soft_quota": ["int"],
            "cores_foreign": ["int"],
            "cores_native_foreign": ["int"],
            "ram_ctl": ["int"],
            "ram_limit": ["int"],
            "ram_quota": ["int"],
            "ram_foreign": ["float"],
            "ram_native_foreign": ["float"]
            }
        },
    "view_cloud_status_flavor_slot_detail": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "flavor": ["str", 46],
            "slot_type": ["int"],
            "slot_id": ["str", 380],
            "slot_count": ["int"],
            "core_count": ["int"]
            }
        },
    "view_cloud_status_flavor_slot_detail_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "flavor": ["str", 46],
            "slot_type": ["int"],
            "slot_count": ["int"],
            "core_count": ["int"]
            }
        },
    "view_cloud_status_flavor_slot_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "flavor": ["str", 46],
            "busy": ["int"],
            "idle": ["int"],
            "idle_percent": ["int"]
            }
        },
    "view_cloud_status_slot_detail": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "slot_type": ["int"],
            "slot_id": ["str", 380],
            "slot_count": ["int"],
            "core_count": ["int"]
            }
        },
    "view_cloud_status_slot_detail_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "slot_type": ["int"],
            "slot_count": ["int"],
            "core_count": ["int"]
            }
        },
    "view_cloud_status_slot_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "busy": ["int"],
            "idle": ["int"],
            "idle_percent": ["int"]
            }
        },
    "view_clouds": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "enabled": ["int"],
            "cloud_priority": ["int"],
            "spot_price": ["float"],
            "vm_boot_volume": ["str", 64],
            "vm_flavor": ["str", 64],
            "vm_image": ["str", 64],
            "vm_keep_alive": ["int"],
            "vm_keyname": ["str", 64],
            "vm_network": ["str", 64],
            "vm_security_groups": ["str", 128],
            "cascading_vm_flavor": ["str", 64],
            "cascading_vm_image": ["str", 64],
            "cascading_vm_keep_alive": ["int"],
            "cascading_vm_keyname": ["str", 64],
            "cascading_vm_network": ["str", 64],
            "cascading_vm_security_groups": ["str", 128],
            "authurl": ["str", 128],
            "project_domain_name": ["str", 20],
            "project_domain_id": ["str", 64],
            "project": ["str", 128],
            "user_domain_name": ["str", 20],
            "user_domain_id": ["str", 64],
            "username": ["str", 20],
            "password": ["str"],
            "cacertificate": ["str"],
            "region": ["str", 32],
            "cloud_type": ["str", 64],
            "ec2_owner_id": ["str", 32],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "cores_max": ["int"],
            "cores_used": ["int"],
            "cores_foreign": ["int"],
            "cores_native": ["int"],
            "ram_ctl": ["int"],
            "ram_max": ["int"],
            "ram_used": ["int"],
            "ram_foreign": ["int"],
            "ram_native": ["int"],
            "instances_max": ["int"],
            "instances_used": ["int"],
            "floating_ips_max": ["int"],
            "floating_ips_used": ["int"],
            "security_groups_max": ["int"],
            "security_groups_used": ["int"],
            "server_groups_max": ["int"],
            "server_groups_used": ["int"],
            "image_meta_max": ["int"],
            "keypairs_max": ["int"],
            "personality_max": ["int"],
            "personality_size_max": ["int"],
            "security_group_rules_max": ["int"],
            "server_group_members_max": ["int"],
            "server_meta_max": ["int"],
            "cores_idle": ["int"],
            "ram_idle": ["int"]
            }
        },
    "view_clouds_with_metadata_info": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "enabled": ["int"],
            "cloud_priority": ["int"],
            "spot_price": ["float"],
            "vm_boot_volume": ["str", 64],
            "vm_flavor": ["str", 64],
            "vm_image": ["str", 64],
            "vm_keep_alive": ["int"],
            "vm_keyname": ["str", 64],
            "vm_network": ["str", 64],
            "vm_security_groups": ["str", 128],
            "cascading_vm_flavor": ["str", 64],
            "cascading_vm_image": ["str", 64],
            "cascading_vm_keep_alive": ["int"],
            "cascading_vm_keyname": ["str", 64],
            "cascading_vm_network": ["str", 64],
            "cascading_vm_security_groups": ["str", 128],
            "authurl": ["str", 128],
            "project_domain_name": ["str", 20],
            "project_domain_id": ["str", 64],
            "project": ["str", 128],
            "user_domain_name": ["str", 20],
            "user_domain_id": ["str", 64],
            "username": ["str", 20],
            "password": ["str"],
            "cacertificate": ["str"],
            "region": ["str", 32],
            "cloud_type": ["str", 64],
            "ec2_owner_id": ["str", 32],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "cores_max": ["int"],
            "cores_used": ["int"],
            "cores_foreign": ["int"],
            "cores_native": ["int"],
            "ram_ctl": ["int"],
            "ram_max": ["int"],
            "ram_used": ["int"],
            "ram_foreign": ["int"],
            "ram_native": ["int"],
            "instances_max": ["int"],
            "instances_used": ["int"],
            "floating_ips_max": ["int"],
            "floating_ips_used": ["int"],
            "security_groups_max": ["int"],
            "security_groups_used": ["int"],
            "server_groups_max": ["int"],
            "server_groups_used": ["int"],
            "image_meta_max": ["int"],
            "keypairs_max": ["int"],
            "personality_max": ["int"],
            "personality_size_max": ["int"],
            "security_group_rules_max": ["int"],
            "server_group_members_max": ["int"],
            "server_meta_max": ["int"],
            "cores_idle": ["int"],
            "ram_idle": ["int"],
            "metadata_name": ["str", 64],
            "metadata_enabled": ["int"],
            "metadata_priority": ["int"],
            "metadata_mime_type": ["str", 128]
            }
        },
    "view_clouds_with_metadata_names": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "enabled": ["int"],
            "cloud_priority": ["int"],
            "spot_price": ["float"],
            "vm_boot_volume": ["str", 64],
            "vm_flavor": ["str", 64],
            "vm_image": ["str", 64],
            "vm_keep_alive": ["int"],
            "vm_keyname": ["str", 64],
            "vm_network": ["str", 64],
            "vm_security_groups": ["str", 128],
            "cascading_vm_flavor": ["str", 64],
            "cascading_vm_image": ["str", 64],
            "cascading_vm_keep_alive": ["int"],
            "cascading_vm_keyname": ["str", 64],
            "cascading_vm_network": ["str", 64],
            "cascading_vm_security_groups": ["str", 128],
            "authurl": ["str", 128],
            "project_domain_name": ["str", 20],
            "project_domain_id": ["str", 64],
            "project": ["str", 128],
            "user_domain_name": ["str", 20],
            "user_domain_id": ["str", 64],
            "username": ["str", 20],
            "password": ["str"],
            "cacertificate": ["str"],
            "region": ["str", 32],
            "cloud_type": ["str", 64],
            "ec2_owner_id": ["str", 32],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "cores_max": ["int"],
            "cores_used": ["int"],
            "cores_foreign": ["int"],
            "cores_native": ["int"],
            "ram_ctl": ["int"],
            "ram_max": ["int"],
            "ram_used": ["int"],
            "ram_foreign": ["int"],
            "ram_native": ["int"],
            "instances_max": ["int"],
            "instances_used": ["int"],
            "floating_ips_max": ["int"],
            "floating_ips_used": ["int"],
            "security_groups_max": ["int"],
            "security_groups_used": ["int"],
            "server_groups_max": ["int"],
            "server_groups_used": ["int"],
            "image_meta_max": ["int"],
            "keypairs_max": ["int"],
            "personality_max": ["int"],
            "personality_size_max": ["int"],
            "security_group_rules_max": ["int"],
            "server_group_members_max": ["int"],
            "server_meta_max": ["int"],
            "cores_idle": ["int"],
            "ram_idle": ["int"],
            "flavor_exclusions": ["str"],
            "flavor_names": ["str"],
            "group_exclusions": ["str"],
            "metadata_names": ["str"]
            }
        },
    "view_condor_host": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "htcondor_fqdn": ["str", 128],
            "vmid": ["str", 128],
            "hostname": ["str", 128],
            "primary_slots": ["int"],
            "dynamic_slots": ["int"],
            "retire": ["int"],
            "terminate": ["int"],
            "machine": ["str", 256],
            "updater": ["str", 128],
            "retire_time": ["int"]
            }
        },
    "view_condor_jobs_group_defaults_applied": {
        "keys": [
            ],
        "columns": {
            "global_job_id": ["str", 128],
            "group_name": ["str", 32],
            "target_alias": ["str", 32],
            "job_status": ["int"],
            "request_cpus": ["int"],
            "request_disk": ["int"],
            "request_ram": ["int"],
            "request_swap": ["int"],
            "requirements": ["str", 512],
            "job_priority": ["int"],
            "cluster_id": ["int"],
            "proc_id": ["int"],
            "user": ["str", 512],
            "image": ["str"],
            "instance_type": ["str", 512],
            "network": ["str", 512],
            "keep_alive": ["str", 512],
            "max_price": ["str", 512],
            "user_data": ["str", 512],
            "job_per_core": ["int"],
            "entered_current_status": ["int"],
            "q_date": ["int"],
            "hold_job_reason": ["str", 64],
            "held_reason": ["str", 128],
            "js_idle": ["int"],
            "js_running": ["int"],
            "js_completed": ["int"],
            "js_held": ["int"],
            "js_other": ["int"]
            }
        },
    "view_ec2_images": {
        "keys": [
            ],
        "columns": {
            "region": ["str", 32],
            "id": ["str", 128],
            "borrower_id": ["str", 32],
            "owner_id": ["str", 32],
            "owner_alias": ["str", 64],
            "disk_format": ["str", 128],
            "size": ["int"],
            "image_location": ["str", 512],
            "visibility": ["str", 128],
            "name": ["str", 256],
            "description": ["str", 256],
            "last_updated": ["int"],
            "lower_location": ["str", 512],
            "opsys": ["str", 8],
            "arch": ["str", 5]
            }
        },
    "view_ec2_instance_types": {
        "keys": [
            ],
        "columns": {
            "region": ["str", 32],
            "instance_type": ["str", 32],
            "operating_system": ["str", 32],
            "instance_family": ["str", 32],
            "processor": ["str", 64],
            "storage": ["str", 32],
            "cores": ["int"],
            "memory": ["float"],
            "cost_per_hour": ["float"],
            "memory_per_core": ["float"],
            "processor_manufacturer": ["str", 64]
            }
        },
    "view_foreign_flavors": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "authurl": ["str", 128],
            "region": ["str", 32],
            "project": ["str", 128],
            "flavor_id": ["str", 128],
            "count": ["int"],
            "name": ["str", 128],
            "cores": ["int"],
            "ram": ["float"]
            }
        },
    "view_foreign_resources": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "count": ["int"],
            "cores": ["int"],
            "ram": ["float"]
            }
        },
    "view_groups_of_idle_jobs": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "target_alias": ["str", 32],
            "instance_type": ["str", 512],
            "requirements": ["str", 512],
            "job_priority": ["int"],
            "user": ["str", 512],
            "image": ["str"],
            "network": ["str", 512],
            "keep_alive": ["str", 512],
            "max_price": ["str", 512],
            "user_data": ["str", 512],
            "job_per_core": ["int"],
            "request_cpus_min": ["int"],
            "request_cpus_max": ["int"],
            "request_cpus_total": ["int"],
            "request_disk_min": ["int"],
            "request_disk_max": ["int"],
            "request_disk_total": ["int"],
            "request_ram_min": ["int"],
            "request_ram_max": ["int"],
            "request_ram_total": ["int"],
            "request_swap_min": ["int"],
            "request_swap_max": ["int"],
            "request_swap_total": ["int"],
            "queue_date": ["int"],
            "idle": ["int"],
            "running": ["int"],
            "completed": ["int"],
            "held": ["int"],
            "other": ["int"],
            "flavors": ["str"]
            }
        },
    "view_groups_with_metadata_info": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "htcondor_fqdn": ["str", 128],
            "htcondor_container_hostname": ["str", 128],
            "htcondor_other_submitters": ["str", 128],
            "metadata_name": ["str", 64],
            "metadata_enabled": ["int"],
            "metadata_priority": ["int"],
            "metadata_mime_type": ["str", 128]
            }
        },
    "view_groups_with_metadata_names": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "htcondor_fqdn": ["str", 128],
            "htcondor_container_hostname": ["str", 128],
            "htcondor_other_submitters": ["str", 128],
            "metadata_names": ["str"]
            }
        },
    "view_idle_vms": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "come_alive": ["str", 128],
            "job_alive": ["str", 128],
            "error_delay": ["str", 128],
            "keep_alive": ["int"],
            "vmid": ["str", 128],
            "hostname": ["str", 128],
            "primary_slots": ["int"],
            "dynamic_slots": ["int"],
            "retire": ["int"],
            "terminate": ["int"],
            "poller_status": ["str", 12],
            "age": ["int"]
            }
        },
    "view_job_status": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "Jobs": ["int"],
            "Idle": ["int"],
            "Running": ["int"],
            "Completed": ["int"],
            "Held": ["int"],
            "Other": ["int"],
            "foreign": ["int"],
            "htcondor_fqdn": ["str", 128],
            "state": ["str", 4],
            "plotable_state": ["str", 1],
            "error_message": ["str", 256],
            "condor_days_left": ["int"],
            "worker_days_left": ["int"]
            }
        },
    "view_job_status_by_target_alias": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "target_alias": ["str", 32],
            "Jobs": ["int"],
            "Idle": ["int"],
            "Running": ["int"],
            "Completed": ["int"],
            "Held": ["int"],
            "Other": ["int"],
            "foreign": ["int"],
            "htcondor_fqdn": ["str", 128],
            "state": ["str", 4],
            "plotable_state": ["str", 1],
            "error_message": ["str", 256],
            "condor_days_left": ["int"],
            "worker_days_left": ["int"]
            }
        },
    "view_metadata_collation": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "type": ["str", 5],
            "priority": ["int"],
            "metadata_name": ["str", 64],
            "mime_type": ["str", 128]
            }
        },
    "view_metadata_collation_json": {
        "keys": [
            ],
        "columns": {
            "group_metadata": ["str"]
            }
        },
    "view_resource_contention": {
        "keys": [
            ],
        "columns": {
            "authurl": ["str", 128],
            "VMs": ["int"],
            "starting": ["int"],
            "unregistered": ["int"],
            "idle": ["int"],
            "running": ["int"],
            "retiring": ["int"],
            "manual": ["int"],
            "error": ["int"]
            }
        },
    "view_service_status": {
        "keys": [
            ],
        "columns": {
            "alias": ["str", 16],
            "state": ["str", 4],
            "plotable_state": ["str", 1],
            "error_message": ["str", 256]
            }
        },
    "view_t0": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "enabled": ["int"],
            "priority": ["int"],
            "authurl": ["str", 128],
            "project": ["str", 128],
            "username": ["str", 20],
            "password": ["str"],
            "obsolete_keyname": ["str", 20],
            "cacertificate": ["str"],
            "region": ["str", 32],
            "user_domain_name": ["str", 20],
            "user_domain_id": ["str", 64],
            "project_domain_name": ["str", 20],
            "project_domain_id": ["str", 64],
            "cloud_type": ["str", 64],
            "ec2_owner_id": ["str", 32],
            "communication_up": ["int"],
            "communication_rt": ["int"],
            "server_meta_ctl": ["int"],
            "instances_ctl": ["int"],
            "personality_ctl": ["int"],
            "image_meta_ctl": ["int"],
            "personality_size_ctl": ["int"],
            "ram_ctl": ["int"],
            "server_groups_ctl": ["int"],
            "security_group_rules_ctl": ["int"],
            "keypairs_ctl": ["int"],
            "security_groups_ctl": ["int"],
            "server_group_members_ctl": ["int"],
            "floating_ips_ctl": ["int"],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "spot_price": ["float"],
            "vm_boot_volume": ["str", 64],
            "vm_flavor": ["str", 64],
            "vm_image": ["str", 64],
            "vm_keep_alive": ["int"],
            "vm_keyname": ["str", 64],
            "vm_network": ["str", 64],
            "vm_security_groups": ["str", 128],
            "error_count": ["int"],
            "error_time": ["int"],
            "machine_subprocess_pid": ["int"],
            "htcondor_fqdn": ["str", 128],
            "htcondor_container_hostname": ["str", 128],
            "htcondor_other_submitters": ["str", 128],
            "default_flavor": ["str", 97],
            "default_image": ["str", 64],
            "default_keep_alive": ["int"],
            "default_keyname": ["str", 64],
            "default_network": ["str", 64],
            "default_security_groups": ["str", 128],
            "VMs_max": ["int"],
            "cores_max": ["int"],
            "cores_limit": ["int"],
            "cores_foreign": ["int"],
            "ram_max": ["int"],
            "ram_limit": ["float"],
            "ram_foreign": ["float"],
            "worker_cert": ["str"],
            "worker_key": ["str"]
            }
        },
    "view_total_used_resources": {
        "keys": [
            ],
        "columns": {
            "authurl": ["str", 128],
            "region": ["str", 32],
            "project": ["str", 128],
            "VMs": ["int"],
            "cores": ["int"],
            "disk": ["int"],
            "ram": ["int"],
            "swap": ["int"]
            }
        },
    "view_user_groups": {
        "keys": [
            ],
        "columns": {
            "username": ["str", 32],
            "cert_cn": ["str", 128],
            "password": ["str", 128],
            "is_superuser": ["int"],
            "join_date": ["int"],
            "flag_global_status": ["int"],
            "flag_jobs_by_target_alias": ["int"],
            "flag_show_foreign_global_vms": ["int"],
            "flag_show_slot_detail": ["int"],
            "flag_show_slot_flavors": ["int"],
            "status_refresh_interval": ["int"],
            "default_group": ["str", 32],
            "user_groups": ["str"],
            "available_groups": ["str"]
            }
        },
    "view_user_groups_available": {
        "keys": [
            ],
        "columns": {
            "username": ["str", 32],
            "group_name": ["str", 32],
            "available": ["str", 32]
            }
        },
    "view_vm_kill_retire_over_quota": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "cloud_type": ["str", 64],
            "cores": ["int"],
            "cores_ctl": ["int"],
            "cores_softmax": ["int"],
            "cores_max": ["int"],
            "cores_native": ["int"],
            "cores_foreign": ["int"],
            "ram": ["float"],
            "ram_ctl": ["int"],
            "ram_max": ["int"],
            "ram_native": ["float"],
            "ram_foreign": ["float"]
            }
        },
    "view_vm_kill_retire_priority_age": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "vmid": ["str", 128],
            "flavor_id": ["str", 128],
            "machine": ["str", 256],
            "killed": ["int"],
            "retired": ["int"],
            "priority": ["int"],
            "flavor_cores": ["int"],
            "flavor_ram": ["int"]
            }
        },
    "view_vm_kill_retire_priority_idle": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "vmid": ["str", 128],
            "flavor_id": ["str", 128],
            "machine": ["str", 256],
            "killed": ["int"],
            "retired": ["int"],
            "priority": ["int"],
            "flavor_cores": ["int"],
            "flavor_ram": ["int"]
            }
        },
    "view_vms": {
        "keys": [
            ],
        "columns": {
            "group_name": ["str", 32],
            "cloud_name": ["str", 32],
            "target_alias": ["str", 32],
            "region": ["str", 32],
            "vmid": ["str", 128],
            "spot_instance": ["int"],
            "instance_id": ["str", 64],
            "cloud_type": ["str", 64],
            "vm_ips": ["str", 128],
            "vm_floating_ips": ["str", 128],
            "auth_url": ["str", 128],
            "project": ["str", 128],
            "hostname": ["str", 128],
            "keep_alive": ["int"],
            "start_time": ["int"],
            "status": ["str", 32],
            "flavor_id": ["str", 128],
            "image_id": ["str", 128],
            "task": ["str", 32],
            "power_status": ["int"],
            "manual_control": ["int"],
            "htcondor_startd_errors": ["str", 256],
            "htcondor_startd_time": ["int"],
            "htcondor_partitionable_slots": ["int"],
            "htcondor_dynamic_slots": ["int"],
            "htcondor_slots_timestamp": ["int"],
            "retire": ["int"],
            "retire_time": ["int"],
            "terminate": ["int"],
            "terminate_time": ["int"],
            "status_changed_time": ["int"],
            "last_updated": ["int"],
            "updater": ["str", 128],
            "flavor_name": ["str", 128],
            "condor_slots": ["int"],
            "condor_slots_used": ["int"],
            "machine": ["str", 256],
            "my_current_time": ["int"],
            "entered_current_state": ["int"],
            "idle_time": ["int"],
            "foreign_vm": ["int"],
            "cores": ["int"],
            "disk": ["int"],
            "ram": ["int"],
            "swap": ["int"],
            "poller_status": ["str", 12],
            "age": ["int"]
            }
        }
    }
