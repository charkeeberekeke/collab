import json
import os
from datetime import datetime
from collections import defaultdict
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor

def selectcmdevice(cucm, 
             username=None, 
             password=None, 
             SelectBy="Name",
             Class="Any",
             Status="Any",
             NodeName="Any"):
    tns = 'http://schemas.cisco.com/ast/soap/'
    imp = Import('http://schemas.xmlsoap.org/soap/encoding/', 'http://schemas.xmlsoap.org/soap/encoding/')
    imp.filter.add(tns)

    wsdl = "https://%s:8443/realtimeservice/services/RisPort?wsdl" % cucm
    location = "https://%s:8443/realtimeservice/services/RisPort" % cucm
    client = Client(wsdl, location=location, username=username, password=password, plugins=[ImportDoctor(imp)])
    result = client.service.SelectCmDevice('', {'SelectBy' : SelectBy, 'Status' : Status, 
                                                'Class' : Class, 'NodeName' : NodeName})

    return result['SelectCmDeviceResult']['TotalDevicesFound'], result['SelectCmDeviceResult']['CmNodes']


def parse_devices(cmnode, devices=None): # cmnode is instance of CmNodes
    try:
        cucm = cmnode["Name"]
        devices = isinstance(devices, defaultdict) and devices or defaultdict(list)        
        for dev in cmnode['CmDevices']:
            devices[dev["Name"]].append({  "ip" : dev["IpAddress"],
                                        "ext" : dev["DirNumber"],
                                        "status" : dev["Status"],
                                        "class_" : dev["Class"],
                                        "user" : dev["LoginUserId"],
                                        "description" : dev["Description"],
                                        "cucm" : cucm,
                                        "timestamp" : dev["TimeStamp"]
                                        })
    except:
        pass
    return devices

def save_devices(devices, path=None, prefix="cucm_devices"):
    if not path:
        path = os.getcwd()
    
    fname = prefix + "_" + datetime.now().strftime("%y%m%d_%H%M") + ".json"
    with open(os.path.join(path, fname), "w") as f:
        json.dump(devices, f, indent=4)
