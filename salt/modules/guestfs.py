# -*- coding: utf-8 -*-
'''
Interact with virtual machine images via libguestfs

:depends:   - libguestfs
'''
from __future__ import absolute_import

# Import Python libs
import os
import tempfile
import hashlib
import logging
log = logging.getLogger(__name__)
# Import Salt libs
import salt.utils


def __virtual__():
    '''
    Only load if libguestfs python bindings are installed
    '''
    if salt.utils.which('guestmount'):
        return 'guestfs'
    return False


def mount(location, access='rw'):
    '''
    Mount an image

    CLI Example:

    .. code-block:: bash

        salt '*' guest.mount /srv/images/fedora.qcow
    '''
    root = os.path.join(
            tempfile.gettempdir(),
            'guest',
            location.lstrip(os.sep).replace('/', '.')
            )
    if not os.path.isdir(root):
        try:
            os.makedirs(root)
        except OSError as exp:
            log.error('OSError {0}'.format(exp))
            # somehow the directory already exists
    while True:
        if os.listdir(root):
            # Stuf is in there, don't use it
            hash_type = getattr(hashlib, __opts__.get('hash_type', 'md5'))
            rand = hash_type(os.urandom(32)).hexdigest()
            root = os.path.join(
                tempfile.gettempdir(),
                'guest',
                location.lstrip(os.sep).replace('/', '.') + rand
                )
        else:
            break
    cmd = 'guestmount -i -a {0} --{1} {2}'.format(location, access, root)
    __salt__['cmd.run'](cmd, python_shell=False)
    return root
