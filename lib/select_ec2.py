'''
Build and return SQL statements to select Amazon EC2 information.
'''

#-------------------------------------------------------------------------------

def select_ec2_images(config, group_name, cloud_name):
    """
    Select EC2 instance_types.
    """

    rc, msg, close_db_on_exit, region, my_ec2_id = _get_ec2_region_and_owner_id(config, group_name, cloud_name)
    if rc != 0:
        return 1, msg, None

    sql = ['select * from view_ec2_images where region="%s"' % region]

    rc, msg = config.db_execute('select * from ec2_image_filters where group_name="%s" and cloud_name="%s"' % (group_name, cloud_name))
    if rc !=0:
        logging.error("error querying ec2 image filters for cloud %s--%s:" % (group_name, cloud_name))
        logging.error(msg)
    ec2_filter = []
    for row in config.db_cursor:
        ec2_filter.append(row)
    if len(ec2_filter) == 1:
        if ec2_filter[0]['owner_aliases']:
            sql.append(_get_ec2_equal('owner_alias', ec2_filter[0]['owner_aliases']))
            sql[-1] = sql[-1].replace('owner_alias="self"', 'owner_id="%s"' % my_ec2_id).replace('owner_alias="shared"', 'borrower_id="%s"' % my_ec2_id)

        if ec2_filter[0]['owner_ids']:
            sql.append(_get_ec2_equal('owner_id', ec2_filter[0]['owner_ids']))


        _bracket_and_bracket_to_or(sql)

        if ec2_filter[0]['like']:
            sql.append(_get_ec2_like('image_location', ec2_filter[0]['like']))

        if ec2_filter[0]['not_like']:
            sql.append(_get_ec2_not_like('image_location', ec2_filter[0]['not_like']))

        if ec2_filter[0]['operating_systems']:
            sql.append(_get_ec2_equal('opsys', ec2_filter[0]['operating_systems']))

        if ec2_filter[0]['architectures']:
            sql.append(_get_ec2_equal('arch', ec2_filter[0]['architectures']))

    if close_db_on_exit:
        config.db_close()

    return 0, None, ' '.join(sql)

#-------------------------------------------------------------------------------

def select_ec2_instance_types(config, group_name, cloud_name):
    """
    Select EC2 instance_types.
    """

    rc, msg, close_db_on_exit, region, my_ec2_id = _get_ec2_region_and_owner_id(config, group_name, cloud_name)
    if rc != 0:
        return 1, msg, None

    sql = ['select * from view_ec2_instance_types where region="%s"' % region]

    rc, msg = config.db_execute('select * from ec2_instance_type_filters where group_name="%s" and cloud_name="%s"' % (group_name, cloud_name))
    if rc !=0:
        logging.error("error querying ec2 instance type filters for %s--%s:" % (group_name, cloud_name))
        logging.error(msg)
    ec2_filter = []
    for row in config.db_cursor:
        ec2_filter.append(row)
    if len(ec2_filter) == 1:
        if ec2_filter[0]['families']:
            sql.append(_get_ec2_equal('instance_family', ec2_filter[0]['families']))

        if ec2_filter[0]['operating_systems']:
            sql.append(_get_ec2_equal('operating_system', ec2_filter[0]['operating_systems']))

        if ec2_filter[0]['processors']:
            sql.append(_get_ec2_equal('processor', ec2_filter[0]['processors']))

        if ec2_filter[0]['processor_manufacturers']:
            sql.append(_get_ec2_like('processor', ec2_filter[0]['processor_manufacturers']))

        if ec2_filter[0]['cores']:
            sql.append(_get_ec2_equal('cores', ec2_filter[0]['cores'], quotes=''))

        if ec2_filter[0]['memory_min_gigabytes_per_core'] or ec2_filter[0]['memory_max_gigabytes_per_core']:
            sql.append(_get_ec2_range('memory_per_core', ec2_filter[0]['memory_min_gigabytes_per_core'], ec2_filter[0]['memory_max_gigabytes_per_core'], quotes=''))

    if close_db_on_exit:
        config.db_close()

    return 0, None, ' '.join(sql)

#-------------------------------------------------------------------------------

def _bracket_and_bracket_to_or(sql):
    """
    Return a clause to select where a column is equal to one or more values.
    """
    
    if len(sql) > 1 and len(sql[-2]) > 0 and len(sql[-1]) > 5 and sql[-2][-1] == ')' and sql[-1][:5] == 'and (':
        sql[-2] = sql[-2][:-1] + ' or ' + sql[-1][5:]
        del sql[-1]

    return

#-------------------------------------------------------------------------------

def _get_ec2_equal(column_name, values, delimiter=',', quotes='"'):
    """
    Return a clause to select where a column is equal to one or more values.
    """
    value_list = values.split(delimiter)

    phrases = []
    for value in value_list:
        phrases.append('%s=%s' % (column_name, '%s%s%s' % (quotes, value, quotes)))

    return 'and (%s)' % ' or '.join(phrases)

#-------------------------------------------------------------------------------

def _get_ec2_like(column_name, values, delimiter=','):
    """
    Return a clause to select where a column is equal to one or more values.
    """
    value_list = values.split(delimiter)

    phrases = []
    for value in value_list:
        phrases.append('%s like "%%%%%s%%%%"' % (column_name, value))

    return 'and (%s)' % ' or '.join(phrases)

#-------------------------------------------------------------------------------

def _get_ec2_not_equal(column_name, values, delimiter=',', quotes='"'):
    """
    Return a clause to select where a column is equal to one or more values.
    """
    value_list = values.split(delimiter)

    phrases = []
    for value in value_list:
        phrases.append('%s!=%s' % (column_name, '%s%s%s' % (quotes, value, quotes)))

    return 'and %s' % ' and '.join(phrases)

#-------------------------------------------------------------------------------

def _get_ec2_not_like(column_name, values, delimiter=','):
    """
    Return a clause to select where a column is equal to one or more values.
    """
    value_list = values.split(delimiter)

    phrases = []
    for value in value_list:
        phrases.append('%s not like "%%%%%s%%%%"' % (column_name, value))

    return 'and %s' % ' and '.join(phrases)

#-------------------------------------------------------------------------------

def _get_ec2_range(column_name, min_value, max_value, quotes='"'):
    """
    Return a clause to select where a column is equal to one or more values.
    """
    if min_value and max_value:
        return('and %s>=%s and %s<=%s' % (column_name, '%s%s%s' % (quotes, min_value, quotes), column_name, '%s%s%s' % (quotes, max_value, quotes)))
    
    if min_value:
        return('and %s>=%s' % (column_name, '%s%s%s' % (quotes, min_value, quotes)))
    
    if max_value:
        return('and %s<=%s' % (column_name, '%s%s%s' % (quotes, max_value, quotes)))
    
#-------------------------------------------------------------------------------

def _get_ec2_region_and_owner_id(config, group_name, cloud_name):
    """
    Select EC2 images.
    """

    if config.db_connection:
        close_db_on_exit = False
    else:
        close_db_on_exit = True
        config.db_open()

    rc, msg = config.db_execute('select * from csv2_clouds where group_name="%s" and cloud_name="%s"' % (group_name, cloud_name))
    if rc!=0:
        logging.error("error querying cloud %s--%s:" % (group_name, cloud_name))
        logging.error(msg)
    cloud = []
    for row in config.db_cursor:
        cloud.append(row)

    if len(cloud) != 1:
        if close_db_on_exit:
            config.db_close()
        return 1, 'specified cloud "%s::%s" does not exist.' % (group_name, cloud_name), None, None, None

    if cloud[0]['cloud_type'] != 'amazon':
        if close_db_on_exit:
            config.db_close()
        return 1, 'specified cloud "%s::%s" is not an "amazon" cloud.' % (group_name, cloud_name), None, None, None

    return 0,  None, close_db_on_exit, cloud[0]['region'], cloud[0]['ec2_owner_id']

