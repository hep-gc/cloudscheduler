Unknown data type for column: slots_percent	double	YES		NULL	
m sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
  metadata = MetaData()

archived_condor_jobs = Table('archived_condor_jobs', metadata,
  Column('global_job_id', String(128), primary_key=True),
  Column('group_name', String(128)),
  Column('target_clouds', String),
  Column('cloud_name', String),
  Column('job_status', Integer),
  Column('request_cpus', Integer),
  Column('request_ram', Integer),
  Column('request_disk', Integer),
  Column('request_swap', Integer),
  Column('request_scratch', Integer),
  Column('requirements', String(512)),
  Column('job_priority', Integer),
  Column('cluster_id', Integer),
  Column('proc_id', Integer),
  Column('user', String(512)),
  Column('image', String),
  Column('instance_type', String(512)),
  Column('network', String(512)),
  Column('keep_alive', String(512)),
  Column('max_price', String(512)),
  Column('user_data', String(512)),
  Column('job_per_core', Integer),
  Column('entered_current_status', Integer),
  Column('q_date', Integer),
  Column('hold_job', Integer)
  )

archived_condor_machines = Table('archived_condor_machines', metadata,
  Column('name', String(128), primary_key=True),
  Column('machine', String(256)),
  Column('condor_host', String(64)),
  Column('hostname', String(32)),
  Column('flavor', String(32)),
  Column('job_id', String(128)),
  Column('global_job_id', String(128)),
  Column('address', String(512)),
  Column('state', String(128)),
  Column('activity', String(128)),
  Column('vm_type', String(128)),
  Column('my_current_time', Integer),
  Column('entered_current_state', Integer),
  Column('start', String(128)),
  Column('remote_owner', String(128)),
  Column('slot_type', String(128)),
  Column('total_slots', Integer),
  Column('condor_off', Integer),
  Column('condor_advertise', Integer)
  )

auth_group = Table('auth_group', metadata,
  Column('id', Integer, primary_key=True),
  Column('name', String(80))
  )

auth_group_permissions = Table('auth_group_permissions', metadata,
  Column('id', Integer, primary_key=True),
  Column('group_id', Integer),
  Column('permission_id', Integer)
  )

auth_permission = Table('auth_permission', metadata,
  Column('id', Integer, primary_key=True),
  Column('name', String(255)),
  Column('content_type_id', Integer),
  Column('codename', String(100))
  )

auth_user = Table('auth_user', metadata,
  Column('id', Integer, primary_key=True),
  Column('password', String(128)),
  Column('last_login', Integer),
  Column('is_superuser', Integer),
  Column('username', String(150)),
  Column('first_name', String(30)),
  Column('last_name', String(30)),
  Column('email', String(254)),
  Column('is_staff', Integer),
  Column('is_active', Integer),
  Column('date_joined', Integer),
  Column('csv2_user', String(64))
  )

auth_user_groups = Table('auth_user_groups', metadata,
  Column('id', Integer, primary_key=True),
  Column('user_id', Integer),
  Column('group_id', Integer)
  )

auth_user_user_permissions = Table('auth_user_user_permissions', metadata,
  Column('id', Integer, primary_key=True),
  Column('user_id', Integer),
  Column('permission_id', Integer)
  )

cloud_defaults = Table('cloud_defaults', metadata,
  Column('auth_url', String(128), primary_key=True),
  Column('project', String(128), primary_key=True),
  Column('image', String),
  Column('flavor', String),
  Column('network', String)
  )

cloud_flavors = Table('cloud_flavors', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('cloud_name', String(128), primary_key=True),
  Column('id', String(128), primary_key=True),
  Column('ram', Integer),
  Column('cores', Integer),
  Column('swap', Integer),
  Column('disk', Integer),
  Column('ephemeral_disk', Integer),
  Column('is_public', Integer),
  Column('last_updated', Integer),
  Column('name', String(128))
  )

cloud_images = Table('cloud_images', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('cloud_name', String(128), primary_key=True),
  Column('id', String(128), primary_key=True),
  Column('container_format', String(128)),
  Column('disk_format', String(128)),
  Column('name', String(256)),
  Column('size', Integer),
  Column('visibility', String(128)),
  Column('min_disk', Integer),
  Column('min_ram', Integer),
  Column('last_updated', Integer)
  )

cloud_limits = Table('cloud_limits', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('cloud_name', String(128), primary_key=True),
  Column('server_meta_max', Integer),
  Column('instances_max', Integer),
  Column('personality_max', Integer),
  Column('image_meta_max', Integer),
  Column('personality_size_max', Integer),
  Column('ram_max', Integer),
  Column('server_groups_max', Integer),
  Column('security_group_rules_max', Integer),
  Column('keypairs_max', Integer),
  Column('security_groups_max', Integer),
  Column('server_group_members_max', Integer),
  Column('floating_ips_max', Integer),
  Column('cores_max', Integer),
  Column('server_groups_used', Integer),
  Column('instances_used', Integer),
  Column('ram_used', Integer),
  Column('security_groups_used', Integer),
  Column('floating_ips_used', Integer),
  Column('cores_used', Integer),
  Column('last_updated', Integer)
  )

cloud_networks = Table('cloud_networks', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('cloud_name', String(128), primary_key=True),
  Column('id', String(128), primary_key=True),
  Column('name', String(256)),
  Column('subnets', String(256)),
  Column('tenant_id', String(128)),
  Column('external_route', Integer),
  Column('shared', Integer),
  Column('last_updated', Integer)
  )

condor_jobs = Table('condor_jobs', metadata,
  Column('global_job_id', String(128), primary_key=True),
  Column('group_name', String(128)),
  Column('target_clouds', String),
  Column('cloud_name', String),
  Column('job_status', Integer),
  Column('request_cpus', Integer),
  Column('request_ram', Integer),
  Column('request_disk', Integer),
  Column('request_swap', Integer),
  Column('request_scratch', Integer),
  Column('requirements', String(512)),
  Column('job_priority', Integer),
  Column('cluster_id', Integer),
  Column('proc_id', Integer),
  Column('user', String(512)),
  Column('image', String),
  Column('instance_type', String(512)),
  Column('network', String(512)),
  Column('keep_alive', String(512)),
  Column('max_price', String(512)),
  Column('user_data', String(512)),
  Column('job_per_core', Integer),
  Column('entered_current_status', Integer),
  Column('q_date', Integer),
  Column('hold_job', Integer)
  )

condor_machines = Table('condor_machines', metadata,
  Column('name', String(128), primary_key=True),
  Column('machine', String(256)),
  Column('group_name', String(128)),
  Column('condor_host', String(64)),
  Column('hostname', String(32)),
  Column('flavor', String(32)),
  Column('job_id', String(128)),
  Column('global_job_id', String(128)),
  Column('address', String(512)),
  Column('state', String(128)),
  Column('activity', String(128)),
  Column('vm_type', String(128)),
  Column('my_current_time', Integer),
  Column('entered_current_state', Integer),
  Column('start', String(128)),
  Column('remote_owner', String(128)),
  Column('slot_type', String(128)),
  Column('total_slots', Integer),
  Column('condor_off', Integer),
  Column('condor_advertise', Integer)
  )

csv2_attribute_mapping = Table('csv2_attribute_mapping', metadata,
  Column('csv2', String(64), primary_key=True),
  Column('os_limits', String(64)),
  Column('os_flavors', String(64)),
  Column('os_images', String(64)),
  Column('os_networks', String(64)),
  Column('os_vms', String(64)),
  Column('condor', String(64))
  )

csv2_cloud_types = Table('csv2_cloud_types', metadata,
  Column('cloud_type', String(50), primary_key=True)
  )

csv2_config = Table('csv2_config', metadata,
  Column('config_name', String(64), primary_key=True),
  Column('yaml', String)
  )

csv2_configuration = Table('csv2_configuration', metadata,
  Column('process_name', String(128)),
  Column('yaml_parameters', String)
  )

csv2_group_defaults = Table('csv2_group_defaults', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('job_cpus', Integer),
  Column('job_ram', Integer),
  Column('job_disk', Integer),
  Column('job_scratch', Integer),
  Column('job_swap', Integer)
  )

csv2_group_metadata = Table('csv2_group_metadata', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('metadata_name', String(128), primary_key=True),
  Column('enabled', Integer),
  Column('priority', Integer),
  Column('metadata', String),
  Column('mime_type', String(128))
  )

csv2_group_resource_metadata = Table('csv2_group_resource_metadata', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('cloud_name', String(128), primary_key=True),
  Column('metadata_name', String(128), primary_key=True),
  Column('enabled', Integer),
  Column('priority', Integer),
  Column('metadata', String),
  Column('mime_type', String(128))
  )

csv2_group_resources = Table('csv2_group_resources', metadata,
  Column('group_name', String(32), primary_key=True),
  Column('cloud_name', String(20), primary_key=True),
  Column('authurl', String(128)),
  Column('project', String(128)),
  Column('username', String(20)),
  Column('password', String),
  Column('keyname', String(20)),
  Column('cacertificate', String),
  Column('region', String(20)),
  Column('user_domain_name', String(20)),
  Column('project_domain_name', String(20)),
  Column('cloud_type', String(64)),
  Column('server_meta_ctl', Integer),
  Column('instances_ctl', Integer),
  Column('personality_ctl', Integer),
  Column('image_meta_ctl', Integer),
  Column('personality_size_ctl', Integer),
  Column('ram_ctl', Integer),
  Column('server_groups_ctl', Integer),
  Column('security_group_rules_ctl', Integer),
  Column('keypairs_ctl', Integer),
  Column('security_groups_ctl', Integer),
  Column('server_group_members_ctl', Integer),
  Column('floating_ips_ctl', Integer),
  Column('cores_ctl', Integer)
  )

csv2_groups = Table('csv2_groups', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('condor_central_manager', String)
  )

csv2_mime_types = Table('csv2_mime_types', metadata,
  Column('mime_type', String(32), primary_key=True)
  )

csv2_poll_times = Table('csv2_poll_times', metadata,
  Column('process_id', String(64), primary_key=True),
  Column('last_poll', Integer)
  )

csv2_user = Table('csv2_user', metadata,
  Column('username', String(32), primary_key=True),
  Column('cert_cn', String(128)),
  Column('password', String(128)),
  Column('is_superuser', Integer),
  Column('join_date', Integer),
  Column('active_group', String(128))
  )

csv2_user_groups = Table('csv2_user_groups', metadata,
  Column('username', String(128), primary_key=True),
  Column('group_name', String(128), primary_key=True)
  )

csv2_vm_status_codes = Table('csv2_vm_status_codes', metadata,
  Column('power_status', Integer),
  Column('vm_status', String(16)),
  Column('condor_off', Integer),
  Column('manual_control', Integer),
  Column('status', String(16))
  )

csv2_vms = Table('csv2_vms', metadata,
  Column('group_name', String(128), primary_key=True),
  Column('cloud_name', String(128), primary_key=True),
  Column('vmid', String(128), primary_key=True),
  Column('auth_url', String(128)),
  Column('project', String(128)),
  Column('hostname', String(128)),
  Column('status', String(16)),
  Column('flavor_id', String(128)),
  Column('task', String(32)),
  Column('power_status', Integer),
  Column('manual_control', Integer),
  Column('terminate', Integer),
  Column('terminate_time', Integer),
  Column('status_changed_time', Integer),
  Column('last_updated', Integer)
  )

django_admin_log = Table('django_admin_log', metadata,
  Column('id', Integer, primary_key=True),
  Column('action_time', Integer),
  Column('object_id', String),
  Column('object_repr', String(200)),
  Column('action_flag', Integer),
  Column('change_message', String),
  Column('content_type_id', Integer),
  Column('user_id', Integer)
  )

django_content_type = Table('django_content_type', metadata,
  Column('id', Integer, primary_key=True),
  Column('app_label', String(100)),
  Column('model', String(100))
  )

django_migrations = Table('django_migrations', metadata,
  Column('id', Integer, primary_key=True),
  Column('app', String(255)),
  Column('name', String(255)),
  Column('applied', Integer)
  )

django_session = Table('django_session', metadata,
  Column('session_key', String(40), primary_key=True),
  Column('session_data', String),
  Column('expire_date', Integer)
  )

view_available_resources = Table('view_available_resources', metadata,
  Column('group_name', String(32)),
  Column('cloud_name', String(20)),
  Column('authurl', String(128)),
  Column('project', String(128)),
  Column('username', String(20)),
  Column('password', String),
  Column('keyname', String(20)),
  Column('cacertificate', String),
  Column('region', String(20)),
  Column('user_domain_name', String(20)),
  Column('project_domain_name', String(20)),
  Column('cloud_type', String(64)),
  Column('cores', Integer),
  Column('ram', Integer),
  Column('flavor_name', String(128)),
  Column('flavor_id', String(128)),
  Column('flavor_instance_type', String(149)),
  Column('flavor_cores', Integer),
  Column('flavor_ram', Integer),
  Column('flavor_disk', Integer),
  Column('flavor_scratch', Integer),
  Column('flavor_swap', Integer),
  Column('flavor_priority', Integer),
  Column('flavor', String(182)),
  Column('flavor_slots', Integer),
  Column('VMs_up', Integer),
  Column('VMs_down', Integer)
  )

view_available_resources_raw = Table('view_available_resources_raw', metadata,
  Column('group_name', String(32)),
  Column('cloud_name', String(20)),
  Column('authurl', String(128)),
  Column('project', String(128)),
  Column('username', String(20)),
  Column('password', String),
  Column('keyname', String(20)),
  Column('cacertificate', String),
  Column('region', String(20)),
  Column('user_domain_name', String(20)),
  Column('project_domain_name', String(20)),
  Column('cloud_type', String(64)),
  Column('cores', Integer),
  Column('ram', Integer),
  Column('flavor_name', String(128)),
  Column('flavor_id', String(128)),
  Column('flavor_instance_type', String(149)),
  Column('flavor_cores', Integer),
  Column('flavor_ram', Integer),
  Column('flavor_disk', Integer),
  Column('flavor_scratch', Integer),
  Column('flavor_swap', Integer),
  Column('flavor_priority', Integer),
  Column('flavor', String(182))
  )

view_claimed_slot_counts = Table('view_claimed_slot_counts', metadata,
  Column('hostname', String(32)),
  Column('claimed_slots', Integer)
  )

