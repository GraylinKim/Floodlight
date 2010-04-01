# -*- coding: utf-8 -*-
import urllib
from xml.dom import minidom

class Bill:
    
    @staticmethod
    def loadFromXML(xml):
        try:
            dom = minidom.parseString(xml)
        except TypeError as inst:
            if isinstance(xml,minidom):
                dom = xml
            else:
                raise inst
        
        elements = dom.getElementsByTagName('bill')
        
        bills = list()
        for element in elements:
            bill = Bill()
            bill.id = element.getAttribute('billId')
            bill.year = element.getAttribute('year')
            bill.title = element.getAttribute('title')
            bill.sponsor = element.getAttribute('sponsor')
            bill.law_section = element.getAttribute('lawSection')
            for child in element.childNodes:
                if 'summary' == child.nodeName.lower():
                    try:
                        bill.summary = child.firstChild.nodeValue
                    except AttributeError:
                        bill.summary = ""
                elif 'committee' == child.nodeName.lower():
                    try:
                        bill.committee = child.firstChild.nodeValue
                    except AttributeError:
                        bill.committee = ""
                elif 'cosponsors' == child.nodeName.lower():
                    try:
                        bill.cosponsors = list()
                        cosponsors = element.getElementsByTagName('cosponsors').item(0)
                        bill.cosponsors = cosponsors.firstChild.firstChild.nodeValue
                    except AttributeError:
                        bill.cosponsors = list()
            bills.append(bill)
        
        return bills

    def __str__(self):
        return 'Bill ' + str(bill.id) + ': ' + str(bill.title)


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
    baseURL = 'http://open-staging.nysenate.gov/legislation/api'
  
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
    import inspect
    from time import time
    
    openleg = OpenLegislation()
    start = time()
    result = openleg.searchbykeyword('bank')
    returned = time()
    bills = Bill.loadFromXML(result)
    loaded = time()
    
    for bill in bills:
        for member in inspect.getmembers(bill):
            print member
        print '\n\n'
    
    print str(returned-start)+' to get xml and '+str(loaded-returned)+' to parse it into bills'
    
