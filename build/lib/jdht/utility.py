import os
import logging as log
logging = log.getLogger("utility")


def strip_escape(s):
    return_value = ""
    i = 1
    while (i < 0x20):
        return_value += chr(i)
        i += 1
    t = s.translate(None, return_value)
    return t


def get_ext_ip():
    import urllib2, re
    url = "http://checkip.dyndns.org/"
    response = urllib2.urlopen(url)
    ip = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}", response.read())
    return ip[0]

    
class UPNP(object):
        

    def __init__(self, upnp_module):
        self.u = upnp_module.UPnP()
        self.u.discoverdelay = 500
        self.discovered = self.u.discover()
        try:
            self.u.selectigd()
        except Exception, e:
            logging.error("No internet gateway device detected.")
        

    def lan_addr(self):
        return self.u.lanaddr
        
        
    def external_addr(self):
        return self.u.externalipaddress()


    def status_info(self):
        return self.u.statusinfo()


    def connection_type(self):
        return self.u.connectiontype()
        

    def add_port_mapping(self, port, proto, lanaddr, lanport, desc, c):
        return self.u.addportmapping(port, proto, lanaddr, lanport, desc,c)


    def delete_port_mapping(self, port, proto):
        return self.u.deleteportmapping(port, proto)


    def get_port_mappings(self):
        port = 0
        proto = 'UDP'
        i = 0
        sol = []
        while True:
            p = self.u.getgenericportmapping(i)
            if p==None:
                break
            sol.append(p)
            (port, proto, (ihost,iport), desc, c, d, e) = p
            i = i + 1


def do_UPNP_mapping(ports=[]):
    if len(ports) == 0:
        return False

    try:
        import miniupnpc
        u = UPNP(miniupnpc)
        lan_addr = u.lan_addr()
        
        for item in ports:
            logging.debug(" [+] port_mapping({0}, {1}, {2}, {3}, {4}, {5})".format(
                item[0], item[1], lan_addr, item[0], "", ""))
            u.add_port_mapping(item[0], item[1], lan_addr, item[0], "port_map", "")
            logging.info("Added port mapping to {0}:{1}".format(lan_addr, item[0]))

        try:
            external_addr = u.external_addr()
        except Exception, e:
            logging.warning("Cannot fetch external addr via uPnP.")
            external_addr = False
    except ImportError, e:
        logging.critical("MiniuPnPc cannot be imported: {0}".format(e))
        return False

        
    return external_addr


def tftp_server(port, directory):
    try:
        import tftpy
    except ImportError, e:
        logging.error("tftpy cannot be imported: {0}".format(e))
        return 0 

    if not os.path.exists(directory):
        os.makedirs(directory)
    server = tftpy.TftpServer(directory)
    server.listen('0.0.0.0', port)
    

