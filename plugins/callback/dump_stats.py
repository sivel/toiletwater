# (c) 2020 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#     (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: dump_stats
    short_description: Callback to dump to stats from set_stat to a JSON file
    description:
        - Dumps the stats from set_stat to a JSON file that can be fed to subsequent
          ansible-playbook calls using --extra-vars
    type: aggregate
    options:
      output:
        description: Output path to JSON file, defaults to stats.json in the CWD
        default: stats.json
        env:
          - name: DUMP_STATS_OUTPUT
        ini:
          - key: output
            section: dump_stats_callback
        type: str
    notes:
      - Run ansible-playbook with ANSIBLE_CALLBACK_WHITELIST=sivel.toiletwater.dump_stats
      - Call the 2nd playbook with --extra-vars @stats.json
'''

import json
import os

from ansible.errors import AnsibleError
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'sivel.toiletwater.dump_stats'
    CALLBACK_NEEDS_WHITELIST = True

    def set_options(self, *args, **kwargs):
        super(CallbackModule, self).set_options(*args, **kwargs)

        self._output = os.path.abspath(self.get_option('output'))
        output_dir = os.path.dirname(self._output)
        if not os.path.isdir(output_dir):
            try:
                os.path.makedirs(output_dir, mode=0o755)
            except Exception:
                pass

    def v2_playbook_on_stats(self, stats):
        with open(self._output, 'w+') as f:
            json.dump(
                stats.custom.get('_run', {}) if hasattr(stats, 'custom') else {},
                f
            )
