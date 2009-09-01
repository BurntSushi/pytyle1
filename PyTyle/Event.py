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
Event.py

This class, along with Probe, are the only two classes interfacing
with X in PyTyle.

Event handles all event related information. Each instance is a
separate event sent from X.

Most of the function of this class is to encapsulate event information.
"""

from PyTyle.Probe import PROBE
from Xlib import X

class Event:    
    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND INSTANCE METHODS
    #------------------------------------------------------------------------------
    
    #
    # Each instance represents one event. Upon initialization, we grab that event
    # from the X server.
    #
    def __init__(self):
        self._event = PROBE.get_display().next_event()
        
    #
    # Fetches the window id from the event. We have to convert it to a long and
    # then a hex so that it matches up with our dictionary of windows (the State).
    #
    def get_window_id(self):
        if self._event and hasattr(self._event, 'window'):
            return hex(long(self._event.window.id))
        return 0
    
    #
    # Fetches the key code from the event object. Make sure it's a KeyPress event.
    #
    def get_keycode(self):
        if self._event and self._event.type == X.KeyPress:
            return self._event.detail
        return None
    
    #
    # The key "state" is a bit mask of which modifiers were pressed when the key
    # was hit. See get_masks.
    #
    def get_key_state(self):
        if self._event and self._event.type == X.KeyPress:
            return self._event.state
        return 0
        
    #
    # This method detects exactly which modifiers are represented in the current
    # key state. Supported modifiers are as follows:
    #    ShiftMask - Shift key
    #    ControlMask - Control key (either)
    #    Mod1Mask - Alt key (either)
    #    Mod4Mask - Super
    #
    def get_masks(self):
        if not self._event or not self.is_keypress():
            return None
        
        ret = 0
        state = self.get_key_state()
        if X.ShiftMask & state:
            ret = ret | X.ShiftMask
        if X.ControlMask & state:
            ret = ret | X.ControlMask
        if X.Mod1Mask & state:
            ret = ret | X.Mod1Mask
        if X.Mod4Mask & state:
            ret = ret | X.Mod4Mask
            
        if not ret:
            ret = X.AnyModifier
        
        return ret
    
    #
    # Reports whether this event is an active window changing event.
    #
    def is_active_change(self):
        if self._event and self._event.type == X.PropertyNotify and self._event.atom == PROBE.atom("_NET_ACTIVE_WINDOW"):
            return True
        return False
    
    #
    # Reports whether this event is a desktop changing event. This event is
    # sent from the root window. We use this to update the active window.
    # Although I am thinking of changing to listening for the
    # _NET_ACTIVE_WINDOW instead. Will investigate more later.
    #
    def is_desktop_change(self):
        if self._event and self._event.type == X.PropertyNotify and (self._event.atom == PROBE.atom("_NET_CURRENT_DESKTOP") or self._event.atom == PROBE.atom("_NET_DESKTOP_VIEWPORT")):
            return True
        return False
    
    #
    # Reports whether the current event is a focus *in* event. (We don't
    # care about focus *out* right now.) We also make sure that this is
    # a normal focus event (otherwise we get flooded with crap we don't
    # need.)
    #
    def is_focus_in(self):
        if self._event and self._event.type == X.FocusIn and self._event.mode == X.NotifyNormal:
            return True
        return False
        
    #
    # Reports whether the current event is a key press or not.
    #
    def is_keypress(self):
        if self._event and self._event.type == X.KeyPress:
            return True
        return False
    
    #
    # Reports whether the screen setup has changed by checking the
    # _NET_DESKTOP_GEOMETRY property.
    #
    def is_screen_change(self):
        if self._event and self._event.type == X.PropertyNotify and (self._event.atom == PROBE.atom("_NET_DESKTOP_GEOMETRY") or self._event.atom == PROBE.atom("_NET_NUMBER_OF_DESKTOPS")):
            return True
        return False
    
    #
    # Reports whether the window's state has changed. If a window's state
    # changes (i.e., it was hidden or something), then we need to refresh
    # its information and tell the screen it needs to be retiled.
    #
    def is_state_change(self):
        if self._event and self._event.type == X.PropertyNotify and self._event.atom == PROBE.atom("WM_STATE"):
            return True
        return False
    
    #
    # Reports whether the window manager's client list has changed or not.
    # Useful for detecting add/removal of windows.
    #
    def is_windowlist_change(self):
        if self._event and self._event.type == X.PropertyNotify and self._event.atom == PROBE.atom("_NET_CLIENT_LIST"):
            return True
        return False
    
    #
    # Reports whether the event is a window change or not. We want to know
    # if the window changes whenever it is resized/moved (ConfigureNotify),
    # or when its _NET_WM_DESKTOP property changes (PropertyNotify). This
    # allows for us to drag windows to and from tiling screens (by using
    # the mouse, keyboard, desktop switch key, etc).
    #
    def is_window_change(self):
        if self._event and ((self._event.type == X.ConfigureNotify and self._event.event != PROBE.get_root()) or (self._event.type == X.PropertyNotify and self._event.atom == PROBE.atom("_NET_WM_DESKTOP"))):
            return True
        return False
    
    #
    # Reports whether we are creating a window or not. This will initiate
    # a scan for new windows in the client list. Why do we scan? Because
    # don't actually use the window object that comes attached to with
    # this event, because its ID might not line up with the one we
    # normally receive in PyTyle (i.e., from the _NET_CLIENT_LIST).
    #
    def is_window_create(self):
        if self._event and self._event.type == X.CreateNotify:
            return True
        return False
    
    #
    # Reports whether a window was destroyed or not. This will initiate
    # a scan of all current windows and the State to see if there are
    # any windows in PyTyle that aren't in the client list. We will
    # then remove it. Like when we create a window, we don't use the
    # window object attached to this event because it is unreliable
    # for our purposes.
    #
    def is_window_destroy(self):
        if self._event and self._event.type == X.DestroyNotify:
            return True
        return False
    
    #
    # Reports whether the workarea has changed (i.e., a dock/panel has
    # been added to the screen).
    #
    def is_workarea_change(self):
        if self._event and self._event.type == X.PropertyNotify and self._event.atom == PROBE.atom("_NET_WORKAREA"):
            return True
        return False