from suds.client import Client
from suds.transport.https import HttpAuthenticated
import os.path

HOME = os.path.expanduser("~")

class Executesqlquery:
    def __init__(self,
            cucm = "127.0.0.1",
            cmport = '8443',
            wsdl = "wsdl/cucm/axl/10.5/AXLAPI.wsdl",
            username = "",
            password = ""):

        self.wsdl = "file://" + os.path.join(HOME, wsdl)
        self.cucm = cucm
        self.cmport = cmport
        self.username = username
        self.password = password
        self.result = None
        self.sql = None
        self.location = "https://" + self.cucm + ":" + self.cmport + "/axl/"
        self.client = Client(self.wsdl, location=self.location, transport=HttpAuthenticated(username=self.username, password=self.password))

    def query(self, sql):
        self.sql = sql
        self.result = self.client.service.executeSQLQuery(sql=self.sql)
 #       print str(self.result)
        if self.result["return"] == "":
            self.result_list = []
        else:
            self.result_list = [ dict(n) for n in self.result['return']['row'] ]

    def rows(self):
        return len(self.result['return']['row'])

    def results(self):
        return self.result_list
        
    def columns(self):
        if self.rows() > 0:
            return dict(self.result['return']['row'][0]).keys()
        else:
            return []
