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
Cascade.py

Performs a full screen cascading layout of all the windows. It's important that
we're able to access the window decoration sizes.
"""

from PyTyle.Tilers.TileDefault import TileDefault

class Cascade (TileDefault):
    #------------------------------------------------------------------------------
    # OVERLOADED INSTANCE METHODS
    #------------------------------------------------------------------------------
        
    #
    # This Cascade layout will essentially do the following:
    #    1. The first window (or bottom) window takes up the full screen.
    #    2. Each subsequent window has its height shrinked by the height of
    #       the window decoration.
    #
    def _tile(self):
        x, y, width, height = self.screen.get_workarea()
        
        # set some vars...
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        
        # If we don't have any decorations... use hard coded value for now
        if masters and masters[0].d_top:
            decor = masters[0].d_top
        elif slaves and slaves[0].d_top:
            decor = slaves[0].d_top
        else:
            decor = self.state.get('decoration_height')
        
        push_over = self.state.get('push_over')
        push_width = push_over
        if self.state.get('horz_align') == 'right':
            push_over = -push_over
        
        masterWidth = (width * self.state.get('width_factor')) - (push_width * len(slaves))
        masterHeight = (height * self.state.get('height_factor')) - (decor * len(slaves))
        masterY = y + (decor * len(slaves))
        
        slaveWidth = width * self.state.get('width_factor')
        slaveHeight = height * self.state.get('height_factor')
        slaveY = y
        
        if self.state.get('horz_align') == 'right':
            masterX = x + (width - masterWidth) + (push_over * len(slaves))
            slaveX = x + (width - slaveWidth)
            push_over = 0
        else:
            masterX = x + (push_over * len(slaves))
            slaveX = x
        
        # now resize the rest... keep track of heights/positioning
        for slave in slaves:
            self.help_resize(slave, slaveX, slaveY, slaveWidth, slaveHeight)
            slaveY += decor
            slaveHeight -= decor
            slaveWidth -= push_width
            slaveX += push_over
            slave.stack_raise()
            
        # resize the master windows
        for master in masters:
            self.help_resize(master, masterX, masterY, masterWidth, masterHeight)
            master.stack_raise()
            
        # just in case...
        self.screen.get_active().stack_raise()
    
    #
    # Not changing much functionality here. Just overloading, inheriting, and
    # making sure the stacking order is kept.
    #
    def _cycle(self):
        TileDefault._cycle(self)
        self.help_reset_stack()
        
    def _make_active_master(self):
        TileDefault._make_active_master(self)
        self.help_reset_stack()
        
    def _win_master(self):
        TileDefault._win_master(self)
        self.help_reset_stack()

    def _win_previous(self):
        self.help_find_previous().activate()
        self.help_reset_stack()

    def _switch_previous(self):
        TileDefault._switch_previous(self)        
        self.help_reset_stack()  

    def _switch_next(self):
        TileDefault._switch_next(self)        
        self.help_reset_stack()
        
    #
    # We want to disable the following methods. They are of no use for this
    # layout.
    # 
    def _master_increase(self, pixels = 50):
        pass
    
    def _master_decrease(self, pixels = 50):
        pass
    
    def _add_master(self):
        pass
    
    def _remove_master(self):
        pass 
    
    
    #------------------------------------------------------------------------------
    # PRIVATE HELPER METHODS
    #------------------------------------------------------------------------------
    
    #
    # Same exact thing as Tile.help_reload, except we add to the top
    # of the window stack instead.
    #
    def help_reload(self):
        # delete first...
        for win in self.storage.get_all():
            if win.id not in self.screen.windows or win.hidden:
                self.storage.remove(win)
                
        # gobble up active window first in case we need a master...
        # and then just add away...
        masters = self.storage.get_masters_by_id()
        
        if self.screen.get_active() and len(masters) < self.storage.get_master_count() and self.screen.get_active().id in self.screen.windows and self.screen.get_active().id not in masters:
            self.storage.remove(self.screen.get_active())
            self.storage.add(self.screen.get_active())
            masters = self.storage.get_masters_by_id()                
        
        all = self.storage.get_all_by_id()
        for window in self.screen.windows.values():
            if not window.id in all:
                self.storage.add_top(window)
            else:
                self.storage.try_to_promote(window) 
     
    #
    # Resets the stacking order. I'm not sure if this is the best way to
    # do it, but it seems fairly quick. There's a small flicker, but that's
    # it. Maybe be more selective with its use?
    # 
    def help_reset_stack(self):
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        
        # now set the stacking order straight...
        for slave in slaves:
            slave.stack_raise()
        self.screen.get_active().stack_raise()
            
# You must have this line's equivalent for your tiling algorithm!
# This makes it possible to dynamically load tiling algorithms.
# (So that you may simply drop them into the Tilers directory,
# and add their name to the configuration- vini, vidi, vicci!)
CLASS = Cascade