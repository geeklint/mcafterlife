'''
Created on Jul 31, 2013

@author: geeklint
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
