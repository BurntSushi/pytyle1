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
HorizontalRows.py

This is something *like* the "Horizontal" layout, except instead of having
one row of slaves "beneath" the master, it can have multiple rows. By
default, it will be two windows per row (or, two columns). This can be
changed in the LAYOUT portion of the configuration file.
"""

from PyTyle.Tilers.TileDefault import TileDefault
import math

class HorizontalRows (TileDefault):
    #
    # Does almost the same thing as the Horizontal layout,
    # but is a bit more complex to account for multiple
    # rows.
    #
    def _tile(self):
        x, y, width, height = self.screen.get_workarea()

        # set some vars...
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        row_size = self.state.get('row_size')
        rows = int(math.ceil(float(len(slaves)) / float(row_size)))
        last_row_size = len(slaves) % row_size
        if not last_row_size: last_row_size = row_size

        masterWidth = width if not masters else (width / len(masters))
        masterHeight = height if not slaves else int(height * self.state.get('height_factor'))
        masterY = y
        masterX = x

        slaveWidth = width if not slaves else (width / row_size)
        slaveHeight = height if not slaves else ((height if not masters else height - masterHeight) / rows)
        slaveY = y if not masters else (y + masterHeight)
        slaveX = x

        # resize the master windows
        for master in masters:
            self.help_resize(master, masterX, masterY, masterWidth, masterHeight, self.state.get('margin'))
            masterX += masterWidth

        current_row = 1
        current_window = 1
        for slave in slaves:
            # last row!
            if current_row == rows:
                slaveWidth = width / last_row_size

            self.help_resize(slave, slaveX, slaveY, slaveWidth, slaveHeight, self.state.get('margin'))
            slaveX += slaveWidth

            if current_window % row_size == 0:
                current_row += 1
                current_window = 1
                slaveX = x
                slaveY += slaveHeight
            else:
                current_window += 1

    #
    # This one is actually pretty neat. First we need to take care
    # of our masters, which is pretty straight forward. Then we move
    # the first row of slaves up by the regular pixel amount. Then the
    # second row gets moved up slightly less (pixels - (pixels/rows))
    # to be exact. And so on and so forth. Each row gets a height
    # increase of pixels/rows.
    #
    # Note: We of course deal with integers here. In order to get around
    # what could be a nasty rounding problem, we modify the pixel
    # increase/decrease number right away to make sure it's a multiple
    # of the number of rows. (We go down instead of up.)
    #
    def _master_increase(self, factor = 0.05):
        x, y, width, height = self.screen.get_workarea()
        slaves = self.storage.get_slaves()
        masters = self.storage.get_masters()
        row_size = self.state.get('row_size')
        rows = int(math.ceil(float(len(slaves)) / float(row_size)))

        # Stop if neither of either... haha
        if not slaves or not masters:
            return

        # first calculate pixels...
        pixels = int(((self.state.get('height_factor') + factor) * height) - (self.state.get('height_factor') * height))
        self.state.set('height_factor', self.state.get('height_factor') + factor)

        # Make it easy... change pixels to next closest
        # multiple of the number of rows...
        pixels = pixels - (pixels % rows)
        slave_pixels = pixels / rows

        current_row = 1
        current_window = 1
        height_pixels = pixels
        for slave in slaves:
            slave.resize(slave.x, slave.y + height_pixels, slave.width, slave.height - slave_pixels)

            if current_window % row_size == 0:
                current_row += 1
                current_window = 1
                height_pixels -= slave_pixels
            else:
                current_window += 1
        for master in masters:
            master.resize(master.x, master.y, master.width, master.height + pixels)

    #
    # See master_increase.
    #
    def _master_decrease(self, factor = 0.05):
        x, y, width, height = self.screen.get_workarea()
        slaves = self.storage.get_slaves()
        masters = self.storage.get_masters()
        row_size = self.state.get('row_size')
        rows = int(math.ceil(float(len(slaves)) / float(row_size)))

        # Stop if neither of either... haha
        if not slaves or not masters:
            return

        # first calculate pixels...
        pixels = int((self.state.get('height_factor') * height) - ((self.state.get('height_factor') - factor) * height))
        self.state.set('height_factor', self.state.get('height_factor') - factor)

        # Make it easy... change pixels to next closest
        # multiple of the number of rows...
        pixels = pixels - (pixels % rows)
        slave_pixels = pixels / rows

        current_row = 1
        current_window = 1
        height_pixels = pixels
        for slave in slaves:
            slave.resize(slave.x, slave.y - height_pixels, slave.width, slave.height + slave_pixels)

            if current_window % row_size == 0:
                current_row += 1
                current_window = 1
                height_pixels -= slave_pixels
            else:
                current_window += 1
        for master in masters:
            master.resize(master.x, master.y, master.width, master.height - pixels)

    #------------------------------------------------------------------------------
    # OVERLOADED PRIVATE HELPER METHODS
    #------------------------------------------------------------------------------


    #
    # In HorizontalRows, the alignment of the masters is a bit weird. We would like
    # to have a consistent ordering style like so:
    # win --- win
    #       -
    #      -
    #     -
    # win --- win
    #       -
    #      -
    #     -
    # win --- win
    #
    # Note: See this method in Tile.TileDefault for additional comments.
    #
    def help_find_next(self):
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        all = masters + slaves

        if masters and self.screen.get_active().id == masters[-1].id:
            if not slaves:
                return masters[0]
            else:
                return slaves[0]
        elif slaves and self.screen.get_active().id == slaves[-1].id:
            if not masters:
                return slaves[0]
            else:
                return masters[0]
        elif slaves and self.screen.get_active().id in [win.id for win in slaves]:
            for i in range(len(slaves) - 1):
                if self.screen.get_active().id == slaves[i].id:
                    return slaves[(i + 1)]
        elif masters:
            for i in range(0, len(masters) - 1):
                if self.screen.get_active().id == masters[i].id:
                    return masters[(i + 1)]

    #
    # See help_find_next above. Also see the comments in the code,
    # as help_find_previous is basically the same thing- we're just
    # going in reverse.
    #
    def help_find_previous(self):
        masters = self.storage.get_masters()
        slaves = self.storage.get_slaves()
        all = masters + slaves

        if masters and self.screen.get_active().id == masters[0].id:
            if not slaves:
                return masters[-1]
            else:
                return slaves[-1]
        elif slaves and self.screen.get_active().id == slaves[0].id:
            if not masters:
                return slaves[-1]
            else:
                return masters[-1]
        elif masters and self.screen.get_active().id in [win.id for win in masters]:
            for i in range(1, len(masters)):
                if self.screen.get_active().id == masters[i].id:
                    return masters[(i - 1)]
        elif slaves:
            for i in range(1, len(slaves)):
                if self.screen.get_active().id == slaves[i].id:
                    return slaves[(i - 1)]

# You must have this line's equivalent for your tiling algorithm!
# This makes it possible to dynamically load tiling algorithms.
# (So that you may simply drop them into the Tilers directory,
# and add their name to the configuration- vini, vidi, vicci!)
CLASS = HorizontalRows