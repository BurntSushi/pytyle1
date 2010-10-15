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
TileState.py

Keeps a record of the state of your tiler. This is helpful for automatically
keeping window sizes consistent when new windows are added, removed, etc. 

TileState also interfaces with the LAYOUT config.
"""

from PyTyle.Config import Config

class TileState:
    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND INSTANCE METHODS
    #------------------------------------------------------------------------------
    
    #
    # Just starts the state and tiler instance variables.
    #
    def __init__(self, tiler):
        self._state = {}
        self._tiler = tiler
        
    #
    # Retrieves a state item. First we check our current state.
    # If we don't have a record of it, then look in the layout
    # config (and copy this value to our current state). Otherwise
    # return nothing- we don't have a state yet.
    #
    def get(self, key):
        if key in self._state:
            return self._state[key]
        elif Config.layout(self._tiler, key) is not None:
            self.set(key, Config.layout(self._tiler, key))
            return Config.layout(self._tiler, key)
        return None
    
    #
    # Empties the current state. Remember, the state *starts* as
    # empty, so tiling algorithms need to make sure they can
    # handle bad values. (Or put it in the config.)
    #
    def reset(self):
        self._state = {}
    
    #
    # Sets a state item.
    #
    def set(self, key, value):
        self._state[key] = value