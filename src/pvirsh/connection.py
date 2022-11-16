#!/usr/bin/env python3
# Authors: Antoine Ginies <aginies@suse.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import libvirt
import pvirsh.util as util

class LibVirtConnect:
    """ Connection method to libvirt """
    def __init__(self, connector, dst):
        self.connector = connector
        self.dst = dst
        print(connector +" "+ dst)

    def local():
        """
        Local connection
        """
        conn = None
        try:
            conn = libvirt.open("qemu:///system")
            ver = conn.getVersion()
            util.print_ok('Connected; Version: '+str(ver))
            return conn
        except libvirt.libvirtError as verror:
            print(repr(verror), file=sys.stderr)
            return 666

    def remote(connector, dst):
        """
        Remote connection
        """
        dst_conn = None
        try:
            if connector.startswith('xen'):
                dst_conn = libvirt.open(connector+'://'+dst)
            else:
                dst_conn = libvirt.open(connector+'://'+dst+'/system')
            ver = dst_conn.getVersion()
            util.print_ok('Connected; Version: '+str(ver))
            return dst_conn
        except libvirt.libvirtError as verror:
            print(repr(verror), file=sys.stderr)
            return 666
