from multiprocessing import Process, Pipe
from time import sleep 
from jdht import ProcessingDHT

import logging

def dht_connect():
    dht = ProcessingDHT(
                addr="", 
                port=45000, 
                console_logging=True,
                log_level=logging.DEBUG,
             )
    dht.start()


if __name__ == "__main__":
    dht_connect()
    

