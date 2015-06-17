from collections import defaultdict

class Devices:
    def __init__(self, devices=None, from_json=None):
        if from_json:
            self.devices = json.loads(from_json)
        elif devices and isinstance(devices, dict):
            self.devices = devices
        else:
            self.devices = {}
        self.attributes_list = self.get_attributes_list()
        self.registered_devices = self.get_registered()
        
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
    
    def get_device_w_attribute(self, devices=None, **kwargs):
        tmp = {}
        devices = devices and devices or self.devices
        for attrib,value in kwargs.iteritems():
            if attrib not in self.attributes_list:
                continue
            #tmp.update({k:v for (k,v) in devices.iteritems() for _v in v if _v[attrib] == value})
            tmp.update({k:v for (k,v) in devices.iteritems() for _v in v if value.upper() in _v[attrib].upper()})
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
