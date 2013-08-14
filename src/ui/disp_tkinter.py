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
import Tkinter as tk
import ScrolledText as tkst
from functools import partial

from . import BaseDisp, BaseLogger

class Logger(BaseLogger):
    pass


class TkDisp(BaseDisp):
    def wait(self):
        self.app.run()


class DefaultFront(object):
    def __init__(self, disp, app):
        self.disp = disp
        self.app = app
    
    def send_msg(self, msg):
        for front in self.app.fronts.values():
            if front[0] is not self:
                front[0].send_msg(msg)
    
    def set_front(self):
        self.disp.clear()
    
    def drop_front(self):
        pass


class App(threading.Thread):
    def __init__(self, disp):
        threading.Thread.__init__(self)
        self.disp = disp
        self.root = root = tk.Tk()
        self.button_frame = tk.Frame(root, relief=tk.FLAT)
        self.button_frame.pack(side=tk.LEFT, fill=tk.X)
        front_frame = tk.Frame(root, relief=tk.FLAT)
        front_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.text_box = tkst.ScrolledText(front_frame, state=tk.DISABLED)
        self.text_box.pack(fill=tk.X, expand=1, side=tk.TOP)
        self.entry_box = tk.Entry(front_frame)
        self.entry_box.bind('<Return>', self.on_text_entry)
        self.entry_box.pack(fill=tk.BOTH, side=tk.TOP)
        self.fronts = dict()
        self.disp.add('@', DefaultFront(disp, self))
    
    def on_text_entry(self, event):
        entry = event.widget
        self.current_front.send_msg(entry.get())
        entry.delete(0, tk.END)
    
    def tick(self):
        self.root.after(200, self.tick)
        for event, args in self.disp.events(timeout=0.0):
            if event is BaseDisp.EVENT_DISPLAY:
                self.text_box.config(state=tk.NORMAL)
                self.text_box.insert(tk.END, ''.join((args[0], '\n')))
                self.text_box.yview(tk.END)
                self.text_box.config(state=tk.DISABLED)
            elif event is BaseDisp.EVENT_CLEAR:
                self.text_box.config(state=tk.NORMAL)
                self.text_box.delete('1.0', tk.END)
                self.text_box.config(state=tk.DISABLED)
            elif event is BaseDisp.EVENT_ADD:
                command = partial(self.disp.front, args[0])
                button = tk.Button(self.button_frame,
                                   text=args[0],
                                   command=command)
                button.pack(fill=tk.X, side=tk.TOP)
                label = tk.Label(self.button_frame)
                label.pack(fill=tk.X, side=tk.TOP)
                self.fronts[args[0]] = args[1], [], button, label
                if not hasattr(self, 'current_front'):
                    self.current_front = args[1]
                    args[1].set_front()
                    self.current_button = button
                    button.config(state=tk.ACTIVE)
            elif event is BaseDisp.EVENT_RM:
                front, _l, button, label = self.fronts.pop(args[0])
                if front is self.current_front:
                    self.disp.front('@')
                button.destroy()
                label.destroy()
            elif event is BaseDisp.EVENT_FRONT:
                self.current_front.drop_front()
                self.current_button.config(state=tk.NORMAL)
                self.current_front = self.fronts[args[0]][0]
                self.current_button = self.fronts[args[0]][2]
                self.current_front.set_front()
                self.current_button.config(state=tk.ACTIVE)
            elif event is BaseDisp.EVENT_ADD_LIST:
                front = self.fronts[args[0]]
                front[1].append(args[1])
                front[3].config(text='\n'.join(front[1]))
            elif event is BaseDisp.EVENT_RM_LIST:
                front = self.fronts[args[0]]
                front[1].remove(args[1])
                front[3].config(text='\n'.join(front[1]))
    
    def run(self):
        self.tick()
        self.root.mainloop()


def get_disp():
    disp = TkDisp()
    disp.app = app = App(disp)
    return disp
