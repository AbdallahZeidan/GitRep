#!/usr/bin/env python3

##############################################################################
##                                                                          ##
## Copyright (c) 2015-2021 - AirTies Wireless Networks                      ##
##                                                                          ##
## The source code form of this Open Source Project components              ##
## is subject to the terms of the Clear BSD license.                        ##
##                                                                          ##
## You can redistribute it and/or modify it under the terms of the          ##
## Clear BSD License (http://directory.fsf.org/wiki/License:ClearBSD)       ##
## See COPYING file/LICENSE file for more details.                          ##
##                                                                          ##
## This software project does also include third party Open Source Software:##
## See COPYING file/LICENSE file for more details.                          ##
##                                                                          ##
##############################################################################

from server import AvroStreamServer
import json
import sys
import time

from io import BytesIO
from _pyio import BufferedIOBase

import avro.io
import avro.schema

SERVER_PORT = 8080

def collAuthFailCB(cls):
    print("coll auth fail callback")

def format_bytes_with_semicolons(obj):
    if isinstance(obj, dict):
        return {key:format_bytes_with_semicolons(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [format_bytes_with_semicolons(x) for x in obj]
    if isinstance(obj, bytes):
        return ':'.join('{:02x}'.format(b) for b in obj)
    return obj

def newEvent(event):
    if event:
        print(json.dumps(format_bytes_with_semicolons(event),ensure_ascii=False))

def handleCSPostCB(http_request_handler):
    return False;

def run():
    terminate = False
    commands = {
                'q' : sys.exit,
                }

    while False == terminate:
        comm = input("")
        try:
            commands[comm[0]](comm)
        except Exception:
            print("")
        except SystemExit:
            break

if __name__ == "__main__":
    server = AvroStreamServer(newEvent, collAuthFailCB, handleCSPostCB, {'port': SERVER_PORT})
    server.start()
    #print "Server Started"
    run()
    server.stop()
    server.waitForFinish()
    #print "Server Stopped"
