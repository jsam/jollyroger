
import logging

from jdht.virtual_co import Scheduler
from jdht.networkio import SenderTask, ReceiverTask, RefresherTask
from jdht.networkio import request_buffer

from jdht import DHT


args1 = { "console_logging": True,
          "log_level": logging.DEBUG
}


#d1 = DHT("", 45000, args=args1)
d2 = DHT("", 55000, args=args1, boot_addr="95.178.228.142", boot_port=45000)
