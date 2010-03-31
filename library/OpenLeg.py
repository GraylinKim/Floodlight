# -*- coding: utf-8 -*-
import urllib
from xml.dom import minidom

class Bill:
    
    def __init__(self,xml):
        pass
        
    def loadXML(self, xml):
        dom = minidom.parseString(xml)
        bill = dom.getElementsByTagName('bills')
        assert bill.length==1,"Only 1 Bill can be loaded at a time. %s bills recieved" % bill.length
        
  
class OpenLegislation:
    """Provides a simple interface to the open legislation API
    
    USAGE:
        openleg = OpenLegislation(version='1.0',format='xml')
        bills = openleg.searchbysponsor('alesi') //Returns the XML text
    
    TODO:
        One time format requests (instead of always using set default)
        Returning varied numbers of results, by appending '/first/last' to the end
        Documentation of functions and more usage
        Study other APIs to see how they handle some of these things
    
    """
  
    #Base Request URL
    baseURL = 'http://open.nysenate.gov/legislation/api'
  
    #Meta data on the state of the wrapper
    supportedVersions = ['1.0']
    supportedCommands = ['bill','committee','search','sponsor']
    supportedFormats = ['xml','csv','json','html']
  
    #Data defaults
    defaultVersion = '1.0'
    defaultFormat = 'xml'
    
    def __init__(self,format=defaultFormat,version=defaultVersion):
        self.setVersion(version)
        self.setFormat(format)
    
    def setFormat(self,format):
        assert (format in self.supportedFormats),'Format '+format+' is not supported'
        self.format = format
    
    def setVersion(self,version):
        assert (version in self.supportedVersions), 'Version '+version+' is not supported'
        self.version = version
    
    def searchbysponsor(self,sponsor):
        return self._makeRequest('sponsor',urllib.quote(sponsor,""))
    
    def searchbycommittee(self,committee):
        return self._makeRequest('search',urllib.quote(committee,""))
    
    def searchbyid(self,billid):
        return self._makeRequest('search',urllib.quote(billid,""))
    
    def searchbykeyword(self,keywordtext):
        return self._makeRequest('search',urllib.quote(keywordtext,""))
    
    #Internal Request mechanism, pretty simple at this point
    def _makeRequest(self,command,argument):
        requestURL = '/'.join([self.baseURL,self.version,self.format,command,argument])
        request = urllib.urlopen(requestURL)
        return request.read()
    

#Protect our testing code. Will only execute if file is directly run
if __name__ == '__main__':
    openleg = OpenLegislation()
    result = openleg.searchbyid('S3153')
    bill = Bill()
    bill.loadXML(result)
    
    print result
