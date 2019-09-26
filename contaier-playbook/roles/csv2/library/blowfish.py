#!/usr/bin/env python3
from ansible.module_utils.basic import *
import bcrypt

# Set up the global ansible_module environment.
ansible_module = AnsibleModule(
  argument_spec = dict(
    password = dict(required=False, no_log=True),
  )
)

def main():
    clear_text_password = ansible_module.params['password']

    # If help requested (config=None), print messages and exit.
    if clear_text_password == None:
      help = [
        'Use the ansible module \'blowfish\' to encrypt a password.The module is invoked as follows:',
        '',
        '  ansible -m blowfish {-a password=<clear_text_password>}',
        '',
        ]
      ansible_module.exit_json(ansible_facts={ "blowfish": { "Help": help } }, changed=False)

    ansible_module.exit_json(ansible_facts={
        "blowfish": {
            "hash": bcrypt.hashpw(clear_text_password.encode(), bcrypt.gensalt(prefix=b"2a"))
        }
    }, changed=False)

if __name__ == '__main__':
    main()
