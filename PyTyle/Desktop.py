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

from PyTyle.Viewport import Viewport

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
            for viewport in desktop.viewports.values():
                for screen in viewport.screens.values():
                    desk_or_view = desktop.id
                    if PROBE.is_compiz():
                        desk_or_view = viewport.id
                        
                    screen.set_tiler(Config.tilers(Config.tiling(screen.id, desk_or_view)))
                    
    #
    # Simply refreshes the desktop information. Used mainly when the workarea
    # changes to accomodate docks/panels.
    #
    @staticmethod
    def refresh_desktops():
        for desk in PROBE.get_desktops().values():
            if desk['id'] in State.get_desktops():
                desktop = State.get_desktops()[desk['id']]
                desktop.update_attributes(desk)
                for viewport in desktop.viewports.values():
                    for screen in viewport.screens.values():
                        screen.needs_tiling()
                    
    #
    # Same as "load_desktops" except we're just refreshing their information.
    #   
    @staticmethod
    def reload_desktops():
        # initialize all desktops and their associated windows
        for desktop in State.get_desktops().values():
            for viewport in desktop.viewports.values():
                for screen in viewport.screens.values():
                    desk_or_view = desktop.id
                    if PROBE.is_compiz():
                        desk_or_view = viewport.id
                        
                    screen.set_tiler(Config.tilers(Config.tiling(screen.id, desk_or_view)))
                    screen.needs_tiling()
                    
    
    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND DESKTOP RELATED ATTRIBUTES/METHODS
    #------------------------------------------------------------------------------ 
                    
    #
    # The desktop constructor takes a dict of attributes fetched from X. It also
    # adds itself to the current State and loads all of its screens.
    #
    def __init__(self, attrs):
        self.update_attributes(attrs)
        self._VIEWPORT = None
        self.viewports = {}
        State.add_desktop(self)
        self.load_viewports()
        
    #
    # Probes X for all available viewports. For every desktop, an instance
    # of each viewport is newly created. (So the total number of "screens" 
    # in PyTyle is # of physical screens * viewports * desktops.)
    #
    def load_viewports(self):
        viewports = PROBE.get_viewports()
        for viewport in viewports:
            obj = Viewport(self, viewport)
            self.viewports[viewport['id']] = obj
            
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
        
        for viewport in self.viewports.values():
            retval += '\t' + str(viewport) + '\n'
        
            for screen in viewport.screens.values():
                retval += '\t\t' + str(screen) + '\n'
                for window in screen.windows.values():
                    retval += '\t\t\t' + str(window) + '\n'
                retval += '\n'
            retval += '\n'
            
        return retval