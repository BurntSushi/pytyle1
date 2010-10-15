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

"""
Debug.py

A very simple class to log messages.
"""

import time, os, sys
from PyTyle.Config import Config
from PyTyle.State import State

class Debug:
    #------------------------------------------------------------------------------
    # CONSTRCUTOR AND INSTANCE METHODS
    #------------------------------------------------------------------------------
    
    
    #
    # Simply opens the log file. Keep the log file going.
    #
    def __init__(self, filename):
        self._log = sys.stderr
        if Config.DEBUG:
            self._log = open(filename, 'a+')
            print >> self._log, '\n\n', '---------------------------------'
            self.write('PyTyle started')
            
    #
    # Writes a message to the log file
    #
    def write(self, msg):
        if not self._log:
            return
        
        t = time.localtime()
        write = '%d/%d/%d at %d:%d:%d:    %s' % (t.tm_mon, t.tm_mday, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec, msg)
        print >> self._log, write 
        self._log.flush()
        
DEBUG = Debug(os.getenv('HOME') + '/pytyle.log')