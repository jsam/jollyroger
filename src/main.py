#!/usr/bin/python

import logging

from managers import shell_manager, shell_client
from managers import broadcast_ping
from virtualization import Scheduler


class App(object):

    def __init__(self, args):
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
            logging.getLogger("").addHandler(console)

        logging.info("Scheduler initializing...")
        sched = Scheduler()
        
        if args["endpoint"]:
            logging.info("Starting as network endpoint.")
            #sched.new(shell_manager("", 0))
            #sched.new(broadcast_ping())

        if args["console_hook"]:
            logging.info("Hooking console to {0}:{1}".format(
                args["console_hook"][0],
                args["console_hook"][1]))

            #sched.new(shell_client(args["console_hook"], ["ls", "pwd"]))
            #sched.new(shell_client(args["console_hook"], ["@ping", "ls", "pwd", "@ping"]))
    
        sched.start()
        

if __name__ == "__main__":

    import sys
    if len(sys.argv) < 2:
        print "README"
    else:
        try:
            addr_index = sys.argv.index('-c')
            addr = sys.argv[addr_index + 1].split(":")
            addr[1] = int(addr[1])
            addr = tuple(addr)
        except ValueError:
            addr = None

        try:
            endpoint_index = sys.argv.index('-e')
            endpoint = True
        except ValueError:
            endpoint = False
            

    try:
        args = { "console_logging": True,
                 "log_level": logging.INFO,
                 "console_hook": addr,
                 "endpoint": endpoint }

        App(args)
    except KeyboardInterrupt:
        exit(0)
