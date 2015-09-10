import json
from collections import defaultdict

class Devices:
    def __init__(self, devices=None):
        self.devices = isinstance(devices, dict) and devices or {}
        self.attributes_list = self.get_attributes_list()
        self.registered_devices = self.get_registered()
        self.devices_purged = self.purge_latest()
        
    def get_attributes_list(self):
        try:
            return  list(set(sum((_v.keys() for k,v in self.devices.iteritems() for _v in v), [])))
        except:
            # malformed devices dict
            return []
    
    def get_attribute_types(self, attribute):
        try:
            tmp = list(set([ _v[attribute] for k,v in self.devices.iteritems() for _v in v ]))
        except:
            tmp = []
        return tmp
    
    def get_device_w_attribute(self, exact=True, union=False, purge=True, devices=None, **kwargs):
        tmp = {}
        if purge:
            devices = devices and purge_latest(devices) or self.devices_purged    
        else:
            devices = devices and devices or self.devices
        attribs = filter(lambda x: x in self.attributes_list, kwargs)
        condition = union and any or all # union = any, intersection = all
        equal = exact and (lambda x, y: x == y) or (lambda x, y: x.lower() in y.lower())
        if attribs:
            tmp.update({k:v for (k,v) in devices.iteritems() for _v in v 
                if condition(equal(kwargs[attrib], _v[attrib]) for attrib in attribs)})
        return tmp
    
    def purge_latest(self, devices=None):
        devs = devices and devices.copy() or self.devices.copy()
        for k,v in devs.iteritems():
            if len(v) <= 1:
                continue
            latest = max(v, key=lambda x: int(x["timestamp"]))
            devs[k] = [latest]
        return devs
    
    def get_registered(self, devices=None):
        devs = devices and devices.copy() or self.devices.copy()
        registered_devices = defaultdict(list)
        for k,v in devs.iteritems():
            for _v in v:
                if _v["status"] == "Registered":
                    registered_devices[k].append(_v["cucm"]+":"+_v["ip"])
                    
        return registered_devices

    def summary(self):
        self.get_attribute_types("class_")
        print "Total number of devices: %s" % len(self.devices)
        for d in self.get_attribute_types("class_"):
            devs_list = self.get_device_w_attribute(purge=False, class_=d)
            print "Total number of %ss: %s" % (d, len(devs_list))
