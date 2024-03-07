# -*- coding: utf-8 -*-
# (c) 2021, Matt Martz  <matt@sivel.net>
# GNU General Public License v3.0+
#     (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


ARCH_MAP = {
    'i386': '386',
    'x86_64': 'amd64',
}


class ActionModule(ActionBase):

    _supports_async = True

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)

        new_args = self._task.args.copy()
        action = new_args.pop(
            'module',
            self._task.resolved_action or self._task.action
        )
        arch = new_args.pop('arch', 'auto')
        system = new_args.pop('system', 'auto')

        if arch == 'auto' or system == 'auto':
            conf = self._determine_auto(task_vars)
            result.update({f'_{k}': v for k, v in conf.items()})
            if arch == 'auto':
                arch = conf['architecture']
            if system == 'auto':
                system = conf['system']

        module = result['_module'] = f'{action}_{system}_{arch}'

        try:
            result.update(
                self._execute_module(
                    module_name=module,
                    module_args=new_args,
                    task_vars=task_vars,
                    wrap_async=self._task.async_val
                )
            )
        except AnsibleError as e:
            if module in f'{e}' and all((arch, system)):
                result.update({
                    'msg': (
                        'Could not find a binary module implementation of '
                        f'{action} for {system} {arch}.'
                    ),
                    'failed': True,
                })
            else:
                raise

        return result

    def _determine_auto(self, task_vars):
        conf = None
        try:
            if dt := self._task.delegate_to:
                conf = self._templar.template({
                    'system': (
                        "{{hostvars[%r].ansible_facts.system}}" % dt
                    ),
                    'architecture': (
                        "{{hostvars[%r].ansible_facts.architecture}}" % dt
                    ),
                })
            else:
                conf = self._templar.template({
                    'system': '{{ansible_facts.system}}',
                    'architecture': '{{ansible_facts.architecture}}',
                })
        except Exception:
            pass
        else:
            conf['system'] = conf['system'].lower()
            conf['architecture'] = conf['architecture'].lower()

        if not conf:
            gather_facts_task = self._task.copy()
            gather_facts_task.action = 'ansible.legacy.gather_facts'
            gather_facts_task.args = {
                'filter': [
                    'ansible_architecture',
                    'ansible_system',
                ],
                'gather_subset': ['!all', 'platform'],
            }
            gather_facts_action = self._shared_loader_obj.action_loader.get(
                'ansible.legacy.gather_facts',
                task=gather_facts_task,
                connection=self._connection,
                play_context=self._play_context,
                loader=self._loader,
                templar=self._templar,
                shared_loader_obj=self._shared_loader_obj,
            )
            facts = gather_facts_action.run(task_vars=task_vars)
            af = facts['ansible_facts']
            conf = {
                'system': af['ansible_system'].lower(),
                'architecture': af['ansible_architecture'].lower(),
            }

        arch = conf['architecture']
        conf['architecture'] = ARCH_MAP.get(arch, arch)
        return conf
