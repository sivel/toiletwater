#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    module: cert_locations
    short_description: Returns list of SSL CA cert locations used by ansible.module_utils.urls
    description:
        - Returns list of SSL CA cert locations used by ansible.module_utils.urls
    options: {}
    requirements: []
    notes: []
    author: 'Matt Martz (@sivel)'
'''

EXAMPLES = r'''
- name: Get CA paths used by ansible.module_utils.urls
  cert_locations:
  register: result

- debug:
    var: result
'''

import os
import ssl

from ansible.module_utils.basic import AnsibleModule
try:
    from ansible.module_utils.urls import SSLValidationHandler
except ImportError:
    from ansible.module_utils.urls import get_ca_certs
else:
    get_ca_certs = SSLValidationHandler(None, None).get_ca_certs


def main():
    module = AnsibleModule({})
    paths = get_ca_certs()[-1]
    try:
        default = ssl.get_default_verify_paths()
    except AttributeError:
        pass
    else:
        paths[0:0] = [
            default.capath or default.cafile
        ]

    seen = set()
    cleaned = []
    for path in paths:
        if not path or path in seen:
            continue
        if not os.path.exists(path):
            continue
        cleaned.append(path)
        seen.add(path)

    module.exit_json(paths=cleaned)


if __name__ == '__main__':
    main()
