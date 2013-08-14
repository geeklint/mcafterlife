
import sys
import threading
import Queue
from datetime import datetime

__all__ = ['get_disp',]


class BaseLogger(object):
    no_colors = {
        'error': '',
        'warning': '',
        'info': '',
        'debug': '',
        'reset': '',
    }
    
    def __init__(self, disp, level, use_colors):
        self.disp = disp
        self.level = level
        if not (use_colors and hasattr(self, 'colors')):
            self.colors = self.no_colors
    
    def format_time(self):
        return datetime.today().isoformat(' ')[:19]
    
    def base(self, level, title, msg):
        if self.level >= level:
            self.disp.display('%s%s [%s] %s%s' % (
                self.colors[title], self.format_time(), title.upper(), msg,
                self.colors['reset']))
    
    def e(self, msg):
        self.base(1, 'error', msg)
    
    def w(self, msg):
        self.base(2, 'warning', msg)
    
    def i(self, msg):
        self.base(3, 'info', msg)
    
    def d(self, msg):
        self.base(4, 'debug', msg)


class BaseDisp(object):
    (EVENT_CLEAR,
     EVENT_DISPLAY,
     EVENT_ADD,
     EVENT_FRONT,
     EVENT_RM,
     EVENT_ADD_LIST,
     EVENT_RM_LIST) = xrange(7)
    
    def __init__(self):
        self.shutdown = threading.Event()
        self.event_q = Queue.Queue()
    
    def stop(self):
        self.shutdown.set()
    
    @property
    def stopped(self):
        return self.shutdown.is_set()
        
    def wait(self):
        try:
            self.shutdown.wait()
        except KeyboardInterrupt:
            pass
    
    def clear(self):
        self.event_q.put((self.EVENT_CLEAR, tuple()))
    
    def display(self, line):
        self.event_q.put((self.EVENT_DISPLAY, (line,)))
    
    def add(self, name, interface):
        self.event_q.put((self.EVENT_ADD, (name, interface)))
    
    def front(self, name):
        self.event_q.put((self.EVENT_FRONT, (name,)))
    
    def rm(self, name):
        self.event_q.put((self.EVENT_RM, (name,)))
    
    def add_list(self, name, item):
        self.event_q.put((self.EVENT_ADD_LIST, (name, item)))
    
    def rm_list(self, name, item):
        self.event_q.put((self.EVENT_RM_LIST, (name, item)))
    
    def events(self, timeout):
        while True:
            try:
                yield self.event_q.get(timeout=timeout)
            except Queue.Empty:
                break


def get_disp(options):
    if options.nogui:
        term = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        disp_name = 'shell' if term else 'file'
    else:
        for name in ('Tkinter',): # support possible more disps
            try:
                __import__(name)
            except ImportError:
                continue
            else:
                disp_name = name.lower()
                break
        else:
            term = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            disp_name = 'shell' if term else 'file'
    module = __import__(''.join(('disp_', disp_name)), globals=globals())
    disp = module.get_disp()
    Logger = getattr(module, 'Logger', BaseLogger)
    disp.log = Logger(disp, options.v or 3, options.colors)
    return disp
