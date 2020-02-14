#!/usr/bin/env python3
from cloudscheduler.lib.db_config import Config
from inspect import stack
import datetime
import os
import pika
import shutil
import signal as Signal
import socket
import time

def _get_amqp_connection_(config, log=False):
    """
    Internal function to establish a connection with the AMQP (RabbitMQ) server.
    """

    if config.signals['port'] == config.public_ports['amqp']:
        protocol = 'amqps'
    else:
        protocol = 'amqp'

    URL = '%s://%s:%s@%s:%s/%%2F' % (
        protocol,
        config.signals['user'],
        config.signals['password'],
        config.signals['host'],
        config.signals['port']
        )

    connection = pika.BlockingConnection(pika.URLParameters(URL))

    if log:
        _log_signal_(config, '-', 'connected: %s@%s:%s' % (
            config.signals['user'],
            config.signals['host'],
            config.signals['port']
            ), depth=3)

    return connection

def _get_caller_(ix):
    """
    Internal function to retrieve a caller location from the program stack. The user
    specifies the index of the stack entry they are interested in.
    """

    callers_stack = stack()
    callers_stack_ix = ix + 1
    return 'File %s, line %d, in %s' % (callers_stack[callers_stack_ix].filename, callers_stack[callers_stack_ix].lineno, callers_stack[callers_stack_ix].function)

def _get_pid_info_(pid, registry):
    """
    Internal function to retrieve the start time for the specified process.
    """

    try:
        proc_start_time = str(os.stat('/proc/%s' % pid).st_ctime)
    except:
        proc_start_time = None

    return proc_start_time, '%s/%s' % (registry, pid)

def _log_signal_(config, event, action, pid=os.getpid(), signame='-', depth=2):
    """
    Internal function to log messages to the database.
    """

    if event == 'signal_tests' and 'signal_monitor' in config.categories and config.categories['signal_monitor']['log_signal_tests'] == False:
        return

    if not config.db_session:
        auto_close = True
        config.db_open()
    else:
        auto_close = False

    caller = _get_caller_(depth)

    config.db_session.execute('insert into csv2_signal_log (timestamp,fqdn,pid,event,action,signame,caller) values (%f,"%s",%d,"%s","%s","%s","%s");' % (
        time.time(),
        socket.gethostname(),
        pid,
        event,
        action,
        signame,
        caller
        ))

    if auto_close:
        config.db_close(commit=True)
    else:
        config.db_session.commit()

def _verify_event_registration_(config, event, pid, action='deregister'):
    """
    Internal function to verify the validity of the specified registration.
    """

    registry = _verify_event_registry_(config, event)
    proc_start_time, registration = _get_pid_info_(pid, registry)
    if os.path.exists(registration):
        if proc_start_time:
            if os.path.isfile(registration):
                with open(registration) as fd:
                    pid_start_time = fd.read()

                if float(pid_start_time) < float(proc_start_time):
                    event_receiver_deregistration(config, event, pid=int(pid), action='deleting_obsolete_registration')
                    return None

            elif os.path.isfile(registration):
                event_receiver_deregistration(config, event, pid=int(pid), action='deleting_invalid_registration')
                return None

        else:
            event_receiver_deregistration(config, event, pid=int(pid), action='deleting_registration_for_defunct_process')
            return None

    else:
        _log_signal_(config, event, 'event_registration_doesnt_exist')
        return None

    return int(pid)

def _verify_event_registry_(config, event):
    """
    Internal function to verify the validity of an event and create it's registry
    if it does not exist.
    """

    if event in config.signals['events']:
        registry = '%s/%s' % (config.signals["registry"], event)
        if not os.path.exists(registry):
            os.makedirs(registry, mode=0o755, exist_ok=True)
                
        elif not os.path.isdir(registry):
            raise Exception('Error: The specified registry path "%s" exists but is not a directory.' % event)
                
        return registry

    raise Exception('Error: The specified event "%s" does not exist.' % event)

def deliver_event_signals(config_file, categories=[]):
    """
    User callable function to delivere messages. Function does not return but establishes
    a message processing loop with the 'start_consuming()' statement. 
    """

    def _event_signal_delivery_(channel, method, properties, body):
        """
        Internal pika callback function to handle incoming AMQP messages.
        """

        global signals_config
        signals_config.refresh()
        event, signame, caller = body.decode('utf-8').split(',', 2)

        try:
            signo = Signal.Signals[signame].value

            if event in signals_config.signals['events']:
                for pid_file in os.listdir('%s/%s' % (signals_config.signals['registry'], event)):
                    pid = _verify_event_registration_(signals_config, event, pid_file)
                    if pid:
                        os.kill(pid, int(signo))
                        _log_signal_(signals_config, event, 'delivered', signame=signame, depth=8)

            else:
                _log_signal_(signals_config, event, 'undeliverable_event_undefined', signame=signame, depth=8)

        except:
            _log_signal_(signals_config, event, 'undeliverable_signal', signame=signame, depth=8)

    global signals_config
    if isinstance(categories, str):
        current_categories = categories.split(',')
    else:
        current_categories = categories


    if 'signal_monitor' not in current_categories:
        current_categories += ['signal_monitor']
    
    signals_config = Config(config_file, current_categories, signals=True)

    connection = _get_amqp_connection_(signals_config, log=True)
    channel = connection.channel()
    channel.exchange_declare(exchange=signals_config.signals['host'], exchange_type='fanout')
    channel_attributes = channel.queue_declare(queue='', exclusive=True)
    queue_name = channel_attributes.method.queue
    channel.queue_bind(exchange=signals_config.signals['host'], queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=_event_signal_delivery_, auto_ack=True)
    channel.start_consuming()

def event_receiver_deregistration(config, event, pid=os.getpid(), action='deregister'):
    """
    User callable function to deregister the current process from handling the
    specified event.
    """

    registry = _verify_event_registry_(config, event)
    registration = '%s/%s' % (registry, pid)

    if os.path.isdir(registration):
        shutil.rmtree(registration)
    else:
        os.unlink(registration)

    _log_signal_(config, event, action, pid=int(pid))

def event_receiver_registration(config, event):
    """
    User callable function to register the current process to handle the
    specified event.
    """

    registry = _verify_event_registry_(config, event)

    start_time, registration = _get_pid_info_(os.getpid(), registry)
    fd = open(registration, 'w')
    fd.write(start_time)
    fd.close()

    _log_signal_(config, event, 'register')

def event_signal_send(config, event, signal_name='SIGINT'):
    """
    User callable function to send an event signal.
    """

    registry = _verify_event_registry_(config, event)

    caller = _get_caller_(1)

    signame = signal_name.upper()
    try:
        signo = Signal.Signals[signame].value
    except:
        _log_signal_(config, event, 'cant_send_bad_signal_name', signame=signame)

    connection = _get_amqp_connection_(config)
    channel = connection.channel()
    channel.exchange_declare(exchange=config.signals['host'], exchange_type='fanout')
    channel.basic_publish(exchange=config.signals['host'], routing_key='', body='%s,%s,%s' % (event, signame, caller))
    connection.close()

    _log_signal_(config, event, 'sent', signame=signame)

def verify_event_registrations(config):
    """
    User callable function to verify all registrations (event handling processes).
    Obsolete registrations will automatically be deregistered.
    """

    events = []
    registrations = {}
    for event in sorted(os.listdir(config.signals['registry'])):
        events.append(event)
        registrations[event] = []
        for pid in sorted(os.listdir('%s/%s' % (config.signals['registry'], event))):
            registrations[event].append(pid)

    for event in events:
        if event in config.signals['events']:
            for pid in registrations[event]:
                _verify_event_registration_(config, event, pid)

        else:
            shutil.rmtree('%s/%s' % (config.signals['registry'], event))
            _log_signal_(config, event, 'event_registry_deleted')

