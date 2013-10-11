###################################################
# Coroutine multitasking virtualization module.
###################################################

import select
import types
from Queue import Queue


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr
    return start


@coroutine
def grep(pattern):
    print "Looking for %s" % pattern
    try:
        while True:
            line = (yield)
            if pattern in line:
                print line
    except GeneratorExit:
        raise Error("GeneratorExit")
      
      

class Error(BaseException):

    def __init__(self, error_msg):
        super(Error, self).__init__()
        logging.error(error_msg)


class TimeoutError(BaseException):
    
    def __init__(self, error_msg):
        super(TimeoutError, self).__init__()
        logging.error(error_msg)


class SystemCall(object):

    def __init__(self):
        pass

    def handle(self):
        pass


class Task(object):
    taskid = 0

    def __init__(self, target):
        Task.taskid += 1
        self.tid = Task.taskid
        self.target = target
        self.sendval = None
        self.stack = []


    def run(self):
        while True:  #return self.target.send(self.sendval)
            try:
                result = self.target.send(self.sendval)
                if isinstance(result, SystemCall): return result
                if isinstance(result, types.GeneratorType):
                    self.stack.append(self.target)
                    self.sendval = None
                    self.target = result
                else:
                    if not self.stack: return
                    self.sendval = result
                    self.target = self.stack.pop()
            except StopIteration:
                if not self.stack: raise
                self.sendval = None
                self.target = self.stack.pop()


    def getId(self):
        return self.tid


class GetTid(SystemCall):

    def __init__(self):
        super(GetTid, self).__init__()

    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)


class NewTask(SystemCall):

    def __init__(self, target):
        self.exec_target = target

    def handle(self):
        tid = self.sched.new(self.exec_target)
        self.task.sendval = tid
        self.sched.schedule(self.task)


class KillTask(SystemCall):

    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        task = self.sched.taskmap.get(self.tid, None)
        if task:
            task.target.close()
            self.task.sendval = True
        else:
            self.task.sendval = False
        self.sched.schedule(self.task)


class ReadWait(SystemCall):

    def __init__(self, f):
        self.f = f

    def handle(self):
        fd = self.f.fileno()
        self.sched.waitforread(self.task, fd)


class WriteWait(SystemCall):

    def __init__(self, f):
        self.f = f

    def handle(self):
        fd = self.f.fileno()
        self.sched.waitforwrite(self.task, fd)


class WaitTask(SystemCall):

    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        result = self.sched.waitforexit(self.task, self.tid)
        self.task.sendval = result
        # if waiting on non-existing task return
        if not result:
            self.sched.schedule(self.task)


class Scheduler(object):

    def __init__(self):
        self.ready = Queue()
        self.taskmap = {}
        self.exit_waiting = {}

        self.read_waiting = {}
        self.write_waiting = {}

    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def schedule(self, task):
        self.ready.put(task)

    def exit(self, task):
        print "Task %d terminated" % task.tid
        del self.taskmap[task.tid]
        for task in self.exit_waiting.pop(task.tid, []):
            self.schedule(task)

    def waitforexit(self, task, waittid):
        if waittid in self.taskmap:
            self.exit_waiting.setdefault(waittid, []).append(task)
            return True
        else:
            return False

    def waitforread(self, task, fd):
        self.read_waiting[fd] = task

    def waitforwrite(self, task, fd):
        self.write_waiting[fd] = task

    def iopoll(self, timeout):
        if self.read_waiting or self.write_waiting:
            r, w, e = select.select(self.read_waiting,
                                    self.write_waiting, [], timeout)
            for fd in r:
                self.schedule(self.read_waiting.pop(fd))
            for fd in w:
                self.schedule(self.write_waiting.pop(fd))

    def iotask(self):
        while True:
            if self.ready.empty():
                self.iopoll(None)
            else:
                self.iopoll(0) # 0
            yield

    def start(self):
        self.new(self.iotask())  # start io task
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task = task
                    result.sched = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)


#def Recv(sock, recv_size):
#    yield ReadWait(sock)
#    yield sock.recvfrom(recv_size)


#def Send(sock, packet, addr):
#    yield WriteWait(sock)
#    sock.sendto(packet, addr)


import logging
import socket
import random
import cPickle as pickle
from blowfish import Blowfish
from config import KEY
from config import PACKET_SIZE


class UDPSocket(object):
    """Abstraction over socket object. Implements (de)encryption and (de)serialization."""

    def __init__(self, socket):
        self.socket = socket
        self.cipher = Blowfish(KEY)


    def recv(self):
        self.cipher.initCTR()
        yield ReadWait(self.socket) # put socket to waitforread buffer
        packet, addr = self.socket.recvfrom(PACKET_SIZE)
        yield (pickle.loads(self.cipher.decryptCTR(packet)) , addr)
            

    def send(self, packet, addr):
        self.cipher.initCTR()
        #yield WriteWait(self.socket) # put socket to waitforwrite buffer(TCP)
        if len(addr) > 2:
            addr = (addr[0], addr[1])
        self.socket.sendto(self.cipher.encryptCTR(pickle.dumps(packet)), addr)
        

    def close(self):
        self.socket.close()


from weakref import WeakKeyDictionary
from cPickle import dumps
class Monitor():
    
    def __init__(self):
        self.objects = WeakKeyDictionary()
        
    def is_changed(self, obj):
        current_pickle = dumps(obj, -1)
        changed = False
        if obj in self.objects:
            changed = current_pickle != self.objects[obj]
        self.objects[obj] = current_pickle
        return changed


class ResultObject():
    
    def __init__(self, result=None):
        self.result = result