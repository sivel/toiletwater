# (c) 2017, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError, AnsibleRuntimeError
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.module_utils.six import string_types

from ansible.plugins.inventory.toml import toml_dumps
try:
    from ansible.plugins.inventory.toml import toml_loads
except ImportError:
    def toml_loads(v):
        raise AnsibleRuntimeError(
            'The python "toml" or "tomli" library is required.'
        )


def from_toml(o):
    if not isinstance(o, string_types):
        raise AnsibleFilterError('from_toml requires a string, got %s' % type(o))
    return toml_loads(to_text(o, errors='surrogate_or_strict'))


def to_toml(o):
    if not isinstance(o, MutableMapping):
        raise AnsibleFilterError('to_toml requires a dict, got %s' % type(o))
    return to_text(toml_dumps(o), errors='surrogate_or_strict')


class FilterModule(object):
    def filters(self):
        return {
            'to_toml': to_toml,
            'from_toml': from_toml
        }
