from django.conf import settings
config = settings.CSV2_CONFIG

from django.views.decorators.csrf import requires_csrf_token

from cloudscheduler.lib.select_ec2 import \
    select_ec2_images, \
    select_ec2_instance_types

from cloudscheduler.lib.view_utils import \
    lno, \
    qt, \
    qt_filter_get, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields

from cloudscheduler.lib.schema import *

from cloudscheduler.lib.log_tools import get_frame_info

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: EV - error code identifier.

#-------------------------------------------------------------------------------

@silkp(name="EC2 Images List")
@requires_csrf_token
def images(request):

    keys = {
        'auto_active_group': True,
        # Named argument formats (anything else is a string).
        'format': {
            'cloud_name':                                                   'lowerdash',

            'architectures':                                                ('view_ec2_images', 'arch', True, True),
            'like':                                                         'lowernull',
            'not_like':                                                     'lowernull',
            'operating_systems':                                            ('view_ec2_images', 'opsys', True, True),
            'owner_aliases':                                                'lowernull',
            'owner_ids':                                                    'lowernull',

            'csrfmiddlewaretoken':                                          'ignore',
            'group':                                                        'ignore',
            },
        'mandatory': [
            'cloud_name',
            ],
        }

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/ec2_images.html', {'response_code': 1, 'message': msg})

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [keys], ['ec2_image_filters'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/ec2_images.html', {'response_code': 1, 'message': '%s ec2 images, %s' % (lno('EV00'), msg)})

        # Update the user.
        table = tables['ec2_image_filters']
        rc, msg = config.db_session_execute(table.update().where((table.c.group_name==active_user.active_group) & (table.c.cloud_name==fields['cloud_name'])).values(table_fields(fields, table, columns, 'update')))
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/ec2_images.html', {'response_code': 1, 'message': '%s ec2 images, %s' % (lno('EV00'), msg)})

        config.db_session.commit()

        active_user.kwargs['cloud_name'] = fields['cloud_name']

    # Retrieve EC2 image filters.
    ec2_image_filters = qt(config.db_connection.execute('select * from ec2_image_filters where group_name="%s" and cloud_name="%s"' % (active_user.active_group, active_user.kwargs['cloud_name'])))

    # Retrieve EC2 image filter options.
    architectures = qt(config.db_connection.execute('select distinct arch as architecture from view_ec2_images order by architecture'))
    operating_systems = qt(config.db_connection.execute('select distinct opsys as operating_system from view_ec2_images order by operating_system'))
    owner_aliases = qt(config.db_connection.execute('select distinct alias from ec2_image_well_known_owner_aliases order by alias'))

    # Retrieve EC2 images.
    rc, msg, sql_select = select_ec2_images(config, active_user.active_group, active_user.kwargs['cloud_name'])
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/ec2_images.html', {'response_code': 1, 'message': '%s ec2 images, %s' % (lno('EV00'), msg)})

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", sql_select)
    ec2_images = qt(config.db_connection.execute(sql_select))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'ec2_image_filters': ec2_image_filters,
            'ec2_images': ec2_images,
            'architectures': architectures,
            'operating_systems': operating_systems,
            'owner_aliases': owner_aliases,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/ec2_images.html', context)

#-------------------------------------------------------------------------------

@silkp(name="EC2 Instance Type List")
@requires_csrf_token
def instance_types(request):

    keys = {
        'auto_active_group': True,
        # Named argument formats (anything else is a string).
        'format': {
            'cloud_name':                                                   'lowerdash',

            'cores':                                                        ('view_ec2_instance_types', 'cores', True, True),
            'families':                                                     ('view_ec2_instance_types', 'instance_family', True, True),
            'memory_min_gigabytes_per_core':                                'float',
            'memory_max_gigabytes_per_core':                                'float',
            'operating_systems':                                            ('view_ec2_instance_types', 'operating_system', True, True),
            'processors':                                                   ('view_ec2_instance_types', 'processor', True, True),
            'processor_manufacturers':                                      ('view_ec2_instance_types', 'processor_manufacturer', True, True),

            'csrfmiddlewaretoken':                                          'ignore',
            'group':                                                        'ignore',
            },
        'mandatory': [
            'cloud_name',
            ],
        }

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/ec2_instance_types.html', {'response_code': 1, 'message': msg})

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [keys], ['ec2_instance_type_filters'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/ec2_instance_types.html', {'response_code': 1, 'message': '%s ec2 instance-types, %s' % (lno('EV00'), msg)})

        # Update the user.
        table = tables['ec2_instance_type_filters']
        rc, msg = config.db_session_execute(table.update().where((table.c.group_name==active_user.active_group) & (table.c.cloud_name==fields['cloud_name'])).values(table_fields(fields, table, columns, 'update')))
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/ec2_instance_types.html', {'response_code': 1, 'message': '%s ec2 instance-types, %s' % (lno('EV00'), msg)})

        config.db_session.commit()

        active_user.kwargs['cloud_name'] = fields['cloud_name']

    # Retrieve EC2 instance type filters.
    ec2_instance_type_filters = qt(config.db_connection.execute('select * from ec2_instance_type_filters where group_name="%s" and cloud_name="%s"' % (active_user.active_group, active_user.kwargs['cloud_name'])))

    # Retrieve EC2 instance type filter options.
    families = qt(config.db_connection.execute('select distinct instance_family from view_ec2_instance_types order by instance_family'))
    operating_systems = qt(config.db_connection.execute('select distinct operating_system from view_ec2_instance_types order by operating_system'))
    processors = qt(config.db_connection.execute('select distinct processor from view_ec2_instance_types order by processor'))
    manufacturers = qt(config.db_connection.execute('select distinct processor_manufacturer from view_ec2_instance_types order by processor_manufacturer'))
    cores = qt(config.db_connection.execute('select distinct cores from view_ec2_instance_types order by cores'))

    # Retrieve EC2 instance types.
    rc, msg, sql_select = select_ec2_instance_types(config, active_user.active_group, active_user.kwargs['cloud_name'])
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/ec2_instance_types.html', {'response_code': 1, 'message': '%s ec2 instance-types, %s' % (lno('EV00'), msg)})

    ec2_instance_types = qt(config.db_connection.execute(sql_select))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'ec2_instance_type_filters': ec2_instance_type_filters,
            'ec2_instance_types': ec2_instance_types,
            'families': families,
            'operating_systems': operating_systems,
            'processors': processors,
            'manufacturers': manufacturers,
            'cores': cores,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/ec2_instance_types.html', context)

