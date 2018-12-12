# -*- coding: utf8 -*-
import json
import socket
import urllib
from collections import OrderedDict
from time import sleep


with open('../data/station_name') as fp:
    line = fp.readline()
    fields = line.split("|")
    station_info = []
    tmp =[]
    last = ''
    for i, station in enumerate(fields):
        if '@' in station and '@' not in last:
            if len(tmp) > 0:
                station_info.append(tmp)
                print "\t".join(tmp)
            tmp = []
            tmp.append(station)
        else:
            tmp.append(station)
        last = station

    station_info.append(tmp)
    print "\t".join(tmp)