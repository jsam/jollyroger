import logging
from networkio import Sender, Receiver
from cachedb import DB, get_hash
from utility import tftp_server

from multiprocessing import Process
from uuid import getnode as get_mac

arka = ("161.53.120.19", 0)
db = DB()


def shell_manager(ip, port):
    db.load()

    ## start listener
    receiver = Receiver((ip, port))
    port = receiver.get_addr()[1]
        
    ## Do UPnP mapping
    try:
        from utility import UPNP
        u = UPNP()
        lan_addr = u.lan_addr()
        
        u.add_port_mapping(port, "UDP", lan_addr, port, "jolly desc", "")
        logging.info("Added port mapping to {0}:{1}".format(lan_addr, port))
        u.add_port_mapping(port + 1, "UDP", lan_addr, port + 1, "jolly+1", "")
        logging.info("Added port mapping to {0}:{1}".format(lan_addr, port+1))
        
        db.add("port_mappings", [(port, "UDP"), (port + 1, "UDP")])

        try:
            external_addr = u.external_addr()
        except Exception, e:
            logging.warning(
                "Cannot fetch external address via uPnP: {0}".format(e))
    except Exception, e:
        logging.error("Cannot import UPNP class or port map is busy -> audit.")

    ## Do STUN probing - !
    logging.info("Sending STUN probe...")
    try:
        import stun
        nat_type, external_ip, external_port = stun.get_ip_info() 
        logging.info(
            """STUN probe results:\n
            [+] NAT: {0}
            [+] External IP: {1}:{2}
            """.format(nat_type, external_ip, external_port))

        db.add("nat_type", nat_type)
        db.add("external_ip", external_ip)
        db.add("external_port", port) ## audit for stun/turn port map
        
    except Exception, e:
        logging.error("STUN probing failed: {0}".format(e))

    ## start tftp receiver
    p = Process(target=tftp_server, args=(port + 1, "./tasks"))
    p.start()
    

    logging.info("Shell manager started on {0}:{1}".format(
        external_ip, port))
    
    db.add("shell_manager", (external_ip, port))
    db.add("uuid", get_hash(str(get_mac())))
    
    yield db.save()
    logging.info("DB saved to hdd: {0}".format(db.get_all()))
    
    ## event rpc listener loop
    while True:
        resp, addr, rpc_no, uuid = yield receiver.recv()
        sender = Sender(addr, receiver.get_addr(), uuid)
        yield sender.send_resp(resp, rpc_no)
    


def shell_client(sendto=db.get("shell_manager"), command_list=None):
    receiver = Receiver()
    cdb = yield db.load()

    logging.debug("UUID: {0}".format(db.get("uuid")))
    sender = Sender(sendto, receiver.get_addr(), db.get("uuid"))
   
    if command_list == None:
        input_ = lambda (host, port): (
            yield raw_input("{0}:{1} ~/ $: ".format(host, port))
        )
    elif type(command_list) == list:
        input_ = lambda (host, port): (
                yield command_list.pop() if len(command_list) > 0 else "quit" 
        )
    
    while True:
        command = input_(sendto).next()
        if not command:
            continue

        if command.startswith("@ping"):
            query = ("", "ping")
            resp, addr, rpc_no, uuid = yield rpc_call(query, sender, receiver)
            #print resp["data"]
            yield resp
            continue
 
        if command.startswith("upload"):
            try:
                filename = command.split()[1]
                yield sender.send_file(filename)
            except Exception, e:
                logging.error("No file specified, error: {0}".format(e))
            continue
                   
        if command.startswith("quit"):
            break
        
        ## RPC call!
        # yield sender.send_query(command, "shellcmd")
        # resp, addr = yield receiver.recv()
        
        query = (command, "shellcmd")
        resp, addr, rpc_no, uuid = yield rpc_call(query, sender, receiver) 

        #print resp["data"]
        yield resp["data"]

        
import random
from time import time

def rpc_call((q_data, q_type), sender, receiver):
    rpc_no_gen = int(random.random() * 100000)
    packet_sent = 0
    
    yield sender.send_query(q_data, q_type, rpc_no_gen)
    logging.debug("Packet sent: {0}".format(packet_sent))

    resp, addr, rpc_no_recv, uuid = yield receiver.recv()
        
    ## problem with lost packets :(

    if rpc_no_gen != rpc_no_recv:
        resp["data"] = "Network error"

    if uuid != db.get("uuid"):
        resp["data"] = "Network error"

    yield resp, addr, rpc_no_recv, uuid



def broadcast_ping():
    while True:
        s = yield shell_client(db.get("shell_manager"), ["@ping"])
        logging.info("broadcast_ping: {0}".format(s["data"]))
        yield

