# Copyright: Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#    (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import contextlib

from ansible.errors import AnsibleFilterError

PASSLIB_E = None
HAS_PASSLIB = False
try:
    import passlib.hash
    from passlib.ifc import PasswordHash
    HAS_PASSLIB = True
except ImportError as e:
    PASSLIB_E = e


def _is_password_hash(name):
    obj = getattr(passlib.hash, name, None)
    with contextlib.suppress(TypeError):
        if issubclass(obj, PasswordHash):
            return True
    return False


def do_passlib_hash(secret, hashtype='sha512', salt=None, salt_size=None,
                    rounds=None, ident=None, **kwargs):
    if not HAS_PASSLIB:
        raise AnsibleFilterError(
            'python passlib required for passlib filter',
            orig_exc=PASSLIB_E
        )

    try:
        algo = getattr(passlib.hash, hashtype)
    except AttributeError:
        algos = ', '.join(
            k for k in dir(passlib.hash) if _is_password_hash(k)
        )
        raise AnsibleFilterError(
            f'{hashtype!r} is not a valid passlib hash algorithm. '
            f'Valid algorithms: {algos}'
        )

    settings = kwargs.copy()
    if salt:
        settings['salt'] = salt
    if salt_size:
        settings['salt_size'] = salt_size
    if rounds:
        settings['rounds'] = rounds
    if ident:
        settings['ident'] = ident

    if invalid := set(settings) - set(algo.setting_kwds):
        raise AnsibleFilterError(
            f'Invalid options provided for {hashtype!r}: {", ".join(invalid)}'
        )

    try:
        result = algo.using(**settings).hash(secret)
    except ValueError as e:
        raise AnsibleFilterError('Unable to hash secret', orig_exc=e)

    if not result:
        raise AnsibleFilterError(f'Failed to hash secret with {hashtype!r}')

    return result


class FilterModule(object):
    def filters(self):
        return {
            'passlib_hash': do_passlib_hash,
        }
