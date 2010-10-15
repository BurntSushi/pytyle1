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
TileStorage.py

My attempt at abstracting the storage of windows for tiling algorithms.
Namely, the handling of window ordering so that we have a data structure
that closely resembles that which you see on the screen. Additionally, it
will handle the management of masters and slaves. Tiling algorithms need
only be aware of the masters and slaves, and shouldn't have to manage which
windows become masters or slaves (unless you need to).

This is also where we run our filter specified in the configuration.
(Should this be moved to load_window?) This is also where we decide to
show/hide hidden windows. Namely, you can "add" a window to the tiling
storage, and it's possible that it won't be added. That is intentional.

Remember, if a window isn't in the storage, it will *not* be tiled. While
it will have a place in PyTyle, the tiling algorithm will not be able
to see it.
"""

class TileStorage:
    #------------------------------------------------------------------------------
    # CONSTRUCTOR AND INSTANCE METHODS
    #------------------------------------------------------------------------------
    
    #
    # Will start the master count at 1, and initialize the master and slave
    # *ordered* lists.
    #
    def __init__(self):
        self._master_count = 1
        self._masters = []
        self._slaves = []
        
    #
    # Adds a window to the storage. This will detect if that window should
    # be a slave or a master based on the current master count and how
    # many masters are currently loaded in the storage.
    #
    def add(self, window):
        if window.hidden: return
        
        if len(self._masters) < self.get_master_count():
            if window.id in self.get_slaves_by_id():
                self._remove_slave(window)
            self._add_master(window)
        else:
            self._add_slave(window)
            
    def add_top(self, window):
        if window.hidden: return
        
        if len(self._masters) < self.get_master_count():
            if window.id in self.get_slaves_by_id():
                self._remove_slave(window)
            self._add_top_master(window)
        else:
            self._add_top_slave(window)
            
    def add_bottom(self, window):
        if window.hidden: return
        
        if len(self._masters) < self.get_master_count():
            if window.id in self.get_slaves_by_id():
                self._remove_slave(window)
            self._add_bottom_master(window)
        else:
            self._add_bottom_slave(window)
        
    #
    # Decrements the number of masters allowed for this tiler. It cannot
    # go below 0 for obvious reasons (but can be equal to 0).
    #
    def dec_master_count(self):
        if self._master_count == 0: return
        self._master_count -= 1
    
    #
    # Returns all windows currently in the storage.
    #    
    def get_all(self):
        return self.get_masters() + self.get_slaves()
    
    #
    # Returns all windows currently in the storage by their id.
    #
    def get_all_by_id(self):
        return self.get_masters_by_id() + self.get_slaves_by_id()
    
    #
    # Returns all masters currently in the storage. It will
    # conveniently extract the windows from the tupling storage
    # mechanism.
    #
    def get_masters(self):
        return [window for (title, window) in self._masters]
    
    #
    # Returns all the masters' ids.
    #
    def get_masters_by_id(self):
        return [window.id for (title, window) in self._masters]
    
    #
    # Returns the number of masters currently allowed.
    #
    def get_master_count(self):
        return self._master_count
    
    #
    # Returns all slaves currently in the storage.
    #
    def get_slaves(self):
        return [window for (title, window) in self._slaves]
    
    #
    # Returns all slaves' ids.
    #
    def get_slaves_by_id(self):
        return [window.id for (title, window) in self._slaves]
    
    #
    # Tells the tiling storage to allow for one more master.
    # There is no theoretical limit.
    #
    # Note: It is *possible* that your tiling algorithm will
    # want to restrict the number of masters. (See XMonad's
    # circle tiling algorithm.)
    #
    # Remember: This is not the number of masters, but rather
    # the number of *POSSIBLE* masters.
    #
    def inc_master_count(self):
        self._master_count += 1
        
    #
    # Removes a window from the storage.
    #
    def remove(self, window):
        if window.id in self.get_masters_by_id():
            self._remove_master(window)
        if window.id in self.get_slaves_by_id():
            self._remove_slave(window)
            
    #
    # Will sort the entire storage. This is currently
    # only called when you need to reload your storage.
    # It is not recommended to do so elsewhere, as it might
    # introduce inconsistencies between the storage and
    # the screen.
    #
    def sort(self):
        self._masters.sort()
        self._slaves.sort()
        
    #
    # Will switch any two windows. This preseves the
    # representation of storage as it pertains to the
    # screen's physical appearence.
    #
    def switch(self, win1, win2):
        for i in range(len(self._masters)):
            win = self._masters[i][1]
            if win1.id == win.id:
                self._masters[i] = (win2.title.lower(), win2)
            if win2.id == win.id:
                self._masters[i] = (win1.title.lower(), win1)
        
        for i in range(len(self._slaves)):
            win = self._slaves[i][1]
            if win1.id == win.id:
                self._slaves[i] = (win2.title.lower(), win2)
            if win2.id == win.id:
                self._slaves[i] = (win1.title.lower(), win1)
                
    #
    # This will try to promote a given window (has to be
    # a slave) to master status. Useful for reloading the
    # storage. (There could be slaves and extra room for
    # masters.)
    #
    def try_to_promote(self, window):
        if len(self._masters) < self.get_master_count() and window.id in self.get_slaves_by_id():
            self._remove_slave(window)
            self._add_master(window)
    
    
    #------------------------------------------------------------------------------
    # PRIVATE HELPER (INSTANCE) METHODS
    #------------------------------------------------------------------------------
    
    #
    # Explicitly adds a master to the storage. Please do not
    # call this directly, as it doesn't sync with the master
    # count.
    #
    def _add_master(self, window):
        self._masters.append(
                            (window.title.lower(), window)
                            )
        
    #
    # Explicitly adds a slave to the storage.
    #
    def _add_slave(self, window):
        self._slaves.append(
                           (window.title.lower(), window)
                           )
    
    #
    # Explicitly adds a master to the storage. Please do not
    # call this directly, as it doesn't sync with the master
    # count.
    #
    def _add_bottom_master(self, window):
        self._masters.append(
                            (window.title.lower(), window)
                            )
        
    #
    # Explicitly adds a slave to the storage.
    #
    def _add_bottom_slave(self, window):
        self._slaves.append(
                           (window.title.lower(), window)
                           )
        
    #
    # Explicitly adds a master to the storage. Please do not
    # call this directly, as it doesn't sync with the master
    # count.
    #
    def _add_top_master(self, window):
        self._masters.insert(0,
                            (window.title.lower(), window)
                            )
        
    #
    # Explicitly adds a slave to the storage.
    #
    def _add_top_slave(self, window):
        self._slaves.insert(0,
                           (window.title.lower(), window)
                           )
    
    #
    # Explicitly removes a master from the storage.
    #        
    def _remove_master(self, window):
        for i in range(len(self._masters)):
            win = self._masters[i][1]
            if window.id == win.id:
                del self._masters[i]
                break
     
    #
    # Explicitly removes a slave from the storage.
    #       
    def _remove_slave(self, window):
        for i in range(len(self._slaves)):
            win = self._slaves[i][1]
            if window.id == win.id:
                del self._slaves[i]
                break
    
    #
    # A nice output of the current storage. Useful for
    # debugging.
    #
    def __str__(self):
        ret = 'Master(s):\n'
        for master in self.get_masters():
            ret += '\t%s - %s\n' % (master.title, master.id)
        
        ret += 'Slave(s):\n'
        for slave in self.get_slaves():
            ret += '\t%s - %s\n' % (slave.title, slave.id)
            
        return ret