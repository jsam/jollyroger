import logging

from networkio import SenderTask, ReceiverTask, RefresherTask
from virtual_co import Scheduler

from networkio import request_buffer, response_buffer
from cachedb import random_id, DB



class DHT(object):


    def __init__(self, addr, port, boot_addr=None, boot_port=None, args=None):
        
        logging.basicConfig(
            level=args["log_level"],
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%d-%m %H:%M", 
            filename=".log", 
            filemode="w")
        
        if args["console_logging"]:
            console = logging.StreamHandler()
            console.setLevel(args["log_level"])
            formatter = logging.Formatter(
                "%(asctime)s %(name)-12s: %(levelname)-8s %(message)s")
            console.setFormatter(formatter)
            logging.getLogger("networkio").addHandler(console)
            logging.getLogger("utility").addHandler(console)

        self.uuid = random_id()
        cache = DB()
        cache["uuid"] = self.uuid
        cache["values"] = dict()

        logging.info("Scheduler initializing, id: {0}".format(self.uuid))
        s = Scheduler()
        s.new(ReceiverTask(addr, port))
        s.new(SenderTask())
        s.new(RefresherTask())

                
        if boot_addr and boot_port:
            msg = self.send_query((boot_addr, boot_port), "ping", "")
            request_buffer.append(msg)
            request_buffer.append(msg)
            request_buffer.append(msg)
            request_buffer.append(msg)
        s.start()
        

    def send_query(self, send_to, query_type, query_data):
        return {"query_data": query_data,
                "query_type": query_type, # ping, store, find_node, find_value
                "send_to": send_to, 
                "uuid": self.uuid }

    def __getitem__(self, key):
        pass


    def __setitem__(self, key, value):
        pass