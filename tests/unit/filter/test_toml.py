# Copyright: (c) 2018, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

import collections
OrderedDict = getattr(collections, 'OrderedDict', dict)

from ansible_collections.sivel.toiletwater.plugins.filter import toml


dict_data = OrderedDict([
    ('DEFAULT', OrderedDict([('remove_unused_original_minimum_age_seconds', 16000)])),
    ('libvirt', OrderedDict([('cpu_mode', 'host-model'), ('disk_cachemodes', 'file=directsync,block=none')])),
    ('database', OrderedDict([('idle_timeout', 900), ('max_pool_size', 30)]))
])

toml_data = '''[DEFAULT]
remove_unused_original_minimum_age_seconds = 16000

[libvirt]
cpu_mode = "host-model"
disk_cachemodes = "file=directsync,block=none"

[database]
idle_timeout = 900
max_pool_size = 30
'''


@pytest.mark.skipif(OrderedDict is dict, reason="requires python2.7 or higher")
def test_to_toml():
    assert toml.toml_loads(toml.to_toml(dict_data)) == dict_data


def test_from_toml():
    assert toml.from_toml(toml_data) == dict_data
