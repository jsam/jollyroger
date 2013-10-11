
import logging

from jdht.virtual_co import Scheduler
from jdht.networkio import SenderTask, ReceiverTask, RefresherTask
from jdht.networkio import request_buffer

from jdht import DHT


args1 = { 
	"console_logging": True,
        "log_level": logging.DEBUG
}

dht = DHT("", 56000, args=args1, 
	boot_addr="192.168.1.1", 
	boot_port=45000)

# EXAMPLE: retrieving from dht
logging.info("Value retrieved from DHT: {}".format(dht["key1"]))
#logging.info("Value retrieved from DHT: {}".format(dht["key2"]))

dht.connect()
