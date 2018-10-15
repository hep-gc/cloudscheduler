from cloudscheduler.lib.db_config import *

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

rowid_dict = {}
attr_list_dict = {}

def map_attributes(src, dest, attr_dict):
    global rowid_dict
    global attr_list_dict
    if len(rowid_dict) == 0 or len(attr_list_dict) == 0:
        build_mapping_dictionaries()

    unmapped_keys = []
    mapped_dict = {}
    for key, value in attr_dict.items():
        if key not in rowid_dict[src]:
            unmapped_keys.append((key, value))
        else:
            mapped_dict[attr_list_dict[dest][rowid_dict[src][key]]] = value

    
    return mapped_dict, unmapped_keys

def build_mapping_dictionaries():
    global rowid_dict
    global attr_list_dict

    config = Config('db_only', db_config_dict=True)

    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + config.db_config['db_user'] + ":" + config.db_config['db_password'] + \
        "@" + config.db_config['db_host'] + ":" + str(config.db_config['db_port']) + "/" + config.db_config['db_name'])
    Base.prepare(engine, reflect=True)
    Mappings = Base.classes.csv2_attribute_mapping
    session = Session(engine)

    mapping_rows = session.query(Mappings)
    mapping_names = Mappings.__table__.columns.keys()

    # Generate rowid dict
    for language in mapping_names:
        row_id = 0
        row_dict = {}
        for row in mapping_rows:
            # These ifs will need to be updated every time a new translation language is added
            # since there is no way to use the contents of a variable as a variable name reliably
            # (possible with exec())
            if language == "csv2":
                row_dict[row.csv2] = row_id
            elif language == "os_limits":
                row_dict[row.os_limits] = row_id
            elif language == "os_flavors":
                row_dict[row.os_flavors] = row_id
            elif language == "os_images":
                row_dict[row.os_images] = row_id
            elif language == "os_networks":
                row_dict[row.os_networks] = row_id
            elif language == "os_vms":
                row_dict[row.os_vms] = row_id
            elif language == "condor":
                row_dict[row.condor] = row_id
            else:
                print("Found column not implemented in code, breaking")
                break
            row_id = row_id + 1
        rowid_dict[language] = row_dict


    # Generate attribute list dict
    for language in mapping_names:
        attr_list = []
        for row in mapping_rows:
            # These ifs will need to be updated every time a new translation language is added
            # since there is no way to use the contents of a variable as a variable name reliably
            # (possible with exec())
            if language == "csv2":
                attr_list.append(row.csv2)
            elif language == "os_limits":
                attr_list.append(row.os_limits)
            elif language == "os_flavors":
                attr_list.append(row.os_flavors)
            elif language == "os_images":
                attr_list.append(row.os_images)
            elif language == "os_networks":
                attr_list.append(row.os_networks)
            elif language == "os_vms":
                attr_list.append(row.os_vms)
            elif language == "condor":
                attr_list.append(row.condor)
            else:
                print("Found column not implemented in code, breaking")
                break
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
