from suds.client import Client
from suds import WebFault
from suds.transport.https import HttpAuthenticated
import os.path

HOME = os.path.expanduser("~")

class Executesqlquery:
    """
    Container for executesqlquery in CUCM AXL
    Sample usage is:

    from collab.axl import Executesqlquery
    axl_sql = Executesqlquery(cucm = "10.254.254.254", username="admin", password="password")
    if axl_sql.query(sql="select * from device"):
        print axl_sql.results()
    else:
        print axl_sql.error()

    Tested to work in Python 2.7.5 & centos 7
    requires cucm cert to be installed in local trust store
    """
    def __init__(self,
            cucm = "127.0.0.1",
            cmport = '8443',
            wsdl = "wsdl/cucm/axl/10.5/AXLAPI.wsdl",
            username = "",
            password = ""):
        """
        wsdl is set as file, no known url wsdl for AXL
        """
        self.wsdl = "file://" + os.path.join(HOME, wsdl)
        self.cucm = cucm
        self.cmport = cmport
        self.username = username
        self.password = password
        self.result = None
        self.sql = None
        self.result_error = None
        self.location = "https://" + self.cucm + ":" + self.cmport + "/axl/"
        self.client = Client(self.wsdl, location=self.location, transport=HttpAuthenticated(username=self.username, password=self.password))

    def query(self, sql):
        """
        Return True if sql query succeeds, False if otherwise
        """
        self.sql = sql
        try:
            self.result = self.client.service.executeSQLQuery(sql=self.sql)
        except WebFault, e:
            self.result_error = str(e)
            self.result_list = []
            return False
        if self.result["return"] == "":
            self.result_list = []
        else:
            self.result_list = [ dict(n) for n in self.result['return']['row'] ]

        return True

    def rows(self):
        """
        Return number of returned rows
        """
        return len(self.result_list)

    def results(self):
        """
        Return list of rows with every row entry represented as a dict
        in column : value form
        """
        return self.result_list
        
    def columns(self):
        """
        Return list of columns for returned query
        """
        if self.rows() > 0:
            return dict(self.result['return']['row'][0]).keys()
        else:
            return []

    def error(self):
        """
        Return error message
        """
        return self.result_error
