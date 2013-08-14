'''
Created on Aug 1, 2013

@author: geeklint
'''

import Queue
import asyncore
import json
import socket
import struct
import threading
from contextlib import closing

from datafunc import get_data, get_options
from instances import Instance

ENCODING = 'utf-16be'
PROTO_INT = u'74'
PROTO_STR = u'1.6.2'

def compose_list_ping():
    with get_options as options:
        motd = options.motd.decode('utf-8')
        maxc = unicode(options.n)
    c = unicode(Handler.clients)
    list_ping = u'\x00'.join((u'\xa71', PROTO_INT, PROTO_STR, motd, c, maxc))
    return struct.pack('>BH%ds' % (2 * len(list_ping)),
            0xFF, len(list_ping), list_ping.encode(ENCODING))


def compose_str_packet(packet, msg):
    enc_msg = msg.encode(ENCODING)
    return struct.pack('>BH%ds' % len(enc_msg), packet, len(msg), enc_msg)


def compose_server_full():
    return compose_str_packet(0xff, u'The server is full!')


def compose_server_not_ready():
    return compose_str_packet(0xff, u'Please wait for server to start')


def compose_chat(chat):
    obj = {'translate': 'chat.type.text', 'using': chat}
    return compose_str_packet(0x03, json.dumps(obj, separators=(',',':')))


def comprehend_handshake(packet):
    length, = struct.unpack('>H', packet[1:3])
    return packet[3:3+length*2].decode(ENCODING)


class Forwarder(asyncore.dispatcher_with_send):
    fwds = []
    def __init__(self, port, handler):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('localhost', port))
        self.handler = handler
        self.fwds.append(self)
    
    def close(self):
        asyncore.dispatcher_with_send.close(self)
        self.fwds.remove(self)
    
    def handle_read(self):
        self.handler.send(self.recv(4096))
    
    def handle_close(self):
        self.handler.close()
        self.close()


class Handler(asyncore.dispatcher_with_send):
    clients = 0
    def __init__(self, disp, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.disp = disp
    
    def handle_read(self):
        packet_id = ord(self.recv(1))
        if packet_id == 0x02:
            packet = self.recv(4096)
            username = comprehend_handshake(packet)
            with get_data as data:
                ins = data['users'][username]['world']
                port = data['ports'][ins]
            if Handler.clients > get_options().n:
                self.send(compose_server_full())
                self.close()
                return
            Handler.clients += 1
            instance = Instance.get(ins, self.disp)
            if not instance.ready.is_set():
                self.send(compose_server_not_ready())
                self.close()
            else:
                self.disp.log.i('%s joined on instance %d' % (username, ins))
                self.disp.add_list(str(ins), username)
                instance.player_join(username, self)
                self.forwarder = Forwarder(port, self)
                self.forwarder.send(''.join(('\x02', packet)))
                self.handle_read = self.handle_read_forwarder
        elif packet_id == 0xFE:
            self.send(compose_list_ping())
            self.close()
        else:
            self.close()
    
    def handle_read_forwarder(self):
        self.forwarder.send(self.recv(4096))
    
    def handle_close(self):
        self.close()
    
    def close(self):
        asyncore.dispatcher_with_send.close(self)
        Handler.clients -= 1
        if self.handle_read is self.handle_read_forwarder:
            self.forwarder.close()


class Server(asyncore.dispatcher):
    def __init__(self, disp, shutdown, host, port):
        asyncore.dispatcher.__init__(self)
        self.disp = disp
        self.shutdown = shutdown
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
    
    def handle_accept(self):
        pair = self.accept()
        if pair:
            Handler(self.disp, *pair)
    
    def readable(self):
        if self.shutdown.is_set():
            raise asyncore.ExitNow
        while False: # disable (it's broken)
            try:
                msg = compose_chat(Instance.chat_q.get_nowait())
            except Queue.Empty:
                break
            else:
                for fwd in Forwarder.fwds:
                    fwd.send(msg)
        return asyncore.dispatcher.readable(self)


def server_thread(shutdown, disp):
    options = get_options()
    with closing(Server(disp, shutdown, options.host, options.port)):
        try:
            asyncore.loop(timeout=5, use_poll=True) # use poll if available
        except asyncore.ExitNow:
            return


SHUTDOWN = threading.Event()
SERVER_THREAD = None
def start_server(disp):
    global SERVER_THREAD
    SERVER_THREAD = threading.Thread(target=server_thread,
                                     args=(SHUTDOWN,disp))
    SERVER_THREAD.start()

def stop_server():
    SHUTDOWN.set()
    SERVER_THREAD.join()
