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
Window.py

Serves as a layer between tiling and interfacing with the Probe. It also
provides the function to load a window into PyTyle.

Windows are actually kept in three different data structures: (I should
probably change this so that Screen and TileStorage simply point to
windows in State?)
    State
        The State class keeps track of all windows currently known by
        PyTyle. This includes hidden windows, but doesn't include things
        like popups.
    Screen
        Each Screen keeps a record of which windows are on its screen.
        This will include hidden windows.
    TileStorage
        Each screen has its own tiling algorithm, and each tiling
        algorithm has its own tiling storage. In this storage, all tiling
        windows are kept. This will *not* include hidden windows.
"""

from PyTyle.Config import Config
from PyTyle.State import State
from PyTyle.Probe import PROBE

class Window:
    #------------------------------------------------------------------------------
    # STATIC METHODS
    #------------------------------------------------------------------------------

    #
    # This method uses the State to scan for any new windows (not currently in
    # the WINDOW state dict), and loads them into PyTyle. This is called at
    # program start up, and also when a new window has been created.
    #
    @staticmethod
    def load_new_windows():
        wins = State.scan_new_windows()
        for win in wins:
            Window.load_window(win)

    #
    # This loads a new window into PyTyle. It instantiates an object of this
    # class, and tells the window's screen that it needs to be retiled. It
    # will also activate itself if it's the active window. (This is
    # necessary because activating a window also updates the current
    # desktop and screen.)
    #
    # Note: This method also has logic to *skip* windows. Namely, it will
    # check to make sure that the window is in one of our stored desktops.
    # Also, it will make sure that it isn't a popup- otherwise it simply
    # won't be tiled.
    #
    @staticmethod
    def load_window(window_id):
        attrs = PROBE.get_window_by_id(window_id)
        if not attrs['popup'] and attrs['desktop'] in State.get_desktops():
            for viewport in State.get_desktops()[attrs['desktop']].viewports.values():
                if viewport.is_on_viewport(attrs['x'], attrs['y']):
                    for screen in viewport.screens.values():
                        if screen.is_on_screen(attrs['x'], attrs['y']):
                            win = Window(screen, attrs)
                            if not win.filtered():
                                screen.add_window(win)
                                screen.needs_tiling()

                                if win.id == PROBE.get_active_window_id():
                                    win.activate()


    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND WINDOW RELATED ATTRIBUTES/METHODS
    #------------------------------------------------------------------------------

    #
    # The window constructor needs a screen to attach itself to, and a dict
    # of window attributes fetched from X. It also saves its current position so
    # that it may be "untiled." This is also where we'll start listening to the
    # window: (X.FocusChangeMask | X.StructureNotifyMask | X.PropertyChangeMask)
    #
    def __init__(self, screen, attrs):
        self.update_attributes(attrs)
        self.x = 0
        self.y = 0
        self.origx = attrs['x']
        self.origy = attrs['y']
        self.origwidth = self.width
        self.origheight = self.height
        self.screen = screen

        if self.xobj:
            PROBE.window_listen(self.xobj)

    #
    # Activates this window. It sets the input focus and also updates the
    # current State. (The desktop, screen, and active window.)
    #
    def activate(self):
        # we don't know where we are...
        if not self.screen:
            return

        PROBE.window_activate(self.xobj)
        State.reload_active(self)

    #
    # Attempts to add decorations to the window. It's currently only working
    # in OpenBox.
    #
    def add_decorations(self):
        PROBE.window_add_decorations(self.xobj)
        self.static = True

    #
    # Closes the current window. There are some problems with this right
    # now- namely, if I have any number of thunar windows open, closing
    # one of them will close all of them. However, if I close it using
    # OpenBox instead of PyTyle, everything is fine and dandy.
    #
    # Note: The close method in PyTyle isn't even needed. PyTyle can handle
    # the closing of a window in any way- nothing special happens if PyTyle
    # closes it. I am including it currently simply for completeness sake.
    # It *could* be removed in the future. I'm not sure. It is the only key
    # binding that doesn't do anything extra/different than any standard
    # WM event.
    #
    def close(self):
        PROBE.window_close(self.xobj)

    #
    # Deletes the window from existence. It also makes sure to queue its screen
    # for tiling.
    #
    def delete(self):
        self.screen.delete_window(self)
        self.screen.needs_tiling()
        State.reload_active()

    #
    # Runs the filter from the configuration on the given window.
    #
    # Note: This will check the window name, and class. It
    # might be a bit haphazard, but has worked so far. (Namely,
    # gmrun and gimp.)
    #
    # Note 2: It used to check the window title. But I saw that
    # Firefox doesn't set its download window as a pop up, and so
    # I had to use "download" to make PyTyle ignore it. That could
    # easily catch more windows than we want if we searched the
    # titles.
    #
    # Note 3: VLC (and quite probably, some other programs) aren't
    # reporting a proper class. I need something else to search by.
    #
    def filtered(self):
        if self.winclass:
            for winfilter in Config.filter():
                if self.winclass[0].lower().find(winfilter.lower()) != -1 or self.winclass[1].lower().find(winfilter.lower()) != -1: # or window.title.lower().find(winfilter.lower()) != -1:
                    return True

        return False

    #
    # Tests to see if this window is still alive.
    #
    def lives(self):
        try:
            PROBE.get_window_geometry(self.xobj)
        except:
            return False
        return True

    #
    # Asks the window manager to maximize the window. It does not currently
    # resize to the max screen coordinates.
    #
    def maximize(self):
        PROBE.window_maximize(self.xobj)

    #
    # Refreshs the current window. It probes for new window information and
    # updates the attributes on every call. It will then check if it has
    # moved to another desktop or screen. If it has, then it will queue both
    # the old and new screens to retile. It will then also update the State
    # information with the new desktop, screen, and window- if it's active.
    # See also the comments in the method for a few more interesting caveats.
    #
    def refresh(self):
        oldscreen = self.screen
        oldviewport = oldscreen.viewport
        olddesk = oldviewport.desktop
        oldstate = self.hidden
        update = PROBE.get_window(self.xobj)

        # So this is a little bit weird- we're updating the window, but while
        # we care about it's new x,y (screen change?), we don't care about it's
        # new width and height. We're tiling, so we're in complete control of
        # width and height. (The key here is that x/y *completely* determines
        # which screen the window is on.) Therefore, we don't update them- but
        # why? It would seem harmless, except that some windows (like terminals,
        # text editors, etc) set width_inc/height_inc hints which standards
        # compliant window managers honor- like OpenBox. Therefore, the WM could
        # be resizing the width/height of a given window slightly differently than
        # what PyTyle thinks it's at. This causes the width/height to change slightly
        # on each window update, and has a cascading effect that mangles the
        # window's size. YUCK. (And these width_inc/height_inc hints seemingly
        # cannot be reset.)
        update['width'] = self.width
        update['height'] = self.height
        self.update_attributes(update)

        if olddesk.id != self.desktop or not oldviewport.is_on_viewport(update['x'], update['y']) or not oldscreen.is_on_screen(update['x'], update['y']):
            for viewport in State.get_desktops()[self.desktop].viewports.values():
                if viewport.is_on_viewport(update['x'], update['y']):
                    for screen in viewport.screens.values():
                        if screen.is_on_screen(update['x'], update['y']):
                            oldscreen.delete_window(self)
                            screen.add_window(self)
                            screen.needs_tiling()
                            oldscreen.needs_tiling()
                            self.screen = screen
        elif oldstate != self.hidden:
            self.screen.needs_tiling()

        # If it's the active window, then make sure PyTyle knows that. We don't
        # want to set input focus (well, it should already have it if X tells us
        # it's the active window) because it will generate another window change
        # event, and we end up in a positive feedback loop. Yuck.
        if self.id == PROBE.get_active_window_id():
            State.reload_active()

    #
    # Attempts to remove decorations on the window. It's currently only
    # working in OpenBox.
    #
    # Note: devilspie seems to try to get it to work with most other
    # window managers as well. OpenBox has a special atom for the
    # "_NET_WM_STATE" property, namely, "_OB_WM_STATE_UNDECORATED".
    # But other window managers seem to use "_MOTIF_WM_HINTS" to
    # add/remove decorations. However, I could not get such a thing
    # to work in Fluxbox (it's the only other window manager I tried).
    #
    # Either way, I don't recommend using it- especially not yet. With
    # the decorations gone, it's pretty difficult to easily see which
    # window is the active window. (I haven't investigated drawing custom
    # borders around windows yet.)
    #
    def remove_decorations(self):
        PROBE.window_remove_decorations(self.xobj)
        self.static = False

    #
    # Yet another weird thing to handle. Sometimes windows will set their
    # own gravity to static (ex., Goggles Music Manager and OpenOffice).
    # Essentially, this changes how the window is positioned- and it really
    # mucks things up. The current solution I have is to simply change its
    # gravity to NorthWest (default). This seems to make everything play
    # nice, but I am weary of unpredictable behavior from windows that want
    # their gravity to be static, but instead I remove it. So far, so good,
    # though.
    #
    def remove_static_property(self):
        PROBE.window_remove_static(self.xobj)

    #
    # A simple resize method. This also updates the window with the given
    # coordinates.
    #
    # Note: It is possible (and perhaps, likely), that the real window
    # coordinates will become out of sync with the coordinates that PyTyle
    # has. Namely, if you're tiling a screen, you can still currently move
    # a window around that screen while it's floating. Since the
    # desktop/screen didn't change, PyTyle doesn't really care about it,
    # so nothing changes. So far though, nothing bad seems to have come
    # from it. PyTyle simply moves the window back to where it thinks it
    # should be on the next tiling action.
    #
    def resize(self, x, y, width, height):
        if width < 1 or height < 1 or not self.screen.is_in_screen(x, y, width, height):
            return

        PROBE.window_resize(self.xobj, x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    #
    # Asks the window to restore the window. This does not use the window's
    # original x/y/width/height saved in the constructor, but instead asks
    # the window manager to do it. (It should really just be called
    # "unmaximize".)
    #
    def restore(self):
        PROBE.window_reset(self.xobj)

    #
    # An on the fly way of saving the window's position. When this method is
    # called, it resets its original x/y/width/height, so that when it's
    # untiled, it will revert to this new position. Mainly useful for when
    # the window switches screens? (I'm not sure about that- if a window
    # goes to another screen on the same desktop, should it be untiled back
    # to its original screen, or an arbitrary position on its new screen?)
    #
    def save_geometry(self):
        geom = PROBE.get_window_geometry(self.xobj)
        self.origx = geom['x']
        self.origy = geom['y']
        self.origwidth = geom['width']
        self.origheight = geom['height']

    #
    # Lowers a window. Only use this if you're changing the stacking order.
    #
    def stack_lower(self):
        PROBE.window_stackbelow(self.xobj)

    #
    # Raises a window. Only use this if you're changing the stacking order.
    #
    def stack_raise(self):
        PROBE.window_stackabove(self.xobj)

    #
    # Simply updates all the window attributes.
    #
    def update_attributes(self, attrs):
        self.id = attrs['id']
#        self.x = attrs['x']
#        self.y = attrs['y']
        self.width = attrs['width']
        self.height = attrs['height']
        self.d_left = attrs['d_left']
        self.d_right = attrs['d_right']
        self.d_top = attrs['d_top']
        self.d_bottom = attrs['d_bottom']
        self.desktop = attrs['desktop']
        self.title = attrs['title']
        self.winclass = attrs['class']
        self.static = attrs['static']
        self.hidden = attrs['hidden']
        self.xobj = attrs['xobj'] if 'xobj' in attrs else None

    #
    # A simple string representation of the window. Useful for some debugging
    # purposes. Also see the string representations of desktop and screen.
    #
    def __str__(self):
        return self.title + ' - [ID: ' + str(self.id) + ', X: ' + str(self.x) + ', Y: ' + str(self.y) + ', WIDTH: ' + str(self.width) + ', HEIGHT: ' + str(self.height) + ', DESKTOP: ' + str(self.screen.viewport.desktop.id) + ', VIEWPORT: ' + str(self.screen.viewport.id) + ', SCREEN: ' + str(self.screen.id) + ']'
