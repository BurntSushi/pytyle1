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
Viewport.py

The Viewport class will handle all viewport related functionality. For instance,
it provides methods to detect if a given window is on its viewport.
"""

from PyTyle.State import State
from PyTyle.Probe import PROBE

from PyTyle.Screen import Screen

class Viewport:
    #------------------------------------------------------------------------------
    # CONSTRCUTOR AND VIEWPORT RELATED ATTRIBUTES/METHODS
    #------------------------------------------------------------------------------ 
    
    #
    # Initialization requies a desktop and attributes fetched from X. We also make
    # sure that it starts out with:
    #    1. Tiling disabled
    #    2. Untiled state
    #    3. No tiler
    #
    def __init__(self, desktop, attrs):
        self.update_attributes(attrs)
        self._SCREEN = None
        self.desktop = desktop 
        
        if PROBE.is_compiz():
            self.width = self.desktop.width
            self.height = self.desktop.height
        else:
            self.width = self.desktop.resx
            self.height = self.desktop.resy
        
        self.screens = {}
        self.load_screens()
    
    #
    # Takes a pair of x,y coordinates and tells us whether they are in the
    # viewport's grid. Also, take special care for windows with a negative x,y
    # position- simply say that it is on the viewport with x,y coordinates
    # equal to 0.
    #
    def is_on_viewport(self, x, y):
        if x >= self.x and y >= self.y and x < (self.x + self.width) and y < (self.y + self.height):
            return True
        
        # off the screen?
        if (x < 0 or y < 0) and self.x == 0 and self.y == 0:
            return True
        
        return False
    
    #
    # Probes X (using xinerama) for all available screens. For every viewport,
    # an instance of each screen is newly created. (So the total number of
    # "screens" in PyTyle is # of physical screens * viewports * desktops.) We 
    # do *not* queue screens for tiling here.
    #
    def load_screens(self):
        screens = PROBE.get_screens()
        for screen in screens:
            obj = Screen(self, screen)
            obj.x += self.x
            obj.y += self.y
            self.screens[screen['id']] = obj
                
    #
    # Updates viewport with attributes fetched from X.
    #
    def update_attributes(self, attrs):
        self.id = attrs['id']
        self.x = attrs['x']
        self.y = attrs['y']
        
    #
    # String representation of the current screen. See also the string
    # representations of desktop and window.
    #                
    def __str__(self):
        return 'Viewport ' + str(self.id) + ' - [ID: ' + str(self.id) + ', X: ' + str(self.x) + ', Y: ' + str(self.y) + ', WIDTH: ' + str(self.width) + ', HEIGHT: ' + str(self.height) + ', DESKTOP: ' + str(self.desktop.id) + ']'