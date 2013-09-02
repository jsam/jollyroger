#!/usr/bin/python

from distutils.core import setup

setup(name='jollyroger',
      version='0.0.1',
      description='Kademlia DHT implementation for distributed computing.',
      author='SamEpps',
      author_email='samepps.dev@gmail.com',
      packages=['jdht', 'jdht.stun', 'jdht.tasks'])  #'src.stun', 'src.tasks', 'src.tests', 'src.tftpy', 'src.upnp'])
