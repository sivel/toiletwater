# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#     (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.six import text_type
from ansible.parsing.ajson import AnsibleJSONEncoder

from jinja2 import Undefined


try:
    import jq
    HAS_JQ = True
except ImportError:
    HAS_JQ = False


def do_jq(value, expression, text=False, multiple=False):
    if not HAS_JQ:
        raise AnsibleFilterError(
            'jq python module required for use of the |jq filter'
        )

    # fire undefined error
    for v in (value, expression):
        if isinstance(v, Undefined):
            str(v)

    try:
        program = jq.compile(to_text(expression))
    except ValueError as e:
        raise AnsibleFilterError(
            'Error compile jq expression: %s' % to_native(e)
        )
    except AttributeError as e:
        raise AnsibleFilterError(
            'Invalid type (%s) provided as an expression: %s' % (
                type(expression),
                to_native(e)
            )
        )
    except Exception as e:
        raise AnsibleFilterError(
            'Unknown error compiling jq expression: %s' % to_native(e)
        )

    kwargs = {}
    if isinstance(value, text_type):
        kwargs['text'] = value
    else:
        kwargs['text'] = json.dumps(value, cls=AnsibleJSONEncoder)

    try:
        ret = program.input(**kwargs)
        if text:
            return ret.text()
        elif multiple:
            return ret.all()
        else:
            return ret.first()

    except TypeError as e:
        raise AnsibleFilterError(
            'Invalid type (%s) provided as value: %s' % (
                type(value),
                to_native(e)
            )
        )
    except Exception as e:
        raise AnsibleFilterError(
            'Unknown error evaluating jq expression against %r: %s' % (
                value,
                to_native(e)
            )
        )


class FilterModule(object):
    def filters(self):
        filters = {
            'jq': do_jq,
        }

        return filters
