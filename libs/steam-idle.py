#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import platform
from ctypes import CDLL

try:  # Python 2
    from urllib2 import urlopen
except ImportError: # Python 3
    from urllib.request import urlopen


def get_steam_api():
    if sys.platform.startswith('win32'):
        print('Loading Windows library')
        steam_api = CDLL('steam_api.dll')
    elif sys.platform.startswith('linux'):
        if platform.architecture()[0].startswith('32bit'):
            print('Loading Linux 32bit library')
            steam_api = CDLL('./libs/libsteam_api32.so')
        elif platform.architecture()[0].startswith('64bit'):
            print('Loading Linux 64bit library')
            steam_api = CDLL('./libs/libsteam_api64.so')
        else:
            print('Linux architecture not supported')
    elif sys.platform.startswith('darwin'):
        print('Loading OSX library')
        steam_api = CDLL('./libsteam_api.dylib')
    else:
        print('Operating system not supported')
        sys.exit()
        
    return steam_api

    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        sys.exit()
        
    str_app_id = sys.argv[1]
    
    os.environ["SteamAppId"] = str_app_id
    try:
        get_steam_api().SteamAPI_Init()
    except:
        print("Couldn't initialize Steam API")
        sys.exit()
