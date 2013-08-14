#!/usr/bin/env python

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
