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
    ### Storing here all data parsed from all the received envelopes ###
    GroupID_List = []
    WiFiDoctorAgentVersion_List = []
    env_WLANControllerVersion_List = []
    MIMO_BAND = []
    SSID_RadioID_List = []
    SSID_InterfaceID_List = []
    # -------------------------------------------------------------#
    print("Device ID: " + device_id)

    ### Loop inside envelopes json file and parse info to store them in lists ###
    for envelope_line in x:
        if json_validator(envelope_line):
            loaded_envelope_line = json.loads(envelope_line)
            if (loaded_envelope_line["type"] == "Platform"):
                env_groupId = loaded_envelope_line["data"]["groupId"]
                env_WiFiDoctorAgentVersion = loaded_envelope_line["data"]["WiFiDoctorAgentVersion"]
                env_WLANControllerVersion = loaded_envelope_line["data"]["WLANControllerVersion"]
                GroupID_List.append(env_groupId)
                WiFiDoctorAgentVersion_List.append(env_WiFiDoctorAgentVersion)
                env_WLANControllerVersion_List.append(env_WLANControllerVersion)
                
            if (loaded_envelope_line["type"] == "Interface"):
                interface_ssid = loaded_envelope_line["data"]["ssid"]
                if (interface_ssid == "WFD-2G-S2" or interface_ssid == "WFD-5G-S2" or interface_ssid == "WFD-6G-S2"):
                    RadioID = loaded_envelope_line["data"]["interfaceId"]["radioId"]["id"]
                    InterfaceID = loaded_envelope_line["data"]["interfaceId"]["id"]

                    SSID_RadioID = interface_ssid, RadioID
                    SSID_InterfaceID = interface_ssid, InterfaceID
                    SSID_RadioID_List.append(SSID_RadioID)
                    SSID_InterfaceID_List.append(SSID_InterfaceID)
                    

            if (loaded_envelope_line["type"] == "Radio"):
                MIMO_TX = loaded_envelope_line["data"]["capabilities"]["spatialStreamsTX"]
                BAND = loaded_envelope_line["data"]["capabilities"]["bands"]
                BAND_NSS = MIMO_TX , BAND
                MIMO_BAND.append(BAND_NSS)
    # ------------------------------------------------------------------------------------------------#

    print("DEVICE INFO\n###########","\nGroup_ID --> ",GroupID_List[-1] ,"\nWiFiDoctorAgentVersion --> ",WiFiDoctorAgentVersion_List[-1], "\nWLANControllerVersion --> ", env_WLANControllerVersion_List[-1])
    print ("\nSSID, RadioID -- >", SSID_RadioID_List[-1],SSID_RadioID_List[-2],SSID_RadioID_List[-3])
    print("\nSSID, InterfaceID -- >", SSID_InterfaceID_List[-1],SSID_InterfaceID_List[-2],SSID_InterfaceID_List[-3])
    print("\nMIMO NSS, BAND --> ",  MIMO_BAND[-1],MIMO_BAND[-2],MIMO_BAND[-3])
    
    #print(len(SSID_RadioID_List))
        
    

if __name__ == "__main__":
    #EnvTracker()
    EnvReaderLocal()
