# Copyright (c) 2025 Matthew Martin <phy1729@gmail.com>
# ISC

DOCUMENTATION = r'''
---
module: firefox_extension_preferences

short_description: Set firefox extension preferences.

description: Set firefox extension preferences.

extends_documentation_fragment:
    - files

options:
    extension:
        description: Id of the extension on which to set the preference.
        required: true
        type: str
    permission:
        description: Permission to set on the extension.
        required: true
        type: str
    profile_path:
        description: Path to the Firefox profile.
        required: true
        type: str

author:
    - Matthew Martin (@phy1729)
'''

EXAMPLES = r'''
- name: Get firefox profiles
  firefox_extension_preferences:
    profile_path:
    extension: uBlock0@raymondhill.net
    permission: internal:privateBrowsingAllowed
'''

from copy import deepcopy
from json import dump
from json import load
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule


def main() -> None:
    module = AnsibleModule(
        argument_spec={
            'profile_path': {
                'type': 'str',
                'required': True,
            },
            'extension': {
                'type': 'str',
                'required': True,
            },
            'permission': {
                'type': 'str',
                'required': True,
            },
        },
        add_file_common_args=True,
        supports_check_mode=True
    )
    extension = module.params['extension']
    permission = module.params['permission']

    changed = False
    diff = {
        'before': {},
        'after': {},
    }

    path = Path(module.params['profile_path'])/'extension-preferences.json'

    try:
        with path.open() as stream:
            preferences = load(stream)
    except FileNotFoundError:
        preferences = {}

    ext_preferences = preferences.get(extension, {
        'origins': [],
        'permissions': [],
    })

    if permission not in ext_preferences['permissions']:
        changed = True
        diff['before']['preferences'] = deepcopy(preferences)
        ext_preferences['permissions'].append(permission)
        preferences[extension] = ext_preferences
        diff['after']['preferences'] = preferences

        if not module.check_mode:
            with path.open('w') as stream:
                dump(preferences, stream, separators=(',', ':'))

    file_args = module.load_file_common_arguments(module.params, path=str(path))
    changed = module.set_fs_attributes_if_different(file_args, changed, diff, expand=False)

    module.exit_json(changed=changed, diff=diff)


if __name__ == '__main__':
    main()
