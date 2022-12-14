#!/usr/bin/env python

# Copyright (C) 2011 Sven Petai <hadara@bsd.ee> 
# Use of this source code is governed by the MIT license found in the LICENSE file.


import datetime
import optparse
import sys
import time
from pprint import pprint

import plugwise.util
from plugwise import *
from plugwise.nodes.circle_plus import *
from plugwise.stick import *
from serial.serialutil import SerialException

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

parser = optparse.OptionParser()
parser.add_option("-m", "--mac", dest="mac", help="MAC address")
parser.add_option("-d", "--device", dest="device", 
    help="Serial port device")
parser.add_option("-p", "--power", action="store_true", 
    help="Get current power usage")
parser.add_option("-t", "--time", dest="time",
    help="""Set circle's internal clock to given time. 
Format is 'YYYY-MM-DD hh:mm:ss' use the special value 'sync' if you want to set Circles clock to the same time as your computer""")
parser.add_option("-C", "--counter", action="store_true", 
    help="Print out values of the pulse counters")
parser.add_option("-c", "--continuous", type="int",
    help="Perform the requested action in an endless loop, sleeping for the given number of seconds in between.")
parser.add_option("-s", "--switch", dest="switch", 
    help="Switch power on/off. Possible values: 1,on,0,off")
parser.add_option("-l", "--log", dest="log", 
    help="""Read power usage history from the log buffers of the Circle. 
    Argument should be 'cur' or 'current' if you want to read the log buffer that is currently being written.
    It can also be a numeric log buffer index if you want to read an arbitrary log buffer. 
""")
parser.add_option("-i", "--info", action="store_true", dest="info", 
    help="Perform the info request")
parser.add_option("-q", "--query", dest="query",
    help="""Query data. Possible values are: time, pulses, last_logaddr, relay_state""")
parser.add_option("-v", "--verbose", dest="verbose",
    help="""Verbose mode. Argument should be a number represeting verboseness. 
    Currently all the debug is logged at the same level so it doesn't really matter which numbre you use.""")

options, args = parser.parse_args()

device = DEFAULT_SERIAL_PORT

if options.device:
    device = options.device

if not options.mac:
    print("you have to specify mac with -m")
    parser.print_help()
    sys.exit(-1)

if options.verbose:
    plugwise.util.DEBUG_PROTOCOL = True

def print_pulse_counters(c):
    try:
        print("%d %d %d" % c.get_pulse_counters())
    except ValueError:
        print("Error: Failed to read pulse counters")

def handle_query(c, query):
    if query == 'time':
        print(c.get_clock().strftime("%H:%M:%S"))
    elif query == 'pulses':
        print_pulse_counters(c)
    elif query in ('last_logaddr', 'relay_state'):
        print(c.get_info()[query])

def handle_log(c, log_opt):
    if log_opt in ('cur', 'current'):
        log_idx = None
    else:
        try:
            log_idx = int(log_opt)
        except ValueError:
            print("log option argument should be either number or string current")
            return False

    print("power usage log:")
    for dt, watt_hours in c.get_power_usage_history(log_idx):

        if dt is None:
            ts_str,watt_hours = "N/A", "N/A"
        else:
            ts_str = dt.strftime("%Y-%m-%d %H")
            watt_hours = "%f" % (watt_hours,)

        print("\t%s %s Wh" % (ts_str, watt_hours))

    return True


def set_time(c, time_opt):
    if time_opt == 'sync':
        set_ts = datetime.datetime.now()
    else:
        try:
            set_ts = datetime.datetime.strptime(time_opt, "%Y-%m-%d %H:%M:%S")
        except ValueError as reason:
            print("Error: Could not parse the time value: %s" % (str(reason),))
            sys.exit(-1)

    c.set_clock(set_ts)

try:
    device = stick(device)
    c = PlugwiseCirclePlus(options.mac, device)
    
    if options.time:
        set_time(c, options.time)

    if options.switch:
        sw_direction = options.switch.lower()

        if sw_direction in ('on', '1'):
            c.switch_on()
        elif sw_direction in ('off', '0'):
            c.switch_off()
        else:
            print("Error: Unknown switch direction: "+sw_direction)
            sys.exit(-1)
    
    while 1:
        if options.power:
            try:
                print("power usage: %.2fW" % (c.get_power_usage(),))
            except ValueError:
                print("Error: Failed to read power usage")

        if options.log != None:
            handle_log(c, options.log)

        if options.info:
            print("info:")
            pprint(c.get_info())

        if options.counter:
            print_pulse_counters(c)

        if options.query:
            handle_query(c, options.query)

        if options.continuous is None:
            break
        else:
            time.sleep(options.continuous)

except (SerialException) as reason:
    print("Error: %s" % (reason,))
