'''
Created on Jul 30, 2013

@author: geeklint
'''

# most comprehensive way to determine version

import sys

if sys.hexversion >= 34013184 and sys.hexversion < 50331648:
    import main
    sys.exit(main.main())
else:
    print ('Please use python 2.7')