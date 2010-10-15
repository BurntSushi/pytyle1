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

A simple container class for the configuration of PyTyle. See pytylerc
for more information on configuring PyTyle.

The only variable here that isn't in pytylerc is Config.TILERS. This
configuration variable is loaded at program start up as a dict of all
available tiling algorithms (as Python modules).

There is also a getter method here, just in case we're looking for an
option that isn't specified in the config.
"""

class Config:
    #------------------------------------------------------------------------------
    # CONFIGURATION VARIABLES
    #------------------------------------------------------------------------------

    MISC = {}
    KEYMAP = {}
    WORKAREA = {}
    FILTER = []
    LAYOUT = {}
    TILING = {}
    TILERS = {}
    CALLBACKS = {}


    #------------------------------------------------------------------------------
    # CONFIGURATION DEFAULTS
    #------------------------------------------------------------------------------

    DEFAULTS = {
                'MISC': {
                         'tilers': ['Vertical', 'Horizontal', 'Maximal', 'Cascade'],
                         'global_tiling': False,
                         'timeout': 0.1,
                         'decorations': True,
                         'original_decor': True,
                         },
                'KEYMAP': {
                           'Alt-A': 'tile.default',
                           'Alt-U': 'untile',
                           'Alt-Z': 'cycle_tiler',
                           'Alt-Shift-space': 'reset',
                           'Alt-C': 'cycle',
                           'Alt-W': 'screen0_focus',
                           'Alt-E': 'screen1_focus',
                           'Alt-R': 'screen2_focus',
                           'Alt-Shift-W': 'screen0_put',
                           'Alt-Shift-E': 'screen1_put',
                           'Alt-Shift-R': 'screen2_put',
                           'Alt-H': 'master_decrease',
                           'Alt-L': 'master_increase',
                           'Alt-period': 'add_master',
                           'Alt-comma': 'remove_master',
                           'Alt-Return': 'make_active_master',
                           'Alt-M': 'win_master',
                           'Alt-Shift-C': 'win_close',
                           'Alt-J': 'win_previous',
                           'Alt-K': 'win_next',
                           'Alt-Shift-J': 'switch_previous',
                           'Alt-Shift-K': 'switch_next',
                           'Alt-X': 'max_all',
                           'Alt-S': 'restore_all',
                           },
                'WORKAREA': {
                             0: {
                                 'top': 0,
                                 'bottom': 0,
                                 'right': 0,
                                 'left': 0,
                                 },
                             },
                'FILTER': [
                           'gmrun', 'gimp', 'download',
                           ],
                'LAYOUT': {
                           'Vertical': {
                                        'width_factor': 0.5,
                                        'margin': 0,
                                        },
                           'Horizontal': {
                                          'height_factor': 0.5,
                                          'margin': 0,
                                          },
                           'Maximal': {},
                           'Cascade': {
                                       'decoration_height': 25,
                                       'width_factor': 1.0,
                                       'height_factor': 1.0,
                                       'push_over': 0,
                                       'horz_align': 'left',
                                       },
                           'HorizontalRows': {
                                              'row_size': 2,
                                              'height_factor': 0.5,
                                              'margin': 0,
                                              },
                           },
                'TILING': {
                           'default': 'Vertical',
                           },
                'CALLBACKS': {
                            0:'make_active_master',
                            1:'switch_previous',
                            2:'switch_next'
                            }
                }


    #------------------------------------------------------------------------------
    # CONFIGURATION GETTERS
    #------------------------------------------------------------------------------

    @staticmethod
    def misc(name):
        if name in Config.MISC:
            return Config.MISC[name]

        if name in Config.DEFAULTS['MISC']:
            return Config.DEFAULTS['MISC'][name]

        return None

    @staticmethod
    def keymap(keys):
        if keys in Config.KEYMAP:
            return Config.KEYMAP[keys]

        if keys in Config.DEFAULTS['KEYMAP']:
            return Config.DEFAULTS['KEYMAP'][keys]

        return None

    @staticmethod
    def workarea(screen_number, section):
        if screen_number in Config.WORKAREA and section in Config.WORKAREA[screen_number]:
            return Config.WORKAREA[screen_number][section]

        return Config.DEFAULTS['WORKAREA'][0][section]

    @staticmethod
    def filter():
        return Config.FILTER

    @staticmethod
    def layout(tiler, option):
        layout = tiler.__class__.__name__
        if layout in Config.LAYOUT and option in Config.LAYOUT[layout]:
            return Config.LAYOUT[layout][option]

        if layout in Config.DEFAULTS['LAYOUT'] and option in Config.DEFAULTS['LAYOUT'][layout]:
            return Config.DEFAULTS['LAYOUT'][layout][option]

        return None

    @staticmethod
    def tiling(screen, desk_or_view):
        if screen in Config.TILING:
            if isinstance(Config.TILING[screen], dict) and desk_or_view in Config.TILING[screen]:
                return Config.TILING[screen][desk_or_view]
            elif not isinstance(Config.TILING[screen], dict):
                return Config.TILING[screen]
        elif 'default' in Config.TILING:
            return Config.TILING['default']

        return Config.DEFAULTS['TILING']['default']

    @staticmethod
    def tilers(layout):
        if layout in Config.TILERS:
            return Config.TILERS[layout]

    @staticmethod
    def callbacks(num):
        if num in Config.CALLBACKS:
            return Config.CALLBACKS[num]
        if num in Config.DEFAULTS['CALLBACKS']:
            return Config.DEFAULTS['CALLBACKS'][num]
        return None

    # Special flag to enable/disable debugging
    #
    # PRIVACY NOTE: This may log the titles of
    # your windows!
    DEBUG = False
