# collab

Use CUCM's RIS API to get list of devices.
Currently works on CUCM version 9.x and above.

Sample usage:

from pprint import pprint
from ris import *


cmnodes = ["UCM-01.example.ltd", "UCM-02.example.ltd"]

devices = defaultdict(list)
for cm in cmnodes:
    data = selectCMDevice(NodeName=cm)
    res_soap = risquery(server="10.0.20.248", username='admin', password='admin', data=data)
    devices = parse_devices(res_soap, devices)
    parse_status(res_soap)

devs = Devices(devices)
sip = devs.get_device_w_attribute(devices, class_="SIP Trunk")
gws = devs.get_device_w_attribute(devices, class_="Gateway")
phones = devs.get_device_w_attribute(devices, class_="Phone")
print "Total registered devices: %s " % len(devs.registered_devices)
print "Total registered phones: %s " % len(devs.get_registered(devices=phones))
print "Total registered SIP Trunks: %s " % len(devs.get_registered(devices=sip))
print "Total registered gateway devices: %s " % len(devs.get_registered(devices=gws))
pprint(dict(devs.registered_devices))
