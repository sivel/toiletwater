# (c) 2023 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#     (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: cprofile
    short_description: Noop inventory plugin used to enable cProfile
    description:
        - Noop inventory plugin used to enable cProfile as early as possible
        - Must be used with the C(sivel.toiletwater.cprofile) callback plugin
'''

import cProfile

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.plugins.loader import callback_loader


class InventoryModule(BaseInventoryPlugin):
    NAME = 'cprofile'

    def __init__(self):
        cprofile_cb = callback_loader.get('sivel.toiletwater.cprofile', class_only=True)
        cprofile_cb._p = p = cProfile.Profile()
        p.enable()
        super().__init__()

    def verify_file(self, path):
        return True
