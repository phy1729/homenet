# Copyright (c) 2025 Matthew Martin <phy1729@gmail.com>
# ISC

DOCUMENTATION = r'''
---
module: firefox_profiles_info

short_description: Query firefox profile info

description: Get information about a user's firefox profiles.

options:
    user:
        description: User whose profiles to retrieve.
        required: true
        type: str

author:
    - Matthew Martin (@phy1729)
'''

EXAMPLES = r'''
- name: Get firefox profiles
  firefox_profiles_info:
    user: phy1729
  register: profiles
'''

RETURN = r'''
profiles:
    description: A dictionary mapping a profile's name to it's values
    type: dict[str, dict[str, Any]]
    returned: always
    sample:
        default:
            default: 1
            isrelative: 1
            name: default
            path: abcdefgh.default
'''

from configparser import ConfigParser
from os.path import expanduser

from ansible.module_utils.basic import AnsibleModule


def main() -> None:
    module_args = {
        'user': {
            'type': 'str',
            'required': True,
        },
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    config = ConfigParser()
    path = expanduser(f'~{module.params["user"]}/.mozilla/firefox/profiles.ini')
    config.read(path)

    profiles = {
        section['Name']: dict(section)
        for section_name, section in config.items()
        if section_name.startswith('Profile')
    }

    module.exit_json(
        changed=False,
        profiles=profiles,
    )


if __name__ == '__main__':
    main()
