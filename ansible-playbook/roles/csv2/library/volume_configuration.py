#!/usr/bin/env python
#
# For information, in Inventory use:
#
#    .bin/ansible_util -m volume_configuration <node>
#
# Otherwise, use:
#
#    ansible -m volume_configuration <node>
#
#      
import os
import re
import sys
import time
from ansible.module_utils.basic import *
from inspect import currentframe
from stat import *
from subprocess import Popen, PIPE

sys_devices_dir = '/sys/devices'

# Set up the global ansible_module environment.
ansible_module = AnsibleModule(
  argument_spec = dict(
    config = dict(required=False),
  )
)

# Execute a command. Either return a list of output lines or fail with messages.
def _debug_log (msg):
  debug = True

  if debug == True:
    fd = open('/tmp/volume_configuration.log', 'a')
    fd.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg))
    fd.close()

# DESTROY the configuration.
def _destroy_configuration (SYS):
  if '/' not in SYS['dftab']:
    ansible_module.fail_json(msg='volume_configuration(_destroy_configuration,%s): Cannot determine the root filesystem.' % _get_linenumber())
    
  # Loop through the fstab and removing entries for everything except the root volume.
  for dv in SYS['fstab']:
    dv_type, dv_path = _device_type_and_path(SYS, SYS['fstab'][dv][2])
    # _debug_log('%s, %s, %s' % (dv, dv_type, dv_path))
    if dv_path != SYS['dftab']['/'][1]:
      w = dv.split('/')
      _execute(SYS, ['sed', '-i', '/%s/ D' % '\/'.join(w), '/etc/fstab'])
    
  # Loop through the dftab and unmount anything that is not a file and is not on the root volume.
  for mp in SYS['dftab']:
    if SYS['dftab'][mp][0] != 'file' and SYS['dftab'][mp][1] != SYS['dftab']['/'][1]:
      if SYS['dftab'][mp][0] == 'zfs':
        w = mp.split('/')
        if len(w) == 2:
          _execute(SYS, ['zpool', 'destroy', '-f', w[1]])
      else:
        _execute(SYS, ['umount', '-f', mp])
    
  # Loop through LVM physical volumes (PVs) and delete anything that is not on the root volume.
  for UUID in SYS['PVs']:
    if SYS['PVs'][UUID]['device'] != SYS['dftab']['/'][1]:
      for lv in SYS['PVs'][UUID]['LVs']:
        _execute(SYS, ['lvremove', '-f', '-S', 'vg_uuid=%s,lv_name=%s' % (SYS['PVs'][UUID]['VG_UUID'], lv)])

      if SYS['PVs'][UUID]['VG_UUID'] != '-':
        _execute(SYS, ['vgremove', '-f', '-S', 'vg_uuid=%s' % SYS['PVs'][UUID]['VG_UUID']])

      if SYS['PVs'][UUID]['status'] == 'ACTIVE':
        _execute(SYS, ['pvremove', '-f', '/dev/%s' % SYS['PVs'][UUID]['device']])

  # Loop through the disk bays and undefine everything except the root volume.
  for Bn in range(len(SYS['bays'])):
    # Skip bays with no disk.
    if SYS['bays'][Bn]['Disk'] == '-':
      continue

    xxx = '%s, %s' % (Bn, SYS['bays'][Bn])
    _execute(SYS, ['echo', xxx])

    # Configure any currently undefined disks in order to clear their content.
    if SYS['bays'][Bn]['Disk'] == 'available':
      _megacli(SYS, ['0', '%s' % Bn, '-', '-', '-', '-', '-'], True)

    # Retrieve the device information.
    An = SYS['bays'][Bn]['An']; Ln = int(SYS['bays'][Bn]['Disk']); Pn = SYS['ctl_xref'][An];
    SDx = SYS['controllers'][Pn]['devs'][Ln]

    # Ensure the disk is NOT the root volume.
    if SDx == SYS['dftab']['/'][1]:
      continue

    # Destroy any data on the logical disk.
    _execute(SYS, ['wipefs', '-af', '/dev/%s' % SDx])

    # Unconfigure the disk.
    _execute(SYS, ['MegaCli64', '-CfgLdDel', '-L%s' % Ln, '-Force', '-a%s' % An])

  # Loop through the HDDs and undefine everything except the root volume.
  _get_HDD_info(SYS)
  for SDx in SYS['HDD_list']:
    if SDx == SYS['dftab']['/'][1]:
      continue

    _execute(SYS, ['wipefs', '-af', '/dev/%s' % SDx])

# Return the device type and path for the ACTIVE logical device.
def _device_type_and_path(SYS, device):
  dv_array = device.split('/')
  if len(dv_array) > 1 and dv_array[1] == 'dev':
    if len(dv_array) > 3 and dv_array[2] == 'mapper':
      pv = '-'
      for UUID in SYS['PVs']:
        if SYS['PVs'][UUID]['status'] == 'ACTIVE':
          vg = '%s-' % SYS['PVs'][UUID]['VG']; vgl = len(vg)
          if dv_array[3][:vgl] == vg:
            pv = SYS['PVs'][UUID]['device']
      return ['lvm', pv]
    else:
      return ['dev', dv_array[2].rstrip('0123456789')]
  else:
    if SYS['zfs']:
      lines = _execute(SYS, ["zfs", "list"])
      for line in lines:
        w = line.split()
        if len(w) > 0 and w[0] == device:
          return ['zfs', device]

    return ['file', device]

# Execute a command. Either return a list of output lines or fail with messages.
def _execute (SYS, cmd, error_return=False):
  if not SYS['megacli64'] and cmd[0] == 'MegaCli64':
    _debug_log('_execute: ignoring MegaCli64 command, not installed.')
    if error_return:
      return [], []
    else:
      return []

  _debug_log('_execute: %s' % cmd)

  try:
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
      if error_return:
        return stdout[:-1].split("\n"), []
      else:
        return stdout[:-1].split("\n")

    if error_return:
      return None, stderr[:-1].split("\n")

    msg = [ 'volume_configuration(_execute): command=%s, rc=%s' % (cmd, p.returncode), 'stdout:' ]
    msg += stdout[:-1].split("\n") + [ 'stderr:' ]
    msg += stderr[:-1].split("\n")
    ansible_module.fail_json(msg=msg)
  except:
    ansible_module.fail_json(msg='volume_configuration(_execute,%s): Popen failed, command=%s' % (_get_linenumber(), cmd))

def _get_device_info(SYS, Disks):
  bays = Disks.split(',')
  Bn = int(bays[0])

  if len(SYS['bays']) < 1:
    SDx = SYS['HDD_list'][Bn]
    device = '/dev/%s' % SDx
    return bays, Bn, None, None, None, SDx, device
  else:
    An = SYS['bays'][Bn]['An']; Pn = SYS['ctl_xref'][An];
    if SYS['bays'][Bn]['Disk'] == 'jbod':
      Ln = int(SYS['bays'][Bn]['EnSn'].split(':')[1]);
    else:
      Ln = int(SYS['bays'][Bn]['Disk']);

    SDx = SYS['controllers'][Pn]['devs'][Ln]
    device = '/dev/%s' % SDx
    return bays, Bn, An, Pn, Ln, SDx, device

def _get_dev_list(SYS, Pn):
  devs = []
  for dirname, subdirs, files in os.walk('%s%s' % (sys_devices_dir, Pn)):
    w = dirname.split('/')
    if w[-2] == 'block' and (w[-1][0:2] == 'sd' or w[-1][0:2] == 'vd'):
      devs.append(w[-1])
  return devs

def _get_full_pci_address(Dn):
  for dirname, subdirs, files in os.walk(sys_devices_dir):
    if dirname[-len(Dn):] == Dn:
      return dirname[len(sys_devices_dir):]

def _get_HDD_info(SYS):
  SYS['HDD_list'] = []
  SYS['HDD_sizes'] = {}
  lines = _execute(SYS, ['lsblk', '-dbno', 'name,size'])
  for line in lines:
    SDx, bytes = line.split()
    SYS['HDD_list'].append(SDx)
    SYS['HDD_sizes'][SDx] = bytes

def _get_LDs(SYS):
  lines = _execute(SYS, ["MegaCli64", "-LdPdInfo", "-aall"])
  for line in lines:
    w = line.split(); wl = len(w); msg = []

    if wl == 2 and w[0] == 'Adapter':
      msg += [1]
      An = w[1][1:]
      Pn = SYS['ctl_xref'][An]
      SYS['controllers'][Pn]['adapters'][An]['counts']['online'] = 0
      SYS['controllers'][Pn]['adapters'][An]['LDs'] = {}

    if wl == 6 and w[0] == 'Virtual' and w[1] == 'Drive:' and w[3] == '(Target' and w[4] == 'Id:':
      msg += [2]
      Ln = w[2]

    if wl == 8 and w[0] == 'RAID' and w[1] == 'Level' and w[2] == ':' and w[5] == 'RAID' and w[6] == 'Level':
      msg += [3]
      SYS['controllers'][Pn]['adapters'][An]['LDs'][Ln] = w[3][8:-1]

    if wl == 4 and w[0] == 'Enclosure' and w[1] == 'Device' and w[2] == 'ID:':
      msg += [4]
      En = w[3]

    if wl == 3 and w[0] == 'Slot' and w[1] == 'Number:':
      msg += [5]
      Sn = w[2]
      EnSn = '%s:%s' % (En, Sn)

      SYS['controllers'][Pn]['adapters'][An]['counts']['online'] += 1
      SYS['controllers'][Pn]['adapters'][An]['LDs'][Ln] += ',%s' % EnSn

      Bn = SYS['bay_xref'][EnSn]
      SYS['bays'][Bn]['Disk'] = Ln

def _get_linenumber():
  cf = currentframe()
  return cf.f_back.f_lineno

def _hexpad(hexstr,length):
  xl = len(hexstr)
  if xl < length:
    return '%s%s' % ('0' * (length-xl), hexstr)
  else:
    return hexstr

def _is_executable(program):
  import os
  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program):
      return program
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      path = path.strip('"')
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return True

  return False

# Configure LVM.
def _lvm (SYS, request, changed_state):
  RAIDlvl, Disks, VG, LV, GBs, FStype, Mountpoint = request
  changed = changed_state

  if not _is_executable('pvscan') or Disks == '999':
    return changed

  if LV != '-':
    if FStype[:3] == 'zfs':
      ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Invalid request (%s) - can\'t specify a logical volume name for ZFS filesystems.' % (_get_linenumber(), request))

    bays, Bn, An, Pn, Ln, SDx, device = _get_device_info(SYS, Disks)

    # Create physical volume.
    if SDx not in SYS['PV_xref']:
      _execute(SYS, ['pvcreate', device])

      # Retrieve UUID of new PV.
      lines = _execute(SYS, ['pvdisplay', '-S', 'pv_name=/dev/%s' % SDx])
      UUID = '-'
      for line in lines:
        w = line.split(); wl = len(w)
        if wl >=3 and w[1] == 'UUID':
          UUID = w[2] 

      if UUID == '-':
        ansible_module.fail_json(msg='volume_configuration(_lvm,%s): Failed to retrieve UUID for new PV=/dev/%s.' % (_get_linnumber(), SDx))

      SYS['PVs'][UUID] = { 'device': SDx, 'status': 'ACTIVE', 'VG': VG, 'VG_UUID': '-', 'LVs': {} }
      SYS['PV_xref'][SDx] = UUID
      SYS['VG_xref'][VG] = UUID

      # Create the volume group on the new PV and update the configuration.
      _execute(SYS, ['vgcreate', VG, '/dev/%s' % SDx])

      # Retrieve UUID of new VG.
      lines = _execute(SYS, ['vgdisplay', '-S', 'pv_name=/dev/%s' % SDx])
      vg_uuid = '-'
      for line in lines:
        w = line.split(); wl = len(w)
        if wl >=3 and w[1] == 'UUID':
          vg_uuid = w[2] 

      if vg_uuid == '-':
        ansible_module.fail_json(msg='volume_configuration(_lvm,%s): Failed to retrive UUID for new PV=/dev/%s.' % (_get_linenumber(), SDx))

      SYS['PVs'][UUID]['VG_UUID'] = vg_uuid
      changed = True

    UUID = SYS['VG_xref'][VG]
    if LV != '*' and LV not in SYS['PVs'][UUID]['LVs']:
      _execute(SYS, ['lvcreate', '-L%sG' % GBs, '-n', LV, VG])
      SYS['PVs'][UUID]['LVs'][LV] = int(GBs) * 1024
      changed = True

  return changed

# Configure RAID devices.
def _megacli (SYS, request, changed_state):
  changed = changed_state
  if len(SYS['bays']) < 1:
    return changed

  RAIDlvl, Disks, VG, LV, GBs, FStype, Mountpoint = request
  bays = Disks.split(',')

  if not SYS['megacli64'] or Disks == '999':
    return changed

  if  RAIDlvl == '0' or RAIDlvl == '1' or RAIDlvl == '5' or RAIDlvl == '6':
    disk_count = len(bays)

    # RAID 0.
    if RAIDlvl == '0':
      if disk_count < 1:
        ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Invalid RAID 0 request (%s) - must specify at least 1 disk.' % (_get_linenumber(), request))

    # RAID 1.
    elif RAIDlvl == '1':
      if disk_count < 2 or disk_count % 2 != 0:
        ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Invalid RAID 1 request (%s) - must specify an even number of disks.' % (_get_linenumber(), request))

    # RAID 5.
    elif RAIDlvl == '5':
      if disk_count < 3:
        ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Invalid RAID 5 request (%s) - must specify at least 3 disks.' % (_get_linenumber(), request))

    # RAID 6.
    elif RAIDlvl == '6':
      if disk_count < 4:
        ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Invalid RAID 6 request (%s) - must specify at least 4 disks.' % (_get_linenumber(), request))

    # Check the state of the required disks.
    disks = [RAIDlvl]
    for ix in range(len(bays)):
      Bn = int(bays[ix]); An = SYS['bays'][Bn]['An']; Pn = SYS['ctl_xref'][An]; Ln = SYS['bays'][Bn]['Disk']
      
      _debug_log('_megacli, check state: Bn=%s, An=%s, Pn=%s, Ln=%s' % (Bn, An, Pn, Ln))

      if ix == 0:
        if SYS['controllers'][Pn]['adapters'][An]['counts']['jbod'] > 0:
          ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID array (%s); adapter (%s) is supporting %s JBOD devices.' % (_get_linenumber(), request, An, SYS['controllers'][Pn]['adapters'][An]['counts']['jbod']), SYS=SYS)
        An_1 = An; Pn_1 = Pn;  Ln_1 = Ln
      else:
        if An != An_1:
          ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID array (%s); request spans multiple adapters (%s/%s).' % (_get_linenumber(), request, An_1, An), SYS=SYS)
        
        if FStype[:3] == 'zfs':
          if SYS['bays'][int(bays[ix])]['Disk'] != 'available':
            for iy in range(len(bays)):
              if iy != ix:
                if SYS['bays'][int(bays[iy])]['Disk'] == SYS['bays'][int(bays[ix])]['Disk']:
                  ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID 0 for ZFS (%s); requested bay %s in same logical device as bay %s.' % (_get_linenumber(), request, Bn, int(bays[iy])), SYS=SYS)
        else:
          if Ln != Ln_1:
            ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID array (%s); requested disks are in conflicting states (Bn=%s, Ln=%s, Ln_1=%s).' % (_get_linenumber(), request, Bn, Ln, Ln_1), SYS=SYS)
        
      disks += [ SYS['bays'][Bn]['EnSn'] ]

    LD_1 = ','.join(disks)

    # If disks are "available" (available but undefined), define the logical device and return (change =) True.
    if Ln_1 == 'available':
      if SYS['controllers'][Pn_1]['adapters'][An_1]['JBOD'] == 'enabled':
        # Disable JBOD on the adapter.
        _execute(SYS, ["MegaCli64", "-AdpSetProp", "-EnableJBOD", "-0", "-a%s" % An_1])
        SYS['controllers'][Pn_1]['adapters'][An_1]['JBOD'] == 'disabled'

      if disks[0] == '0' and FStype[:3] == 'zfs':
        # Define multiple single disk, RAID 0 (JBOD not available) LDs for zpool/zfs.
        for ix in range(1, len(disks)):
          _execute(SYS, ["MegaCli64", "-CfgLdAdd", "-r%s[%s]" % (disks[0], disks[ix]), "WT", "RA", "-strpsz1024", "-a%s" % An_1])
      else:
        # Define the array.
        _execute(SYS, ["MegaCli64", "-CfgLdAdd", "-r%s[%s]" % (disks[0], ','.join(disks[1:])), "WT", "RA", "-strpsz1024", "-a%s" % An_1])

      # Update the configuration.
      _get_LDs(SYS); ld_count = len(SYS['controllers'][Pn_1]['adapters'][An_1]['LDs'])

      sleep_count = 0
      while len(SYS['controllers'][Pn_1]['devs']) < ld_count:
        if sleep_count > 4:
          ansible_module.fail_json(msg='volume_configuration(_megecli,%s): Timeout waiting for UDEV to create device in /sys/devices for request(%s).' % (_get_linenumber(), request))
        # _debug_log('_megacli, sleeping: /sys/devices.')
        time.sleep(1)
        sleep_count += 1
        SYS['controllers'][Pn_1]['devs'] = _get_dev_list(SYS, Pn_1);

      Bn = int(bays[0]); An = SYS['bays'][Bn]['An']; Pn = SYS['ctl_xref'][An]; Ln = int(SYS['bays'][Bn]['Disk'])

      sleep_count = 0
      while _no_device(SYS['controllers'][Pn]['devs'][Ln]):
        if sleep_count > 4:
          ansible_module.fail_json(msg='volume_configuration(_megecli,%s): Timeout waiting for UDEV to create device in /dev for request(%s).' % (_get_linenumber(), request))
        time.sleep(1)
        sleep_count += 1

      _get_HDD_info(SYS)
      return True

    # if array is already defined correctly, return (change =) False. Otherwise, fail.
    if disks[0] == '0' and FStype[:3] == 'zfs':
      for ix in range(len(bays)):
        Bn = int(bays[ix]); An = SYS['bays'][Bn]['An']; Pn = SYS['ctl_xref'][An]; Ln = SYS['bays'][Bn]['Disk']
        if Ln in SYS['controllers'][Pn]['adapters'][An]['LDs'] and '%s,%s' % (RAIDlvl, SYS['bays'][Bn]['EnSn']) != SYS['controllers'][Pn]['adapters'][An]['LDs'][Ln]:
          ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID 0 devices for ZFS (%s); requested disks are already configured differently (%s/%s).' % (_get_linenumber(), request, LD, SYS['controllers'][Pn]['adapters'][An]['LDs'][Ln]), SYS=SYS)
      return False

    elif Ln_1 in SYS['controllers'][Pn_1]['adapters'][An_1]['LDs']:
      if LD_1 == SYS['controllers'][Pn_1]['adapters'][An_1]['LDs'][Ln_1]:
        return False
      else:
        ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID array (%s); requested disks are already configured differently (%s/%s).' % (_get_linenumber(), request, LD_1, SYS['controllers'][Pn_1]['adapters'][An_1]['LDs'][Ln_1]), SYS=SYS)

    ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create RAID array (%s); requested disks (%s) are already in use.' % (_get_linenumber(), request, disks[1:]), SYS=SYS)

  # Hotspares and JBODs.
  elif RAIDlvl == 'hs' or RAIDlvl == 'jbod' or RAIDlvl == 'md':
    for ix in range(len(bays)):
      Bn = int(bays[ix])
      if SYS['bays'][Bn]['Disk'] != RAIDlvl:

        # Define Hotspares.
        if SYS['bays'][Bn]['Disk'] == 'available':
          An = SYS['bays'][Bn]['An']; Pn = SYS['ctl_xref'][An]; EnSn = SYS['bays'][Bn]['EnSn']

          if RAIDlvl == 'hs':
            if SYS['controllers'][Pn]['adapters'][An]['counts']['jbod'] > 0:
              ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create Hotspare; adapter (%s) is supporting %s JBOD devices.' % (_get_linenumber(), An, SYS['controllers'][Pn]['adapters'][An]['counts']['jbod']), SYS=SYS)

            if SYS['controllers'][Pn]['adapters'][An]['JBOD'] != 'disabled':
              # Disable JBOD on the adapter.
              _execute(SYS, ["MegaCli64", "-AdpSetProp", "-EnableJBOD", "-0", "-a%s" % An])
              SYS['controllers'][Pn_1]['adapters'][An_1]['JBOD'] == 'disabled'

            # Define Hotspare.
            _execute(SYS, ["MegaClii64", "-PDHSP", "-Set", "-PhysDrv[%s]" % EnSn, "-a%s" % An])

            # Update the configuration.
            SYS['controllers'][Pn_1]['adapters'][An_1]['counts']['hs'] += 1
            SYS['bays'][Bn] = 'hs'

        # Define JBODs.
          else:
            if SYS['controllers'][Pn]['adapters'][An]['counts']['hs'] > 0 or SYS['controllers'][Pn]['adapters'][An]['counts']['online'] > 0:
              ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create JBOD; adapter (%s) is supporting %s Hotspare and %s RAID devices.' % (_get_linenumber(), An, SYS['controllers'][Pn]['adapters'][An]['counts']['hs'], SYS['controllers'][Pn]['adapters'][An]['counts']['online']), SYS=SYS)

            if SYS['controllers'][Pn]['adapters'][An]['JBOD'] != 'enabled':
              # Enable JBOD on the adapter.
              _execute(SYS, ["MegaCli64", "-AdpSetProp", "-EnableJBOD", "-1", "-a%s" % An])
              SYS['controllers'][Pn_1]['adapters'][An_1]['JBOD'] == 'enabled'

            # Define JBOD.
            _execute(SYS, ["MegaClii64", "-PDMakeJBOD", "-PhysDrv[%s]" % EnSn, "-a%s" % An])

            # Update the configuration.
            SYS['controllers'][Pn_1]['adapters'][An_1]['counts']['jbod'] += 1
            SYS['bays'][Bn] = 'jbod'

          changed = True

        # Disk is unavailable, fail.
        else:
          if RAIDlvl == 'hs':
            ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create Hotspare; requested disk (%s) is already configured differently.' % (_get_linenumber(), Bn), SYS=SYS)
          else:
            ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Can not create JBOD; requested disk (%s) is already configured differently.' % (_get_linenumber(), Bn), SYS=SYS)

      return changed

  # Unsupported request type.
  else:
    ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Storage request (%s) specified an invalid RAID/disk configuration (%s).' % (_get_linenumber(), request, RAIDlvl)) 

  ansible_module.fail_json(msg='volume_configuration(_megacli,%s): Logic error.' % _get_linenumber()) 

def _mkfs (SYS, request, changed_state):
  RAIDlvl, Disks, VG, LV, GBs, FStype, Mountpoint = request
  changed = changed_state
  bays = Disks.split(',')

  # Ignore anything without a mountpoint. Otherwise, determine the label, device, and mount (eg: LABEL=, /dev/sdX, /swapfile, etc.) for the request.
  if Mountpoint != '-':
    # Determine filesystem label.
    label = os.path.basename(Mountpoint)
    if label == '/':
      label = 'root'
    else:  
      if FStype == 'xfs' and len(label) > 12:
        label = label[-12:]
      elif len(label) > 16 and FStype[:3] != 'zfs':
        label = label[-16:]

    # Determine the device and mount (eg: LABEL=, /dev/sdX, /swapfile, etc.).
    if Disks == '999':
      # Process device files.
      if FStype == 'xfs':
        ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device file="%s" cannot be specified for an XFS filesystem.' % (_get_linenumber(), device))

      if FStype == 'swap':
        device = Mountpoint
      else:
        device = '%s.%s' % (Mountpoint, FStype)

      # If device file does not exist, create it.
      if not os.path.exists(device):
        MBs = int(GBs) * 1024
        _execute(SYS, ['dd', 'if=/dev/zero', 'of=%s' % device, 'bs=1048576', 'count=%s' % MBs])

        if FStype == 'swap':
          _execute(SYS, ['chmod', '0600', device])

        changed = True

      elif not os.path.isfile(device):
        ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): "%s" is not a device file.' % (_get_linenumber(), device))

      mount = device
    elif FStype[:3] == 'zfs':
      device = []
      mount = Mountpoint
      for ix in range(len(bays)):
        Bn = int(bays[ix])

        if len(SYS['bays']) < 1:
          device.append(SYS['HDD_list'][Bn])
        else:
          An = SYS['bays'][Bn]['An']; Pn = SYS['ctl_xref'][An]; Ln = int(SYS['bays'][Bn]['Disk'])
          device.append(SYS['controllers'][Pn]['devs'][Ln])
    else:
      # Process LVM and physical devices.
      if LV != '-' and LV != '*':
        device = '/dev/mapper/%s-%s' % (VG, LV)
      else:
        bays, Bn, An, Pn, Ln, SDx, device = _get_device_info(SYS, Disks)

      mount = 'LABEL=%s' % label

    _debug_log('_mkfs: label=%s, mount=%s, device=%s' % (label, mount, device))

    # Check for existing filesystem/swap space.
    if FStype[:3] == 'zfs':
      dev_states = {'unused': [], 'zfs': [], 'other': []}
      for ix in range(len(device)):
        dev = device[ix]
        actual_type, actual_label = _mkfs_check_single_device(SYS, '/dev/%s' % device[ix], FStype, label)    
        if actual_type:
          if actual_type == 'zfs':
            dev_states['zfs'].append(device[ix])
          else:
            dev_states['other'].append(device[ix])
        else:
          dev_states['unused'].append(device[ix])

      if len(dev_states['unused']) != len(device) and len(dev_states['zfs']) != len(device):
        ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but disks are in an inconsistent filesystem state (unused: %s, zfs: %s, other: %s).' % (_get_linenumber(), dev_states['unused'], dev_states['zfs'], dev_states['other']))
    else:
      actual_type, actual_label = _mkfs_check_single_device(SYS, device, FStype, label)    

    # Check the existing filesystem is of the right type.
    if actual_type:
      if actual_type != FStype[:len(actual_type)]:
          if actual_type == 'swap':
            ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Existing SWAP space on device=%s does not match requested type=%s.' % (_get_linenumber(), device, FStype))
          else:
            ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Existing %s filesystem on device=%s does not match requested type=%s.' % (_get_linenumber(), device, actual_type, FStype))

    # The requested the filesystem/swap space does not exist; make it.
    else:
      if FStype[:3] == 'zfs':
        if SYS['zfs'] and SYS['zpool']:
          w = Mountpoint.split('/')
          if len(w) > 2 and not w[0] and w[1] and w[2]:
            # Ensure mountpoint doesn't already exist.
            _execute(SYS, ['rmdir', Mountpoint], error_return=True)
            _execute(SYS, ['rmdir', '/%s' % w[1]], error_return=True)
            if os.path.exists('/%s' % w[1]):
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but failed to initialize mountpoint.' % _get_linenumber())


            # Create the ZFS storage pool.
            if FStype == 'zfs':
              if len(device) > 0:
                _execute(SYS, ['zpool', 'create', '-f', w[1]] + device)
              else:
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but requires at least 1 disks.' % _get_linenumber())
            elif FStype == 'zfs1':
              if len(device) > 1:
                _execute(SYS, ['zpool', 'create', '-f', w[1], 'raidz1'] + device)
              else:
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but raidz1 requires at least 2 disks - %s specified.' % (_get_linenumber(), len(devices)))
            elif FStype == 'zfs2':
              if len(device) > 2:
                _execute(SYS, ['zpool', 'create', '-f', w[1], 'raidz2', ' '.join(device)])
              else:
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but raidz2 requires at least 3 disks - %s specified.' % (_get_linenumber(), len(devices)))
            elif FStype == 'zfs3':
              if len(device) > 3:
                _execute(SYS, ['zpool', 'create', '-f', w[1], 'raidz3', ' '.join(device)])
              else:
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but raidz3 requires at least 4 disks - %s specified.' % (_get_linenumber(), len(devices)))
            elif FStype == 'zfsm':
              if len(device) > 1 and len(device) % 2 == 0:
                mirror_devs = int(len(device)/2)
                _execute(SYS, ['zpool', 'create', '-f', w[1], 'mirror', ' '.join(device[:mirror_devs]), 'mirror', ' '.join(device[mirror_devs:])])
              else:
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but mirrors require an even number of disks - %s specified.' % (_get_linenumber(), len(devices)))
            else:
              ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but specified an invalid zpool type "%s".' % (_get_linenumber(), FStype))

            # Set properties for the storage pool.
            _execute(SYS, ['zpool', 'export', w[1]])
            _execute(SYS, ['zpool', 'import', '-d', '/dev', w[1]])
            _execute(SYS, ['zpool', 'set', 'autoreplace=on', w[1]])
            _execute(SYS, ['zpool', 'set', 'autoexpand=on', w[1]])

            _execute(SYS, ['zfs', 'set', 'compression=lz4', w[1]])
            _execute(SYS, ['zfs', 'set', 'xattr=sa', w[1]])
            _execute(SYS, ['zfs', 'set', 'relatime=on', w[1]])
            _execute(SYS, ['zfs', 'set', 'dnodesize=auto', w[1]])

            # Create the ZFS filesystem and dftab entry.
            _execute(SYS, ['zfs', 'create', '%s/%s' % (w[1], w[2])])
            SYS['dftab']['/%s/%s' % (w[1], w[2])] = [ 'zfs', '%s/%s' % (w[1], w[2]) ]

          else:
            ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but an invalid mountpoint specified "%s"; must be in the form "/<zpool>/<filesystem>".' % (_get_linenumber(), Mountpoint))
        else:
          ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): ZFS filesystem requested, but the zpool and zfs commands are not installed.' % _get_linenumber())
      else:
        # If a swap file was requested, create it.
        if FStype == 'swap':
          _execute(SYS, ['mkswap', '-f', '-L', label, device])
          changed = True
        # Otherwise, created the requested filesystem.
        else:
          if FStype == 'xfs':
            _execute(SYS, ['mkfs.xfs', '-L', label, device])
          else:
            _execute(SYS, ['mkfs', '-F', '-t', FStype, '-L', label, device])
          changed = True

    # If necessary, create /etc/fstab and dftab entries for the request.
    if not mount in SYS['fstab']:
      if FStype == 'swap':
        mp = 'none'; dump = '0'; fsck = '0'
      else:
        SYS['fstab_fsck'] += 1
        mp = Mountpoint; dump = '1'; fsck = SYS['fstab_fsck']

      sequence = len(SYS['fstab']) + 1
      fd = open('/etc/fstab', 'a')
      fd.write("%s %s %s defaults %s %s\n" % (mount, mp, FStype, dump, fsck))
      fd.close()
      SYS['fstab'][mount] = [ Mountpoint, FStype, '-' ]
      SYS['fxtab'][Mountpoint] = mount

      dv_type, dv_path = _device_type_and_path(SYS, device)
      SYS['dftab'][mp] = [ dv_type, dv_path ]

      changed = True

    # If necessary, create a mountpoint for the request.
    if FStype != 'swap':
      if not os.path.exists(Mountpoint):
        _execute(SYS, ['mkdir', '-p', Mountpoint])
        changed = True

      if not os.path.isdir(Mountpoint):
        ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Mount point "%s" is not a directory.' % (_get_linenumber(), Mountpoint))

    # If necessary, mount the device.
    if SYS['fstab'][mount][2] == '-':
      if FStype == 'swap':
        _execute(SYS, ['swapon', '-a'])
      else:
        _execute(SYS, ['mount', '-a'])
      SYS['fstab'][mount][2] = device
      changed = True

  return changed

def _mkfs_check_single_device(SYS, device, FStype, label):
  # Check device for existing filesystem/swap space.
  actual_type = None
  actual_label = None

  # Check for ZFS filesystems.
  lines, errors = _execute(SYS, ['fdisk', '-l', device], error_return=True)
  if lines:
    for line in lines:
      w = line.split()
      if len(w) > 4 and w[4] == 'Solaris':
        actual_type = 'zfs'
        break

  # Check for ext filesystems or swap spaces.
  if not actual_type:
    lines, errors = _execute(SYS, ['tune2fs', '-l', device], error_return=True)
    if lines == None:
      # tune2fs (retrieve filesystem information) failed. Check if device contains a swap file and retrieve its' label
      for line in errors:
        w = line.split()
        if len(w) == 8 and ' '.join(w[1:-1]) == 'contains a swap file system labelled':
          actual_type = 'swap'
          actual_label =  w[-1][1:-1]
          if actual_label == label:
            break
          else:
            ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device=\'%s\', FStype=\'%s\', label=\'%s\', but label=\'%s\' required.' % (_get_linenumber(), device, FStype, actual_label, label))
        elif len(w) == 6 and ' '.join(w[1:]) == 'contains a swap file system':
          ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device=\'%s\' contains an unlabelled swap file that may be in use.'  % (_get_linenumber(), device))

      # On some Linux distributions (eg CentOS), tune2fs does not return the label of a swap file. Try the file command:
      if not actual_type:
        lines = _execute(SYS, ['file', '-b', device])
        for line in lines:
          w = line.split(',')
          if len(w) == 5 and w[0] == 'Linux/i386 swap file (new style)':
            if w[3].strip()[0:6] == 'LABEL=':
              actual_type = 'swap'
              actual_label =  w[3].strip()[6:]
              if actual_label == label:
                break
              else:
                ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device=\'%s\', FStype=\'%s\', label=\'%s\', but label=\'%s\' required.' % (_get_linenumber(), device, FStype, actual_label, label))
            else:
              ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device=\'%s\' contains an unlabelled swap file that may be in use.'  % (_get_linenumber(), device))

    # tune2fs (retrieve filesystem information) succeded. Continue if filesystem label is correct. Otherwise, fail.
    else:
      actual_type = 'ext'
      for line in lines:
        w = line.split(':')
        if w[0] == 'Filesystem volume name':
          actual_label =  w[1].strip()
          if actual_label == label:
            break
          else:
            ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device=\'%s\', FStype=\'%s\', label=\'%s\', but label=\'%s\' required.' % (_get_linenumber(), device, FStype, actual_label, label))

      if not actual_label:
        ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Can\'t find filesystem label.' % _get_linenumber())

  # Check for xfs filesystems.
  if not actual_type:
    lines, errors = _execute(SYS, ['xfs_admin', '-l', device], error_return=True)
    if lines != None:
      actual_type = 'xfs'
      w = lines[0].split()
      actual_label =  w[2][1:-1]
      if actual_label != label:
        ansible_module.fail_json(msg='volume_configuration(_mkfs,%s): Device=\'%s\', FStype=\'%s\', label=\'%s\', but label=\'%s\' required.' % (_get_linenumber(), device, FStype, actual_label, label))

  return actual_type, actual_label

def _no_device(SDx):
  device = '/dev/%s' % SDx

  _debug_log('_no_device, checking for device %s ...' % device)

  try:
    return not S_ISBLK(os.stat(device).st_mode)
  except:
   return True

def _which(cmd):
  p = Popen(['which', cmd], stdout=PIPE, stderr=PIPE)
  stdout, stderr = p.communicate()

  if p.returncode == 0:
    return True
  else:
    return False

def main():
  os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin'
  _debug_log("Starting.")

  _debug_log(ansible_module.params)
  # Retrive optional disk configuration file path.
  config_path = ansible_module.params['config']

  # if help requested (config=None), print messages and exit.
  if config_path == None:
    help = [
      'Use the ansible module \'volume_confguration\' to display and optionally reconfigure the',
      'storage on a node. The module is invoked as follows:',
      '',
      '  ansible -m volume_configuration {-a config=[ show | <config_file_path> | DESTROY ] } <node>',
      '',
      'Where the optional argument \'config\' has the following values:',
      '',
      '  o If omitted, these help messages are displayed.',
      '',
      '  o If the value is \'show\', the current configuration is displayed.',
      '',
      '  o If the value is \'DESTROY\', all current filesystems excluding the root filesystem are destroyed,',
      '    LVM logical volumes/volume groups are removed, and hardware RAID logical devices are deleted.',
      '    This option should be used with EXTREME care!',
      '',
      '  o If the value is the absolute path of a configuration file, RAID devices, LVM volume groups/',
      '    logical volumes, mount points, fstab entries, and filessystems will be created and mounted.',
      '    The configuration file is a text file. Each line of the file defines one storage area and',
      '    is composed of the following fields separated by virtical bars:',
      '',
      '    o fqdn_of_node   - The fully qualified domain name of the host on which the storage is', 
      '                       to be defined.',
      '',
      '    o RAID_type      - RAID level of the disk group. The following RAID_types are supported:',
      '                       o 999 - indicating no logical device or MD definition',
      '                       o 0, 1, 5, or 6',
      '                       o hs - device is a hot spare',
      '                       o jbod',
      '                       o md - device is a Linux MD device',
      '',
      '    o disk_bays      - A list of disk bay numbers separated by commas.',
      '',
      '    o volume_group   - The name assigned to a group of disk bays. If a \'logical_volume\'',
      '                       is also specified, this will also be used as the LVM volume group',
      '                       name.',
      '',
      '    o logical_volume - The LVM logical volume name.',
      '',
      '    o size           - The size of the logical volume/file system in gigabytes.',
      '',
      '    o fs_type        - The file system type. Supported types include \'swap\', \'xfs\', and any',
      '                       other file system type supported by the mkfs command on the host.',
      '',
      '    o mount_point    - The file system mount point.',
      '',
      'This module is usually invoked via the \'configure_volumes.yaml\' common playbook. This playbook',
      'installs the \'pciutils\' pre-requisite package and provides a template to generate the configuration',
      'file from variables provided by the \'Inventory\' system.',
      '',
      'For debugging purposes, this module maintains a log file of its\' activities in \'/tmp/volume_configuration.log\'',
      'on the target node.',
      ]
    _debug_log("HELP completed.")
    ansible_module.exit_json(ansible_facts={ "volume_configuration": { "Help": help } }, changed=False)

  # Initialize system status dictionary.
  SYS = {
    "bays": [],
    "bay_xref": {},
    "controllers": {},
    "ctl_xref": {},
    "dftab": {},
    "fstab": {},
    "fstab_fsck": 0,
    "fxtab": {},
    "HDD_list": [],
    "HDD_sizes": {},
    "internal_adapter_count": 0,
    "megacli64": _which('MegaCli64'),
    "pci_xref": {},
    "PVs": {},
    "PV_xref": {},
    "VG_xref": {},
    "zfs": _which('zfs'),
    "zpool": _which('zpool'),
  }

  # Retrieve HDD configuration.
  _get_HDD_info(SYS)

  # Clear forign configurations.
  _execute(SYS, ["MegaCli64", "-CfgForeign", "-Clear", "-aall"])

  # Retrieve SAS controllers on PCI bus.
  lines = _execute(SYS, ["lspci"])
  for line in lines:
    w = line.split(' ',2); wl = len(w)
    if ' MegaRAID ' in w[2] or ' SAS ' in w[2] or ' SATA ' in w[2] or ' Virtio block ' in w[2]:
      Pn = _get_full_pci_address(w[0])
      if w[0] not in SYS['pci_xref']:
        SYS['pci_xref'][w[0]] = Pn

      if Pn not in SYS['controllers']:
        SYS['controllers'][Pn] = {}

      SYS['controllers'][Pn]['description'] = w[2]
      SYS['controllers'][Pn]['devs'] = _get_dev_list(SYS, Pn)
      SYS['controllers'][Pn]['type'] = w[1]

      if SYS['controllers'][Pn]['type'] == 'IDE' or SYS['controllers'][Pn]['type'] == 'SATA' or SYS['controllers'][Pn]['type'] == 'SCSI':
        SYS['internal_adapter_count'] += 1
        An = 1000 + SYS['internal_adapter_count']
        SYS['controllers'][Pn]['adapters'] = { An: { "counts": { "slots": len(SYS['controllers'][Pn]['devs']) } } }

        if An not in SYS['ctl_xref']:
          SYS['ctl_xref'][An] = Pn

  # Retrieve RAID adapter IDs:
  msg = []
  lines = _execute(SYS, ["MegaCli64", "-AdpGetPciInfo", "-aall"])
  for line in lines:
    w = line.split(); wl = len(w)

    if wl == 5 and w[0] == 'PCI' and w[3] == 'Controller':
      msg += [1]
      An = w[4]

    elif wl == 4 and w[0] == 'Bus' and w[1] == 'Number':
      msg += [2]
      Bn = w[3]

    elif wl == 4 and w[0] == 'Device' and w[1] == 'Number':
      msg += [3]
      Dn = w[3]

    elif wl == 4 and w[0] == 'Function' and w[1] == 'Number':
      msg += [4]
      Fn = w[3]

      Dn = '%s:%s.%s' % (_hexpad(Bn,2), _hexpad(Dn,2), _hexpad(Fn,1))
      if Dn not in SYS['pci_xref']:
        ansible_module.fail_json(msg='volume_configuration(main,%s): MegaCli64 -AdpGetPciInfo device %s not found by lspci.' % (_get_linenumber(), Dn))

      Pn = SYS['pci_xref'][Dn]
      if An not in SYS['ctl_xref']:
        SYS['ctl_xref'][An] = Pn

      if 'adapters' not in SYS['controllers'][SYS['pci_xref'][Dn]]:
        SYS['controllers'][SYS['pci_xref'][Dn]]['adapters'] = {}

      if An not in SYS['controllers'][SYS['pci_xref'][Dn]]['adapters']:
        SYS['controllers'][SYS['pci_xref'][Dn]]['adapters'][An] = {
          "counts": {
            "hs": 0,
            "jbod": 0,
            "online": 0,
            "slots": 0,
          },
          "enc": {},
          "LDs": {},
          "JBOD": "disabled"
        }

# ansible_module.fail_json(msg=msg) # parse command check

  # Retrieve enclosure/adapter information.
  msg = []
  lines = _execute(SYS, ["MegaCli64", "-EncInfo", "-aall"])
  for line in lines:
    w = line.split(); wl = len(w)

    if wl == 8 and w[0] == 'Number' and w[2] == 'enclosures' and w[4] == 'adapter':
      msg += [1]
      An = w[5]
      Pn = SYS['ctl_xref'][An]

    elif wl == 5 and w[0] == 'Number' and w[2] == 'Slots':
      msg += [2]
      slots = int(w[4])
      SYS['controllers'][Pn]['adapters'][An]['counts']['slots'] += slots
      SYS['controllers'][Pn]['adapters'][An]['enc'][En]['slots'] = slots

    elif wl == 2 and w[0] == 'Enclosure':
      msg += [3]
      En = w[1][:-1]
      SYS['controllers'][Pn]['adapters'][An]['enc'][En] = {}

    elif wl == 4 and w[0] == 'Device' and w[1] == 'ID':
      msg += [4]
      SYS['controllers'][Pn]['adapters'][An]['enc'][En]['id'] = w[3]

# ansible_module.fail_json(msg=msg) # parse command check

  # Retrieve adapter JBOD state.
  msg = []
  lines = _execute(SYS, ["MegaCli64", "-AdpGetProp", "EnableJBOD", "-aall"])
  for line in lines:
    w = line.split(); wl = len(w)

    if wl == 4 and w[0] == 'Adapter' and w[2] == 'JBOD:' and w[3] == 'Disabled':
      msg += [1]
      An = w[1][:-1]
      Pn = SYS['ctl_xref'][An]
      SYS['controllers'][Pn]['adapters'][An]['JBOD'] = 'disabled'

    if wl == 4 and w[0] == 'Adapter' and w[2] == 'JBOD:' and w[3] == 'Enabled':
      msg += [1]
      An = w[1][:-1]
      Pn = SYS['ctl_xref'][An]
      SYS['controllers'][Pn]['adapters'][An]['JBOD'] = 'enabled'
      
# ansible_module.fail_json(msg=msg) # parse command check

  # Create all disk bay variables.
  for Pn in sorted(SYS['controllers']):
    for An in sorted(SYS['controllers'][Pn]['adapters']):
      if SYS['controllers'][Pn]['type'] == 'RAID':
        for En in sorted(SYS['controllers'][Pn]['adapters'][An]['enc']):
          msg += [ An + ',' + En ]
          for Sn in range(SYS['controllers'][Pn]['adapters'][An]['enc'][En]['slots']):
            EnSn = '%s:%s' % (SYS['controllers'][Pn]['adapters'][An]['enc'][En]['id'], Sn)
            SYS['bays'] += [ { "An": An, "Disk": "-", "EnSn": EnSn } ]
            SYS['bay_xref'][EnSn] =  len(SYS['bays']) - 1
      elif SYS['controllers'][Pn]['type'] == 'IDE' or SYS['controllers'][Pn]['type'] == 'SATA' or SYS['controllers'][Pn]['type'] == 'SCSI':
        En = An
        for Sn in range(SYS['controllers'][Pn]['adapters'][An]['counts']['slots']):
            EnSn = '%s:%s' % (En, Sn)
            SYS['bays'] += [ { "An": An, "Disk": Sn, "EnSn": EnSn } ]
            SYS['bay_xref'][EnSn] =  len(SYS['bays']) - 1
      else:
        ansible_module.fail_json(msg='volume_configuration(main,%s): PCI controller type "%s" is invalid.' % (_get_linenumber(), SYS['controllers'][Pn]['type']))

# ansible_module.fail_json(msg=msg) # parse command check
      
  # Retrieve all physical device states.
  msg = []
  lines = _execute(SYS, ["MegaCli64", "-PDList", "-aall"])
  for line in lines:
    w = line.split(); wl = len(w)

    if wl == 4 and w[0] == 'Enclosure' and w[1] == 'Device' and w[2] == 'ID:':
      msg += [1]
      En = w[3]

    if wl == 3 and w[0] == 'Slot' and w[1] == 'Number:':
      msg += [2]
      Sn = w[2]
      EnSn = '%s:%s' % (En, Sn)
      Bn = SYS['bay_xref'][EnSn]

    if wl == 5 and w[0] == 'Firmware' and w[1] == 'state:' and w[2] == 'Online,' and w[3] == 'Spun' and w[4] == 'Up':
      msg += [3]
      SYS['bays'][Bn]['Disk'] = 'online'

    if wl == 5 and w[0] == 'Firmware' and w[1] == 'state:' and w[2] == 'Unconfigured(good),' and w[3] == 'Spun' and w[4] == 'Up':
      msg += [3]
      SYS['bays'][Bn]['Disk'] = 'available'

    if wl == 5 and w[0] == 'Firmware' and w[1] == 'state:' and w[2] == 'Hotspare,' and w[3] == 'Spun' and w[4] == 'Up':
      msg += [4]
      SYS['bays'][Bn]['Disk'] = 'hs'
      Pn = SYS['ctl_xref'][SYS['bays'][Bn]['An']]
      SYS['controllers'][Pn]['adapters'][SYS['bays'][Bn]['An']]['counts']['hs'] += 1

    if wl == 3 and w[0] == 'Firmware' and w[1] == 'state:' and w[2] == 'JBOD':
      msg += [5]
      SYS['bays'][Bn]['Disk'] = 'jbod'
      Pn = SYS['ctl_xref'][SYS['bays'][Bn]['An']]
      SYS['controllers'][Pn]['adapters'][SYS['bays'][Bn]['An']]['counts']['jbod'] += 1
      
# ansible_module.fail_json(msg=msg) # parse command check

  # Retrieve all logical device states.
  _get_LDs(SYS)
      
  # Retrieve LVM information.
  if _is_executable('pvscan'):
    lines = _execute(SYS, ['pvscan', '-u'])
    for line in lines:
      UUID = None
      w = line.split(); wl = len(w)
      if wl >=5 and w[0] == 'PV':
        SDx = w[1]; UUID = w[4]

        if len(SDx) > 5 and SDx[:5] == '/dev/':
          SYS['PVs'][UUID] = { 'device': SDx[5:].rstrip('0123456789'), 'status': 'ACTIVE', 'VG': '-', 'VG_UUID': '-', 'LVs': {} }
        else:
          SYS['PVs'][UUID] = { 'device': UUID, 'status': 'inactive', 'VG': '-', 'VG_UUID': '-', 'LVs': {} }

        SYS['PV_xref'][SYS['PVs'][UUID]['device']] = UUID

      if UUID:
        sublines = _execute(SYS, ['vgdisplay', '-S', 'pv_uuid=%s' % UUID])
        for line in sublines:
          w = line.split(); wl = len(w)
          if wl >=3 and w[0] == 'VG':
            if w[1] == 'Name':
              SYS['PVs'][UUID]['VG'] = w[2] 
              SYS['VG_xref'][w[2]] = UUID
            elif w[1] == 'UUID':
              SYS['PVs'][UUID]['VG_UUID'] = w[2] 

        if SYS['PVs'][UUID]['VG_UUID'] != '-':
          sublines = _execute(SYS, ["lvdisplay", '-S', 'vg_uuid=%s' % SYS['PVs'][UUID]['VG_UUID']])
          for line in sublines:
            w = line.split(); wl = len(w)
            if wl >=3 and w[0] == 'LV' and w[1] == 'Name':
              lv = w[2]
            elif wl >= 3 and w[1] == 'Size':
              SYS['PVs'][UUID]['LVs'][lv] = int(float(re.sub('[^0-9.]', '', w[2]))*1024)

  # Retrieve current mount information.
  lines = _execute(SYS, ['awk', 'NF>0 && !/^#/', '/etc/fstab'])
  for line in lines:
    w = line.split(); wl = len(w)

    if wl >= 3:
      if not w[0] in SYS['fstab']:
        SYS['fstab'][w[0]] = [ w[1], w[2], '-' ]
        SYS['fxtab'][w[1]] = w[0]

        if SYS['fstab'][w[0]][1] == 'swap':
          SYS['fstab'][w[0]][2] = w[0]

        if wl >=6 and SYS['fstab_fsck'] < int(w[5]):
          SYS['fstab_fsck'] = int(w[5])

  lines = _execute(SYS, ['df'])
  for ix in range(1, len(lines)):
    w = lines[ix].split(); dv = w[0]; mp = w[-1]
    dv_type, dv_path = _device_type_and_path(SYS, dv)
    SYS['dftab'][mp] = [dv_type, dv_path]

    if mp in SYS['fxtab']:
      SYS['fstab'][SYS['fxtab'][mp]][2] = dv

# ansible_module.fail_json(msg=msg) # parse command check

  # If fact gathering, display the facts and exit.
  if config_path == 'show':
    _debug_log("Completed.")
    ansible_module.exit_json(ansible_facts={ "ansible_volumes": { "SYS": SYS } }, changed=False)

  # If "DESTROY" is requested (config=DESTROY), destroy the existing disk confiuration, deleteing
  # all data (except the root (/) volume) and exit.
  if config_path == 'DESTROY':
    _debug_log("Destroying configuration...")
    _destroy_configuration(SYS)
    _debug_log("Configuration DESTROYed.")
    ansible_module.exit_json(changed=True)

  # Process configuration updates.
  changed = False
  fqdn = _execute(SYS, [ "hostname", "-f"])[0]
  config_path_expanded = os.path.expanduser(config_path)

  # Filter out config lines for other hosts and for the root filesystem.
  config = []
  lines = _execute(SYS, ["cat", config_path])
  for line in lines:
    w = line.split('|')
    if len(w) > 7 and w[0] == fqdn:
      config += [ w[1:] ] 
    else:
      if w[0] != fqdn:
        _debug_log('main, hostname (%s) does not match, ignoring: %s' % (fqdn, line))
      else:
        _debug_log('main, too few fields, ignoring: %s' % line)

  # Process storage device configuration request.
  _debug_log("Updating...")
  for request in config:
    _debug_log('main, request: %s' % request)

    RAIDlvl, Disks, VG, LV, GBs, FStype, Mountpoint = request

    if Mountpoint != '/':
      changed = _megacli(SYS, request, changed)
      changed = _lvm(SYS, request, changed)
      changed = _mkfs(SYS, request, changed)

  _debug_log("Completed.")
  ansible_module.exit_json(changed=changed)
# ansible_module.exit_json(ansible_facts={ "ansible_volumes": { "SYS": SYS } }, changed=changed)

if __name__ == '__main__':
  main()
