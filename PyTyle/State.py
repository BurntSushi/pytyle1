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
State.py

Keeps a record of everything going on in the outside world. It keeps track
of all windows that PyTyle knows about, along with all desktops (but not
all screens- no need). It also keeps a record of the current desktop. Since
each desktop keeps a record of its current screen, and each screen keeps a
record of its current window, State provides us with easy access to the active
window while also giving us its desktop and screen.

Additionally, State keeps track of which screens need tiling. This serves as
a queue, and periodically, after certain things have happened (eg., a window
was hidden), a screen will be queued up.

State also serves to initialize hot keys and scans for new windows.
"""

from PyTyle.Config import Config
from PyTyle.Probe import PROBE

class State:
    #------------------------------------------------------------------------------
    # CLASS VARIABLES
    #------------------------------------------------------------------------------ 
    
    #
    # Keeps track of the currently active desktop.
    #
    _DESKTOP = None
    
    #
    # Keeps a record of all instantiated desktops.
    #
    _DESKTOPS = {}
    
    #
    # Keeps a mapping of keys to tiling actions
    #
    _DISPATCHER = {}
    
    #
    # Tells us whether we need to reload the config file.
    #
    _RELOAD = False
    
    #
    # Queue of screens to tile. It's flushed at the start of each event loop
    # iteration.
    #
    _TO_TILE = []
    
    #
    # Keeps a record of all instantiated windows.
    #
    # Note: If a window is loaded in this dict, it does *not* mean it will
    # definitely be tiled. Which windows are actually tiled is up to the TileStorage
    # class to determine. (That is where the window filter is used.)
    #
    _WINDOWS = {}
        
    
    #------------------------------------------------------------------------------
    # STATIC METHODS
    #------------------------------------------------------------------------------
    
    #
    # Adds a desktop to the state.
    #
    @staticmethod
    def add_desktop(desktop):
        State._DESKTOPS[desktop.id] = desktop
        
    #
    # Adds a window to the state.
    #
    @staticmethod
    def add_window(window):
        State._WINDOWS[window.id] = window
        
    #
    # Removes a window from the state.
    #
    @staticmethod
    def delete_window(window):
        del State._WINDOWS[window.id]
        
    #
    # Removes a screen from queue. Only used when flushing the queue
    # at the start of each event iteration.
    #
    @staticmethod
    def dequeue_screen():
        return State._TO_TILE.pop(0)
    
    #
    # Unsets the flag to reload the config file.
    #
    @staticmethod
    def did_reload():
        State._RELOAD = False
    
    #
    # Sets a flag to have PyTyle reload the config file.
    #
    @staticmethod
    def do_reload():
        State._RELOAD = True
    
    #
    # Retrieves the current desktop.
    #
    @staticmethod
    def get_desktop():
        return State._DESKTOP
    
    #
    # Retrieves the desktops in the state.
    #
    @staticmethod
    def get_desktops():
        return State._DESKTOPS
    
    #
    # Retrieves the dispatcher.
    #
    @staticmethod
    def get_dispatcher():
        return State._DISPATCHER
    
    #
    # Retrieves the windows in the state.
    #
    @staticmethod
    def get_windows():
        return State._WINDOWS
    
    #
    # Retrieves the name of the currently running window manager.
    #
    @staticmethod
    def get_wm_name():
        return PROBE.get_wm_name()
    
    #
    # Tells us whether we need to reload the config file.
    #
    @staticmethod
    def needs_reload():
        return State._RELOAD
        
    #
    # Reports whether the tiling queue is empty or not.
    #
    @staticmethod
    def queue_has_screens():
        return True if State._TO_TILE else False
    
    #
    # Adds a screen to the tiling queue. (You shouldn't use this method
    # directly to queue up a screen, but rather, the "needs_tiling" method
    # in the Screen class.)
    #
    @staticmethod
    def queue_screen(screen):
        State._TO_TILE.append(screen)
        
    #
    # Simply ties a key code to a callback method in the Tile class. Valid key codes
    # can be found in the documentation provided. (But are based on the key symbols
    # defined in Xlib. Probably in Xlib/keysymdef/latin1.py and Xlib/keysymdef/miscellany.py)
    # 
    @staticmethod
    def register_hotkey(keycode, mask, callback):
        if not keycode in State._DISPATCHER:
            State._DISPATCHER[keycode] = {}
        State._DISPATCHER[keycode][mask] = callback
        
    #
    # Registers all the key bindings specified in the configuration file. Currently,
    # only Shift, Ctrl, Alt, and/or Super are supported are modifier keys. See also,
    # State.register_hotkey and the documentation for a more complete description
    # of key combinations.
    #
    @staticmethod
    def register_hotkeys():
        for mapping in Config.KEYMAP:
            callback = Config.KEYMAP[mapping]
            
            codes = mapping.split('-')
            mods = codes[:-1]
            key = codes[-1]
            
            # No key?
            if not key:
                print >> sys.stderr, "Could not map %s to %s" % (mapping, callback) 
                continue
            
            # generate key code and mod mask...
            keycode = PROBE.generate_keycode(key)
            modmask = PROBE.generate_modmask(mods)
            
            # Tell X we want to hear about it when this key is pressed...
            try:
                PROBE.grab_key(keycode, modmask)
            except:
                print "Nada:", callback
            
            # Finally register the key with the dispatcher...            
            State.register_hotkey(keycode, modmask, callback)
        
    #
    # Simply probes for the currently active window, and updates the currently
    # active desktop, screen, and window accordingly.
    #
    @staticmethod
    def reload_active(active = None, force = False):
        if not active: 
            activeid = PROBE.get_active_window_id()
        else:
            activeid = active.id
            
        # Check to make sure we need to probe for anything...
        if not force and activeid and State._DESKTOP and State._DESKTOP._VIEWPORT and State._DESKTOP._VIEWPORT._SCREEN:
            current = State._DESKTOP._VIEWPORT._SCREEN.get_active()
            if current and current.id == activeid:
                return
            
        State._DESKTOP = State.get_desktops()[PROBE.get_desktop()]        
                
        if not activeid:
            if not State._DESKTOP._VIEWPORT:
                State._DESKTOP._VIEWPORT = State._DESKTOP.viewports[0]
                
            if not State._DESKTOP._VIEWPORT._SCREEN:
                State._DESKTOP._VIEWPORT._SCREEN = State._DESKTOP._VIEWPORT.screens[0]
        else:
            for viewport in State._DESKTOP.viewports.values():
                for screen in viewport.screens.values():
                    if activeid in screen.windows:
                        State._DESKTOP._VIEWPORT = viewport
                        State._DESKTOP._VIEWPORT._SCREEN = screen
                        State._DESKTOP._VIEWPORT._SCREEN.set_active(screen.windows[activeid])
                        break
            
    #
    # Similar to scan_new_windows, except it returns all windows reported by
    # the window manager. We used this when we get a DestroyNotify event: iterate
    # over the State windows and see which ones aren't in this list and delete
    # them.
    #
    @staticmethod
    def scan_all_windows():
        ret = []
        windows = PROBE.get_window_list()
        for window in windows:
            ret.append(window) 
                
        return ret
    
    #
    # There are problems with using the window given via the CreateNotify event
    # type, and thus, PyTyle currently listens for that event and scans for new
    # windows manually.
    #
    @staticmethod
    def scan_new_windows():
        ret = []
        windows = PROBE.get_window_list()
        for window in windows:
            if hex(window) not in State.get_windows():
                ret.append(window) 
                
        return ret
    
    #
    # UN-registers all the key bindings specified in the configuration file. This
    # allows us to dynamically change key bindings as PyTyle is running.
    #
    @staticmethod
    def unregister_hotkeys():
        for mapping in Config.KEYMAP:
            callback = Config.KEYMAP[mapping]
            
            codes = mapping.split('-')
            mods = codes[:-1]
            key = codes[-1]
            
            # No key?
            if not key:
                print >> sys.stderr, "Could not map %s to %s" % (mapping, callback) 
                continue
            
            # generate key code and mod mask...
            keycode = PROBE.generate_keycode(key)
            modmask = PROBE.generate_modmask(mods)
            
            # Tell X we want to hear about it when this key is pressed...
            try:
                PROBE.ungrab_key(keycode, modmask)
            except:
                print "Nada:", callback
            
        # And finally reset the dispatcher...
        State._DISPATCHER = {}
    
    #
    # Wipes the current state. Useful for when the screen orientation changes.
    #
    @staticmethod
    def wipe():
        State._DESKTOP = None
        State._WINDOWS = {}
        State._DESKTOPS = {}
        State._TO_TILE = []