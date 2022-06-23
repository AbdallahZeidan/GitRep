#######!/usr/bin/env python3
import time
import os
import json

def EnvTracker():
    os.system("python3 /home/cpesit/WFD-NG/automation/02052022/wifi-doctor-certification/ENVELOPE_TRACKER/cs_test_stub.py > /home/cpesit/WFD-NG/automation/02052022/tmpEnvelopes.json")
    time.sleep(2)
    Device_ID=""
    x=open('tmpEnvelopes.json','r')
    for lines in x:
        if 'Device ID' in lines:
            Device_ID = lines.split(":")[-1]
            #print(Device_ID)
            break
    ParseEnvelopePlatform(x,Device_ID)
    

def EnvReaderLocal():
    x=open('tmpEnvelopes.json','r')
    for lines in x:
        if 'Device ID' in lines:
            Device_ID = lines.split(":")[-1]
            #print(Device_ID)
            break
    ParseEnvelopePlatform(x,Device_ID)


def json_validator(data):
    try:
        json.loads(data)
        return True
    except ValueError as error:
        return False


def ParseEnvelopePlatform(x,device_id):
    LIST_1 = []
    LIST_2 = []
    List_3 = []
    List_4 = []
    List_5 = []
    RadioIdList = []
    MIMO_BAND = []
    print("Device ID: " + device_id)
    for envelope_line in x:
        if json_validator(envelope_line):
            loaded_envelope_line = json.loads(envelope_line)
            if (loaded_envelope_line["type"] == "Platform"):
                env_groupId = loaded_envelope_line["data"]["groupId"]
                env_WiFiDoctorAgentVersion = loaded_envelope_line["data"]["WiFiDoctorAgentVersion"]
                env_WLANControllerVersion = loaded_envelope_line["data"]["WLANControllerVersion"]
                LIST_1.append(env_groupId)
                LIST_2.append(env_WiFiDoctorAgentVersion)
                List_3.append(env_WLANControllerVersion)
                
            if (loaded_envelope_line["type"] == "Interface"):
                interface = loaded_envelope_line["data"]["ssid"]
                if (interface == "WFD-2G-S2" or interface == "WFD-5G-S2"):
                    RadioID = loaded_envelope_line["data"]["interfaceId"]["radioId"]["id"]
                    List_4.append(interface)
                    RadioIdList.append(RadioID)

            if (loaded_envelope_line["type"] == "Radio"):
                MIMO_TX = loaded_envelope_line["data"]["capabilities"]["spatialStreamsTX"]
                BAND = loaded_envelope_line["data"]["capabilities"]["bands"]
                BAND_NSS = MIMO_TX , BAND
                List_5.append(MIMO_TX)
                MIMO_BAND.append(BAND_NSS)


    print("DEVICE INFO\n###########","\nGroup_ID --> ",LIST_1[-1] ,"\nWiFiDoctorAgentVersion --> ",LIST_2[-1], "\nWLANControllerVersion --> ", List_3[-1])
    print("\nSSID_1 --> ",List_4[-2], "|| RadioID:",RadioIdList[-2], "\nSSID_2 --> ", List_4[-1] , "|| RadioID:",RadioIdList[-1])
    #print("\nMIMO_NSS:",List_5)
    print("\nMIMO BAND NSS --> ",  MIMO_BAND[-1],MIMO_BAND[-2],MIMO_BAND[-3])
        
    

if __name__ == "__main__":
    #EnvTracker()
    EnvReaderLocal()
