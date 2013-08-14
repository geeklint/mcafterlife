'''
    mcafterlife: Minecraft heavens emulation
    Copyright (C) 2013  Sky Leonard

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re

PREFIX = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[[A-Z]+\]'
PLAYER = r'([a-zA-Z0-9_]+)'

MESSAGES = [
    'was squashed by a falling anvil',
    'was pricked to death',
    'walked into a cactus whilst trying to escape',
    'was shot by arrow',
    'drowned',
    'drowned whilst trying to escape',
    'blew up',
    'was blown up by',
    'hit the ground too hard',
    'fell from a high place',
    'fell off a ladder',
    'fell off some vines',
    'fell out of the water',
    'fell into a patch of fire',
    'fell into a patch of cacti',
    'was doomed to fall',
    'was doomed to fall by',
    'was shot off some vines by',
    'was shot off a ladder by',
    'was blown from a high place by',
    'went up in flames',
    'burned to death',
    'was burnt to a crisp whilst fighting',
    'walked into a fire whilst fighting',
    'was slain by',
    'was shot by',
    'was fireballed by',
    'was killed by using magic',
    'got finished off by',
    'was slain by',
    'tried to swim in lava',
    'tried to swim in lava while trying to escape',
    'died',
    'got finished off by',
    'was slain by',
    'was shot by',
    'was killed by using magic',
    'was killed by magic',
    'starved to death',
    'suffocated in a wall',
    'was killed while trying to hurt',
    'was pummeled by',
    'fell out of the world',
    'fell from a high place and fell out of the world',
    'was knocked into the void by',
    'withered away',
]

REGEX = re.compile('%s %s (?:%s)' % (PREFIX, PLAYER,
                                     '|'.join(msg for msg in MESSAGES)))

def get_dead_player(line, regex=REGEX, match=re.match):
    m = match(regex, line)
    return m.group(1) if m else None


LEAVE_REGEX = re.compile('%s %s left the game' % (PREFIX, PLAYER))

def get_leave_player(line, regex=LEAVE_REGEX, match=re.match):
    m = match(regex, line)
    return m.group(1) if m else None

CHAT_REGEX = re.compile('%s <%s> (.*)' % (PREFIX, PLAYER))

def get_chat_player(line, regex=CHAT_REGEX, match=re.match):
    m = match(regex, line)
    return (m.group(1), m.group(2)) if m else None
