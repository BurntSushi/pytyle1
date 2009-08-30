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
Vertical.py

The most basic and default tiling algorithm. It consists of a master pane
on the left, and keeps the slaves over to the right.

Remember that this class inherits _cycle, help_find_next, and help_find_previous
from TileDefault.

Note that if you're creating your own tiling algorithm, you *MUST* add
    CLASS = CLASS_NAME
at the bottom of your class definition file (see the bottom of this file
for an example). This is so tiling algorithms can be dynamically loaded.
"""

from PyTyle.Tilers.TileDefault import TileDefault

class Vertical (TileDefault):
    #------------------------------------------------------------------------------
    # OVERLOADED INSTANCE METHODS
    #------------------------------------------------------------------------------
    
    #
    # The core tiling algorithm. Every core tiling algorithm should start with
    # grabbing the current screen's workarea and factoring that into your
    # calculations. Feel free to follow my approach to tiling algorithms, or
    # come up with something else.
    #
    # Note: As I've been going through the source code writing these comments,
    # I've been thinking about generalizing tiling algorithms even more. So this
    # approach could change a little in the future. (Although I imagine the class
    # hierarchy will be staying the same, I like it.)
    #
    def _tile(self):
        x, y, width, height = self.screen.get_workarea()
        
        # set some vars...
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        
        masterWidth = width if not slaves else int(width * self.state.get('width_factor'))
        masterHeight = height if not masters else (height / len(masters))
        masterY = y
        masterX = x
        
        slaveWidth = width if not masters else width - masterWidth
        slaveHeight = height if not slaves else (height / len(slaves))
        slaveY = y
        slaveX = x if not masters else (x + masterWidth)
        
        # resize the master windows
        for master in masters:
            self.help_resize(master, masterX, masterY, masterWidth, masterHeight)                
            masterY += masterHeight
        
        # now resize the rest... keep track of heights/positioning
        for slave in slaves:
            self.help_resize(slave, slaveX, slaveY, slaveWidth, slaveHeight)                
            slaveY += slaveHeight
    
    #
    # Increases the width of all master windows. Don't forget to decrease
    # the width of all slave windows. Won't do anything if there are either
    # no masters or no slaves.
    # 
    def _master_increase(self, factor = 0.05):
        x, y, width, height = self.screen.get_workarea()

        slaves = self.storage.get_slaves()
        masters = self.storage.get_masters()
        
        # Stop if neither of either... haha
        if not slaves or not masters:
            return
        
        # first calculate pixels...
        pixels = int(((self.state.get('width_factor') + factor) * width) - (self.state.get('width_factor') * width))
        self.state.set('width_factor', self.state.get('width_factor') + factor)
        
        for slave in slaves:
            slave.resize(slave.x + pixels, slave.y, slave.width - pixels, slave.height)
        for master in masters:            
            master.resize(master.x, master.y, master.width + pixels, master.height)
    
    #
    # Decreases the width of all master windows. Don't forget to increase
    # the width of all slave windows. Won't do anything if there are either
    # no masters or no slaves.
    # 
    def _master_decrease(self, factor = 0.05):
        x, y, width, height = self.screen.get_workarea()
        
        slaves = self.storage.get_slaves()
        masters = self.storage.get_masters()
        
        # Stop if neither of either... haha
        if not slaves or not masters:
            return
        
        # first calculate pixels...
        pixels = int((self.state.get('width_factor') * width) - ((self.state.get('width_factor') - factor) * width))
        self.state.set('width_factor', self.state.get('width_factor') - factor)
        
        for slave in slaves:
            slave.resize(slave.x - pixels, slave.y, slave.width + pixels, slave.height)
        for master in masters:            
            master.resize(master.x, master.y, master.width - pixels, master.height)
            
# You must have this line's equivalent for your tiling algorithm!
# This makes it possible to dynamically load tiling algorithms.
# (So that you may simply drop them into the Tilers directory,
# and add their name to the configuration- vini, vidi, vicci!)
CLASS = Vertical