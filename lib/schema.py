schema = {
    "apel_accounting": {
        "keys": [
            "group_name",
            "cloud_name",
            "vmid"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "hostname": {"type": "str", "len": "128", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "32", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "YES"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "YES"},
            "image_id": {"type": "str", "len": "128", "nulls": "YES"},
            "benchmark_type": {"type": "str", "len": "32", "nulls": "YES"},
            "benchmark": {"type": "int"},
            "start_time": {"type": "int"},
            "end_time": {"type": "int"},
            "last_update": {"type": "int"},
            "cpu_time": {"type": "int"},
            "network_type": {"type": "str", "len": "32", "nulls": "YES"},
            "rx": {"type": "int"},
            "tx": {"type": "int"}
            }
        },
    "archived_condor_jobs": {
        "keys": [
            "global_job_id"
            ],
        "columns": {
            "global_job_id": {"type": "str", "len": "128", "nulls": "NO"},
            "group_name": {"type": "str", "len": "128", "nulls": "YES"},
            "target_clouds": {"type": "str", "nulls": "YES"},
            "cloud_name": {"type": "str", "nulls": "YES"},
            "job_status": {"type": "int"},
            "request_cpus": {"type": "int"},
            "request_ram": {"type": "int"},
            "request_disk": {"type": "int"},
            "request_swap": {"type": "int"},
            "request_scratch": {"type": "int"},
            "requirements": {"type": "str", "len": "512", "nulls": "YES"},
            "job_priority": {"type": "int"},
            "cluster_id": {"type": "int"},
            "proc_id": {"type": "int"},
            "user": {"type": "str", "len": "512", "nulls": "YES"},
            "image": {"type": "str", "nulls": "YES"},
            "instance_type": {"type": "str", "len": "512", "nulls": "YES"},
            "network": {"type": "str", "len": "512", "nulls": "YES"},
            "keep_alive": {"type": "str", "len": "512", "nulls": "YES"},
            "max_price": {"type": "str", "len": "512", "nulls": "YES"},
            "user_data": {"type": "str", "len": "512", "nulls": "YES"},
            "job_per_core": {"type": "int"},
            "entered_current_status": {"type": "int"},
            "q_date": {"type": "int"},
            "hold_job_reason": {"type": "str", "len": "64", "nulls": "YES"},
            "held_reason": {"type": "str", "len": "64", "nulls": "YES"}
            }
        },
    "archived_condor_machines": {
        "keys": [
            "name"
            ],
        "columns": {
            "name": {"type": "str", "len": "128", "nulls": "NO"},
            "machine": {"type": "str", "len": "256", "nulls": "YES"},
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "condor_host": {"type": "str", "len": "64", "nulls": "YES"},
            "flavor": {"type": "str", "len": "32", "nulls": "YES"},
            "job_id": {"type": "str", "len": "128", "nulls": "YES"},
            "global_job_id": {"type": "str", "len": "128", "nulls": "YES"},
            "address": {"type": "str", "len": "512", "nulls": "YES"},
            "state": {"type": "str", "len": "128", "nulls": "YES"},
            "activity": {"type": "str", "len": "128", "nulls": "YES"},
            "vm_type": {"type": "str", "len": "128", "nulls": "YES"},
            "my_current_time": {"type": "int"},
            "entered_current_state": {"type": "int"},
            "start": {"type": "str", "len": "128", "nulls": "YES"},
            "remote_owner": {"type": "str", "len": "128", "nulls": "YES"},
            "slot_type": {"type": "str", "len": "128", "nulls": "YES"},
            "total_slots": {"type": "int"},
            "idle_time": {"type": "int"},
            "retire_request_time": {"type": "int"},
            "retired_time": {"type": "int"}
            }
        },
    "auth_group": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "name": {"type": "str", "len": "80", "nulls": "NO"}
            }
        },
    "auth_group_permissions": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "group_id": {"type": "int"},
            "permission_id": {"type": "int"}
            }
        },
    "auth_permission": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "name": {"type": "str", "len": "255", "nulls": "NO"},
            "content_type_id": {"type": "int"},
            "codename": {"type": "str", "len": "100", "nulls": "NO"}
            }
        },
    "auth_user": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "password": {"type": "str", "len": "128", "nulls": "NO"},
            "last_login": {"type": "str", "nulls": "YES"},
            "is_superuser": {"type": "int"},
            "username": {"type": "str", "len": "150", "nulls": "NO"},
            "first_name": {"type": "str", "len": "30", "nulls": "NO"},
            "last_name": {"type": "str", "len": "150", "nulls": "NO"},
            "email": {"type": "str", "len": "254", "nulls": "NO"},
            "is_staff": {"type": "int"},
            "is_active": {"type": "int"},
            "date_joined": {"type": "str", "nulls": "NO"}
            }
        },
    "auth_user_groups": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "user_id": {"type": "int"},
            "group_id": {"type": "int"}
            }
        },
    "auth_user_user_permissions": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "user_id": {"type": "int"},
            "permission_id": {"type": "int"}
            }
        },
    "cloud_flavors": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "id": {"type": "str", "len": "128", "nulls": "NO"},
            "name": {"type": "str", "len": "128", "nulls": "YES"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "ram": {"type": "int"},
            "cores": {"type": "int"},
            "swap": {"type": "int"},
            "disk": {"type": "int"},
            "ephemeral_disk": {"type": "int"},
            "is_public": {"type": "int"},
            "last_updated": {"type": "int"}
            }
        },
    "cloud_images": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "id": {"type": "str", "len": "128", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "container_format": {"type": "str", "len": "128", "nulls": "YES"},
            "disk_format": {"type": "str", "len": "128", "nulls": "YES"},
            "name": {"type": "str", "len": "256", "nulls": "YES"},
            "size": {"type": "int"},
            "visibility": {"type": "str", "len": "128", "nulls": "YES"},
            "min_disk": {"type": "int"},
            "min_ram": {"type": "int"},
            "checksum": {"type": "str", "len": "64", "nulls": "YES"},
            "created_at": {"type": "str", "len": "32", "nulls": "YES"},
            "last_updated": {"type": "int"}
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
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "fingerprint": {"type": "str", "len": "64", "nulls": "NO"},
            "key_name": {"type": "str", "len": "64", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"}
            }
        },
    "cloud_limits": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "server_meta_max": {"type": "int"},
            "instances_max": {"type": "int"},
            "personality_max": {"type": "int"},
            "image_meta_max": {"type": "int"},
            "personality_size_max": {"type": "int"},
            "ram_max": {"type": "int"},
            "server_groups_max": {"type": "int"},
            "security_group_rules_max": {"type": "int"},
            "keypairs_max": {"type": "int"},
            "security_groups_max": {"type": "int"},
            "server_group_members_max": {"type": "int"},
            "floating_ips_max": {"type": "int"},
            "cores_max": {"type": "int"},
            "server_groups_used": {"type": "int"},
            "instances_used": {"type": "int"},
            "ram_used": {"type": "int"},
            "security_groups_used": {"type": "int"},
            "floating_ips_used": {"type": "int"},
            "cores_used": {"type": "int"},
            "volumes_max": {"type": "int"},
            "volumes_used": {"type": "int"},
            "volume_gigs_max": {"type": "int"},
            "volume_gigs_used": {"type": "int"},
            "last_updated": {"type": "int"}
            }
        },
    "cloud_networks": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "id": {"type": "str", "len": "128", "nulls": "NO"},
            "name": {"type": "str", "len": "256", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "subnets": {"type": "str", "len": "256", "nulls": "YES"},
            "tenant_id": {"type": "str", "len": "128", "nulls": "YES"},
            "external_route": {"type": "int"},
            "shared": {"type": "int"},
            "last_updated": {"type": "int"}
            }
        },
    "cloud_security_groups": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "id": {"type": "str", "len": "64", "nulls": "NO"},
            "name": {"type": "str", "len": "128", "nulls": "YES"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "last_updated": {"type": "int"}
            }
        },
    "cloud_volumes": {
        "keys": [
            "group_name",
            "cloud_name",
            "id"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "name": {"type": "str", "len": "256", "nulls": "NO"},
            "host": {"type": "str", "len": "256", "nulls": "NO"},
            "id": {"type": "str", "len": "128", "nulls": "NO"},
            "size": {"type": "int"},
            "volume_type": {"type": "str", "len": "64", "nulls": "NO"},
            "status": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "32", "nulls": "NO"},
            "last_updated": {"type": "int"}
            }
        },
    "condor_jobs": {
        "keys": [
            "global_job_id"
            ],
        "columns": {
            "global_job_id": {"type": "str", "len": "128", "nulls": "NO"},
            "htcondor_host_id": {"type": "int"},
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "target_clouds": {"type": "str", "nulls": "YES"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "job_status": {"type": "int"},
            "request_cpus": {"type": "int"},
            "request_ram": {"type": "int"},
            "request_disk": {"type": "int"},
            "request_swap": {"type": "int"},
            "request_scratch": {"type": "int"},
            "requirements": {"type": "str", "len": "512", "nulls": "YES"},
            "job_priority": {"type": "int"},
            "cluster_id": {"type": "int"},
            "proc_id": {"type": "int"},
            "user": {"type": "str", "len": "512", "nulls": "YES"},
            "image": {"type": "str", "nulls": "YES"},
            "instance_type": {"type": "str", "len": "512", "nulls": "YES"},
            "network": {"type": "str", "len": "512", "nulls": "YES"},
            "keep_alive": {"type": "str", "len": "512", "nulls": "YES"},
            "max_price": {"type": "str", "len": "512", "nulls": "YES"},
            "user_data": {"type": "str", "len": "512", "nulls": "YES"},
            "job_per_core": {"type": "int"},
            "entered_current_status": {"type": "int"},
            "q_date": {"type": "int"},
            "hold_reason_code": {"type": "int"},
            "hold_reason_subcode": {"type": "int"},
            "last_remote_host": {"type": "str", "len": "64", "nulls": "YES"},
            "held_reason": {"type": "str", "len": "128", "nulls": "YES"},
            "hold_job_reason": {"type": "str", "len": "64", "nulls": "YES"}
            }
        },
    "condor_machines": {
        "keys": [
            "name"
            ],
        "columns": {
            "name": {"type": "str", "len": "128", "nulls": "NO"},
            "htcondor_host_id": {"type": "int"},
            "machine": {"type": "str", "len": "256", "nulls": "YES"},
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "condor_host": {"type": "str", "len": "64", "nulls": "YES"},
            "flavor": {"type": "str", "len": "32", "nulls": "YES"},
            "job_id": {"type": "str", "len": "128", "nulls": "YES"},
            "global_job_id": {"type": "str", "len": "128", "nulls": "YES"},
            "address": {"type": "str", "len": "512", "nulls": "YES"},
            "state": {"type": "str", "len": "128", "nulls": "YES"},
            "activity": {"type": "str", "len": "128", "nulls": "YES"},
            "vm_type": {"type": "str", "len": "128", "nulls": "YES"},
            "my_current_time": {"type": "int"},
            "entered_current_state": {"type": "int"},
            "start": {"type": "str", "len": "128", "nulls": "YES"},
            "remote_owner": {"type": "str", "len": "128", "nulls": "YES"},
            "total_disk": {"type": "int"},
            "slot_type": {"type": "str", "len": "128", "nulls": "YES"},
            "slot_cpus": {"type": "int"},
            "total_slots": {"type": "int"},
            "idle_time": {"type": "int"},
            "deprecated-retire_request_time": {"type": "int"},
            "deprecated-retired_time": {"type": "int"}
            }
        },
    "condor_worker_gsi": {
        "keys": [
            "htcondor_fqdn"
            ],
        "columns": {
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "NO"},
            "htcondor_host_id": {"type": "int"},
            "worker_dn": {"type": "str", "len": "128", "nulls": "YES"},
            "worker_eol": {"type": "int"},
            "worker_cert": {"type": "str", "nulls": "YES"},
            "worker_key": {"type": "str", "nulls": "YES"}
            }
        },
    "csv2_attribute_mapping": {
        "keys": [
            "csv2"
            ],
        "columns": {
            "csv2": {"type": "str", "len": "64", "nulls": "NO"},
            "os_limits": {"type": "str", "len": "64", "nulls": "YES"},
            "os_flavors": {"type": "str", "len": "64", "nulls": "YES"},
            "os_images": {"type": "str", "len": "64", "nulls": "YES"},
            "os_networks": {"type": "str", "len": "64", "nulls": "YES"},
            "os_vms": {"type": "str", "len": "64", "nulls": "YES"},
            "os_sec_grps": {"type": "str", "len": "64", "nulls": "YES"},
            "condor": {"type": "str", "len": "64", "nulls": "YES"},
            "ec2_flavors": {"type": "str", "len": "64", "nulls": "YES"},
            "ec2_limits": {"type": "str", "len": "64", "nulls": "YES"},
            "ec2_regions": {"type": "str", "len": "64", "nulls": "YES"},
            "ec2_images": {"type": "str", "len": "64", "nulls": "YES"},
            "ec2_vms": {"type": "str", "len": "20", "nulls": "NO"}
            }
        },
    "csv2_cloud_aliases": {
        "keys": [
            "group_name",
            "cloud_name",
            "alias_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "alias_name": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "csv2_cloud_flavor_exclusions": {
        "keys": [
            "group_name",
            "cloud_name",
            "flavor_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "flavor_name": {"type": "str", "len": "128", "nulls": "NO"}
            }
        },
    "csv2_cloud_metadata": {
        "keys": [
            "group_name",
            "cloud_name",
            "metadata_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "metadata_name": {"type": "str", "len": "64", "nulls": "NO"},
            "enabled": {"type": "int"},
            "priority": {"type": "int"},
            "metadata": {"type": "str", "nulls": "NO"},
            "mime_type": {"type": "str", "len": "128", "nulls": "NO"}
            }
        },
    "csv2_cloud_types": {
        "keys": [
            "cloud_type"
            ],
        "columns": {
            "cloud_type": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "csv2_clouds": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "enabled": {"type": "int"},
            "priority": {"type": "int"},
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "username": {"type": "str", "len": "20", "nulls": "NO"},
            "userid": {"type": "str", "len": "64", "nulls": "YES"},
            "password": {"type": "str", "nulls": "NO"},
            "obsolete_keyname": {"type": "str", "len": "20", "nulls": "YES"},
            "cacertificate": {"type": "str", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "user_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "user_domain_id": {"type": "str", "len": "64", "nulls": "YES"},
            "project_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "project_domain_id": {"type": "str", "len": "64", "nulls": "YES"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "NO"},
            "ec2_owner_id": {"type": "str", "len": "32", "nulls": "YES"},
            "auth_type": {"type": "str", "len": "32", "nulls": "YES"},
            "app_credentials": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_secret": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_expiry": {"type": "int"},
            "communication_up": {"type": "int"},
            "communication_rt": {"type": "int"},
            "server_meta_ctl": {"type": "int"},
            "instances_ctl": {"type": "int"},
            "personality_ctl": {"type": "int"},
            "image_meta_ctl": {"type": "int"},
            "personality_size_ctl": {"type": "int"},
            "ram_ctl": {"type": "int"},
            "server_groups_ctl": {"type": "int"},
            "security_group_rules_ctl": {"type": "int"},
            "keypairs_ctl": {"type": "int"},
            "security_groups_ctl": {"type": "int"},
            "server_group_members_ctl": {"type": "int"},
            "floating_ips_ctl": {"type": "int"},
            "cores_ctl": {"type": "int"},
            "cores_softmax": {"type": "int"},
            "spot_price": {"type": "float"},
            "vm_boot_volume": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_flavor": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_image": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_keep_alive": {"type": "int"},
            "vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_network": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "error_count": {"type": "int"},
            "error_time": {"type": "int"},
            "machine_subprocess_pid": {"type": "int"}
            }
        },
    "csv2_configuration": {
        "keys": [
            "category",
            "config_key"
            ],
        "columns": {
            "category": {"type": "str", "len": "32", "nulls": "NO"},
            "config_key": {"type": "str", "len": "32", "nulls": "NO"},
            "config_type": {"type": "str", "len": "16", "nulls": "NO"},
            "config_value": {"type": "str", "len": "128", "nulls": "YES"}
            }
        },
    "csv2_group_metadata": {
        "keys": [
            "group_name",
            "metadata_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "metadata_name": {"type": "str", "len": "64", "nulls": "NO"},
            "enabled": {"type": "int"},
            "priority": {"type": "int"},
            "metadata": {"type": "str", "nulls": "NO"},
            "mime_type": {"type": "str", "len": "128", "nulls": "NO"}
            }
        },
    "csv2_group_metadata_exclusions": {
        "keys": [
            "group_name",
            "metadata_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "metadata_name": {"type": "str", "len": "64", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "csv2_groups": {
        "keys": [
            "group_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_host_id": {"type": "int"},
            "htcondor_gsi_dn": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_gsi_eol": {"type": "int"},
            "htcondor_container_hostname": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_other_submitters": {"type": "str", "len": "128", "nulls": "YES"},
            "job_cpus": {"type": "int"},
            "job_ram": {"type": "int"},
            "job_disk": {"type": "int"},
            "job_scratch": {"type": "int"},
            "job_swap": {"type": "int"},
            "vm_flavor": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_image": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_keep_alive": {"type": "int"},
            "vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_network": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"}
            }
        },
    "csv2_image_cache": {
        "keys": [
            "image_name",
            "checksum"
            ],
        "columns": {
            "image_name": {"type": "str", "len": "256", "nulls": "NO"},
            "checksum": {"type": "str", "len": "64", "nulls": "NO"},
            "container_format": {"type": "str", "len": "128", "nulls": "NO"},
            "disk_format": {"type": "str", "len": "128", "nulls": "YES"},
            "downloaded": {"type": "str", "nulls": "NO"}
            }
        },
    "csv2_image_pull_requests": {
        "keys": [
            "tx_id"
            ],
        "columns": {
            "tx_id": {"type": "str", "len": "16", "nulls": "NO"},
            "target_group_name": {"type": "str", "len": "128", "nulls": "NO"},
            "target_cloud_name": {"type": "str", "len": "128", "nulls": "NO"},
            "image_name": {"type": "str", "len": "128", "nulls": "NO"},
            "image_id": {"type": "str", "len": "128", "nulls": "NO"},
            "checksum": {"type": "str", "len": "64", "nulls": "NO"},
            "status": {"type": "str", "len": "32", "nulls": "NO"},
            "message": {"type": "str", "len": "512", "nulls": "YES"},
            "request_time": {"type": "str", "nulls": "NO"},
            "requester": {"type": "str", "len": "64", "nulls": "NO"}
            }
        },
    "csv2_image_transactions": {
        "keys": [
            "tx_id"
            ],
        "columns": {
            "tx_id": {"type": "str", "len": "16", "nulls": "NO"},
            "status": {"type": "str", "len": "128", "nulls": "NO"},
            "message": {"type": "str", "len": "128", "nulls": "YES"},
            "target_group_name": {"type": "str", "len": "128", "nulls": "NO"},
            "target_cloud_name": {"type": "str", "len": "128", "nulls": "NO"},
            "image_name": {"type": "str", "len": "128", "nulls": "NO"},
            "image_id": {"type": "str", "len": "128", "nulls": "NO"},
            "checksum": {"type": "str", "len": "64", "nulls": "NO"},
            "request_time": {"type": "str", "nulls": "NO"},
            "requester": {"type": "str", "len": "64", "nulls": "NO"}
            }
        },
    "csv2_job_schedulers": {
        "keys": [
            "htcondor_fqdn"
            ],
        "columns": {
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "NO"},
            "condor_status": {"type": "int"},
            "agent_status": {"type": "int"},
            "foreign_jobs": {"type": "int"}
            }
        },
    "csv2_mime_types": {
        "keys": [
            "mime_type"
            ],
        "columns": {
            "mime_type": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "csv2_service_catalog": {
        "keys": [
            "provider",
            "host_id"
            ],
        "columns": {
            "provider": {"type": "str", "len": "64", "nulls": "NO"},
            "host_id": {"type": "int"},
            "last_updated": {"type": "float"},
            "last_error": {"type": "float"},
            "error_message": {"type": "str", "len": "512", "nulls": "YES"},
            "counter": {"type": "int"}
            }
        },
    "csv2_service_providers": {
        "keys": [
            "provider"
            ],
        "columns": {
            "provider": {"type": "str", "len": "64", "nulls": "NO"},
            "service": {"type": "str", "len": "64", "nulls": "NO"},
            "alias": {"type": "str", "len": "16", "nulls": "YES"},
            "alias_priority": {"type": "int"}
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
            "timestamp": {"type": "float"},
            "fqdn": {"type": "str", "len": "128", "nulls": "NO"},
            "pid": {"type": "int"},
            "event": {"type": "str", "len": "64", "nulls": "NO"},
            "action": {"type": "str", "len": "64", "nulls": "NO"},
            "signame": {"type": "str", "len": "16", "nulls": "NO"},
            "caller": {"type": "str", "len": "256", "nulls": "NO"}
            }
        },
    "csv2_system_status": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "csv2_main_status": {"type": "int"},
            "csv2_main_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "mariadb_status": {"type": "int"},
            "mariadb_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_openstack_error_count": {"type": "int"},
            "csv2_openstack_status": {"type": "int"},
            "csv2_openstack_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_jobs_error_count": {"type": "int"},
            "csv2_jobs_status": {"type": "int"},
            "csv2_jobs_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_machines_error_count": {"type": "int"},
            "csv2_machines_status": {"type": "int"},
            "csv2_machines_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_condor_gsi_error_count": {"type": "int"},
            "csv2_condor_gsi_status": {"type": "int"},
            "csv2_condor_gsi_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_status_error_count": {"type": "int"},
            "csv2_status_status": {"type": "int"},
            "csv2_status_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_timeseries_error_count": {"type": "int"},
            "csv2_timeseries_status": {"type": "int"},
            "csv2_timeseries_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_ec2_error_count": {"type": "int"},
            "csv2_ec2_status": {"type": "int"},
            "csv2_ec2_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_htc_agent_error_count": {"type": "int"},
            "csv2_htc_agent_status": {"type": "int"},
            "csv2_htc_agent_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_glint_error_count": {"type": "int"},
            "csv2_glint_status": {"type": "int"},
            "csv2_glint_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_watch_error_count": {"type": "int"},
            "csv2_watch_status": {"type": "int"},
            "csv2_watch_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "csv2_vm_data_error_count": {"type": "int"},
            "csv2_vm_data_status": {"type": "int"},
            "csv2_vm_data_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "condor_status": {"type": "int"},
            "condor_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "rabbitmq_server_status": {"type": "int"},
            "rabbitmq_server_msg": {"type": "str", "len": "512", "nulls": "YES"},
            "load": {"type": "float"},
            "ram": {"type": "float"},
            "ram_size": {"type": "float"},
            "ram_used": {"type": "float"},
            "swap": {"type": "float"},
            "swap_size": {"type": "float"},
            "swap_used": {"type": "float"},
            "disk": {"type": "float"},
            "disk_size": {"type": "float"},
            "disk_used": {"type": "float"},
            "last_updated": {"type": "int"}
            }
        },
    "csv2_timestamps": {
        "keys": [
            "entity"
            ],
        "columns": {
            "entity": {"type": "str", "len": "64", "nulls": "NO"},
            "last_updated": {"type": "int"}
            }
        },
    "csv2_user": {
        "keys": [
            "username"
            ],
        "columns": {
            "username": {"type": "str", "len": "32", "nulls": "NO"},
            "cert_cn": {"type": "str", "len": "128", "nulls": "YES"},
            "password": {"type": "str", "len": "128", "nulls": "NO"},
            "is_superuser": {"type": "int"},
            "join_date": {"type": "str", "nulls": "NO"},
            "default_group": {"type": "str", "len": "32", "nulls": "YES"},
            "flag_global_status": {"type": "int"},
            "flag_jobs_by_target_alias": {"type": "int"},
            "flag_show_foreign_global_vms": {"type": "int"},
            "flag_show_slot_detail": {"type": "int"},
            "flag_show_slot_flavors": {"type": "int"},
            "status_refresh_interval": {"type": "int"}
            }
        },
    "csv2_user_groups": {
        "keys": [
            "username",
            "group_name"
            ],
        "columns": {
            "username": {"type": "str", "len": "32", "nulls": "NO"},
            "group_name": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "csv2_vms": {
        "keys": [
            "group_name",
            "cloud_name",
            "vmid"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "YES"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "spot_instance": {"type": "int"},
            "instance_id": {"type": "str", "len": "64", "nulls": "YES"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_ips": {"type": "str", "len": "128", "nulls": "YES"},
            "vm_floating_ips": {"type": "str", "len": "128", "nulls": "YES"},
            "auth_url": {"type": "str", "len": "128", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "hostname": {"type": "str", "len": "128", "nulls": "NO"},
            "keep_alive": {"type": "int"},
            "start_time": {"type": "int"},
            "status": {"type": "str", "len": "32", "nulls": "YES"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "YES"},
            "image_id": {"type": "str", "len": "128", "nulls": "YES"},
            "task": {"type": "str", "len": "32", "nulls": "YES"},
            "power_status": {"type": "int"},
            "manual_control": {"type": "int"},
            "htcondor_startd_errors": {"type": "str", "len": "256", "nulls": "YES"},
            "htcondor_startd_time": {"type": "int"},
            "htcondor_partitionable_slots": {"type": "int"},
            "htcondor_dynamic_slots": {"type": "int"},
            "htcondor_slots_timestamp": {"type": "int"},
            "retire": {"type": "int"},
            "retire_time": {"type": "int"},
            "terminate": {"type": "int"},
            "terminate_time": {"type": "int"},
            "status_changed_time": {"type": "int"},
            "last_updated": {"type": "int"},
            "updater": {"type": "str", "len": "128", "nulls": "YES"}
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
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "project": {"type": "str", "len": "32", "nulls": "NO"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "NO"},
            "count": {"type": "int"},
            "cloud_type": {"type": "str", "len": "32", "nulls": "YES"}
            }
        },
    "django_admin_log": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "action_time": {"type": "str", "nulls": "NO"},
            "object_id": {"type": "str", "nulls": "YES"},
            "object_repr": {"type": "str", "len": "200", "nulls": "NO"},
            "action_flag": {"type": "int"},
            "change_message": {"type": "str", "nulls": "NO"},
            "content_type_id": {"type": "int"},
            "user_id": {"type": "int"}
            }
        },
    "django_content_type": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "app_label": {"type": "str", "len": "100", "nulls": "NO"},
            "model": {"type": "str", "len": "100", "nulls": "NO"}
            }
        },
    "django_migrations": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "app": {"type": "str", "len": "255", "nulls": "NO"},
            "name": {"type": "str", "len": "255", "nulls": "NO"},
            "applied": {"type": "str", "nulls": "NO"}
            }
        },
    "django_session": {
        "keys": [
            "session_key"
            ],
        "columns": {
            "session_key": {"type": "str", "len": "40", "nulls": "NO"},
            "session_data": {"type": "str", "nulls": "NO"},
            "expire_date": {"type": "str", "nulls": "NO"}
            }
        },
    "ec2_image_filters": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "owner_aliases": {"type": "str", "len": "128", "nulls": "YES"},
            "owner_ids": {"type": "str", "len": "128", "nulls": "YES"},
            "like": {"type": "str", "len": "128", "nulls": "YES"},
            "not_like": {"type": "str", "len": "128", "nulls": "YES"},
            "operating_systems": {"type": "str", "len": "128", "nulls": "YES"},
            "architectures": {"type": "str", "len": "128", "nulls": "YES"}
            }
        },
    "ec2_image_well_known_owner_aliases": {
        "keys": [
            "alias"
            ],
        "columns": {
            "alias": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "ec2_images": {
        "keys": [
            "region",
            "id",
            "borrower_id"
            ],
        "columns": {
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "id": {"type": "str", "len": "128", "nulls": "NO"},
            "borrower_id": {"type": "str", "len": "32", "nulls": "NO"},
            "owner_id": {"type": "str", "len": "32", "nulls": "YES"},
            "owner_alias": {"type": "str", "len": "64", "nulls": "YES"},
            "disk_format": {"type": "str", "len": "128", "nulls": "YES"},
            "size": {"type": "int"},
            "image_location": {"type": "str", "len": "512", "nulls": "YES"},
            "visibility": {"type": "str", "len": "128", "nulls": "YES"},
            "name": {"type": "str", "len": "256", "nulls": "YES"},
            "description": {"type": "str", "len": "256", "nulls": "YES"},
            "last_updated": {"type": "int"}
            }
        },
    "ec2_instance_status_codes": {
        "keys": [
            "ec2_state"
            ],
        "columns": {
            "ec2_state": {"type": "str", "len": "32", "nulls": "NO"},
            "csv2_state": {"type": "str", "len": "32", "nulls": "NO"}
            }
        },
    "ec2_instance_type_filters": {
        "keys": [
            "group_name",
            "cloud_name"
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "families": {"type": "str", "len": "128", "nulls": "YES"},
            "operating_systems": {"type": "str", "len": "128", "nulls": "YES"},
            "processors": {"type": "str", "len": "128", "nulls": "YES"},
            "processor_manufacturers": {"type": "str", "len": "128", "nulls": "YES"},
            "cores": {"type": "str", "len": "32", "nulls": "YES"},
            "memory_min_gigabytes_per_core": {"type": "int"},
            "memory_max_gigabytes_per_core": {"type": "int"}
            }
        },
    "ec2_instance_types": {
        "keys": [
            "region",
            "instance_type",
            "operating_system"
            ],
        "columns": {
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "instance_type": {"type": "str", "len": "32", "nulls": "NO"},
            "operating_system": {"type": "str", "len": "32", "nulls": "NO"},
            "instance_family": {"type": "str", "len": "32", "nulls": "YES"},
            "processor": {"type": "str", "len": "64", "nulls": "YES"},
            "storage": {"type": "str", "len": "32", "nulls": "YES"},
            "cores": {"type": "int"},
            "memory": {"type": "float"},
            "cost_per_hour": {"type": "float"}
            }
        },
    "ec2_regions": {
        "keys": [
            "region"
            ],
        "columns": {
            "region": {"type": "str", "len": "64", "nulls": "NO"},
            "location": {"type": "str", "len": "64", "nulls": "NO"},
            "endpoint": {"type": "str", "len": "128", "nulls": "NO"}
            }
        },
    "silk_profile": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "name": {"type": "str", "len": "300", "nulls": "NO"},
            "start_time": {"type": "str", "nulls": "NO"},
            "end_time": {"type": "str", "nulls": "YES"},
            "time_taken": {"type": "float"},
            "file_path": {"type": "str", "len": "300", "nulls": "NO"},
            "line_num": {"type": "int"},
            "end_line_num": {"type": "int"},
            "func_name": {"type": "str", "len": "300", "nulls": "NO"},
            "exception_raised": {"type": "int"},
            "dynamic": {"type": "int"},
            "request_id": {"type": "str", "len": "36", "nulls": "YES"}
            }
        },
    "silk_profile_queries": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "profile_id": {"type": "int"},
            "sqlquery_id": {"type": "int"}
            }
        },
    "silk_request": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "str", "len": "36", "nulls": "NO"},
            "path": {"type": "str", "len": "190", "nulls": "NO"},
            "query_params": {"type": "str", "nulls": "NO"},
            "raw_body": {"type": "str", "nulls": "NO"},
            "body": {"type": "str", "nulls": "NO"},
            "method": {"type": "str", "len": "10", "nulls": "NO"},
            "start_time": {"type": "str", "nulls": "NO"},
            "view_name": {"type": "str", "len": "190", "nulls": "YES"},
            "end_time": {"type": "str", "nulls": "YES"},
            "time_taken": {"type": "float"},
            "encoded_headers": {"type": "str", "nulls": "NO"},
            "meta_time": {"type": "float"},
            "meta_num_queries": {"type": "int"},
            "meta_time_spent_queries": {"type": "float"},
            "pyprofile": {"type": "str", "nulls": "NO"},
            "num_sql_queries": {"type": "int"},
            "prof_file": {"type": "str", "len": "300", "nulls": "NO"}
            }
        },
    "silk_response": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "str", "len": "36", "nulls": "NO"},
            "status_code": {"type": "int"},
            "raw_body": {"type": "str", "nulls": "NO"},
            "body": {"type": "str", "nulls": "NO"},
            "encoded_headers": {"type": "str", "nulls": "NO"},
            "request_id": {"type": "str", "len": "36", "nulls": "NO"}
            }
        },
    "silk_sqlquery": {
        "keys": [
            "id"
            ],
        "columns": {
            "id": {"type": "int"},
            "query": {"type": "str", "nulls": "NO"},
            "start_time": {"type": "str", "nulls": "YES"},
            "end_time": {"type": "str", "nulls": "YES"},
            "time_taken": {"type": "float"},
            "traceback": {"type": "str", "nulls": "NO"},
            "request_id": {"type": "str", "len": "36", "nulls": "YES"}
            }
        },
    "view_active_resource_shortfall": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "request_cores": {"type": "int"},
            "active_cores": {"type": "int"},
            "shortfall_cores": {"type": "int"},
            "request_disk": {"type": "int"},
            "active_disk": {"type": "int"},
            "shortfall_disk": {"type": "int"},
            "request_ram": {"type": "int"},
            "active_ram": {"type": "int"},
            "shortfall_ram": {"type": "int"},
            "starting": {"type": "int"},
            "unregistered": {"type": "int"},
            "idle": {"type": "int"},
            "running": {"type": "int"}
            }
        },
    "view_available_resources": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_priority": {"type": "int"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "NO"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_container_hostname": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_other_submitters": {"type": "str", "len": "128", "nulls": "YES"},
            "vm_boot_volume": {"type": "str", "len": "64", "nulls": "YES"},
            "spot_price": {"type": "float"},
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "cacertificate": {"type": "str", "nulls": "YES"},
            "project_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "project_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "user_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "user_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "username": {"type": "str", "len": "20", "nulls": "NO"},
            "password": {"type": "str", "nulls": "NO"},
            "default_flavor": {"type": "str", "len": "97", "nulls": "YES"},
            "default_image": {"type": "str", "len": "64", "nulls": "YES"},
            "default_keep_alive": {"type": "int"},
            "default_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "default_network": {"type": "str", "len": "64", "nulls": "YES"},
            "default_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "VMs": {"type": "int"},
            "VMs_max": {"type": "int"},
            "cores_ctl": {"type": "int"},
            "cores_softmax": {"type": "int"},
            "cores_limit": {"type": "int"},
            "cores_max": {"type": "int"},
            "cores_used": {"type": "int"},
            "cores_foreign": {"type": "int"},
            "disk_used": {"type": "int"},
            "ram_ctl": {"type": "int"},
            "ram_max": {"type": "int"},
            "ram_limit": {"type": "float"},
            "ram_used": {"type": "int"},
            "ram_foreign": {"type": "float"},
            "swap_used": {"type": "int"},
            "flavor": {"type": "str", "len": "161", "nulls": "YES"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "NO"},
            "flavor_slots": {"type": "int"},
            "flavor_cores": {"type": "int"},
            "flavor_disk": {"type": "int"},
            "flavor_ram": {"type": "int"},
            "flavor_swap": {"type": "int"},
            "auth_type": {"type": "str", "len": "32", "nulls": "YES"},
            "app_credentials": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_secret": {"type": "str", "len": "128", "nulls": "YES"},
            "flavor_VMs": {"type": "int"},
            "flavor_starting": {"type": "int"},
            "flavor_unregistered": {"type": "int"},
            "flavor_idle": {"type": "int"},
            "flavor_running": {"type": "int"},
            "flavor_retiring": {"type": "int"},
            "flavor_error": {"type": "int"},
            "flavor_manual": {"type": "int"},
            "updater": {"type": "str", "nulls": "YES"},
            "worker_cert": {"type": "str", "nulls": "NO"},
            "worker_key": {"type": "str", "nulls": "NO"}
            }
        },
    "view_cloud_aliases": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "alias_name": {"type": "str", "len": "32", "nulls": "NO"},
            "clouds": {"type": "str", "nulls": "YES"}
            }
        },
    "view_cloud_status": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "app_credentials_expiry": {"type": "str", "len": "11", "nulls": "YES"},
            "VMs": {"type": "int"},
            "VMs_manual": {"type": "int"},
            "VMs_in_error": {"type": "int"},
            "VMs_starting": {"type": "int"},
            "VMs_retiring": {"type": "int"},
            "VMs_unregistered": {"type": "int"},
            "VMs_idle": {"type": "int"},
            "VMs_running": {"type": "int"},
            "cores_native": {"type": "int"},
            "ram_native": {"type": "float"},
            "slot_count": {"type": "int"},
            "slot_core_count": {"type": "int"},
            "slot_idle_core_count": {"type": "int"},
            "Foreign_VMs": {"type": "int"},
            "enabled": {"type": "int"},
            "communication_up": {"type": "int"},
            "communication_rt": {"type": "int"},
            "cores_ctl": {"type": "int"},
            "cores_limit": {"type": "int"},
            "VMs_quota": {"type": "int"},
            "VMs_native_foreign": {"type": "int"},
            "cores_quota": {"type": "int"},
            "cores_soft_quota": {"type": "int"},
            "cores_foreign": {"type": "int"},
            "cores_native_foreign": {"type": "int"},
            "ram_ctl": {"type": "int"},
            "ram_limit": {"type": "int"},
            "ram_quota": {"type": "int"},
            "ram_foreign": {"type": "float"},
            "ram_native_foreign": {"type": "float"}
            }
        },
    "view_cloud_status_flavor_slot_detail": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "flavor": {"type": "str", "len": "46", "nulls": "YES"},
            "slot_type": {"type": "int"},
            "slot_id": {"type": "str", "len": "380", "nulls": "YES"},
            "slot_count": {"type": "int"},
            "core_count": {"type": "int"}
            }
        },
    "view_cloud_status_flavor_slot_detail_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "flavor": {"type": "str", "len": "46", "nulls": "YES"},
            "slot_type": {"type": "int"},
            "slot_count": {"type": "int"},
            "core_count": {"type": "int"}
            }
        },
    "view_cloud_status_flavor_slot_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "flavor": {"type": "str", "len": "46", "nulls": "YES"},
            "busy": {"type": "int"},
            "idle": {"type": "int"},
            "idle_percent": {"type": "int"}
            }
        },
    "view_cloud_status_slot_detail": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "slot_type": {"type": "int"},
            "slot_id": {"type": "str", "len": "380", "nulls": "YES"},
            "slot_count": {"type": "int"},
            "core_count": {"type": "int"}
            }
        },
    "view_cloud_status_slot_detail_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "slot_type": {"type": "int"},
            "slot_count": {"type": "int"},
            "core_count": {"type": "int"}
            }
        },
    "view_cloud_status_slot_summary": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "busy": {"type": "int"},
            "idle": {"type": "int"},
            "idle_percent": {"type": "int"}
            }
        },
    "view_clouds": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "enabled": {"type": "int"},
            "cloud_priority": {"type": "int"},
            "spot_price": {"type": "float"},
            "vm_boot_volume": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_flavor": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_image": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_keep_alive": {"type": "int"},
            "vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_network": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "userid": {"type": "str", "len": "64", "nulls": "YES"},
            "auth_type": {"type": "str", "len": "32", "nulls": "YES"},
            "app_credentials": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_secret": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_expiry": {"type": "int"},
            "cascading_vm_flavor": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_image": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_keep_alive": {"type": "int"},
            "cascading_vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_network": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "project_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "project_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "user_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "user_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "username": {"type": "str", "len": "20", "nulls": "NO"},
            "password": {"type": "str", "nulls": "NO"},
            "cacertificate": {"type": "str", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "NO"},
            "ec2_owner_id": {"type": "str", "len": "32", "nulls": "YES"},
            "cores_ctl": {"type": "int"},
            "cores_softmax": {"type": "int"},
            "cores_max": {"type": "int"},
            "cores_used": {"type": "int"},
            "cores_foreign": {"type": "int"},
            "cores_native": {"type": "int"},
            "ram_ctl": {"type": "int"},
            "ram_max": {"type": "int"},
            "ram_used": {"type": "int"},
            "ram_foreign": {"type": "int"},
            "ram_native": {"type": "int"},
            "instances_max": {"type": "int"},
            "instances_used": {"type": "int"},
            "floating_ips_max": {"type": "int"},
            "floating_ips_used": {"type": "int"},
            "security_groups_max": {"type": "int"},
            "security_groups_used": {"type": "int"},
            "server_groups_max": {"type": "int"},
            "server_groups_used": {"type": "int"},
            "image_meta_max": {"type": "int"},
            "keypairs_max": {"type": "int"},
            "personality_max": {"type": "int"},
            "personality_size_max": {"type": "int"},
            "security_group_rules_max": {"type": "int"},
            "server_group_members_max": {"type": "int"},
            "server_meta_max": {"type": "int"},
            "cores_idle": {"type": "int"},
            "ram_idle": {"type": "int"}
            }
        },
    "view_clouds_with_metadata_info": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "enabled": {"type": "int"},
            "cloud_priority": {"type": "int"},
            "spot_price": {"type": "float"},
            "vm_boot_volume": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_flavor": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_image": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_keep_alive": {"type": "int"},
            "vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_network": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "userid": {"type": "str", "len": "64", "nulls": "YES"},
            "auth_type": {"type": "str", "len": "32", "nulls": "YES"},
            "app_credentials": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_secret": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_expiry": {"type": "int"},
            "cascading_vm_flavor": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_image": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_keep_alive": {"type": "int"},
            "cascading_vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_network": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "project_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "project_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "user_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "user_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "username": {"type": "str", "len": "20", "nulls": "NO"},
            "password": {"type": "str", "nulls": "NO"},
            "cacertificate": {"type": "str", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "NO"},
            "ec2_owner_id": {"type": "str", "len": "32", "nulls": "YES"},
            "cores_ctl": {"type": "int"},
            "cores_softmax": {"type": "int"},
            "cores_max": {"type": "int"},
            "cores_used": {"type": "int"},
            "cores_foreign": {"type": "int"},
            "cores_native": {"type": "int"},
            "ram_ctl": {"type": "int"},
            "ram_max": {"type": "int"},
            "ram_used": {"type": "int"},
            "ram_foreign": {"type": "int"},
            "ram_native": {"type": "int"},
            "instances_max": {"type": "int"},
            "instances_used": {"type": "int"},
            "floating_ips_max": {"type": "int"},
            "floating_ips_used": {"type": "int"},
            "security_groups_max": {"type": "int"},
            "security_groups_used": {"type": "int"},
            "server_groups_max": {"type": "int"},
            "server_groups_used": {"type": "int"},
            "image_meta_max": {"type": "int"},
            "keypairs_max": {"type": "int"},
            "personality_max": {"type": "int"},
            "personality_size_max": {"type": "int"},
            "security_group_rules_max": {"type": "int"},
            "server_group_members_max": {"type": "int"},
            "server_meta_max": {"type": "int"},
            "cores_idle": {"type": "int"},
            "ram_idle": {"type": "int"},
            "metadata_name": {"type": "str", "len": "64", "nulls": "YES"},
            "metadata_enabled": {"type": "int"},
            "metadata_priority": {"type": "int"},
            "metadata_mime_type": {"type": "str", "len": "128", "nulls": "YES"}
            }
        },
    "view_clouds_with_metadata_names": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "enabled": {"type": "int"},
            "cloud_priority": {"type": "int"},
            "spot_price": {"type": "float"},
            "vm_boot_volume": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_flavor": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_image": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_keep_alive": {"type": "int"},
            "vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_network": {"type": "str", "len": "64", "nulls": "NO"},
            "vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "userid": {"type": "str", "len": "64", "nulls": "YES"},
            "auth_type": {"type": "str", "len": "32", "nulls": "YES"},
            "app_credentials": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_secret": {"type": "str", "len": "128", "nulls": "YES"},
            "app_credentials_expiry": {"type": "int"},
            "cascading_vm_flavor": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_image": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_keep_alive": {"type": "int"},
            "cascading_vm_keyname": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_network": {"type": "str", "len": "64", "nulls": "YES"},
            "cascading_vm_security_groups": {"type": "str", "len": "128", "nulls": "YES"},
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "project_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "project_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "user_domain_name": {"type": "str", "len": "20", "nulls": "NO"},
            "user_domain_id": {"type": "str", "len": "64", "nulls": "NO"},
            "username": {"type": "str", "len": "20", "nulls": "NO"},
            "password": {"type": "str", "nulls": "NO"},
            "cacertificate": {"type": "str", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "NO"},
            "ec2_owner_id": {"type": "str", "len": "32", "nulls": "YES"},
            "cores_ctl": {"type": "int"},
            "cores_softmax": {"type": "int"},
            "cores_max": {"type": "int"},
            "cores_used": {"type": "int"},
            "cores_foreign": {"type": "int"},
            "cores_native": {"type": "int"},
            "ram_ctl": {"type": "int"},
            "ram_max": {"type": "int"},
            "ram_used": {"type": "int"},
            "ram_foreign": {"type": "int"},
            "ram_native": {"type": "int"},
            "instances_max": {"type": "int"},
            "instances_used": {"type": "int"},
            "floating_ips_max": {"type": "int"},
            "floating_ips_used": {"type": "int"},
            "security_groups_max": {"type": "int"},
            "security_groups_used": {"type": "int"},
            "server_groups_max": {"type": "int"},
            "server_groups_used": {"type": "int"},
            "image_meta_max": {"type": "int"},
            "keypairs_max": {"type": "int"},
            "personality_max": {"type": "int"},
            "personality_size_max": {"type": "int"},
            "security_group_rules_max": {"type": "int"},
            "server_group_members_max": {"type": "int"},
            "server_meta_max": {"type": "int"},
            "cores_idle": {"type": "int"},
            "ram_idle": {"type": "int"},
            "flavor_exclusions": {"type": "str", "nulls": "YES"},
            "flavor_names": {"type": "str", "nulls": "YES"},
            "group_exclusions": {"type": "str", "nulls": "YES"},
            "metadata_names": {"type": "str", "nulls": "YES"}
            }
        },
    "view_condor_host": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "hostname": {"type": "str", "len": "128", "nulls": "NO"},
            "primary_slots": {"type": "int"},
            "dynamic_slots": {"type": "int"},
            "retire": {"type": "int"},
            "terminate": {"type": "int"},
            "machine": {"type": "str", "len": "256", "nulls": "YES"},
            "updater": {"type": "str", "len": "128", "nulls": "YES"},
            "retire_time": {"type": "int"}
            }
        },
    "view_condor_jobs_group_defaults_applied": {
        "keys": [
            ],
        "columns": {
            "global_job_id": {"type": "str", "len": "128", "nulls": "NO"},
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "job_status": {"type": "int"},
            "request_cpus": {"type": "int"},
            "request_disk": {"type": "int"},
            "request_ram": {"type": "int"},
            "request_swap": {"type": "int"},
            "requirements": {"type": "str", "len": "512", "nulls": "YES"},
            "job_priority": {"type": "int"},
            "cluster_id": {"type": "int"},
            "proc_id": {"type": "int"},
            "user": {"type": "str", "len": "512", "nulls": "YES"},
            "image": {"type": "str", "nulls": "YES"},
            "instance_type": {"type": "str", "len": "512", "nulls": "YES"},
            "network": {"type": "str", "len": "512", "nulls": "YES"},
            "keep_alive": {"type": "str", "len": "512", "nulls": "YES"},
            "max_price": {"type": "str", "len": "512", "nulls": "YES"},
            "user_data": {"type": "str", "len": "512", "nulls": "YES"},
            "job_per_core": {"type": "int"},
            "entered_current_status": {"type": "int"},
            "q_date": {"type": "int"},
            "hold_job_reason": {"type": "str", "len": "64", "nulls": "YES"},
            "held_reason": {"type": "str", "len": "128", "nulls": "YES"},
            "js_idle": {"type": "int"},
            "js_running": {"type": "int"},
            "js_completed": {"type": "int"},
            "js_held": {"type": "int"},
            "js_other": {"type": "int"}
            }
        },
    "view_ec2_images": {
        "keys": [
            ],
        "columns": {
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "id": {"type": "str", "len": "128", "nulls": "NO"},
            "borrower_id": {"type": "str", "len": "32", "nulls": "NO"},
            "owner_id": {"type": "str", "len": "32", "nulls": "YES"},
            "owner_alias": {"type": "str", "len": "64", "nulls": "YES"},
            "disk_format": {"type": "str", "len": "128", "nulls": "YES"},
            "size": {"type": "int"},
            "image_location": {"type": "str", "len": "512", "nulls": "YES"},
            "visibility": {"type": "str", "len": "128", "nulls": "YES"},
            "name": {"type": "str", "len": "256", "nulls": "YES"},
            "description": {"type": "str", "len": "256", "nulls": "YES"},
            "last_updated": {"type": "int"},
            "lower_location": {"type": "str", "len": "512", "nulls": "YES"},
            "opsys": {"type": "str", "len": "8", "nulls": "YES"},
            "arch": {"type": "str", "len": "5", "nulls": "YES"}
            }
        },
    "view_ec2_instance_types": {
        "keys": [
            ],
        "columns": {
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "instance_type": {"type": "str", "len": "32", "nulls": "NO"},
            "operating_system": {"type": "str", "len": "32", "nulls": "NO"},
            "instance_family": {"type": "str", "len": "32", "nulls": "YES"},
            "processor": {"type": "str", "len": "64", "nulls": "YES"},
            "storage": {"type": "str", "len": "32", "nulls": "YES"},
            "cores": {"type": "int"},
            "memory": {"type": "float"},
            "cost_per_hour": {"type": "float"},
            "memory_per_core": {"type": "float"},
            "processor_manufacturer": {"type": "str", "len": "64", "nulls": "YES"}
            }
        },
    "view_foreign_flavors": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "authurl": {"type": "str", "len": "128", "nulls": "NO"},
            "region": {"type": "str", "len": "32", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "YES"},
            "count": {"type": "int"},
            "name": {"type": "str", "len": "128", "nulls": "YES"},
            "cores": {"type": "int"},
            "ram": {"type": "float"}
            }
        },
    "view_foreign_resources": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "count": {"type": "int"},
            "cores": {"type": "int"},
            "ram": {"type": "float"}
            }
        },
    "view_groups_of_idle_jobs": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "instance_type": {"type": "str", "len": "512", "nulls": "YES"},
            "requirements": {"type": "str", "len": "512", "nulls": "YES"},
            "job_priority": {"type": "int"},
            "user": {"type": "str", "len": "512", "nulls": "YES"},
            "image": {"type": "str", "nulls": "YES"},
            "network": {"type": "str", "len": "512", "nulls": "YES"},
            "keep_alive": {"type": "str", "len": "512", "nulls": "YES"},
            "max_price": {"type": "str", "len": "512", "nulls": "YES"},
            "user_data": {"type": "str", "len": "512", "nulls": "YES"},
            "job_per_core": {"type": "int"},
            "request_cpus_min": {"type": "int"},
            "request_cpus_max": {"type": "int"},
            "request_cpus_total": {"type": "int"},
            "request_disk_min": {"type": "int"},
            "request_disk_max": {"type": "int"},
            "request_disk_total": {"type": "int"},
            "request_ram_min": {"type": "int"},
            "request_ram_max": {"type": "int"},
            "request_ram_total": {"type": "int"},
            "request_swap_min": {"type": "int"},
            "request_swap_max": {"type": "int"},
            "request_swap_total": {"type": "int"},
            "queue_date": {"type": "int"},
            "idle": {"type": "int"},
            "running": {"type": "int"},
            "completed": {"type": "int"},
            "held": {"type": "int"},
            "other": {"type": "int"},
            "flavors": {"type": "str", "nulls": "YES"}
            }
        },
    "view_groups_with_metadata_info": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_container_hostname": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_other_submitters": {"type": "str", "len": "128", "nulls": "YES"},
            "metadata_name": {"type": "str", "len": "64", "nulls": "YES"},
            "metadata_enabled": {"type": "int"},
            "metadata_priority": {"type": "int"},
            "metadata_mime_type": {"type": "str", "len": "128", "nulls": "YES"}
            }
        },
    "view_groups_with_metadata_names": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_container_hostname": {"type": "str", "len": "128", "nulls": "YES"},
            "htcondor_other_submitters": {"type": "str", "len": "128", "nulls": "YES"},
            "metadata_names": {"type": "str", "nulls": "YES"}
            }
        },
    "view_idle_vms": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "come_alive": {"type": "str", "len": "128", "nulls": "YES"},
            "job_alive": {"type": "str", "len": "128", "nulls": "YES"},
            "error_delay": {"type": "str", "len": "128", "nulls": "YES"},
            "keep_alive": {"type": "int"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "hostname": {"type": "str", "len": "128", "nulls": "NO"},
            "primary_slots": {"type": "int"},
            "dynamic_slots": {"type": "int"},
            "retire": {"type": "int"},
            "terminate": {"type": "int"},
            "poller_status": {"type": "str", "len": "12", "nulls": "YES"},
            "age": {"type": "int"}
            }
        },
    "view_job_status": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "Jobs": {"type": "int"},
            "Idle": {"type": "int"},
            "Running": {"type": "int"},
            "Completed": {"type": "int"},
            "Held": {"type": "int"},
            "Other": {"type": "int"},
            "foreign": {"type": "int"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "state": {"type": "str", "len": "4", "nulls": "YES"},
            "plotable_state": {"type": "str", "len": "1", "nulls": "YES"},
            "error_message": {"type": "str", "len": "512", "nulls": "NO"},
            "condor_days_left": {"type": "int"},
            "worker_days_left": {"type": "int"}
            }
        },
    "view_job_status_by_target_alias": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "Jobs": {"type": "int"},
            "Idle": {"type": "int"},
            "Running": {"type": "int"},
            "Completed": {"type": "int"},
            "Held": {"type": "int"},
            "Other": {"type": "int"},
            "foreign": {"type": "int"},
            "htcondor_fqdn": {"type": "str", "len": "128", "nulls": "YES"},
            "state": {"type": "str", "len": "4", "nulls": "YES"},
            "plotable_state": {"type": "str", "len": "1", "nulls": "YES"},
            "error_message": {"type": "str", "len": "512", "nulls": "NO"},
            "condor_days_left": {"type": "int"},
            "worker_days_left": {"type": "int"}
            }
        },
    "view_metadata_collation": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "type": {"type": "str", "len": "5", "nulls": "NO"},
            "priority": {"type": "int"},
            "metadata_name": {"type": "str", "len": "64", "nulls": "YES"},
            "mime_type": {"type": "str", "len": "128", "nulls": "YES"}
            }
        },
    "view_metadata_collation_json": {
        "keys": [
            ],
        "columns": {
            "group_metadata": {"type": "str", "nulls": "YES"}
            }
        },
    "view_resource_contention": {
        "keys": [
            ],
        "columns": {
            "authurl": {"type": "str", "len": "128", "nulls": "YES"},
            "VMs": {"type": "int"},
            "starting": {"type": "int"},
            "unregistered": {"type": "int"},
            "idle": {"type": "int"},
            "running": {"type": "int"},
            "retiring": {"type": "int"},
            "manual": {"type": "int"},
            "error": {"type": "int"}
            }
        },
    "view_service_status": {
        "keys": [
            ],
        "columns": {
            "alias": {"type": "str", "len": "16", "nulls": "YES"},
            "state": {"type": "str", "len": "4", "nulls": "YES"},
            "plotable_state": {"type": "str", "len": "1", "nulls": "YES"},
            "error_message": {"type": "str", "len": "512", "nulls": "YES"}
            }
        },
    "view_total_used_resources": {
        "keys": [
            ],
        "columns": {
            "authurl": {"type": "str", "len": "128", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "YES"},
            "project": {"type": "str", "len": "128", "nulls": "YES"},
            "VMs": {"type": "int"},
            "cores": {"type": "int"},
            "disk": {"type": "int"},
            "ram": {"type": "int"},
            "swap": {"type": "int"}
            }
        },
    "view_user_groups": {
        "keys": [
            ],
        "columns": {
            "username": {"type": "str", "len": "32", "nulls": "NO"},
            "cert_cn": {"type": "str", "len": "128", "nulls": "YES"},
            "password": {"type": "str", "len": "128", "nulls": "NO"},
            "is_superuser": {"type": "int"},
            "join_date": {"type": "str", "nulls": "NO"},
            "flag_global_status": {"type": "int"},
            "flag_jobs_by_target_alias": {"type": "int"},
            "flag_show_foreign_global_vms": {"type": "int"},
            "flag_show_slot_detail": {"type": "int"},
            "flag_show_slot_flavors": {"type": "int"},
            "status_refresh_interval": {"type": "int"},
            "default_group": {"type": "str", "len": "32", "nulls": "YES"},
            "user_groups": {"type": "str", "nulls": "YES"},
            "available_groups": {"type": "str", "nulls": "YES"}
            }
        },
    "view_user_groups_available": {
        "keys": [
            ],
        "columns": {
            "username": {"type": "str", "len": "32", "nulls": "NO"},
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "available": {"type": "str", "len": "32", "nulls": "YES"}
            }
        },
    "view_vm_kill_retire_over_quota": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "YES"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "cores": {"type": "int"},
            "cores_ctl": {"type": "int"},
            "cores_softmax": {"type": "int"},
            "cores_max": {"type": "int"},
            "cores_native": {"type": "int"},
            "cores_foreign": {"type": "int"},
            "ram": {"type": "float"},
            "ram_ctl": {"type": "int"},
            "ram_max": {"type": "int"},
            "ram_native": {"type": "float"},
            "ram_foreign": {"type": "float"}
            }
        },
    "view_vm_kill_retire_priority_age": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "YES"},
            "machine": {"type": "str", "len": "256", "nulls": "YES"},
            "killed": {"type": "int"},
            "retired": {"type": "int"},
            "priority": {"type": "int"},
            "flavor_cores": {"type": "int"},
            "flavor_ram": {"type": "int"}
            }
        },
    "view_vm_kill_retire_priority_idle": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "YES"},
            "machine": {"type": "str", "len": "256", "nulls": "YES"},
            "killed": {"type": "int"},
            "retired": {"type": "int"},
            "priority": {"type": "int"},
            "flavor_cores": {"type": "int"},
            "flavor_ram": {"type": "int"}
            }
        },
    "view_vms": {
        "keys": [
            ],
        "columns": {
            "group_name": {"type": "str", "len": "32", "nulls": "NO"},
            "cloud_name": {"type": "str", "len": "32", "nulls": "NO"},
            "target_alias": {"type": "str", "len": "32", "nulls": "YES"},
            "region": {"type": "str", "len": "32", "nulls": "YES"},
            "vmid": {"type": "str", "len": "128", "nulls": "NO"},
            "spot_instance": {"type": "int"},
            "instance_id": {"type": "str", "len": "64", "nulls": "YES"},
            "cloud_type": {"type": "str", "len": "64", "nulls": "YES"},
            "vm_ips": {"type": "str", "len": "128", "nulls": "YES"},
            "vm_floating_ips": {"type": "str", "len": "128", "nulls": "YES"},
            "auth_url": {"type": "str", "len": "128", "nulls": "NO"},
            "project": {"type": "str", "len": "128", "nulls": "NO"},
            "hostname": {"type": "str", "len": "128", "nulls": "NO"},
            "keep_alive": {"type": "int"},
            "start_time": {"type": "int"},
            "status": {"type": "str", "len": "32", "nulls": "YES"},
            "flavor_id": {"type": "str", "len": "128", "nulls": "YES"},
            "image_id": {"type": "str", "len": "128", "nulls": "YES"},
            "task": {"type": "str", "len": "32", "nulls": "YES"},
            "power_status": {"type": "int"},
            "manual_control": {"type": "int"},
            "htcondor_startd_errors": {"type": "str", "len": "256", "nulls": "YES"},
            "htcondor_startd_time": {"type": "int"},
            "htcondor_partitionable_slots": {"type": "int"},
            "htcondor_dynamic_slots": {"type": "int"},
            "htcondor_slots_timestamp": {"type": "int"},
            "retire": {"type": "int"},
            "retire_time": {"type": "int"},
            "terminate": {"type": "int"},
            "terminate_time": {"type": "int"},
            "status_changed_time": {"type": "int"},
            "last_updated": {"type": "int"},
            "updater": {"type": "str", "len": "128", "nulls": "YES"},
            "flavor_name": {"type": "str", "len": "128", "nulls": "YES"},
            "condor_slots": {"type": "int"},
            "condor_slots_used": {"type": "int"},
            "machine": {"type": "str", "len": "256", "nulls": "YES"},
            "my_current_time": {"type": "int"},
            "entered_current_state": {"type": "int"},
            "idle_time": {"type": "int"},
            "foreign_vm": {"type": "int"},
            "cores": {"type": "int"},
            "disk": {"type": "int"},
            "ram": {"type": "int"},
            "swap": {"type": "int"},
            "poller_status": {"type": "str", "len": "12", "nulls": "YES"},
            "age": {"type": "int"}
            }
        }
    }
