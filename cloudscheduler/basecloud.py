"""
cloudscheduler basecloud module.
Defines the basic interface cloudscheduler expects to use across all types of clouds
and contains methods common to all clouds.
"""

from cloudscheduler.lib.db_config import Config
import gzip
import uuid
import logging
from abc import ABC, abstractmethod

import jinja2
try:
    import cloud_init_util
except:
    import cloudscheduler.cloud_init_util
from cloudscheduler.lib.db_config import Config
import config as csconfig


class BaseCloud(ABC):

    """
    Abstract BaseCloud class, meant to be inherited by any specific cloud class for use
    by cloudscheduler.
    """
    def __init__(self, config, group, name, extrayaml=None, metadata=None):
        self.log = logging.getLogger(__name__)
        self.config = Config(config.path, list(config.categories.keys()))
        self.name = name
        self.group = group
        self.enabled = True
        self.extrayaml = extrayaml
        self.metadata = metadata  # list of tuples with (name, select statement, mime type)
        self.log.debug('New Cloud created: %s', self.name)

    def __repr__(self):
        return ' : '.join([self.name, self.enabled])

    @abstractmethod
    def vm_create(self, group_yaml_list=None, num=1, job=None, flavor=None):
        """
        Abstract method for creating a VM on a cloud.
        :param group_yaml_list: The owning group's yaml
        :param num: Number of VMs to boot
        :param job: job row from the database
        :param flavor: the flavor value from database
        """
        assert 0, 'SubClass must implement vm_create()'

    def _generate_next_name(self):
        """Generate hostnames and check they're not in use."""
        name = ''.join([self.group.replace('_', '-').lower(), '--',
                        self.name.replace('_', '-').lower(), '--',
                        str(self.config.csv2_host_id), '--',
                        str(uuid.uuid4().node)])
        # TODO different way to check name collision?
        #for vm in self.vms.values():
        #    if name == vm.hostname:
        #        name = self._generate_next_name()
        return name

    def strip_yaml_comments(self, yaml_string):
        """
        Strip blank lines and anything beyond a hash ("#") symbol, with few exceptions listed in vetos list
        
        """
        import re
        stripped_yaml=""
        vetos=("^\s*#cloud", "^\s*#!", "^\s*##\*", "^\s*### BEGIN", "^\s*### END",
               "^\s*{#", "^\s\"#", "^\s*\x27#", "^\s*/\\#" , "^\s*\/#" , "^\s*# chkconfig" , "^\s*# description")
        
        for line in yaml_string.splitlines():
            remove=False
            # empty line
            if re.match("^\s*$",line):
                remove=True
            # lines with hash, but apply vetoes
            if re.match("^\s*#",line):
                remove=True
                for v in vetos:
                    remove=remove and re.match(v,line) is None
            if not remove:
                stripped_yaml+=line+"\n"
        return stripped_yaml
    
    def prepare_userdata(self, yaml_list, template_dict):
        """ yamllist is a list of strings of file:mimetype format
            group_yaml is a list of tuples with name, yaml content, mimetype format"""

        metadata_yamls = []  # appending the mime type: tuple(name, content, mime type)

        if yaml_list:
            for yam in yaml_list:
                [name, contents, mimetype] = cloud_init_util\
                    .read_file_type_pairs(yam)
                if contents and mimetype:
                    metadata_yamls.append((name, contents, mimetype))

        # metadata_yamls = []  # also appending the mime type again with it in tuple
        self.config.db_open()
        for source in self.metadata:
            if len(source) != 3:
                self.log.debug("Problem with view?: %s", source)
                continue
            rc, msg = self.config.db_execute(source[1])
            for row in self.config.db_cursor:
                db_yaml = row["metadata"]
                break # we only need the first
            metadata_yamls.append([source[0],
                                   db_yaml,
                                   source[2]])
        self.config.db_close()

        for yaml_tuple in metadata_yamls:
            if '.j2' in yaml_tuple[0]:
                template_dict['cs_cloud_name'] = self.name
                yaml_tuple[1] = jinja2.Environment()\
                    .from_string(yaml_tuple[1]).render(template_dict)
        user_data = cloud_init_util \
            .build_multi_mime_message(metadata_yamls)

        # with open('/tmp/metadata_test.txt', 'w') as fd:
        #    fd.write(userdata)
        if not user_data:
            return ""
        compressed = ""
        try:
            compressed = gzip.compress(str.encode(self.strip_yaml_comments(user_data)))
        except ValueError as ex:
            self.log.exception('zip failure bad value: %s', ex)
        except TypeError as ex:
            self.log.exception('zip failure bad type: %s', ex)
        return compressed

    def _attr_list_to_dict(self, attr_list_str):
        """Convert string in form "key1:value1,key2:value2" into a dictionary"""
        if not attr_list_str:
            return {}
        attr_dict = {}
        for keyvaluestr in attr_list_str.split(','):
            keyvalue = keyvaluestr.split(':')
            if len(keyvalue) == 1:
                attr_dict['default'] = keyvalue[0].strip()
            elif len(keyvalue) == 2:
                attr_dict[keyvalue[0].strip().lower()] = keyvalue[1].strip()
            else:
                raise ValueError("Can't split '%s' into suitable host attribute pair: %s"
                                 % (keyvalue, self.name))
        return attr_dict

    def _get_db_engine(self):
        """
        Get a connection to the database.
        :return: db connection object.
        """
        return create_engine("mysql://" + csconfig.config.db_user + ":" +
                             csconfig.config.db_password + "@" +
                             csconfig.config.db_host + ":" +
                             str(csconfig.config.db_port) + "/" +
                             csconfig.config.db_name)
