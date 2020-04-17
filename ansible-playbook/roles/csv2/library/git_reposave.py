#!/usr/bin/env python3
from ansible.module_utils.basic import *
from subprocess import Popen, PIPE
import os
import shutil
import sys
import time

def main():
    """
    This module will save any changed files that are about to be lost by a force pull
    request. Also saves a list of files that have been deleted which will also magically
    re-appear after a force pull request. The following play-book snippet demonstrates
    its' intended use:

        - name: save any changes in the git repository that we are about to pull down
          git_reposave:
              dest: /opt/cloudscheduler/

        - name: pull down git repository
          git:
              repo: 'https://github.com/hep-gc/cloudscheduler.git'
              dest: /opt/cloudscheduler/
              force: yes
              update: yes
              version: "{{ cs_git_branch }}"

    If there any changes to be saved, this module will create a new directory to save 
    the changed files and deleted files list as follows:

        <dest_reppository_path>/
            /git_reposave/
                20200206-102045/
                    deleted_files (if there are any)
                    <changed_file_1>
                    <changed_file_2>
                    <changed_file_N>

    """

    module = AnsibleModule(
        argument_spec = dict(
            dest      = dict(required=True)
        )
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    if not os.path.exists(module.params['dest']):
        module.exit_json(**result)

    if not os.path.isdir('%s/.git' % module.params['dest']):
        module.fail_json(msg='Specified dest "%s" in not a git repository.' % module.params['dest'])

    p = Popen([
        'git',
        'ls-files',
        '-m'
        ], cwd=module.params['dest'], stdout=PIPE, stderr=PIPE)
    stdout,stderr = p.communicate()

    if p.returncode != 0:
        module.fail_json(msg='Failed to "git ls-files -m"; %s' % stderr)

    if stdout == '':
        module.exit_json(**result)
        
    result['changed'] = True
    mods = stdout.split('\n')

    p = Popen([
        'git',
        'ls-files',
        '-d'
        ], cwd=module.params['dest'], stdout=PIPE, stderr=PIPE)
    stdout,stderr = p.communicate()

    if p.returncode != 0:
        module.fail_json(msg='Failed to "git ls-files -d"; %s' % stderr)

    delstring = stdout

    current_time = time.localtime()
    current_dir = '%sgit_reposave/%04d%02d%02d-%02d%02d%02d' % (
        module.params['dest'],
        current_time.tm_year,
        current_time.tm_mon,
        current_time.tm_mday,
        current_time.tm_hour,
        current_time.tm_min,
        current_time.tm_sec
        )

    os.makedirs(current_dir, mode=0o644)

    if delstring == '':
        dels = []
    else:
        dels = delstring.split('\n')
        with open('%s/deleted_file_list' % current_dir, 'w') as fd:
            fd.write(delstring)

    for file in mods:
        if file != '' and file not in dels:
            src = '%s%s' % (module.params['dest'], file)
            dst = '%s/%s' % (current_dir, file)
            try:
                os.makedirs(os.path.dirname(dst), mode=0o644)
            except:
                pass
            shutil.copyfile(src, dst)

#   module.fail_json(msg=current_dir)
    module.exit_json(**result)

if __name__ == '__main__':
    main()
