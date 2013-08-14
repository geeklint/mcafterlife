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

import argparse
import json
import os
import sys
import urllib2
import zipfile
from contextlib import closing
try:
    import cPickle as pickle
except ImportError:
    import pickle

import datafunc
import instances
import server
import ui
from utils import which

class BoolCheck(object):
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg
    def __call__(self, obj):
        if not self.func(obj):
            raise argparse.ArgumentTypeError(self.msg % obj)
        return obj

CACHE_DIR = '.mcafterlifecache'
CACHE_PRFX = 'cache/'
JAR_URL = ('https://s3.amazonaws.com/Minecraft.Download/versions/1.6.2/'
           'minecraft_server.1.6.2.jar')
ARGS = {
    '--last': {
        'help': 'use the last valid settings',
        'action': 'store_true',
    },
    '--working': {
        'help': 'change working directory',
        'default': os.curdir,
        'type': BoolCheck(os.path.isdir, 'dir %r does not exist'),
    },
    '--java': {
        'help': 'location of java binary',
        'default': (which('java') or (None,))[0],
        'required': bool(which('java')),
    },
    '--java-args': {
        'help': 'args to java',
        'default': '-Xmx1024M -Xms1024M',
    },
    '--jar': {
        'help': 'location of minecraft_server.jar',
        'default': 'minecraft_server.jar'
    },
    '-n': {
        'help': 'max players (servers)',
        'type': int,
        'default': 10,
    },
    '--motd': {
        'help': 'motd to return with server list pings',
        'default': 'An Afterlife Server',
    },
    '--keep': {
        'help': 'keep servers after there is nobody left to play on them',
        'action': 'store_true',
    },
    '--host': {
        'help': 'hostname to bind to',
        'default': '',
    },
    '--port': {
        'help': 'port to serve on',
        'default': 25565,
        'type': int,
    },
    '--nogui': {
        'help': 'do not try to launch a gui',
        'action': 'store_true',
    },
    '--colors': {
        'help': 'enable ansi terminal colors',
        'action': 'store_true',
    },
    '-v': {
        'help': 'set level of verbose output',
        'action': 'count',
    }
}

def check_cache():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with zipfile.ZipFile(os.path.dirname(__file__)) as sfx:
        for cachefile in sfx.namelist():
            if cachefile.startswith(CACHE_PRFX):
                writename = os.path.join(CACHE_DIR,
                                         cachefile[len(CACHE_PRFX):])
                if not os.path.exists(writename):
                    with open(writename, 'wb') as writefile:
                        writefile.write(sfx.read(cachefile))


def download_server(localname):
    with open(localname, 'wb') as local:
        with closing(urllib2.urlopen(JAR_URL)) as remote:
            local.write(remote.read())


def main():
    parser = argparse.ArgumentParser()
    for arg in ARGS:
        parser.add_argument(arg, **ARGS[arg])
    options = parser.parse_args()
    os.chdir(options.working)
    check_cache()
    if options.last:
        with open(os.path.join(CACHE_DIR, 'last.txt'), 'w') as lastfile:
            for key, value in json.load(lastfile).iteritems():
                setattr(options, key, value)
        os.chdir(options.working)
    else:
        with open(os.path.join(CACHE_DIR, 'last.txt'), 'w') as lastfile:
            json.dump(vars(options), lastfile)
    if not os.path.exists(options.jar):
        print "Can't find minecraft_server.jar."
        res = raw_input('Download now? [y/N] ')
        if res.startswith('y') or res.startswith('Y'):
            download_server(options.jar)
        else:
            print 'fatal: no minecraft_server.jar.'
            return 1
    options.cachedir = CACHE_DIR
    dataname = os.path.join(options.cachedir, 'data.p')
    data = datafunc.get_data()
    if os.path.exists(dataname):
        with open(dataname) as datafile:
            data.update(pickle.load(datafile))
    datafunc.set_options(options)
    disp = ui.get_disp(options)
    server.start_server(disp)
    disp.wait()
    instances.Instance.stop_all()
    server.stop_server()
    with open(dataname, 'w') as datafile:
        pickle.dump(datafunc.get_data(), datafile)
    print
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())
