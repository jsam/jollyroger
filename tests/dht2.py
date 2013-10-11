from multiprocessing import Process, Pipe
from time import sleep
from jdht import ProcessingDHT

import logging


def dht_connect():
    parent, child = Pipe()
    dht = ProcessingDHT(
                addr="", 
                port=55000,
                console_logging=True,
                log_level=logging.DEBUG,
                boot_addr="192.168.1.1", 
                boot_port=45000,
                pipe = child
             )
    dht.start()
    sleep(5)
    dht["123"] = "values123"
    

if __name__ == "__main__":
    dht_connect()