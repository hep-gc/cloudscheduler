"""
DB utilities and configuration.
"""

import cloudscheduler.lib.schema_na as schema_na

import logging
import os
import signal
import socket
import sys
import time
import yaml
import ipaddress

from subprocess import Popen, PIPE
from inspect import stack

import mysql.connector

class Config:
    def __init__(self, db_yaml, categories, db_config_dict=False, db_config_only=False, pool_size=5, max_overflow=0, signals=False):
        """
        Read the DB configuration file and the specified categories configuration from the database.
        """

        # show we are initializing.
        self.initialized = False

        # Calculate csv2 version
        self.version = self._calculate_version()

        # Retrieve the database configuration.
        if os.path.exists(db_yaml):
            self.path = db_yaml
            with open(self.path, 'r') as ymlfile:
                if hasattr(yaml, 'full_load'):
                    base_config = yaml.full_load(ymlfile)
                else:
                    base_config = yaml.load(ymlfile)
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
            self.initialized = True
            return

        self.db_schema = schema_na.schema

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
            rows = self.db_query(self.db_table, where='category="SQL" and config_key="csv2_host_id"')
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

        self.initialized = True

#-------------------------------------------------------------------------------

    def __db_column_list_csv__(self, column_list):
        """
        Return a quoted comma separated value list of column names.
        """

        columns = []
        for column in list(column_list):
            columns.append('`%s`' % column)

        return ','.join(columns)

#-------------------------------------------------------------------------------

    def __db_get_where_clause__(self, table, column_dict, where):
        """
        Convert the caller's column_dict and where parameters into a valid
        where clause.

        The "where" parameter can either be:
        
            o A dictionary of column names and values, or
            o A list of column names in the column_dict, or
            o A valid where_clause string (used as is), or
            o The value '*' (ie. all rows; no where clause), or
            o None, in which case a where clause using the keys of
              the current table and column_dict will be returned.

        """

        def ___get_where_bits_from_dict___(table, column_dict, keys):
            where_bits = []
            for key in keys:
                if key not in self.db_schema[table]['columns']:
                    self.__db_logging_return__(0, 'column "%s" not defined in table "%s", column dropped from where clause' % (key, table))
                    continue

                if key in self.db_schema[table]['columns']:
                    if key in column_dict:
                        value = self.__db_column_value__(table, key, column_dict[key])
                        if value != None:
                            where_bits.append('`%s`=%s' % (key, value))
                        else:
                            raise Exception('invalid "where" specification, "%s=None"' % key)
                    else:
                        raise Exception('invalid "where" specification, key column "%s" is not within the column dictionary "%s"' % (key, column_dict))
                else:
                    raise Exception('invalid "where" specification, key column "%s" is not within the table columns "%s(%s)"' % (key, table, self.db_schema[table]['columns'].keys()))

            if len(where_bits) < 1:
                raise Exception('table has no keyes')

            return ' and '.join(where_bits)

        if isinstance(where, str):
            if where == '*':
                return ''
            else:
                return where

        elif column_dict == None and where == None:
                return ''

        elif isinstance(where, dict):
            return ___get_where_bits_from_dict___(table, where, list(where.keys()))

        elif isinstance(where, list):
            return ___get_where_bits_from_dict___(table, column_dict, where)

        elif column_dict !=  None and where == None:
            return ___get_where_bits_from_dict___(table, column_dict, self.db_schema[table]['keys'])

        raise Exception('invalid "where" specification, table: %s, column_dict: %s, where: %s' % (table, column_dict, where))

#-------------------------------------------------------------------------------

    def __db_logging_return__(self, rc, msg, rows=[]):
        """
        Depending on the rc parameter (0=debug, otherwise warning) log the
        message together with the caller ID.
        """

        def __get_values_from_stack__(stack_entry):
            # Python < 3.5.
            if isinstance(stack_entry, tuple):
                filename = stack_entry[1]
                lineno = stack_entry[2]
                function = stack_entry[3]

            # Python >= 3.5.
            else:
                filename = stack_entry.filename
                lineno = stack_entry.lineno
                function = stack_entry.function

            return filename, lineno, function

        if self.initialized:
            callers_stack = stack()
            if rc > 0:
                stack_trace = ''
                for ix in range(1, len(callers_stack)):
                    filename, lineno, function = __get_values_from_stack__(callers_stack[ix])

                    if function != '<module>':
                        stack_trace = ' -> %s%s' % (function, stack_trace)

                    if filename[-15:] != 'db_config_na.py':
                        if function != '<module>':
                            stack_trace = 'Function: %s' % stack_trace[4:]
                        break

                logging.warning('file: %s, line: %s %s, rc: %s, msg: %s' % (filename, lineno, stack_trace, rc, msg))
            else:
                filename, lineno, function = __get_values_from_stack__(callers_stack[1])
                logging.debug('function: %s, rc: %s, msg: %s' % (function, rc, msg))

        return rows

#-------------------------------------------------------------------------------

    def __db_column_value__(self, table, column, value, allow_nulls=False):
        """
        This function return strings values to be inserted or updated in the
        database. If the string value is empty (None or '') and the table
        columne accepts nulls, the null value will be returned. Otherwise,
        a quoted/escaped string will be returned.
        """

        if value == None:
            return None

        elif self.db_schema[table]['columns'][column]['type'] == 'str':
            if value == '' or value == 'null':
                if allow_nulls and self.db_schema[table]['columns'][column]['nulls'] == 'YES':
                    result = 'null'
                else:
                    result = '""'
            else:
                result = '"%s"' % str(value).replace('"', '\\"')
        else:
            result = value

        return str(result)

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

        if commit:
            return self.__db_logging_return__(0, 'db_close: successful database commit and close')
        else:
            return self.__db_logging_return__(0, 'db_close: successful database rollback and close')

#-------------------------------------------------------------------------------

    def db_commit(self):
        """
        Commit updates.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')

        self.db_connection.commit()
        return self.__db_logging_return__(0, 'db_commit: successful database commit')

#-------------------------------------------------------------------------------

    def db_delete(self, table, column_dict, where=None):
        """
        Execute a DB delete. If successful, set rc=0 to indicate that
        self.db_cursor has the response. Otherwise, return rc=1 and the
        error message.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')
            
        where_clause = self.__db_get_where_clause__(table, column_dict, where)
        
        sql_bits = ['delete from %s' % table]

        if len(where_clause) > 0:
             sql_bits.append('where %s' % where_clause)

        request = '%s;' % ' '.join(sql_bits)

        try:
            self.db_cursor.execute(request)
            return self.__db_logging_return__(0, 'successful db_delete request: %s' % request)
        except Exception as ex:
            raise Exception('failed db_delete request: %s, error: %s' % (request, ex))

#-------------------------------------------------------------------------------

    def db_execute(self, request):
        """
        Execute a DB request. If successful, iset rc=0 to indicate that
        self.db_cursor has the response. Otherwise, return rc=1 and the
        error message.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')

        try:
            self.db_cursor.execute(request)
            return self.__db_logging_return__(0, 'successful db_execute request: %s' % request)
        except Exception as ex:
            raise Exception('failed db_execute request: %s, error: %s' % (request, ex))

#-------------------------------------------------------------------------------

    def db_insert(self, table, column_dict):
        """
        Execute a DB insert. If successful, set rc=0 to indicate that
        self.db_cursor has the response. Otherwise, return rc=1 and the
        error message.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')
            
        columns = []
        value_bits = []
        for column in sorted(column_dict):
            if column not in self.db_schema[table]['columns']:
                self.__db_logging_return__(0, 'column "%s" not defined in table "%s", column dropped from insert' % (column, table))
                continue

            value = self.__db_column_value__(table, column, column_dict[column], allow_nulls=True)
            if value != None:
                columns.append(column)
                value_bits.append(value)
        
        sql_bits = ['insert into %s' % table]
        sql_bits.append('(%s)' % self.__db_column_list_csv__(sorted(columns)))
        sql_bits.append('values (%s)' % ','.join(value_bits))
        request = '%s;' % ' '.join(sql_bits)

        try:
            self.db_cursor.execute(request)
            return self.__db_logging_return__(0, 'successful db_insert request: %s' % request)
        except Exception as ex:
            raise Exception('failed db_insert request: %s, error: %s' % (request, ex))

#-------------------------------------------------------------------------------

    def db_merge(self, table, column_dict):
        """
        A DB merge request attempts to insert or update the row contained in
        the column_dict.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')

        rows = self.db_query(table, where=self.__db_get_where_clause__(table, column_dict, None))

        if len(rows) > 0:
            self.db_update(table, column_dict)

        else:
            self.db_insert(table, column_dict)

        return self.__db_logging_return__(0, 'successful db_merge request')

#-------------------------------------------------------------------------------

    def db_open(self):
        """
        Open and return a database connection.
        """

        if not self.db_connection.is_connected():
            attempts = 5
            delay = 2

            self.db_connection.reconnect(attempts=attempts, delay=delay)

            if not self.db_connection.is_connected():
                raise Exception('Database connection was severed but failed to reconnect, attempts: %s, delay: %s.' % (attempts, delay)) 

        if not self.db_cursor:
            self.db_cursor = self.db_connection.cursor(buffered=True, dictionary=True)

#-------------------------------------------------------------------------------

    def db_query(self, table, select=[], distinct=False, where=None, order_by=None, limit=None):
        """
        Execute a DB query and return the response. Also, trap and return errors.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')

        if table in self.db_schema:
            if len(select) > 0:
                if isinstance(select, list):
                    selected = select
                elif isinstance(select, str):
                    selected = select.split(',')
                else:
                    raise Exception('failed db_query request, select parameter must either be a list of columns or a string containing a comma separated list of columns')
            else:
                selected = list(self.db_schema[table]['columns'].keys())

            if distinct:
                sql_bits = ['select distinct %s from %s' % (self.__db_column_list_csv__(selected), table)] 
            else:
                sql_bits = ['select %s from %s' % (self.__db_column_list_csv__(selected), table)] 

            where_clause = self.__db_get_where_clause__(table, None, where)

            if len(where_clause) > 0:
               sql_bits.append('where %s' % where_clause)
            
            if order_by:
               sql_bits.append('order by %s' % order_by)

            if limit:
               sql_bits.append('limit %s' % limit)

            request = '%s;' % ' '.join(sql_bits)

        elif table[:7].lower() == 'select ':
            request = table

        else:
            raise Exception('the specified table (%s) is not defined' % table)

        try:
            self.db_cursor.execute(request)
            rows = []
            for row in self.db_cursor:
                rows.append(row)
                for col in row:
                    if isinstance(row[col], bytes) or isinstance(row[col], bytearray):
                        rows[-1][col] = row[col].decode('utf-8')

            return self.__db_logging_return__(0, 'successful db_query request: %s' % request, rows=rows)

        except Exception as ex:
            raise Exception('failed db_query request: %s, error: %s' % (request, ex))

#-------------------------------------------------------------------------------

    def db_rollback(self):
        """
        Rollback updates.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')

        self.db_connection.rollback()
        return self.__db_logging_return__(0, 'db_rollback: successful database rollback')

#-------------------------------------------------------------------------------

    def db_update(self, table, column_dict, where=None):
        """
        Execute a DB update. If successful, set rc=0 to indicate that
        self.db_cursor has the response. Otherwise, return rc=1 and the
        error message.
        """

        if not self.db_cursor:
            raise Exception('the database is not open')
            
        updates = []
        for column in sorted(column_dict):
            if column not in self.db_schema[table]['columns']:
                self.__db_logging_return__(0, 'column "%s" not defined in table "%s", column dropped from update' % (column, table))
                continue

            if column not in self.db_schema[table]['keys']:
                value = self.__db_column_value__(table, column, column_dict[column], allow_nulls=True)
                if value != None:
                    updates.append('`%s`=%s' % (column, value))

        where_clause = self.__db_get_where_clause__(table, column_dict, where)
        
        sql_bits = ['update %s' % table]
        sql_bits.append('set %s' % ','.join(updates))

        if len(where_clause) > 0:
            sql_bits.append('where %s' % where_clause)

        request = '%s;' % ' '.join(sql_bits)

        try:
            self.db_cursor.execute(request)
            return self.__db_logging_return__(0, 'successful db_update request: %s' % request)
        except Exception as ex:
            raise Exception('failed db_update request: %s, error: %s' % (request, ex))

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

            rows = self.db_query(self.db_table, where='category="%s"' % category)

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
        cloud_list = self.db_query('csv2_clouds', select=['group_name', 'cloud_name', 'error_count', 'error_time'], where='group_name="%s" and cloud_name="%s"' % (group_name, cloud_name))
        if cloud_list[0]['error_count'] is None:
            cloud_list[0]['error_count'] = 0
        cloud_list[0]['error_count'] = cloud_list[0]['error_count'] + 1
        cloud_list[0]['error_time'] = time.time()
        self.db_merge(cloud_list[0])
        self.db_commit()
        return 1


#-------------------------------------------------------------------------------

    def refresh(self):
        # If closed, open the database.
        if self.db_cursor:
            close_on_exit = False
        else:
            close_on_exit = True
            self.db_open()

        timestamps = self.db_execute('select last_updated from csv2_service_catalog where provider="csv2_configuration" and host_id=0;')
        if len(timestamps) < 1 or timestamps[0] > self.categories['__timestamp__']['last_updated']:
            self.categories = self.get_config_by_category(list(self.categories.keys()))

        if close_on_exit:
            self.db_close()

#-------------------------------------------------------------------------------

    def reset_cloud_error(self, group_name, cloud_name):
        cloud_list = self.db_query('csv2_clouds', select=['group_name', 'cloud_name', 'error_count'], where='group_name="%s" and cloud_name="%s"' % (group_name, cloud_name))
        cloud_list[0]['error_count'] = 0
        self.db_merge(cloud_list[0])
        self.db_commit()
        return 1

#-------------------------------------------------------------------------------

    def update_service_catalog(self, provider=os.path.basename(sys.argv[0]), host_id=None, error=None, counter=None, logger=None):
        if 'ProcessMonitor' in self.categories and self.categories['ProcessMonitor']['pause'] == True:
            return

        if not self.db_cursor:
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

            self.db_execute('update csv2_service_catalog set counter=%s where provider="%s" and host_id=%s;' % (current_counter, provider, current_host_id))
            if rc == 0 and self.db_cursor.rowcount == 0:
                self.initialized = False
                self.db_execute('insert into csv2_service_catalog (provider,host_id,counter) values("%s",%s,%s);' % (provider, current_host_id, current_counter))
                self.initialized = True

            if logger:
                logger.debug('Counter update for provider: %s, host ID: %s, counter: %s' % (provider, host_id, counter))

        elif error:
            self.db_execute('update csv2_service_catalog set last_error=unix_timestamp(), error_message="%s" where provider="%s" and host_id=%s;' % (error, provider, current_host_id))
            if rc == 0 and self.db_cursor.rowcount == 0:
                self.initialized = False
                self.db_execute('insert into csv2_service_catalog (provider,host_id,last_error,error_message) values("%s",%s,unix_timestamp(),"%s");' % (provider, current_host_id, error))
                self.initialized = True

            if logger:
                logger.error('provider: %s, host ID: %s, error: %s' % (provider, host_id, error))

        else:
            self.db_execute('update csv2_service_catalog set last_updated=unix_timestamp() where provider="%s" and host_id=%s;' % (provider, current_host_id))
            if rc == 0 and self.db_cursor.rowcount == 0:
                self.initialized = False
                self.db_execute('insert into csv2_service_catalog (provider,host_id,last_updated) values("%s",%s,unix_timestamp());' % (provider, current_host_id))
                self.initialized = True

            if logger:
                logger.debug('Heartbeat for provider: %s, host ID: %s' % (provider, host_id))

        if auto_close:
            self.db_close(commit=True)
        else:
            self.db_commit()

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
