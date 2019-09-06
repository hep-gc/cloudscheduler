#!/usr/bin/env python3
import datetime
import os
import signal as Signal

def get_pid_info(pid, registry):
    return str(os.stat('/proc/%s' % pid).st_ctime), '%s/%s' % (registry, pid)

def register_signal_receiver(config, event):
    registry = verify_signal_registry(config, event)

    pid = os.getpid()
    start_time, registration = get_pid_info(pid, registry)
    fd = open(registration, 'w')
    fd.write(start_time)
    fd.close()

    fd = open(config.categories["signal_manager"]["signal_manager_log_file"], 'a')
    fd.write('%s signal_manager: process ID "%s" added to registry "%s".\n' % (datetime.datetime.now(), pid, registry))
    fd.close()

def send_signals(config, event, signal_name='sigint'):
    registry = verify_signal_registry(config, event)

    signals = {'ids': {}, 'xref': {}}
    for sig in Signal.Signals:
        signals['ids'][sig.__dict__['_name_']] = sig.__dict__['_value_']
        signals['xref'][sig.__dict__['_value_']] = sig.__dict__['_name_']

    signal = signal_name.upper()
    if signal not in signals['ids']:
        raise Exception('Error: Invalid signal "%s" specified.' % signal_name)

    for process_id in os.listdir(registry):
        try:
            pid = int(process_id)
        except:
            unregister(config, registry, process_id)
            continue

        # there is no guarantee that the registered process are still running so get_pid might throw an error
        try:
            start_time, registration = get_pid_info(pid, registry)
        except Exception as exc:
            fd = open(config.categories["signal_manager"]["signal_manager_log_file"], 'a')
            fd.write('%s signal_manager: process ID "%s" does not exitst in /proc/, unregistering \n' % (datetime.datetime.now(), pid))
            fd.close()
            unregister(config, registry, process_id)
            continue

        fd = open(registration)
        registered_start_time = fd.read()
        fd.close()

        if start_time == registered_start_time:
            os.kill(pid, signals['ids'][signal])
            fd = open(config.categories["signal_manager"]["signal_manager_log_file"], 'a')
            fd.write('%s signal_manager: "%s" sent to process ID "%s".' % (datetime.datetime.now(), signal, pid))
            fd.close()
        else:
            unregister(config, registry, process_id)

def unregister(config, registry, pid):
    os.unlink('%s/%s' % (registry, pid))
    fd = open(config.categories["signal_manager"]["signal_manager_log_file"], 'a')
    fd.write('%s signal_manager: process ID "%s" removed from registry "%s".' % (datetime.datetime.now(), pid, registry))
    fd.close()

def verify_signal_registry(config, event):
    registry = '%s/%s' % (config.categories["signal_manager"]["signal_registry"], event)
    if os.path.isdir(registry):
        return registry

    raise Exception('Error: The specified signal registry "%s" does not exist.' % registry)

