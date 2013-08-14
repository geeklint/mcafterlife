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

import threading
from collections import defaultdict
from itertools import count

DATA = {}

def get_entry_world():
    return min([user['world'] for user in DATA['users'].values()] or [0,])


def default_user():
    return {
        'world': get_entry_world(),
        'deaths': 0,
    }

def default_port():
    return next(x for x in count(25566) if not x in DATA['ports'].values())

class _GetData(object):
    def __init__(self, data):
        self.data = data
        self.lock = threading.RLock()
        
    def __call__(self):
        if not self.data:
            self.data.update({
                'users': defaultdict(default_user),
                'ports': defaultdict(default_port),
            })
        return self.data
    
    def __enter__(self):
        self.lock.acquire()
        return self.data
    
    def __exit__(self, *exc):
        self.lock.release()

get_data = _GetData(DATA)

get_options = _GetData(None)

def set_options(options):
    get_options.data = options
