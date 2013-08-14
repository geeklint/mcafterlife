'''
Created on Jul 31, 2013

@author: geeklint
'''

import shlex
import sys
import threading
try:
    import readline
except ImportError:
    readline = None

from . import BaseLogger, BaseDisp

class Logger(BaseLogger):
    colors = {
        'error':   '\x1b[31m',
        'warning': '\x1b[33m',
        'info':    '\x1b[32m',
        'debug':   '\x1b[37m',
        'reset':   '\x1b[39m',
    }


class ShellDisp(BaseDisp):
    def __init__(self):
        super(ShellDisp, self).__init__()
        self.prompt = '[@]: '
        self.fronts = {'@': (self, ['console'])}
        self.current_front = self
        self.front_mutex = threading.RLock()
    
    def set_front(self):
        pass
    
    def drop_front(self):
        pass
    
    def send_msg(self, msg):
        cmd = shlex.split(msg)
        if cmd[0] == 'list':
            with self.front_mutex:
                self.display(
                    '\n'.join(
                        '\n\t'.join([name,] + list_)
                        for name, (_, list_) in self.fronts.iteritems()))
        elif cmd[0] == 'stop':
            self.log.i('stopping...')
            self.stop()
            return True
        elif cmd[0] == 'front':
            self.front(cmd[1])
        else:
            self.display('type `list` to see players and instances\n'
                    'type `front [instance]` to focus that instance\n'
                    'type `stop` to shutdown all instances')


def output_thread_rl(disp):
    while not disp.stopped:
        for event, args in disp.events(timeout=1):
            if event is BaseDisp.EVENT_DISPLAY:
                buf = ''.join((disp.prompt, readline.get_line_buffer()))
                whiteout = ''.join(('\r', ' '*len(buf), '\r'))
                sys.stdout.write(''.join((whiteout, args[0], '\n', buf)))
                sys.stdout.flush()
            else:
                output_thread_anyrl(disp, event, args)


def output_thread_norl(disp):
    while not disp.stopped:
        for event, args in disp.events(timeout=1):
            if event is BaseDisp.EVENT_DISPLAY:
                print args[0]
            else:
                output_thread_anyrl(disp, event, args)


def output_thread_anyrl(disp, event, args):
    with disp.front_mutex:
        if event is BaseDisp.EVENT_CLEAR:
            pass # clearing terminal is unnecessarily complex and who cares
        elif event is BaseDisp.EVENT_ADD:
            disp.fronts[args[0]] = args[1], []
        elif event is BaseDisp.EVENT_RM:
            disp.fronts.pop(args[0])
        elif event is BaseDisp.EVENT_FRONT:
            if not args[0] in disp.fronts:
                disp.log.e('cannot focus %s: DNE' % args[0])
            else:
                disp.current_front.drop_front()
                disp.current_front = disp.fronts[args[0]][0]
                disp.current_front.set_front()
                disp.prompt = '[%s]: ' % args[0]
        elif event is BaseDisp.EVENT_ADD_LIST:
            disp.fronts[args[0]][1].append(args[1])
        elif event is BaseDisp.EVENT_RM_LIST:
            disp.fronts[args[0]][1].remove(args[1])


def input_thread(disp):
    while True:
        try:
            cmd = raw_input(disp.prompt)
        except EOFError:
            with disp.front_mutex:
                if disp.current_front is disp:
                    disp.send_msg('stop')
                    return
                else:
                    disp.front('@')
        else:
            with disp.front_mutex:
                if disp.current_front.send_msg(cmd):
                    return


def get_disp():
    disp = ShellDisp()
    output_thread = output_thread_rl if readline else output_thread_norl
    threading.Thread(target=output_thread, args=(disp,)).start()
    inthread = threading.Thread(target=input_thread, args=(disp,))
    # the only thread we can't reliably set timeout on is raw_input, so make
    # it a "daemon" so the program can exit
    #inthread.daemon = True
    # cancel that, it leaves the terminal in a bad state
    # instead we will break from input loop
    inthread.start()
    return disp
