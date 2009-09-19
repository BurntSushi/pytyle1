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
Tile.py

Tile is the guts of the tiling algorithm. It actually does *most* of the heavy
lifting for you, as many of the tiling actions (i.e., the key bindings in the
configuration) aren't really relevant to the physical display of the windows.
(However, the class hierarchy is such that you could make them relevant, if you
wish.)

In fact, to create your own customized tiling algorithm, you need only overload
the following methods: _tile, _cycle, _master_increase, _master_decrease,
help_find_next, and help_find_previous. By default, Vertical and Horizontal are
so similar, that currently, _cycle, help_find_next, and help_find_previous are 
overloaded once in TileDefault (which cannot be used as a tiling algorithm by
itself), and _tile, _master_increase, and _master_decrease are each overloaded
accordingly in two of TileDefault's subclasses: Horizontal and Vertical.

To create your own tiling algorithm, read the comments in this file, along with
Tilers/TileDefault.py, Tilers/Horizontal.py, and Tilers/Vertical.py.
"""

import sys, os, time

from PyTyle.Config import Config
from PyTyle.State import State
from PyTyle.Debug import DEBUG
import traceback

from PyTyle.TileStorage import TileStorage
from PyTyle.TileState import TileState

class Tile:
    #------------------------------------------------------------------------------
    # STATIC METHODS (DISPATCHER RELATED)
    #------------------------------------------------------------------------------ 
    
    #
    # Initiate the dispatching routing.
    #
    # Has two contexts: Called with an action and called without.
    #
    # *Called with an action*
    # Implies that PyTyle is forcing the issue and wants something done. This also
    # means that we are here _not_ because of a key press. However, we still check
    # to see if tiling is enabled for this screen. If it isn't, we die.
    #
    # *Called without an action*
    # Implies that we have initiated the dispatch routine with a key press.
    # Therefore, we should check the currently pressed key, and follow the key
    # binding to run its respective method. Make sure to fail if tiling isn't
    # enabled and we aren't calling tile. (Essentially, pressing the tile key
    # binding is the only way to enable tiling.)
    #
    @staticmethod
    def dispatch(tiler, action=None, keycode=None, masks=None):
        if not action and keycode and masks:
            if keycode not in State.get_dispatcher():
                print >> sys.stderr, "Keycode %s is not bound" % keycode
                return
            
            # Now we need to determine which masks were used...
            if masks in State.get_dispatcher()[keycode]:
                action = State.get_dispatcher()[keycode][masks]
            else:
                print >> sys.stderr, "Keycode %s and keymask %d are not bound" % (keycode, masks)
                return

            if not tiler.screen.is_tiling() and action.find('tile.') == -1:
                return
        elif action:
            # We can only initiate tiling through keycodes...
            if not tiler.screen.is_tiling():
                return
            
        # Turn the action into a method...
        if action.find('tile.') != -1:
            layout = action[(action.find('.') + 1):]
            if layout != 'default' and layout in Config.TILERS:
                tiler.screen.set_tiler(Config.tilers(layout))
                tiler = tiler.screen.get_tiler()
                tiler._reset()
            action = Tile.tile
        else:
            action = eval('Tile.' + action)
            
        action(tiler)
    
    
    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND GENERIC TILING METHODS
    #------------------------------------------------------------------------------
    
    #
    # Constructor simply instantiates the TileStorage class and passes it the window filter.
    # Every tiling instance must be attached to a screen.
    #
    # Also, in general, the following tiling methods are fairly generic (any method beginning
    # with an underscore). However, the class hierarchy is setup in such a way that does not 
    # preclude their customization. Simply overload whichever method that needs customizing
    # in your tiling class. (_tile, _cycle, _master_increase, _master_decrease should be
    # sufficient here. Along with the helper methods help_find_next and help_find_previous.)
    # We also initialize this tiler's "state"- this will automatically save certain things for
    # us, like the sizes of panes.
    # 
    def __init__(self, screen):
        self.screen = screen
        self.storage = TileStorage()
        self.cycleIndex = 0
        self.state = TileState(self)
        
    #
    # The core of the tiling algorithm. This will be called whenever PyTyle senses
    # that a screen needs to be re-tiled. It is essentially the bread and butter of
    # your tiling algorithm. It is responsible for placing *all* masters and slaves
    # in the TileStorage on the screen (unless you desire other behavior, like a
    # limited number of windows, but the behavior could be unpredictable). See the
    # respective tile methods in the algorithms shipped with this release.
    #
    def _tile(self):
        pass
        
    #
    # There is probably no need to overload this one. It simply iterates over all
    # stored windows and resizes them back to their original geometry. Geometry is
    # mainly saved when a window is first created and maybe when it switches screens.
    #
    def _untile(self):
        # just resize all the windows back to their original x/y/width/height        
        for window in self.storage.get_all():
            if Config.misc('original_decor'):
                window.add_decorations()
            else:
                window.remove_decorations()
                
            window.resize(window.origx, window.origy, window.origwidth, window.origheight)
            
    #
    # Tells PyTyle to reload the configuration file.
    #
    def _reload(self):
        State.do_reload()
        
    #
    # Does a hard reset of the current screen. It empties the tiling storage, reloads
    # the current screen (probes for all windows), and adds the screen to the tiling
    # queue. Hopefully shouldn't have to be used, but is worth trying before
    # restarting PyTyle.
    #
    def _reset(self):
        self.storage = TileStorage()
        self.state.reset()
        self.cycleIndex = 0
        self.screen.needs_tiling()
        
    #
    # Responsible for cycling all slaves through the master slot. If there are more
    # than one master, then simply use the first master slot. If there are no masters
    # then do nothing. The cycleIndex should be incremented (or decremented, depending
    # upon your algorithm) after the cycle, and you also need to reset it to 0 when it
    # reaches the end. You should use help_find_next and help_find_previous here.
    #
    def _cycle(self):
        pass
        
    #
    # Simply puts focus on the given screen. The screen is responsible for providing
    # the currently active window. If we don't have one, then don't do anything. Also,
    # immediately quit if the screen is the same as the current tiler screen.
    #
    def _screen_focus(self, screen_num):
        # stop if current window...
        if self.screen.id == screen_num:
            return
        
        for screen in self.screen.viewport.screens.values():
            if screen_num == screen.id:
                if not screen.get_active():
                    return
                else:
                    screen.get_active().activate()
        
    #
    # Moves the active window to the given screen. Immediately quit if the screen is
    # the same as the current tiler screen.
    #
    # This method is a little tricky. Once we find our desired screen, we need to
    # update the storage in each screen (that is, the storage for the old screen
    # and the new screen- and this storage counts for both the tiler instance
    # and the screen instance). While we are only here if the current screen is in
    # tiling mode, we do however need to check if the screen we're moving the window
    # to is in tiling mode. If so, add the screen to the tiling queue (the current screen
    # also has to be added). Thus, if the screen we're moving it to is in tiling mode
    # then that screen is responsible for its placement. If not, arbitrarily assign
    # the window to the upper left coordinates of the screen. (Could be bad.) We 
    # must then update the screen object of the window we moved, and activate the *old*
    # screen. (Incidentally, I did it this way because that is the default behavior
    # of XMonad.)
    # 
    def _screen_put(self, screen_num):
        # stop if current screen...
        if self.screen.id == screen_num:
            return
                
        for screen in self.screen.viewport.screens.values():
            if screen_num == screen.id:
                add = self.screen.get_active()
                self.screen.delete_window(add)
                self.storage.remove(add)
                screen.add_window(add)
                screen.get_tiler().storage.add(add)
                
                if not screen.is_tiling():
                    add.resize(screen.x, screen.y, add.width, add.height)
                
                add.screen = screen
                self.screen.get_active().activate()
    
    #
    # Increases the area of the master pane. What this does is up to your tiling
    # algorithm. Pay special attention to the proper resizing of any other pane(s).
    #
    def _master_increase(self):
        pass
    
    #
    # Inverse of _master_increase.
    # _master_increase(_master_decrease(window placement)) = window placement
    # (Unless you set default pixel amounts of each method to be different... o_O)
    #
    def _master_decrease(self):
        pass
                
    #
    # Simply adds a master to the storage and submits the current screen into the
    # tiling queue. It is possible that your tiling algorithm might not want to
    # support more than one master (ex. XMonad's Circle layout), and in that case,
    # simply overload the method and leave it empty. (Make sure to do the same for
    # _remove_master or else you could be stuck!)
    #
    # Note: Both _add_master and _remove_master try to look at the currently active
    # window. If it is a slave or master, respectively, then that is the window that
    # will be added or removed. Otherwise, the first slave or master, respectively,
    # will be chosen arbitrarily.
    #
    def _add_master(self):
        # use active window if it's a slave
        slaves = self.storage.get_slaves()
        if self.screen.get_active().id in self.storage.get_slaves_by_id():
            self.storage.inc_master_count()
            self.storage.remove(self.screen.get_active())
            self.storage.add(self.screen.get_active())
        elif slaves:
            self.storage.inc_master_count()
            self.storage.remove(slaves[0])
            self.storage.add(slaves[0])
        else:
            return
        
        self.screen.needs_tiling()
        
    #
    # Inverse of _add_master.
    #
    # Note: If we somehow get a bigger master count than the number of windows (which
    # is okay and anticipated behavior), but we are trying to decrement, then decrement
    # the counter until we get to the current number of windows.
    #
    # Note: TileStorage will not let the number of masters go below 0 (0 masters is fine).
    #
    def _remove_master(self):
        # if we have too many windows, decrement master count until we're good...
        all = self.storage.get_all()
        while self.storage.get_master_count() > len(all):
            self.storage.dec_master_count()
             
        # make sure the current window is a master...
        masters = self.storage.get_masters()
        if self.screen.get_active().id in self.storage.get_masters_by_id():
            self.storage.dec_master_count()
            self.storage.remove(self.screen.get_active())
            self.storage.add(self.screen.get_active())
        elif masters:
            self.storage.dec_master_count()
            self.storage.remove(masters[0])
            self.storage.add(masters[0])
        else:
            return
        
        self.screen.needs_tiling()
        
    #
    # A very simple method to make the current window the master. If there are more
    # than one master, then use the first master. If there are no masters, then do
    # nothing.
    #
    def _make_active_master(self):
        if self.storage.get_masters():
            self.help_switch(self.storage.get_masters()[0], self.screen.get_active())
        
    #
    # Simply put the focus on the master window. If there are more than one master,
    # then use the first master. If there are no masters, then do nothing.
    #
    def _win_master(self):
        masters = self.storage.get_masters()
        
        if not masters:
            return
        
        masters[0].activate()
        
    #
    # Simply closes the current window.
    #
    # Note: We don't *really* need this method here. The window can be closed
    # in any way, and it will be detected by PyTyle. It's here mostly for
    # completeness.
    #
    def _win_close(self):
        self.screen.get_active().close()
     
    #
    # Focuses on the previous window.
    #   
    def _win_previous(self):
        self.help_find_previous().activate()
     
    #   
    # Focuses on the next window.
    #
    def _win_next(self):
        self.help_find_next().activate()
        
    #
    # Switches the current window with the previous window.
    #
    def _switch_previous(self):
        previous = self.help_find_previous()
        
        # only one window... bye
        if previous.id == self.screen.get_active().id:
            return
        
        self.help_switch(previous, self.screen.get_active())
     
    #
    # Switches the current window with the next window.
    #   
    def _switch_next(self):
        next = self.help_find_next()
        
        # only one window... bye
        if next.id == self.screen.get_active().id:
            return
        
        self.help_switch(next, self.screen.get_active())
        
    #
    # Maximizes all windows managed by the tiler.
    #
    # Note: This sends a maximize request to the window manager. I'm not sure if this
    # is better than resizing the window to the full screen.
    #
    def _max_all(self):
        for window in self.storage.get_all():
            window.maximize()
     
    #
    # Restores all windows managed by the tiler.
    #   
    def _restore_all(self):
        for window in self.storage.get_all():
            window.restore()
            
    #
    # A simple debugging tool. Only useful if PyTyle is running from a shell.
    # (Tentatively assigned the Alt-Q key binding.)
    #
    def _query(self):
        print State.get_wm_name()
        print self.screen.viewport.desktop
        print self.storage
        
    
    #------------------------------------------------------------------------------
    # PRIVATE HELPER METHODS
    #------------------------------------------------------------------------------ 
    
    #
    # Simply saves the position of all windows on this tiling screen.
    #
    def help_save(self):
        for window in self.screen.windows.values():
            window.save_geometry()
            
    #
    # Resizes the given window. Takes into account its decorations.
    #
    def help_resize(self, window, x, y, width, height):
        if window.static:
            window.remove_static_property()
            
        if Config.misc('decorations'):
            if not Config.misc('original_decor'):
                window.add_decorations()
                
            window.resize(int(x), int(y), int(width - window.d_left - window.d_right), int(height - window.d_top - window.d_bottom))
        else:
            if Config.misc('original_decor'):
                window.remove_decorations()
                
            window.resize(int(x), int(y), int(width - 2), int(height - 2))
            
    #
    # Reloads the entire storage container underlying the tiling algorithm.
    # Unless you have really special needs, this should be sufficient. The
    # TilingStorage class handles master/slave balance for you according to
    # the masterCount. To use more or less masters, make calls to inc_master_count
    # and dec_master_count respectively.
    #
    # This method tries to update existing storage, although it doesn't assume
    # that there is currently any storage. Keep care to keep storage separate
    # from your tiling algorithm.
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
                self.storage.add_bottom(window)
            else:
                self.storage.try_to_promote(window)
        
    #
    # Simple method to switch two windows visually. It also takes care of
    # switching the windows in the storage container as well.
    #
    def help_switch(self, win1, win2):
        # same? weird...
        if win1.id == win2.id:
            return
        
        newpos = [win2.x, win2.y, win2.width, win2.height]
        win2.resize(win1.x, win1.y, win1.width, win1.height)
        win1.resize(newpos[0], newpos[1], newpos[2], newpos[3])
        
        self.storage.switch(win1, win2)
        
    #
    # The help_find_next and help_find_previous helper methods must be implemented
    # in a sub class if the functionality is to be used. Tiling
    # algorithms can sort windows differently such that the next/previous
    # windows cannot be accurately predicted generally. Unfortunately, these
    # little guys can be a little bit of a pain to right. (Edge cases, meh.)
    #
    def help_find_next(self):
        pass
    
    def help_find_previous(self):
        pass
        
    
    #------------------------------------------------------------------------------
    # DISPATCH
    #
    # The following methods are called from the dispatcher, and are directly
    # referenced from inside the .pytylerc configuration file. Most of these
    # methods simply call their member equivalents, but some (like tile/untile)
    # do some house keeping before hand.
    #
    # These should not be overloaded, but rather their equivalent member methods
    # preceded with an "_" should be overloaded to customize your tiling algorithm.
    #
    # You can get cursory information about these methods from the configuration
    # file, or you may peruse their comments above (in this class), and/or may
    # also take a look at the comments in Tilers/TileDefault.py, 
    # Tilers/Vertical.py, and/or Tilers/Horizontal.py.
    #------------------------------------------------------------------------------ 
        
    def tile(self):
        # save state...
        if not self.screen.is_tiling():
            self.help_save()
            
        # If we haven't tiled and we're about to,
        # reload the storage...
        if not self.screen.is_tiled():
            self.help_reload()
            
        self.screen.enable_tiling()
        self._tile()
        self.screen.got_tiling()
        
    def untile(self):
        self._untile()
        self.screen.disable_tiling()
        
    def cycle_tiler(self):
        for i in range(len(Config.misc('tilers'))):
            if Config.misc('tilers')[i] is self.__class__.__name__:
                if (i + 1) == len(Config.misc('tilers')):
                    self.screen.set_tiler(Config.tilers(Config.misc('tilers')[0]))
                else:
                    self.screen.set_tiler(Config.tilers(Config.misc('tilers')[i + 1]))
                    
        self._reset()
        
    def reload(self):
        self._reload()
        
    def reset(self):
        self._reset()
        
    def cycle(self):
        self._cycle()
        
    def screen0_focus(self):
        self._screen_focus(0)
        
    def screen1_focus(self):
        self._screen_focus(1)
        
    def screen2_focus(self):
        self._screen_focus(2)
        
    def screen0_put(self):
        self._screen_put(0)    
        
    def screen1_put(self):
        self._screen_put(1)
        
    def screen2_put(self):
        self._screen_put(2)
            
    def master_increase(self):
        self._master_increase()
            
    def master_decrease(self):
        self._master_decrease()
        
    def add_master(self):
        self._add_master()
        
    def remove_master(self):
        self._remove_master()
                
    def make_active_master(self):
        self._make_active_master()
        
    def win_master(self):
        self._win_master()
    
    def win_close(self):
        self._win_close()
        
    def win_previous(self):
        self._win_previous()
            
    def win_next(self):
        self._win_next()
        
    def switch_previous(self):
        self._switch_previous()
        
    def switch_next(self):
        self._switch_next()
            
    def max_all(self):
        self._max_all()
            
    def restore_all(self):
        self._restore_all()        
    
    def query(self):
        self._query()