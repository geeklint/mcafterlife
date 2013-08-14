#!/usr/bin/env python
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

import os
import zipfile

def main():
    os.chdir(os.path.dirname(__file__))
    with zipfile.PyZipFile('mcafterlife.pyz', 'w') as fd:
        for dirpath, dirnames, filenames in os.walk('src'):
            fd.writepy(dirpath)
        for name in os.listdir('cache'):
            fd.write(os.path.join('cache', name))


if __name__ == '__main__':
    main()
