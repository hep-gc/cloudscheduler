from cloudscheduler.lib.db_config_na import Config

rowid_dict = {}
attr_list_dict = {}

def map_attribute_names(src, dest, attribute_names):
    """
    Example:
        from cloudscheduler.lib.attribute_mapper import map_attribute_names
        column_map, bad_columns = map_attribute_names('ec2_regions', 'csv2', tables[config.ec2_region_and_endpoint_table]['heads'])
        if len(bad_columns) > 1:
            logging.error(<some_message>)
            exit(1)

        for attribute_name in tables[config.ec2_region_and_endpoint_table]['heads']:
            if attribute_name in column_map:
                print("Attribute: %s (ec2_regions) = %s (csv2)" % (attribute_name, column_map[attribute_name]))

    """

    global rowid_dict
    global attr_list_dict

    if isinstance(attribute_names, list):
        attribute_name_list = attribute_names
    else:
        attribute_name_list = [str(attribute_names)]

    if len(rowid_dict) == 0 or len(attr_list_dict) == 0:
        build_mapping_dictionaries(config)

    mapped_dict = {}
    unmapped_list = []
    for attribute_name in attribute_name_list:
        if attribute_name in rowid_dict[src]:
            mapped_dict[attribute_name] = attr_list_dict[dest][rowid_dict[src][attribute_name]]
        else:
            unmapped_list.append(attribute_name)
    
    return mapped_dict, unmapped_list

def map_attributes(src, dest, attr_dict, config):
    global rowid_dict
    global attr_list_dict
    if len(rowid_dict) == 0 or len(attr_list_dict) == 0:
        build_mapping_dictionaries(config)

    unmapped_keys = []
    mapped_dict = {}
    for key, value in attr_dict.items():
        if key not in rowid_dict[src]:
            unmapped_keys.append((key, value))
        else:
            mapped_dict[attr_list_dict[dest][rowid_dict[src][key]]] = value

    
    return mapped_dict, unmapped_keys

def build_mapping_dictionaries(config):
    global rowid_dict
    global attr_list_dict

    config.db_open()

    Mappings = "csv2_attribute_mapping"

    rc, msg, mapping_rows = config.db_query(Mappings)
    mapping_names = mapping_rows[0].keys()

    # Generate rowid dict
    for language in mapping_names:
        row_id = 0
        row_dict = {}
        for row in mapping_rows:
            # These ifs will need to be updated every time a new translation language is added
            # since there is no way to use the contents of a variable as a variable name reliably
            # (possible with exec())
            row_dict[row[language]] = row_id
            '''
            if language == "csv2":
                row_dict[row["csv2"]] = row_id
            elif language == "os_limits":
                row_dict[row["os_limits"]] = row_id
            elif language == "os_flavors":
                row_dict[row["os_flavors"]] = row_id
            elif language == "os_images":
                row_dict[row["os_images"]] = row_id
            elif language == "os_networks":
                row_dict[row["os_networks"]] = row_id
            elif language == "os_vms":
                row_dict[row["os_vms"]] = row_id
            elif language == "os_sec_grps":
                row_dict[row["os_sec_grps"]] = row_id
            elif language == "condor":
                row_dict[row["condor"]] = row_id
            elif language == "ec2_flavors":
                row_dict[row["ec2_flavors"]] = row_id
            elif language == "ec2_limits":
                row_dict[row["ec2_limits"]] = row_id
            elif language == "ec2_networks":
                row_dict[row["ec2_limits"]] = row_id
            elif language == "ec2_regions":
                row_dict[row["ec2_regions"]] = row_id
            else:
                print("Found column not implemented in code, breaking")
                break
            '''
            row_id = row_id + 1
        rowid_dict[language] = row_dict


    # Generate attribute list dict  (mapping_names are the columns)
    for language in mapping_names:
        attr_list = []
        for row in mapping_rows:
            # These ifs will need to be updated every time a new translation language is added
            # since there is no way to use the contents of a variable as a variable name reliably
            # (possible with exec())
            if row[language] is not None:
                attr_list.append(row[language])
            '''
            if language == "csv2":
                attr_list.append(row["csv2"])
            elif language == "os_limits":
                attr_list.append(row["os_limits"])
            elif language == "os_flavors":
                attr_list.append(row["os_flavors"])
            elif language == "os_images":
                attr_list.append(row["os_images"])
            elif language == "os_networks":
                attr_list.append(row["os_networks"])
            elif language == "os_vms":
                attr_list.append(row["os_vms"])
            elif language == "os_sec_grps":
                attr_list.append(row["os_sec_grps"])
            elif language == "condor":
                attr_list.append(row["condor"])
            elif language == "ec2_flavors":
                attr_list.append(row["ec2_flavors"])
            elif language == "ec2_limits":
                attr_list.append(row["ec2_limits"])
            elif language == "ec2_networks":
                attr_list.append(row["ec2_networks"])
            elif language == "ec2_regions":
                attr_list.append(row["ec2_regions"])
            else:
                print("Found column not implemented in code, breaking")
                break
            '''
        attr_list_dict[language] = attr_list

    return True

def dump_dicts():
    global attr_list_dict
    global rowid_dict

    print(attr_list_dict)
    print(rowid_dict)

if __name__ == "__main__":
    #build_mapping_dictionaries()
    #dump_dicts()
    src = "os_limits"
    dest = "csv2"
    a_dict = {
        "maxTotalCores": 4
    }
    trans_dict = map_attributes(src=src, dest=dest, attr_dict=a_dict)

    print("Input dict:")
    print(a_dict)
    print("Translated dict:")
    print(trans_dict)
    print()


    a_dict = {
        "maxServerMeta": 500,
        "maxTotalRAMSize": 12000
    }
    trans_dict = map_attributes(src=src, dest=dest, attr_dict=a_dict)

    print("Input dict:")
    print(a_dict)
    print("Translated dict:")
    print(trans_dict)
    print()
