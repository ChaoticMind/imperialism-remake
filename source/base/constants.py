# Imperialism remake
# Copyright (C) 2014 Trilarion
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
    Game specific path locations for artwork, music, ...

    Only real static values go here.
"""

import os

import lib.utils as u

def extend(path, *parts):
    """
        Uses os.path.join to join parts of a path. Also checks for existence and raises an error
        if the path is not existing.
    """
    extended = os.path.join(path, *parts)
    if not os.path.exists(extended):
        raise RuntimeError('constructed path {} does not exist'.format(extended))
    if Debug_Mode:
        Used_Resources.add(extended)
    return extended

# debug mode and helpers
Debug_Mode = False
Used_Resources = set()

# base folders (do not directly contain data)
Data_Folder = extend('.', 'data')
Artwork_Folder = extend(Data_Folder, 'artwork')

# scenarios (save games)
Scenario_Folder = extend(Data_Folder, 'scenarios')
Core_Scenario_Folder = extend(Scenario_Folder, 'core')
Scenario_Ruleset_Folder = extend(Scenario_Folder, 'rules')
Scenario_Ruleset_Standard_File = extend(Scenario_Ruleset_Folder, 'standard.rules')
#Saved_Scenario_Folder = extend(Scenario_Folder, 'saved')

# music related folders
Music_Folder = extend(Artwork_Folder, 'music')
Soundtrack_Folder = extend(Music_Folder, 'soundtrack')
Soundtrack_Playlist = extend(Soundtrack_Folder, 'playlist.info')

# graphics related folders
Graphics_Folder = extend(Artwork_Folder, 'graphics')
Graphics_UI_Folder = extend(Graphics_Folder, 'ui')
Graphics_Map_Folder = extend(Graphics_Folder, 'map')

# special locations
Options_Default_File = extend(Data_Folder, 'options.info.default')
Manual_Index = extend(Data_Folder, 'manual', 'index.html')
Global_Stylesheet = extend(Graphics_UI_Folder, 'style.css')

# other specific constants

# network communication
Network_Port = 42932

# minimal screen resolution
Screen_Min_Size = (1024, 768)

# actual options version
Options_Version = 1

# option names
O_Version = 'misc.version'
O_Options_Version = 'misc.version.options'
OG_MW_Bounds = 'graphics.mainwindow.bounds'
OG_MW_Maximized = 'graphics.mainwindow.maximized'
OG_MW_Fullscreen = 'graphics.full_screen'
OG_Fullscreen_Supported = 'graphics.full_screen_supported'
OM_Phonon_Supported = 'music.phonon_supported'
OM_BG_Mute = 'music.background.mute'


# predefined channel names for network communication
CH_SCENARIO_PREVIEW = 'general.scenario.preview'
CH_CORE_SCENARIO_TITLES = 'general.core.scenarios.titles'

class TileDirections(u.AutoNumber):
    """
        Six directions for six neighbored tiles in clockwise order.
    """
    West = ()
    NorthWest = ()
    NorthEast = ()
    East = ()
    SouthEast = ()
    SouthWest = ()


class PropertyKeyNames:
    """
        Key names for general properties of a scenario.
    """

    TITLE = 'scenario.title'
    DESCRIPTION = 'scenario.description'
    MAP_COLUMNS = 'map.columns'
    MAP_ROWS = 'map.rows'
    RIVERS = 'rivers'


class NationPropertyKeyNames:
    """
        Key names for nation properties of a scenario.
    """

    COLOR = 'color'
    NAME = 'name'
    DESCRIPTION = 'description'
    CAPITAL_PROVINCE = 'capital_province'