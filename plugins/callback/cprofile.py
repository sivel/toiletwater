# (c) 2018 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#     (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: cprofile
    short_description: Uses cProfile to profile the python execution of ansible
    description:
        - Uses cProfile to profile the python execution of ansible, allowing
          for filtering and sorting
    type: aggregate
    options:
      filters:
        description: A list of python packages to limit output to,
                     e.g. C(ansible.plugins.connection)
        default:
          - ansible
        env:
          - name: CPROFILE_FILTERS
        ini:
          - key: filters
            section: cprofile_callback
        type: list
      sort:
        description: Sort order of cProfile output
        default:
          - cumtime
        env:
          - name: CPROFILE_SORT
        ini:
          - key: sort
            section: cprofile_callback
        type: list
      strip_dirs:
        description: Whether or not to display stripped paths instead of full
                     paths. This functionality differs slightly from the native
                     cProfile implementation, as it will only strip the longest
                     common path.
        default: True
        env:
          - name: CPROFILE_STRIP_DIRS
        ini:
          - key: strip_dirs
            section: cprofile_callback
        type: bool
      per_host_task:
        description: Split output by (host, task) combo
        default: False
        env:
          - name: CPROFILE_PER_HOST_TASK
        ini:
          - key: per_host_task
            section: cprofile_callback
        type: bool
'''

import cProfile
import functools
import importlib.util
import json
import os
import pickle
import pstats
import shutil
import tempfile
import time
from contextlib import contextmanager
from glob import iglob

from ansible.errors import AnsibleError
from ansible.executor.process.worker import WorkerProcess
from ansible.module_utils.six import PY3
from ansible.playbook.block import Block
from ansible.plugins.callback import CallbackBase


VALID_SORTS = frozenset(pstats.Stats.sort_arg_dict_default.keys())


class Stats:
    """Class to mimic a pstats.Stats object, for loading"""
    def __init__(self, stats):
        self.stats = stats

    def create_stats(self):
        pass


def dump_stats(p, filename):
    p.create_stats()
    with open(filename, 'wb') as f:
        pickle.dump(p.stats, f)


def load_stats(filename):
    with open(filename, 'rb') as f:
        ps = pstats.Stats(Stats(pickle.load(f)))
    return ps


def find_module(module):
    """Find the path to a dotted python module"""
    spec = importlib.util.find_spec(module)
    if not spec:
        raise ImportError(module)
    if os.path.splitext(spec.origin)[1] == '.py':
        return os.path.dirname(spec.origin)
    return spec.origin


def filter_pstats(ps, filters):
    """Filter out stats from pstats based on a path filter"""
    for stat in list(ps.stats):
        found = False
        for f in filters:
            if stat[0].startswith(f):
                found = True
                break
        if not found:
            ps.total_calls -= ps.stats[stat][1]
            ps.prim_calls -= ps.stats[stat][0]
            ps.total_tt -= ps.stats[stat][2]
            del ps.stats[stat]
    return ps


def strip_filter(ps, filters=None):
    """Strip the matching filter from the paths"""
    dirname = os.path.dirname
    if filters:
        path = '%s/' % os.path.commonpath(
            [dirname(f) for f in filters]
        )
    else:
        path = '%s/' % os.path.commonpath(
            [dirname(key[0]) for key in ps.stats if key[0][0] == '/']
        )

    for stat, item in list(ps.stats.items()):
        index = stat[0].find(path)
        if index != 0:
            continue
        del ps.stats[stat]
        end = index + len(path)
        stat = (stat[0][end:],) + stat[1:]
        ps.stats[stat] = item
    return ps


def get_play(task):
    obj = task
    while obj._parent:
        if isinstance(obj._parent, Block):
            return obj._parent._play
        obj = obj._parent


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'sivel.toiletwater.cprofile'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)

        if not PY3:
            display.warning('The cprofile callback plugin requires Python3')
            self.disabled = True
        else:
            self._worker_tmp = tempfile.mkdtemp()

            WorkerProcess.run = self._profile_worker(WorkerProcess.run)

            self._p = cProfile.Profile()
            self._p.enable()

    def _profile_worker(self, func):
        """Closure for profiling ``WorkerProcess.run`` with ``cProfile``

        stats are dumped stats to a file for later retrieval
        """
        name = getattr(func, '__qualname__', func.__name__)

        @functools.wraps(func)
        def inner(wp):
            host = wp._host
            task = wp._task
            p = cProfile.Profile()
            p.create_stats()
            p.enable()
            try:
                func(wp)
            finally:
                p.disable()
                pstat_file = os.path.join(
                    self._worker_tmp,
                    '%s-%s-%s.pstat' % (
                        name,
                        os.getpid(),
                        time.time(),
                    )
                )
                with open('%s.json' % pstat_file, 'w+') as f:
                    json.dump(
                        {
                            'host': host.name,
                            'task_name': task.get_name(),
                            'task_uuid': task._uuid,
                            'play': get_play(task).get_name(),
                        },
                        f
                    )
                dump_stats(p, pstat_file)

        return inner

    def set_options(self, *args, **kwargs):
        super(CallbackModule, self).set_options(*args, **kwargs)

        filters = self.get_option('filters')
        sort = self.get_option('sort')
        strip_dirs = self.get_option('strip_dirs')
        self._per_host_task = self.get_option('per_host_task')

        if any(filters):
            self._filters = []
            for f in filters:
                if not f:
                    continue
                try:
                    self._filters.append(find_module(f))
                except ImportError as e:
                    raise AnsibleError(
                        'Invalid cprofile callback filter %s: %s' % (f, e)
                    )
        else:
            self._filters = None

        self._sort = sort
        self._strip_dirs = strip_dirs

        invalid = set(self._sort).difference(VALID_SORTS)
        if invalid:
            raise AnsibleError(
                'Invalid cProfile sort: %s' % ', '.join(invalid)
            )

    def v2_playbook_on_stats(self, stats):
        self._p.disable()

        tmp = self._worker_tmp

        if self._per_host_task:
            ps = pstats.Stats(self._p)
            if self._filters:
                filter_pstats(ps, self._filters)
            if self._strip_dirs:
                strip_filter(ps, self._filters)
            self._display.banner('Control')
            ps.sort_stats(*self._sort).print_stats()

            for item in iglob('%s/*.pstat' % tmp):
                ps = load_stats(item)
                if self._filters:
                    filter_pstats(ps, self._filters)
                if self._strip_dirs:
                    strip_filter(ps, self._filters)
                with open('%s.json' % (item)) as f:
                    data = json.load(f)
                self._display.banner(
                    '%(play)s - %(task_name)s - %(host)s' % data
                )
                ps.sort_stats(*self._sort).print_stats()
        else:
            ps = pstats.Stats(self._p)
            ps.add(
                *(load_stats(item) for item in iglob('%s/*.pstat' % tmp))
            )

            # Prevent ``print_stats`` from printing all files loaded from
            # the above ``ps.add``
            ps.files[:] = []

            if self._filters:
                filter_pstats(ps, self._filters)
            if self._strip_dirs:
                strip_filter(ps, self._filters)
            self._display.banner('Profile')
            ps.sort_stats(*self._sort).print_stats()

        try:
            shutil.rmtree(tmp)
        except Exception:
            pass
