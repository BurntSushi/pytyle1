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
Desktop.py

A simple class to manage all desktops. It also includes a static
initialization method that will load all desktops reported by the
window manager. Each physical screen is initialized for each desktop.
This is also where tilers are initially set to screens.
"""

from PyTyle.Config import Config
from PyTyle.State import State
from PyTyle.Probe import PROBE

from PyTyle.Screen import *

class Desktop:
    #------------------------------------------------------------------------------
    # STATIC METHODS
    #------------------------------------------------------------------------------
    
    #
    # This is what really kicks it all off. It queries the window manager for all
    # available desktops, and instantiates them. When a desktop is initialized,
    # it will also load each of its screens. (Essentially, if xinerama reports two
    # available screens, then each screen will be attached to every desktop.)
    # Finally, this method also takes care of attaching a tiler to each screen,
    # which comes from the configuration file.
    #   
    @staticmethod
    def load_desktops():
        # initialize all desktops and their associated windows
        for desk in PROBE.get_desktops().values():
            desktop = Desktop(desk)
            for screen in desktop.screens.values():
                if screen.id in Config.TILING and isinstance(Config.TILING[screen.id], dict) and desktop.id in Config.TILING[screen.id]:
                    screen.set_tiler(Config.TILERS[Config.TILING[screen.id][desktop.id]])
                elif screen.id in Config.TILING and not isinstance(Config.TILING[screen.id], dict):
                    screen.set_tiler(Config.TILERS[Config.TILING[screen.id]])
                else:
                    screen.set_tiler(Config.TILERS[Config.TILING['default']])
                    
    
    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND DESKTOP RELATED ATTRIBUTES/METHODS
    #------------------------------------------------------------------------------ 
                    
    #
    # The desktop constructor takes a dict of attributes fetched from X. It also
    # adds itself to the current State and loads all of its screens.
    #
    def __init__(self, attrs):
        self.update_attributes(attrs)
        self.SCREEN = None
        self.screens = {}
        State.add_desktop(self)
        self.load_screens()
        
    #
    # Probes X (using xinerama) for all available screens. For every desktop,
    # an instance of each screen is newly created. (So the total number of
    # "screens" in PyTyle is # of physical screens * desktops.) We do *not*
    # queue screens for tiling here.
    #
    def load_screens(self):
        screens = PROBE.get_screens()
        for screen in screens:
            obj = Screen(self, screen)
            self.screens[screen['id']] = obj
            
    #
    # Simply updates all the desktop attributes. Currently only used in the
    # constructor. 
    #
    def update_attributes(self, attrs):
        self.id = attrs['id']
        self.resx = attrs['resx']
        self.resy = attrs['resy']
        self.x = attrs['x']
        self.y = attrs['y']
        self.width = attrs['width']
        self.height = attrs['height']
        self.name = attrs['name']
                
    #
    # Useful debugging string representation of the desktop. It prints
    # information about the current desktop, including each of its screens
    # and each window on each screen. See the string representations of
    # screen and window.
    #
    def __str__(self):
        retval = self.name + ' - [ID: ' + str(self.id) + ', RES: ' + str(self.resx) + 'x' + str(self.resy) + ', X: ' + str(self.x) + ', Y: ' + str(self.y) + ', WIDTH: ' + str(self.width) + ', HEIGHT: ' + str(self.height) + ']\n'
        
        for screen in self.screens.values():
            retval += '\t' + str(screen) + '\n'
        
            for window in screen.windows.values():
                retval += '\t\t' + str(window) + '\n'
            retval += '\n'
            
        return retval