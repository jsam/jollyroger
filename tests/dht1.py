import logging
from jdht import DHT


args1 = { "console_logging": True,
          "log_level": logging.DEBUG
	}


d1 = DHT("", 45000, args=args1)
#d2 = DHT("", 0, args=args1, boot_addr="192.168.1.3", boot_port=45000)
