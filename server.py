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
from io import SEEK_SET, SEEK_CUR, SEEK_END
import threading

from io import BytesIO

from http.server import BaseHTTPRequestHandler
import socketserver

import avro
import avro.io

import snappy
import wifidr_schemas

# Test server port
SERVER_PORT = 8123

class BinaryReader(object):
    def __init__(self, buf):
        self.buffer = buf
        self.offset = 0

    def seek(self, offset, whence=SEEK_SET):
        #logging.info("==== Seek %d bytes (%d) ====", offset, whence)
        if SEEK_SET == whence:
            self.offset = offset
        elif SEEK_CUR == whence:
            self.offset += offset
        elif SEEK_END == whence:
            self.offset = len(self.buffer) + offset
        if self.offset < 0 or self.offset >= len(self.buffer):
            raise EOFError

    def tell(self):
        #logging.info("==== Tell %d bytes ====", self.offset)
        return self.offset

    def read(self, n=-1):
        if self.offset >= len(self.buffer):
            raise EOFError
        if -1 == n:
            data = self.buffer[self.offset:]
            self.offset = len(self.buffer)
        else:
            data = self.buffer[self.offset:self.offset+n]
            self.offset += n
        #logging.info("==== Read %d bytes (%d/%d) : %s",
        #             n, self.offset, len(self.buffer),
        #             ''.join('{:02x}'.format(x) for x in data))
        return data

class AvroStreamHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def classify_event(self, event):
        """Determine the type of event and add a '_type' key."""

        # There is no way to extract the actual type from the data read so we
        # check the contents to determine the type.
        if 'data' in event:
            t = 'unknown'
            data = event['data']
            if 'WiFiDoctorAgentVersion' in data:
                t = 'Platform'
            elif 'mediumAvailable' in data:
                t = 'RadioStats'
            elif 'rssiAvg' in data:
                t = 'StationStats'
            elif 'reasonType' in data:
                t = 'ConnectionAttemptFailed'
            elif 'interfaceId' in data:
                t = 'Interface'
            elif 'radioHeartbeatInterval' in data:
                t = 'Radio'
            elif 'serviceCapabilities' in data:
                t = 'Host'
            elif 'stationStatus' in data:
                t = 'Remove'
            elif 'list' in data:
                t = 'ScannedNetwork'
            elif 'auxiliaryDataMap' in data:
                t = 'AuxData'
            elif 'directInternetConnection' in data:
                t = 'Backbone'
            elif 'stationPowerRadioList' in data:
                t = 'StationPower'
            elif 'isTargetDevice' in data:
                t = 'ControllerCommand'
            elif 'stationId' in data:
                t = 'Station'
            elif 'notAllowedContext' in data:
                t = 'ControllerRoamStatus'
            elif 'commandName' in data:
                t = 'MQTTCommand'
            elif 'detectedChannel' in data:
                t = 'RadarDetection'
            elif 'cpuLoadAvg' in data:
                t = 'VitalStats'
            elif 'eventType' in data:
                t = 'DPPEvent'
            elif 'peerIdentifier' in data:
                t = 'Onboarding'
            elif 'id' in data:
                t = 'EthDevice'
            else:
                t = 'BucketEnd/BRMevent'
            event['type'] = t
        return event




    def read_chunked(self, socket):
        while True:
            line = socket.readline().strip()
            chunk_size = int(line, 16)
            #logging.info("==== Chunk size %d (%s) ====", chunk_size, line)
            if chunk_size == 0:
                break
            newdata = socket.read(chunk_size)
            if 'data' in locals():
                data += newdata
            else:
                data = newdata
            socket.readline()
        return data

    def validate_token(self):
        if 'expected_access_token' in self.server.config:
            if 'Authorization' not in self.headers:
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Bearer error="invalid_request"')
                self.end_headers()
                self.server.newAuthFailure()
                return False
            auth_header = self.headers['Authorization'].split()
            if (auth_header[0].lower() != 'bearer') or (auth_header[1] != self.server.config['expected_access_token']):
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Bearer error="invalid_token"')
                self.end_headers()
                self.server.newAuthFailure()
                return False
        return True

    def do_POST(self):
        print("******************** Check Http Header - Begin ********************")
        print("Device IP: %s" % self.client_address[0])
        print("Device ID: %s" % self.headers['X-Device-Id'])
        print("Timestamp: %s" % self.headers['X-Time-Stamp'])
        print("Content: %s" % self.headers['Content-Type'])
        fingerprint = self.headers['Content-Type'].split('=')[1]
        WIFIDR_EVENT_SCHEMA = wifidr_schemas.get_schema(fingerprint)
        print("******************** Check Http Header - End ********************")

        AVRO_SCHEMA = avro.schema.Parse(WIFIDR_EVENT_SCHEMA)
        self.avro_rd = avro.io.DatumReader(AVRO_SCHEMA)

        if not self.validate_token():
            return

        if self.server.handle_post_cs_cb(self):
            return

        if 'content-length' in self.headers:
            data = self.rfile.read(int(self.headers['content-length']))
        else:
            data = self.read_chunked(self.rfile)

        # when not encoded with snappy, remove the following block
        # crc32 enabled
        # snappy_data = data[:len(data)-4]
        # crc32 disabled
        snappy_data = data[:len(data)]
        data = snappy.uncompress(snappy_data)
        bytes_reader = BytesIO(data)
        decoder = avro.io.BinaryDecoder(bytes_reader)

        while True:
            try:
                data = self.avro_rd.read(decoder)
                self.server.newEvent(self.classify_event(data))
            except EOFError:
                self.server.newEvent(None)
                break
            except AssertionError as error:
                # TODO; investigate this better
                break

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/vnd.technicolor.wifi-doctor.collection+avro; version=0.1')
        self.end_headers()

class _Server(socketserver.TCPServer):

    def __init__(self, event_cb, auth_fail_cb, config, handle_post_cs_cb):
        self.event_cb = event_cb
        self.auth_fail_cb = auth_fail_cb
        self.config = config
        self.handle_post_cs_cb = handle_post_cs_cb
        socketserver.TCPServer.allow_reuse_address = True
        while True:
            try:
                socketserver.TCPServer.__init__(self, ("", self.config['port']), AvroStreamHandler)
                break
            except:
                # try next port
                self.config['port'] += 1
                if self.config['port'] >= config['port'] + 1000:
                    print("Tried 1000 server ports and none worked, aborting!")
                    raise

    def newEvent(self, data):
        self.event_cb(data)

    def newAuthFailure(self):
        if self.auth_fail_cb is not None:
            self.auth_fail_cb()

    def getURL(self):
        return "http://127.0.0.1:{}".format(self.config['port'])

class AvroStreamServer(threading.Thread):
    def __init__(self, event_cb, auth_fail_cb, handle_post_cs_cb, config={'port': SERVER_PORT}):
        threading.Thread.__init__(self)
        self.daemon = True # allow keyboard interrupt to end this thread
        self.server = _Server(event_cb, auth_fail_cb, config, handle_post_cs_cb)
        self.stopped = True

    def run(self):
        self.server.serve_forever()

    def start(self):
        threading.Thread.start(self)
        self.stopped = False

    def stop(self):
        if not self.stopped:
            self.server.shutdown()
            self.join()
            self.stopped = True

    def waitForFinish(self):
        threading.Thread.join(self, 999999999999)

    def getURL(self):
        return self.server.getURL()
