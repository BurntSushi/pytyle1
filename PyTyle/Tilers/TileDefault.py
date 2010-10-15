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
TileDefault.py

TileDefault, in and of itself, cannot be used as a tiling algorithm. It
represents the methods that both the Vertical and Horizontal layouts have
in common. Both Vertical and Horizontal are subclasses of TileDefault.
"""

from PyTyle.Tile import Tile

class TileDefault (Tile):
    #------------------------------------------------------------------------------
    # OVERLOADED INSTANCE METHODS
    #------------------------------------------------------------------------------
    
    #
    # The common algorithm to cycle through all slaves for both the Horizontal
    # and Vertical layouts. Note that if there is more than one master, the first
    # master window will be swapped out. Also note that this will do nothing if
    # there are either no slaves or no masters. There will be nothing to cycle.
    #
    def _cycle(self):
        slaves = self.storage.get_slaves()
        masters = self.storage.get_masters()
        
        # Stop if neither of either... haha
        if not slaves or not masters:
            return
        
        # Might be a little high...
        if self.cycleIndex >= len(slaves):
            self.cycleIndex = len(slaves) - 1
        
        # use the index first to fetch the window to cycle
        self.help_switch(masters[0], slaves[self.cycleIndex])
        self.storage.get_masters()[0].activate()
        
        self.cycleIndex = self.cycleIndex + 1
        if self.cycleIndex == len(slaves): self.cycleIndex = 0
        
        
    #------------------------------------------------------------------------------
    # OVERLOADED PRIVATE HELPER METHODS
    #------------------------------------------------------------------------------ 
        
    #
    # Finds the next window. This is used both by the win_next and switch_next
    # tiling actions. It's a bit hairy, so I've commented the code as we go.
    #
    def help_find_next(self):
        # First retrieve all masters and all slaves... And also
        # pack them together.
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        all = masters + slaves
        
        # If there are masters, then we need to check if the currently
        # active window is the first master. If so, then we need to
        # focus on the first slave, or if there are no slaves, go to
        # the last master.
        if masters and self.screen.get_active().id == masters[0].id:
            if not slaves:
                return masters[-1]
            else:
                return slaves[0]
            
        # If there are slaves, then check if the active window is the
        # last slave. If it is, then focus on the last master, or if
        # there are no masters, then focus on the first slave.
        elif slaves and self.screen.get_active().id == slaves[-1].id:
            if not masters:
                return slaves[0]
            else:
                return masters[-1]
            
        # Now that our edge cases are satisfied, we simply find where
        # we are, and iterate to find the next window. (Same for masters
        # and slaves.)
        elif slaves and self.screen.get_active().id in [win.id for win in slaves]:
            for i in range(len(slaves) - 1):
                if self.screen.get_active().id == slaves[i].id:
                    return slaves[(i + 1)]
        elif masters:
            for i in range(1, len(masters)):
                if self.screen.get_active().id == masters[i].id:
                    return masters[(i - 1)]
        
    #
    # See help_find_next above. Also see the comments in the code,
    # as help_find_previous is basically the same thing- we're just
    # going in reverse.
    #
    def help_find_previous(self):
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        all = masters + slaves
        
        if masters and self.screen.get_active().id == masters[-1].id:
            if not slaves:
                return masters[0]
            else:
                return slaves[-1]
        elif slaves and self.screen.get_active().id == slaves[0].id:
            if not masters:
                return slaves[-1]
            else:
                return masters[0]
        elif masters and self.screen.get_active().id in [win.id for win in masters]:
            for i in range(len(masters) - 1):
                if self.screen.get_active().id == masters[i].id:
                    return masters[(i + 1)]
        elif slaves:
            for i in range(1, len(slaves)):
                if self.screen.get_active().id == slaves[i].id:
                    return slaves[(i - 1)]