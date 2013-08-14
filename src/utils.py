'''
Created on Jul 30, 2013

@author: geeklint
'''

import os
import signal

def which(name, flags=os.X_OK, os=os):
    '''`which` function. Stolen from twisted'''
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in path.split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result


def stop_proc(process, disp):
    if hasattr(signal, 'SIGSTOP'):
        process.send_signal(signal.SIGSTOP)
    else:
        disp.log.d('stopping process is unsupported')
        return False
    return True


def cont_proc(process):
    if hasattr(signal, 'SIGCONT'):
        process.send_signal(signal.SIGCONT)
    

