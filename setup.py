#===============================================================================
# PyTyle - A manual tiling manager
# Copyright (C) 2009  Andrew Gallant <andrew@pytyle.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#===============================================================================

import sys
from distutils import sysconfig
from distutils.core import setup

try:
    from Xlib.display import Display
    from Xlib import X, XK, Xatom, Xutil, protocol
    from Xlib.ext import xinerama
except:
    print ''
    print 'PyTyle requires the Python X Library'
    print 'See: http://python-xlib.sourceforge.net/'
    sys.exit(0)

setup(
      name = "pytyle",
      author = "Andrew Gallant",
      author_email = "andrew@pytyle.com",
      version = "0.7.5",
      license = "GPL",
      description = "A manual tiling manager for EWMH compliant window managers",
      long_description = "See README",
      url = "http://pytyle.com",
      platforms = 'POSIX',
      packages = ['PyTyle', 'PyTyle.Tilers'],
      data_files = [
                    (sysconfig.get_python_lib() + '/PyTyle',
                     ['./pytylerc', './INSTALL', './LICENSE', './README', './TODO', './CHANGELOG'])
                    ],
      scripts = ['pytyle','pytyle-client']
      )
