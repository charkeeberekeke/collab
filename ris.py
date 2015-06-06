import requests
import HTMLParser
from lxml import etree
from collections import defaultdict
from requests.auth import HTTPBasicAuth
from pprint import pprint

def selectCMDevice(Class="Any", Status="Any", NodeName=None, MaxReturnedDevices="1000"):
    """
    Create soap xml for selectCMDevice RIS request
    """
    header = """<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<soapenv:Body>
<ns1:SelectCmDevice soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="http://schemas.cisco.com/ast/soap/">
<StateInfo xsi:type="xsd:string"/>
<CmSelectionCriteria href="#id0"/>
</ns1:SelectCmDevice>
<multiRef id="id0" soapenc:root="0" soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xsi:type="ns2:CmSelectionCriteria" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns2="http://schemas.cisco.com/ast/soap/">
<MaxReturnedDevices xsi:type="xsd:unsignedInt">{2}</MaxReturnedDevices>
<Class xsi:type="xsd:string">{0}</Class>
<Model xsi:type="xsd:unsignedInt">255</Model>
<Status xsi:type="xsd:string">{1}</Status>""".format(Class, Status, MaxReturnedDevices)
    nodename = NodeName and '<NodeName xsi:type="xsd:string">%s</NodeName>' % NodeName or '<NodeName xsi:type="xsd:string" xsi:nil="true"/>'
    footer = """<SelectBy xsi:type="xsd:string">Name</SelectBy>
<SelectItems soapenc:arrayType="ns2:SelectItem[1]" xsi:type="soapenc:Array">
<item href="#id1"/>
</SelectItems>
</multiRef>
<multiRef id="id1" soapenc:root="0" soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xsi:type="ns3:SelectItem" xmlns:ns3="http://schemas.cisco.com/ast/soap/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
<Item xsi:type="xsd:string">*</Item>
</multiRef>
</soapenv:Body>
</soapenv:Envelope>"""
    return "\n".join([header, nodename, footer])

def risquery(server=None, username=None, password=None, data=None):
    """
    Send RIS query to CUCM
    Currently tested working only on selectCMDevice query
    """
    url = 'https://%s:8443/realtimeservice/services/RisPort' % server
    headers = {"SOAPAction" : r'http://schemas.cisco.com/ast/soap/action/#RisPort#SelectCmDevice',
           "Content-type" : "text/xml"}
    auth = HTTPBasicAuth(username, password)
    r = requests.post(url, headers=headers, auth=auth, data=data, verify=False)    
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    xml = r.text.encode("utf-8")
    return etree.fromstring(xml, parser=parser)

def parse_status(tree):
    """
    Parses response status from ris query
    Currently tested working only on selectCMDevice query
    Need to add error-handling logic
    """
    status = tree.xpath("//StateInfo")
    status_raw =  etree.tostring(status[0])
    h = HTMLParser.HTMLParser()
    status_xml = etree.fromstring(h.unescape(status_raw))
    status_nodes = status_xml.xpath("//Node")

    total = 0
    for n in status_nodes:
        print "Name: {Name}, TotalItemsFound: {TotalItemsFound}, TotalItemsReturned: {TotalItemsReturned}".format(**n.attrib)
        total += int(n.get("TotalItemsFound"))
    print "Total : %s" % str(total)

def parse_devices(tree, devices=None):
    """
    Parse devices from selectCMDevices input into dict with 
    device macs as key and the device's attributes in a list of dicts
    """
    cmnodes = tree.xpath("//CmNodes")
    devices = isinstance(devices, defaultdict) and devices or defaultdict(list)
    #devices = defaultdict(list)
    if len(cmnodes) == 1:
        for cms in cmnodes[0]:
            cucm = cms.xpath("Name")[0].text
            devs = len(cms.xpath("CmDevices")) == 1 and cms.xpath("CmDevices")[0] or []
            #devs = cms.xpath("CmDevices")
            for dev in devs:
                name = dev.xpath("Name")[0].text
                ip = dev.xpath("IpAddress")[0].text
                ext = dev.xpath("DirNumber")[0].text
                class_ = dev.xpath("Class")[0].text
                status = dev.xpath("Status")[0].text
                user = dev.xpath("LoginUserId")[0].text
                description = dev.xpath("Description")[0].text
                timestamp = dev.xpath("TimeStamp")[0].text
                devices[name].append({ "ip" : str(ip),
                                   "ext" : str(ext),
                                   "status" : str(status),
                                   "class_" : str(class_),
                                   "user" : str(user),
                                   "description" : str(description),
                                   "cucm" : str(cucm),
                                   "timestamp" : str(timestamp)
                                    })
    return devices

class Devices:
    """
    Performs basic proccessing of device list return by the selectCMDevice soap query
    for CUCM RISquery
    """
    def __init__(self, devices=None):
        self.devices = isinstance(devices, dict) and devices or {}
        self.attributes_list = self.get_attributes_list()
        self.registered_devices = self.get_registered()
        
    def get_attributes_list(self):
        """
        Return attribute list for a devices.
        For a selectCMDevice response for example, the attributes
        list will be: ip, status, class_, user, description, cucm
        and timestamp
        """
        try:
            return  list(set(sum((_v.keys() for k,v in self.devices.iteritems() for _v in v), [])))
        except:
            # malformed devices dict
            return []
    
    def get_attribute_types(self, attribute):
        """
        Return attribute types per given attribute.
        Example is Registered, Unregistered for the status attribute
        """
        try:
            tmp = list(set([ _v[attribute] for k,v in self.devices.iteritems() for _v in v ]))
        except:
            tmp = []
        return tmp
    
    def get_device_w_attribute(self, devices=None, **kwargs):
        """
        Returns devices which match the given attributes as set
        in kwargs. Accepts devices argument to enable to process
        filtered device lists.
        This iteration currently returns 'or' combination of 2 or more attributes
        Will need to add option of 'and' combination.
        """
        tmp = {}
        devices = devices and devices or self.devices
        for attrib,value in kwargs.iteritems():
            if attrib not in self.attributes_list:
                continue
            #tmp.update({k:v for (k,v) in devices.iteritems() for _v in v if _v[attrib] == value})
            tmp.update({k:v for (k,v) in devices.iteritems() for _v in v if value.upper() in _v[attrib].upper()})
        return tmp
    
    def purge_latest(self, devices=None):
        """
        Return most recent entry for devices with duplicate entries.
        Most recent is defined as having the bigger timestamp value
        """
        devs = devices and devices.copy() or self.devices.copy()
        for k,v in devs.iteritems():
            if len(v) <= 1:
                continue
            latest = max(v, key=lambda x: int(x["timestamp"]))
            devs[k] = [latest]
        return devs
    
    def get_registered(self, devices=None):
        """
        Return dict containing devices with registered status
        The dict contains list of device attribute with format
        cucm:ip
        """
        devs = devices and devices.copy() or self.devices.copy()
        registered_devices = defaultdict(list)
        for k,v in devs.iteritems():
            for _v in v:
                if _v["status"] == "Registered":
                    registered_devices[k].append(_v["cucm"]+":"+_v["ip"])
                    
        return registered_devices  

