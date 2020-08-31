# (c) 2017, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy


from functools import partial

from ansible.errors import AnsibleFilterError
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.module_utils.six import string_types
from ansible.module_utils.six.moves import configparser, StringIO


def from_ini(o):
    if not isinstance(o, string_types):
        raise AnsibleFilterError('from_ini requires a string, got %s' % type(o))
    parser = configparser.RawConfigParser()
    parser.optionxform = partial(to_text, errors='surrogate_or_strict')
    parser.readfp(StringIO(o))
    d = dict(parser._sections)
    for k in d:
        d[k] = dict(d[k])
        d[k].pop('__name__', None)
    if parser._defaults:
        d['DEFAULT'] = dict(parser._defaults)
    return d


def to_ini(o):
    if not isinstance(o, MutableMapping):
        raise AnsibleFilterError('to_ini requires a dict, got %s' % type(o))
    data = copy.deepcopy(o)
    defaults = configparser.RawConfigParser(data.pop('DEFAULT', {}))
    parser = configparser.RawConfigParser()
    parser.optionxform = partial(to_text, errors='surrogate_or_strict')
    for section, items in data.items():
        parser.add_section(section)
        for k, v in items.items():
            parser.set(section, k, v)
    out = StringIO()
    defaults.write(out)
    parser.write(out)
    return out.getvalue().rstrip()


class FilterModule(object):
    def filters(self):
        return {
            'to_ini': to_ini,
            'from_ini': from_ini
        }
