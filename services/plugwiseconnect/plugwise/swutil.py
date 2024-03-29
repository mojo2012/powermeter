# Copyright (C) 2012,2013,2014,2015,2016,2017,2018,2019,2020 Seven Watt <info@sevenwatt.com>
# <http://www.sevenwatt.com>
#
# This file is part of Plugwise-2-py.
#
# Plugwise-2-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Plugwise-2-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Plugwise-2-py.  If not, see <http://www.gnu.org/licenses/>.
#
# The program is a major modification and extension to:
#   python-plugwise - written in 2011 by Sven Petai <hadara@bsd.ee>
# which itself is inspired by Plugwise-on-Linux (POL):
#   POL v0.2 - written in 2009 by Maarten Damen <http://www.maartendamen.com>

import logging
import logging.handlers
from typing import Union

import serial
from serial.serialutil import SerialException

LOG_COMMUNICATION = False

def logf(msg):
    if type(msg) == type("  "):
        return msg
    if type(msg) == type(b'  '):
        return repr(msg.decode('utf-8', 'backslashreplace'))[1:-1]
    return repr(msg)[1:-1]

def hexstr(s):
    return ' '.join(hex(ord(x)) for x in s)

def uint_to_int(val, octals):
    """compute the 2's compliment of int value val for negative values"""
    bits=octals<<2
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val

def int_to_uint(val, octals):
    """compute the 2's compliment of int value val for negative values"""
    bits=octals<<2
    if val<0:
        val = val + (1<<bits)
    return val

def log_comm(enable):
    global LOG_COMMUNICATION
    LOG_COMMUNICATION = enable

def open_logcomm(filename):
    global pw_comm_logger
    pw_comm_logger = logging.getLogger("pwcomm")
    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    pw_comm_logger.addHandler(handler)
    pw_comm_logger.setLevel(logging.INFO)
    pw_comm_logger.info("logging started")
    #global logcommfile
    #logcommfile = open(filename, 'w')

def close_logcomm():
    #logcommfile.close()
    return

def logcomm(msg):
    if LOG_COMMUNICATION:
        #logcommfile.write("%s %s \n" % (datetime.datetime.now().isoformat(), msg,))
        pw_comm_logger.info(msg)

class SerialComChannel(object):
    """simple wrapper around serial module"""

    _fd: Union[serial.Serial, None] = None

    def __init__(self, port="/dev/ttyUSB0", baud=115200, bits=8, stop=1, parity='N', timeout=5):
        self.connected = False
        self.port = port
        self.baud = baud
        self.bits = bits
        self.stop = stop
        self.parity = parity
        self.timeout = timeout
        self.open()
        # try:
        # self._fd = serial.Serial(port, baudrate=baud, bytesize=bits, stopbits=stop, parity=parity, timeout=timeout)
        # self.connected = True
        # except SerialException as e:
        # self.connected = False

    def open(self):
        try:
            self._fd = serial.Serial(port=self.port, baudrate=self.baud, bytesize=self.bits, parity=self.parity, stopbits=self.stop, timeout=self.timeout)
            self.connected = True
        except SerialException as e:
            self.connected = False

    def reopen(self):
        if self._fd == None:
            self.open()
        else:
            if(self._fd and self._fd.isOpen() == False):
                self._fd.open()

    def close(self):
        if self._fd != None:
            self._fd.close()
        self.connected = False

    def read(self, bytecount):
        if not self.connected:
            try:
                self.reopen()
            except Exception as e:
                logging.info("read reopen exception %s" % str(e))
        return self._fd.read(bytecount)

    def readline(self):
        if not self.connected:
            try:
                self.reopen()
            except Exception as e:
                logging.info("readline reopen exception %s" % str(e))
        return self._fd.readline()

    def write(self, data):
        if not self.connected:
            try:
                self.reopen()
            except Exception as e:
                logging.info("write reopen exception %s" % str(e))
        self._fd.write(data)
