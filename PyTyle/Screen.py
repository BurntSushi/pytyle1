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
Screen.py

The Screen class will handle all screen related functionality. For instance,
it provides methods to detect if a given window is on its screen. Also, it
will keep track of its state; like if it needs to be tiled, has tiling
enabled/disable, and of course, its current tiling algorithm.
"""

from PyTyle.Config import Config
from PyTyle.State import State
from PyTyle.Debug import DEBUG

from PyTyle.Window import *

class Screen:       
    #------------------------------------------------------------------------------
    # CONSTRCUTOR AND SCREEN RELATED ATTRIBUTES/METHODS
    #------------------------------------------------------------------------------ 
    
    #
    # Initialization requies a desktop and attributes fetched from X. We also make
    # sure that it starts out with:
    #    1. Tiling disabled
    #    2. Untiled state
    #    3. No tiler
    #
    def __init__(self, viewport, attrs):
        self.update_attributes(attrs)
        self._active = None
        self._tile = None
        self._tiled = False
        self._tiling = Config.misc('global_tiling')
        self.windows = {}
        self.viewport = viewport
        
    #
    # Disables tiling for this screen. Essentially, this is called when the
    # untile method is called via a key press. Meaning, if you programmatically
    # call untile, it will not disable tiling. (It will however, resize the
    # windows back to their original state- is that good behavior?)
    def disable_tiling(self):
        self._tiling = False
        
    #
    # Tells the screen that PyTyle can now touch it. Currently, a screen can
    # *only* be enabled for tiling using a key binding tied to the tile method.
    # Even if the tile method is called programmatically (i.e., not instantiated
    # via a key press), it won't tile if tiling isn't enabled.
    #
    def enable_tiling(self):
        self._tiling = True
        
    #
    # Fetches the currently active window for *this* screen. That means that
    # the currently active window for this screen may not be *THE* active
    # window. Be careful about that.
    #
    # Logic: The screen is in charge of reporting back an active window,
    # and also saying when there isn't one. There are four possibilities:
    #    1. If there is no active window set, and there are no windows, 
    #       then return nothing.
    #    2. If there are windows, and no active window, then arbitrarily
    #       select the first window in the screen window storage to make
    #       active. Also, if there are windows and the currently active window
    #       is no longer on this screen, then similarly choose an arbitrary
    #       window to make active.
    #    3. If there are no windows but there is an active window
    #       and it's no longer on the screen, then return nothing.
    #    4. Finally, if it's none of the above, then return the currently
    #       set active window.
    #
    def get_active(self):
        wins = self.get_tiler().storage.get_all()
        if not self._active and not wins:
            self._active = None
        elif wins and (not self._active or self._active.hidden or self._active.screen.id != self.id or not self._active.lives()):
            self._active = wins[0]
        elif not wins and self._active.screen.id != self.id:
            self._active = None
            
        return self._active
    
    #
    # Fetches the current tiling algorithm. The tiling algorithm *must* be
    # a subclass of Tile. (Which does a lot of the grunt work for you.)
    #
    def get_tiler(self):
        return self._tile
    
    #
    # Fetches the workarea of the current screen. Essentially, this has worked
    # quite well in my experience with just one monitor. However, when we add
    # monitors, the window manager doesn't seem to report desktop dimensions
    # back correctly, in a way that allows PyTyle to see where docks/panels are.
    # My solution to this was to provide a manual override in the configuration
    # file for multiple screens. It isn't pretty, but it's what I've got so far.
    #
    # Note: This is used in the core part of the tiling algorithms to place
    # the windows. If you have some fancy setup in your workarea, this is the
    # place to tinker! (If the configuration file isn't enough power.)
    #
    def get_workarea(self):
        # If we have one screen, look for a "Screen 0" config
        # and use it if it exists...
        if len(self.viewport.screens) == 1:
            if 0 in Config.WORKAREA:
                x = self.x + Config.workarea(0, 'left')
                y = self.y + Config.workarea(0, 'top')
                height = self.height - Config.workarea(0, 'bottom') + Config.workarea(0, 'top')
                width = self.width - Config.workarea(0, 'right') + Config.workarea(0, 'left')
            else:
                if PROBE.is_compiz():
                    x = self.viewport.x
                    y = self.viewport.y
                else:
                    x = self.viewport.desktop.x
                    y = self.viewport.desktop.y
                    
                height = self.viewport.desktop.height
                width = self.viewport.desktop.width
                print x, y, width, height
        else:
            x = self.x
            y = self.y
            height = self.height
            width = self.width
            
            # Factor in manual docks...
            x += Config.workarea(self.id, 'left')
            y += Config.workarea(self.id, 'top')
            height -= Config.workarea(self.id, 'bottom') + Config.workarea(self.id, 'top')
            width -= Config.workarea(self.id, 'right') + Config.workarea(self.id, 'left')
                
        return (x, y, width, height)
    
    #
    # This is used whenever the screen's tiler calls the "tile" method. It
    # tells the screen that everything is find and dandy, like sour candy.
    #
    def got_tiling(self):
        self._tiled = True
    
    #
    # Reports whether the screen is currently tiled. This is essentially
    # used by the Tile dispatcher. If we are coming into the tile method,
    # and the screen reports that it isn't tiled, then that means something
    # on the screen triggered it and told it needed to be re-tiled. And
    # thus, we re-tile and set this attribute to true.
    #
    def is_tiled(self):
        return self._tiled
    
    #
    # Reports whether this screen is in tiling mode or not.
    #
    def is_tiling(self):
        return self._tiling
    
    #
    # This tells the screen that something happened and it therefore needs
    # to be re-tiled. So, this should be called any time something changes
    # on a screen (new window, window destroyed, etc). When it's called,
    # it will also queue the screen into the State so that PyTyle will 
    # re-tile the screen when it gets a chance.
    #
    # Note: We need more than just a queue- and that's why this attribute
    # exists. The screen itself needs to be aware if it's in a proper
    # state or not so that the tiler knows if it should reload its storage.
    #
    def needs_tiling(self):
        self._tiled = False
        State.queue_screen(self)
    
    #
    # Simply sets the active window. No questions asked.
    #
    def set_active(self, window):
        self._active = window
    
    #
    # Sets the tiler of this screen. A tiler *must* be a subclass of Tile.
    # To switch tiling layouts (if the default layout cycler isn't enough), 
    # it's as simple as calling this method, followed by a call to the 
    # _reset method in the Tile class.
    # 
    def set_tiler(self, tile):
        self._tile = tile(self)   
        
    #
    # This will add a new window to the screen. It will also take care of
    # updating the State for you. Additionally, it will tell itself that it
    # needs to be re-tiled.
    #
    def add_window(self, window):
        State.add_window(window)
        self.windows[window.id] = window
        self.needs_tiling()
     
    #
    # Opposite of add_window. It will still tell itself it needs to be
    # re-tiled.
    #    
    def delete_window(self, window):
        State.delete_window(window)
        del self.windows[window.id]
        self.needs_tiling()
    
    #
    # Takes a pair of x,y coordinates and tells us whether they are in the
    # screen's grid. Also, take special care for windows with a negative x,y
    # position- simply say that it is on the screen with x,y coordinates
    # equal to 0.
    #
    def is_on_screen(self, x, y):
        if x >= self.x and y >= self.y and x < (self.x + self.width) and y < (self.y + self.height):
            return True
        
        # off the screen?
        if (x < 0 or y < 0) and self.x == 0 and self.y == 0:
            return True
        
        return False
                
    #
    # Updates screen with attributes fetched from X. This is actually everything
    # that the xinerama extension gives us. I'm not sure if screen ids remain
    # the same for each monitor on boot, although I imagine they don't. I'll worry
    # about that later. It's been fine so far. (PyTyle will still function
    # perfectly if id's are rearranged- but the key bindings will be reversed. Not
    # very user-friendly.)
    #
    def update_attributes(self, attrs):
        self.id = attrs['id']
        self.x = attrs['x']
        self.y = attrs['y']
        self.width = attrs['width']
        self.height = attrs['height']
        
    #
    # String representation of the current screen. See also the string
    # representations of desktop, viewport, and window.
    #                
    def __str__(self):
        return 'Screen ' + str(self.id) + ' - [ID: ' + str(self.id) + ', X: ' + str(self.x) + ', Y: ' + str(self.y) + ', WIDTH: ' + str(self.width) + ', HEIGHT: ' + str(self.height) + ', VIEWPORT: ' + str(self.viewport.id) + ', DESKTOP: ' + str(self.viewport.desktop.id) + ']'