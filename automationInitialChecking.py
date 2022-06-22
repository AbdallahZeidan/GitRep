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

                #print("\n"+"Device ID:",device_id)
                #print("\n"+"### PLATFORM DATA ###"+"\n"+"=====================")
                #print("groupId: ", env_groupId)
                #print("WiFiDoctorAgentVersion: ", env_WiFiDoctorAgentVersion)
                #print("WLANControllerVersion: ", env_WLANControllerVersion)
                #print ("========================================================================================" , "\n")
                
            #if (loaded_envelope_line["type"] == "Interface"):
            #    interface = loaded_envelope_line["data"]["ssid"]
            #    if (interface == "WFD-2G-S2" or interface == "WFD-5G-S2"):
            #        print("\n"+"### INTERFACE DATA ###"+"\n"+"=====================")
            #        print("Interface_ssid: ", interface)
    print("DEVICE INFO\n###########","\nGroup_ID",LIST_1[-1] ,"\nWiFiDoctorAgentVersion",LIST_2[-1], "\nWLANControllerVersion", List_3[-1])
        
    

if __name__ == "__main__":
    #EnvTracker()
    EnvReaderLocal()
