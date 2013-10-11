

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
        ids = [observer._id for observer in self._observers]
        if observer_id in ids:
            observer = self._observer[ids.index(observer_id)] 
            observer(event)
        else:
            # rpc is not request, it is reply


class WriteEvent(Observable):

    def __repr__(self):
        return "WriteEvent"


from cachedb import DB
from config import ADDRESS_SPACE
import random
class AsyncRPC(object):
    
    
    def __init__(self, _id):
        self._id = _id # rpc_no
        self.cache = DB()
        self.response = list()
        

    def new_packet(self, send_to, query_type, query_data):
        return {"query_data": query_data, 
                "query_type": query_type,
                "send_to": send_to,
                "uuid": self.cache["uuid"]}

    def send(self, packet):
        """Send packet request"""
        if 'send_to' in packet and 'query_data' in packet:
            sender = Sender(packet["send_to"],
                            (self.cache["addr"], self.cache["port"]),
                            self.cache["uuid"])
            packet["rpc_no"] = random.getrandbits(ADDRESS_SPACE)
            yield sender.send_query(packet["query_data"],
                                    packet["query_type"],
                                    packet["rpc_no"])
                    
                    

        
    def __call__(self, packet):
        """Receive packet response """
        self.response.append(packet)
        print(packet)