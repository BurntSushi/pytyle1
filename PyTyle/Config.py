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
Config.py

A simple container class for the configuration of PyTyle. See .pytylerc
for more information on configuring PyTyle.

The onyl variable here that isn't in .pytylerc is Config.TILERS. This
configuration variable is loaded at program start up as a dict of all
available tiling algorithms (as Python modules).
"""

class Config:
    MISC = {}
    KEYMAP = {}
    WORKAREA = {}
    FILTER = {}
    TILING = {}
    TILERS = {}