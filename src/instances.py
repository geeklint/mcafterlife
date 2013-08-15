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

import Queue
import os
import shlex
import shutil
import signal
import subprocess
import threading
import time
from collections import deque

from datafunc import get_data, get_options, get_entry_world
from deathmessages import get_dead_player, get_leave_player, get_chat_player
from utils import stop_proc, cont_proc


class Instance(threading.Thread):
    instances = {}
    STOP = object()
    chat_q = Queue.Queue()
    def __init__(self, instance, disp):
        threading.Thread.__init__(self)
        self.instance_id = instance
        self.clients = dict()
        self.wakeup = threading.Event()
        self.ready = threading.Event()
        self.msg_q = Queue.Queue()
        self.output_q = Queue.Queue()
        self.log_lines = deque(maxlen=24)
        self.front = False
        self.disp = disp
        Instance.instances[instance] = self
    
    @classmethod
    def stop_all(cls):
        for ins in cls.instances.values():
            ins.send_msg(cls.STOP)
        for ins in cls.instances.values():
            ins.join()
    
    @classmethod
    def get(cls, instance, disp=None):
        ins = cls.instances.get(instance)
        if ins is None:
            ins = cls(instance, disp)
            ins.start()
        return ins
    
    def set_front(self):
        self.disp.clear()
        for line in self.log_lines:
            self.disp.display(line)
        self.front = True
    
    def drop_front(self):
        self.front = False
    
    def player_join(self, name, handler):
        self.clients[name] = handler
        self.wakeup.set()
    
    def send_msg(self, msg):
        self.msg_q.put(msg)
        self.wakeup.set()
    
    def enqueue_output(self, stdout):
        for line in iter(stdout.readline, ''):
            self.output_q.put(line.rstrip('\n'))
        
    def run(self):
        # optimizations:
        join = os.path.join
        exists = os.path.exists
        wakeup = self.wakeup
        disp = self.disp
        options = get_options()
        ins_id = self.instance_id
        ins_dir = join(options.working, 'instance-%d' % ins_id)
        delete = False
        # verify everything in order
        if not exists(ins_dir):
            os.makedirs(ins_dir)
        props = join(ins_dir, 'server.properties')
        if not exists(props):
            shutil.copy(join(options.cachedir, 'server.properties'), ins_dir)
            with open(props, 'a') as propsfile:
                with get_data as data:
                    port = data['ports'][ins_id]
                propsfile.write('\nserver-port=%d\n' % port)
        if not exists(join(ins_dir, 'minecraft_server.jar')):
            shutil.copy(options.jar, join(ins_dir, 'minecraft_server.jar'))
        cmd = [options.java,] + shlex.split(options.java_args) + [
               '-jar', 'minecraft_server.jar', 'nogui']
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, cwd=ins_dir)
        # let server set up
        while process.poll() is None:
            for line in iter(process.stdout.readline, ''):
                line = line.rstrip('\n')
                self.log_lines.append(line)
                if self.front:
                    disp.display(line)
                if 'Done' in line:
                    self.ready.set()
                    break
            if self.ready.is_set():
                break
        else:
            return
        # main loop
        enq_out = threading.Thread(target=self.enqueue_output,
                                   args=(process.stdout,))
        enq_out.daemon = True
        enq_out.start()
        disp.add(str(ins_id), self)
        disp.log.d('instance %d started' % ins_id)
        do_stop = True
        msg = None
        while process.poll() is None:
            while True:
                try:
                    msg = self.msg_q.get(timeout=0.01)
                except Queue.Empty:
                    break
                if msg is self.STOP:
                    break
                process.stdin.write(msg + '\n')
            if msg is self.STOP:
                break
            while True:
                try:
                    line = self.output_q.get(timeout=0.01)
                except Queue.Empty:
                    break
                dead, leave, chat = (get_dead_player(line),
                                     get_leave_player(line),
                                     get_chat_player(line))
                self.log_lines.append(line)
                if any((self.front, dead, leave, chat)):
                    disp.display(line)
                if dead:
                    disp.log.i('%s ascends to heaven %d' % (
                            dead, ins_id+1))
                    with get_data as data:
                        data['users'][dead]['world'] += 1
                elif leave:
                    self.clients.pop(leave).close()
                    disp.rm_list(str(ins_id), leave)
                elif chat:
                    self.chat_q.put(chat)
            if not self.clients:
                if ins_id < get_entry_world():
                    if not options.keep:
                        delete = True
                    break # stop server (unreachable)
                with get_data as data:
                    if not any(u['world'] == ins_id for u in data['users']):
                        break # stop server (no players)
                disp.log.d('putting instance %d to sleep' % ins_id)
                wakeup.clear()
                if stop_proc(process, disp):
                    if wakeup.wait(timeout=120):
                        disp.log.d('waking up instance %d' % ins_id)
                        cont_proc(process)
                    else:
                        break # stop server (timeout)
        else: # out of main loop
            do_stop = False # already stopped
        if do_stop:
            disp.log.i('stopping instance %d' % ins_id)
            disp.rm(str(ins_id))
            process.stdin.write('stop\n')
            for func in (process.terminate, process.kill):
                time.sleep(2)
                if process.poll() is not None:
                    break
                func()
        if delete:
            disp.log.d('deleting instance %d' % ins_id)
            shutil.rmtree(ins_dir)
