#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    module: substring
    short_description: Search for substring in file
    description:
        - Search for substring in a file and return matches
    options:
        path:
            description: Path to a file to search within
            type: path
            required: true
        pattern:
            description: Python regex pattern to look for
            type: str
            required: true
        all:
            description: Return all matches instead of the first
            type: bool
            default: false
        scope:
            description: Whether to restrict search to the whole file
                         or line by line
            type: str
            default: full
            choices:
                - full
                - line
    requirements: []
    notes:
        - For multi-line, dot matches all, case insensitve, and other regex
          flags, use a preceding string in your regex in the format of
          ``(?aiLmsux)``, such as ``(?i)cAsE_iNsEnSiTiVe``.
          See U(http://docs.python.org/3/library/re.html)
    author: 'Matt Martz (@sivel)'
'''

EXAMPLES = r'''
- name: Find ansible in setup.py
  substring:
    path: setup.py
    regex: '(?i)(ansible)'
    all: yes
  register: result

- debug:
    var: result
'''


import mmap
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_native


def regex(v):
    b_value = to_bytes(v, errors='surrogate_or_strict')
    try:
        return re.compile(b_value)
    except Exception as e:
        raise TypeError(to_native(e))


def full_search(path, pattern, return_all):
    b_path = to_bytes(path, errors='surrogate_or_strict')
    with open(b_path, 'rb') as f:
        mm_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        matches = pattern.finditer(mm_file)
        if not return_all:
            return [format_match(next(matches), mm_file=mm_file)]
        return [format_match(m, mm_file=mm_file) for m in matches]


def line_search(path, pattern, return_all):
    b_path = to_bytes(path, errors='surrogate_or_strict')
    i = 0
    ret = []
    with open(b_path, 'rb') as f:
        for line in f:
            i += 1
            matches = pattern.finditer(line)
            try:
                if not return_all:
                    ret.append(format_match(next(matches), lineno=i))
                    break
                ret.extend(format_match(m, lineno=i) for m in matches)
            except StopIteration:
                continue
    return ret


def format_match(match, mm_file=None, lineno=None):
    span = match.span()
    if mm_file is not None:
        lineno = mm_file[:span[0]].count(b'\n') + 1
        try:
            column = span[0] - mm_file[:span[0]].rindex(b'\n')
        except ValueError:
            column = span[0] + 1
    elif lineno is not None:
        column = span[0] + 1
    return {
        'span': span,
        'lineno': lineno,
        'column': column,
        'match': match.group(0),
        'groups': match.groups(),
        'groupdict': match.groupdict(),
    }


def main():
    module = AnsibleModule(
        argument_spec={
            'path': {
                'type': 'path',
                'required': True,
            },
            'pattern': {
                'type': 'str',
                'required': True,
            },
            'all': {
                'type': 'bool',
                'default': False,
            },
            'scope': {
                'type': 'str',
                'choices': [
                    'full',
                    'line',
                ],
                'default': 'full',
            },
        },
    )

    try:
        pattern = regex(module.params['pattern'])
    except TypeError as e:
        module.fail_json(msg='pattern must be valid regex: %s' % e)

    if module.params['scope'] == 'full':
        search = full_search
    else:
        search = line_search

    try:
        matches = search(
            module.params['path'],
            pattern,
            module.params['all'],
        )
    except StopIteration:
        matches = []
        found = False
    else:
        found = bool(matches)

    module.exit_json(matches=matches, found=found, failed=not found)


if __name__ == '__main__':
    main()
