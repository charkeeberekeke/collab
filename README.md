# collab

Use CUCM's RIS API to get list of devices.
Currently works on CUCM version 9.x and above.

suds code borrowed from http://blog.darrenparkinson.uk/2013/01/using-python-to-call-cisco.html

Sample usage:

```
from collections import defaultdict
from pprint import pprint
from collab.ris import *
from collab.devices import Devices

cmnodes = ["UCM-01.foo.ltd", "UCM-02.foo.ltd"]

devices = defaultdict(list)

for cm in cmnodes:
    total, nodes = selectcmdevice(cucm="10.0.254.254", username='admin', 
                   password='foobar', NodeName=cm)
    for node in nodes:
        devices = parse_devices(node, devices)
        
devs = Devices(devices)
sip = devs.get_device_w_attribute(devices, class_="SIP Trunk")
gws = devs.get_device_w_attribute(devices, class_="Gateway")
phones = devs.get_device_w_attribute(devices, class_="Phone")
print "Total registered devices: %s " % len(devs.registered_devices)
print "Total registered phones: %s " % len(devs.get_registered(devices=phones))
print "Total registered SIP Trunks: %s " % len(devs.get_registered(devices=sip))
print "Total registered gateway devices: %s " % len(devs.get_registered(devices=gws))
pprint(dict(devs.registered_devices))
```
