import logging as log
logging = log.getLogger("init")

from time import sleep

from networkio import ReceiverTask
from networkio import AsyncRPC
from networkio import Bootstrap

from networkio import SenderTask
from networkio import  RefresherTask
from networkio import IterativeFindNode
from networkio import IterativeStore
from networkio import IterativeFindValue
from networkio import request_buffer, response_buffer

from virtual_co import coroutine
from virtual_co import Scheduler
from virtual_co import NewTask
from virtual_co import Monitor
from virtual_co import ResultObject

from cachedb import random_id
from cachedb import DB

from multiprocessing import Process


        
class DHT(object):
    """ 
        DHT API: Arguments which should always be provided are:
            - addr = "" (equal to 0.0.0.0)
            - port = 0 (in this case OS will chose random port)
        Optional arguments:
            - boot_addr = ""
            - boot_port = 0
            - log_level = logging.INFO
            - console_logging = True/False
    """

    def __init__(self, **kwargs):
        
        
        if "log_level" in kwargs and kwargs["log_level"]:
            log.basicConfig(
                level=kwargs["log_level"],
                format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                datefmt="%d-%m %H:%M", 
                filename=".log", 
                filemode="w")
        
        if "console_logging" in kwargs and kwargs["console_logging"]:
            console = log.StreamHandler()
            console.setLevel(kwargs["log_level"])
            formatter = log.Formatter(
                        "%(asctime)s %(name)-12s: %(levelname)-8s %(message)s")
            console.setFormatter(formatter)
            log.getLogger("init").addHandler(console)
            log.getLogger("networkio").addHandler(console)
            log.getLogger("cachedb").addHandler(console)
            log.getLogger("utility").addHandler(console)

        self.packet = None
        self.bootstrap = None
        self.uuid = random_id()
        
        cache = DB()
        cache["uuid"] = self.uuid
        cache["values"] = dict()
        
        if "boot_addr" and "boot_port" in kwargs:
            self.bootstrap = (kwargs["boot_addr"], kwargs["boot_port"])

        logging.info("TaskScheduler initializing, id: {0}".format(self.uuid))
        self.s = Scheduler()
        self.s.new(ReceiverTask(kwargs["addr"], kwargs["port"], self.bootstrap))
        #self.s.new(RefresherTask()) # TODO
        #self.connect()
        
        self.query_result = list()


    def send_query(self, send_to, query_type, query_data):
        return {"query_data": query_data,
                "query_type": query_type, # ping, store, find_node, find_value
                "send_to": send_to, 
                "uuid": self.uuid }


    def connect(self):
        self.s.start()


    def __getitem__(self, key):   #register to observable
        # TODO: define callback
        # TODO: call IterativeFindValue
        pass 


    def __setitem__(self, key, value):
        #result = yield IterativeStore(key, value)
        # TODO: define callback
        logging.debug("DHT setting item. {}:{}".format(key, value))
        # TODO: call IterativeStore
        yield IterativeStore(key, value, self.get_result())
        #self.s.new(IterativeStore(key, value, self.get_result()))

    def __call__(self, packet):
        self.packet = packet
    
    

    def get_result(self, resp):
        logging.debug("DHT OBJECT DATA: {}".format(resp))
        self.query_result.append(resp)


class ProcessingDHT(Process):
    """
        ProccessingDHT is a class for handling DHT API over process. It will
        spawn DHT inside new process and handle communication with it. Arguments
        are the same as the DHT API, with one exception and that is communication
        method. Communication with the process can be done via Queue or Pipe.
    """
    
    def __init__(self, **kwargs):
        Process.__init__(self)
        
        self.dht = DHT(**kwargs)
        #self.pipe = kwargs["pipe"]
        self.monitor = Monitor()
        
        self.request = self.bridge()
        

        self.query_result = ResultObject()
        

    def run(self):
        #self.dht.s.new(self.request)
        self.dht.s.start()

    @coroutine
    def bridge(self):
        while True:
            sleep(.1)
            command = (yield)
            logging.debug("Command received: {}".format(command))
            if isinstance(command, str):
                pass
                # TODO: handle get
            elif isinstance(command, dict):
                logging.debug("Command is type dict, executing __setitem__")
                IterativeStore(
                        command["key"], 
                        command["value"], 
                        self._query_callback)


    def _send(self, arg):
        self.request.send(arg)


    def _query_callback(self, resp):
        logging.debug("DHT OBJECT DATA: {}".format(resp)) 
        self.query_result.result = resp

    
    def __setitem__(self, key, value):
        logging.debug("__setitem__({},{})".format(key, value))
        
        self._send({"key": key, "value": value})
        
        return self.query_result


    def __getitem__(self, key):
        pass
    
    def method_call(self):
        logging.debug("DHT CALLED!")
        print("BUUUU!!!")