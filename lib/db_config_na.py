"""
DB utilities and configuration.
"""

import schema_na

import os
import signal
import socket
import sys
import time
import yaml
import ipaddress

from subprocess import Popen, PIPE

import mysql.connector

class Config:
    def __init__(self, db_yaml, categories, db_config_dict=False, db_config_only=False, pool_size=5, max_overflow=0, signals=False):
        """
        Read the DB configuration file and the specified categories configuration from the database.
        """

        # Calculate csv2 version
        self.version = self._calculate_version()

        # Retrieve the database configuration.
        if os.path.exists(db_yaml):
            with open(db_yaml, 'r') as ymlfile:
                base_config = yaml.full_load(ymlfile)
        else:
            raise Exception('Configuration file "%s" does not exist.' % db_yaml)

        for system in base_config:
            if system != 'database':
                self.__dict__[system] = base_config[system]

        db_config = {}
        if 'database' in base_config:
            for item in base_config['database']:
                db_config[item] = base_config['database'][item]

            if 'db_table' not in db_config:
                db_config['db_table'] = 'configuration'

            self.db_table = db_config['db_table']

        if db_config_dict or db_config_only:
            self.db_config = db_config

        self.db_cursor = None

        # Open the database.
        self.db_connection = mysql.connector.connect(
            host=db_config['db_host'],
            database=db_config['db_name'],
            user=db_config['db_user'],
            password=db_config['db_password'],
            autocommit=False
            )

        if db_config_only:
            return

        self.db_map = schema_na.schema

        #
        # Use the integer value of the public IPv4 address to create a unique instance IDs for the
        # CSV2 host (db_host) and the local host.
        #
        if db_config['db_host'] == 'localhost':
            self.csv2_host_id = int(ipaddress.IPv4Address(socket.gethostbyname(socket.gethostname())))
        else:
            self.csv2_host_id = int(ipaddress.IPv4Address(socket.gethostbyname(db_config['db_host'])))

        self.local_host_id = int(ipaddress.IPv4Address(socket.gethostbyname(socket.gethostname())))

        self.db_open()
        if self.local_host_id == self.csv2_host_id:
            rc, msg, rows = self.db_query(self.db_table, where='category="SQL" and config_key="csv2_host_id"')
            if rc == 0:
                if self.csv2_host_id != rows[0]['config_value']:
                    try:
                        self.db_cursor.execute('update %s set config_value="%s" where category="SQL" and config_key="csv2_host_id";' % (self.db_table, self.csv2_host_id))

                        self.db_connection.commit()

                    except Exception as msg:
                        print("Error updating csv2_host_id in db_config: %s" % msg)
            else:
                print("Error retrieving current csv2_host_id from db_config: %s" % msg)

        # Retrieve the configuration for the specified categories.
        self.categories = self.get_config_by_category(categories)

        # Close the session.
        self.db_close()

        # Optionally, retrieve original signal configuration.
        if signals:
            if not hasattr(self, 'signals'):
                self.signals = {}

            self.signals['SIGINT'] = signal.getsignal(signal.SIGINT)
            self.signals['SIGKILL'] = signal.getsignal(signal.SIGKILL)
            self.signals['SIGALRM'] = signal.getsignal(signal.SIGALRM)
            self.signals['SIGTERM'] = signal.getsignal(signal.SIGTERM)
            self.signals['SIGUSR1'] = signal.getsignal(signal.SIGUSR1)
            self.signals['SIGUSR2'] = signal.getsignal(signal.SIGUSR2)

#-------------------------------------------------------------------------------

    def db_close(self, commit=False):
        """
        Commit/rollback and close a session.
        """

        if self.db_connection:
            if commit:
                self.db_connection.commit()
            else:
                self.db_connection.rollback()

        if self.db_cursor:
            self.db_cursor.close()
            self.db_cursor = None

#-------------------------------------------------------------------------------

    def db_open(self):
        """
        Open and return a database connection.
        """

        if not self.db_cursor:
            self.db_cursor = self.db_connection.cursor()

#-------------------------------------------------------------------------------

    def db_query(self, table, select=[], where=None, order_by=None, allow_no_rows=False):
        """
        Execute a DB query and return the response. Also, trap and return errors.
        """

        if len(select) > 0:
            selected = list(select)
        else:
            selected = list(self.db_map[table]['columns'].keys())

        sql_bits = ['select %s from %s' % (','.join(selected), table)]

        if where:
           sql_bits.append('where %s' % where)
        
        if order_by:
           sql_bits.append('order by %s' % order_by)

        try:
            self.db_cursor.execute('%s;' % ' '.join(sql_bits))
            rows = []
            for row in self.db_cursor:
                rows.append({})
                for ix in range(len(selected)):
                    rows[-1][selected[ix]] = row[ix]
            if len(rows) < 1 and not allow_no_rows:
                return 1, 'query returned no rows', []
            else:
                return 0, None, rows
        except Exception as ex:
            return 1, ex, []

#-------------------------------------------------------------------------------

    def db_execute(self, request, allow_no_rows=False):
        """
        Execute a DB request and return the response. Also, trap and return errors.
        """

        try:
            result_proxy = self.db_cursor.execute(request)
            if result_proxy.rowcount == 0 and not allow_no_rows:
                return 1, 'the request did not match any rows'
            return 0, result_proxy.rowcount
        except Exception as ex:
            return 1, ex


#-------------------------------------------------------------------------------

    def get_config_by_category(self, categories):

        # Retrieve the configuration for the specified category.
        if isinstance(categories, str):
            category_list = [ categories ]
        else:
            category_list = categories

        target_dict = {}
        for category in category_list:
            if category in target_dict:
                continue

            target_dict['__timestamp__'] = {'last_updated': time.time()}
            target_dict[category] = {}

            rc, msg, rows = self.db_query(self.db_table, where='category="%s"' % category)

            for row in rows:
                if row['config_type'] == 'bool':
                    target_dict[category][row['config_key']] = row['config_value'] == '1' or row['config_value'].lower() == 'yes' or row['config_value'].lower() == 'true'
                elif row['config_type'] == 'float':
                    target_dict[category][row['config_key']] = float(row['config_value'])
                elif row['config_type'] == 'int':
                    target_dict[category][row['config_key']] = int(row['config_value'])
                elif row['config_type'] == 'null':
                    target_dict[category][row['config_key']] = None
                else:
                    target_dict[category][row['config_key']] = row['config_value']

        return target_dict


#-------------------------------------------------------------------------------

    def get_host_id_by_fqdn(self, fqdn):
        return int(ipaddress.IPv4Address(socket.gethostbyname(fqdn)))


#-------------------------------------------------------------------------------

    def get_host_id_by_ip_or_tag(self, tag):
        return int(ipaddress.IPv4Address(tag.replace('-', '.')))


#-------------------------------------------------------------------------------

    def get_host_ip_by_host_id(self, host_id):
        return str(ipaddress.IPv4Address(host_id))


#-------------------------------------------------------------------------------

    def get_host_tag_by_host_id(self, host_id):
        return str(ipaddress.IPv4Address(host_id)).replace('.', '-')


#-------------------------------------------------------------------------------

    def get_version(self):
        return self.version


#-------------------------------------------------------------------------------

    def incr_cloud_error(self, group_name, cloud_name):
        CLOUD = self.db_map.classes.csv2_clouds
        cloud = self.db_session.query(CLOUD).filter(CLOUD.group_name == group_name, CLOUD.cloud_name == cloud_name)[0]
        if cloud.error_count is None:
            cloud.error_count = 0
        cloud.error_count = cloud.error_count + 1
        cloud.error_time = time.time()
        self.db_session.merge(cloud)
        self.db_session.commit()
        return 1


#-------------------------------------------------------------------------------

    def refresh(self):
        # If closed, open the database.
        if self.db_cursor:
            close_on_exit = False
        else:
            close_on_exit = True
            self.db_open()

        timestamps = self.db_cursor.execute('select last_updated from csv2_service_catalog where provider="csv2_configuration" and host_id=0;')
        if timestamps.rowcount < 1 or timestamps.first()['last_updated'] > self.categories['__timestamp__']['last_updated']:
            self.categories = self.get_config_by_category(list(self.categories.keys()))

        if close_on_exit:
            self.db_close()

#-------------------------------------------------------------------------------

    def reset_cloud_error(self, group_name, cloud_name):
        CLOUD = self.db_map.classes.csv2_clouds
        cloud = self.db_session.query(CLOUD).filter(CLOUD.group_name == group_name, CLOUD.cloud_name == cloud_name)[0]
        cloud.error_count = 0
        self.db_session.merge(cloud)
        self.db_session.commit()
        return 1

#-------------------------------------------------------------------------------

    def update_service_catalog(self, provider=os.path.basename(sys.argv[0]), host_id=None, error=None, counter=None):
        if 'ProcessMonitor' in self.categories and self.categories['ProcessMonitor']['pause'] == True:
            return

        if not self.db_session:
            auto_close = True
            self.db_open()
        else:
            auto_close = False

        if host_id:
            try:
                current_host_id = int(float(host_id))
            except:
                current_host_id = self.local_host_id
        else:
            current_host_id = self.local_host_id

        if counter is not None:
            try:
                current_counter = int(float(counter))
            except:
                current_counter = 0

            result = self.db_session.execute('update csv2_service_catalog set counter=%s where provider="%s" and host_id=%s;' % (current_counter, provider, current_host_id))
            if result.rowcount == 0:
                self.db_session.execute('insert into csv2_service_catalog (provider,host_id,counter) values("%s",%s,%s);' % (provider, current_host_id, current_counter))

        elif error:
            result = self.db_session.execute('update csv2_service_catalog set last_error=unix_timestamp(), error_message="%s" where provider="%s" and host_id=%s;' % (error, provider, current_host_id))
            if result.rowcount == 0:
                self.db_session.execute('insert into csv2_service_catalog (provider,host_id,last_error,error_message) values("%s",%s,unix_timestamp(),"%s");' % (provider, current_host_id, error))

        else:
            result = self.db_session.execute('update csv2_service_catalog set last_updated=unix_timestamp() where provider="%s" and host_id=%s;' % (provider, current_host_id))
            if result.rowcount == 0:
                self.db_session.execute('insert into csv2_service_catalog (provider,host_id,last_updated) values("%s",%s,unix_timestamp());' % (provider, current_host_id))

        if auto_close:
            self.db_close(commit=True)
        else:
            self.db_session.commit()

#-------------------------------------------------------------------------------

    def _calculate_version(self):
        version = None
        try:
            path_info = sys.path[0].split('/')
            path_info_ix = path_info.index('cloudscheduler')
            cloudscheduler_root_dir = '/'.join(path_info[:path_info_ix+1])
            p1 = Popen([
                'git',
                'log',
                '--decorate'],
                cwd=cloudscheduler_root_dir, stdout=PIPE, stderr=PIPE)
            p2 = Popen([
                'awk',
                '/^commit /'],
                stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p2.communicate()
            commits = stdout[:-1].decode('utf-8').split('\n')
            tag_ix = -1
            for ix in range(len(commits)):
                words = commits[ix].replace('(',' ').replace(')',' ').replace(',',' ').split()
                try:
                    words_ix = words.index('tag:')
                except:
                    words_ix = -1
                if words_ix > -1:
                    tag = words[words_ix+1]
                    tag_ix = ix
                    break
            if tag_ix == -1:
                version = 'Build: %d' % len(commits)
            elif tag_ix == 0:
                version = 'Version: %s' % tag
            else:
                version = 'Version: %s + %d commits' % (tag, tag_ix)
        except Exception as exc:
            print("Error Determining version")

        return version
