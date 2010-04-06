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
                        cosponsors = element.getElementsByTagName('cosponsors')
                        
                        for cosponsor in cosponsors.item(0).childNodes:
                            bill.cosponsors.append(cosponsor.firstChild.nodeValue)
                    except AttributeError:
                        bill.cosponsors = list()
                elif 'text' == child.nodeName.lower():
                    try:
                        bill.text = child.firstChild.nodeValue
                    except AttributeError:
                        print "Error getting text!!"
                        bill.text = ""
            bills.append(bill)
        
        return bills

    def __str__(self):
        return 'Bill ' + str(bill.id) + ': ' + str(bill.title)


class OpenLegislation:
    """Provides a simple interface to the open legislation API
    
    USAGE:
        openleg = OpenLegislation(version='1.0',format='xml')
        bills = openleg.searchbysponsor('alesi') //Returns the list of Bill type
    
    TODO:
        Returning varied numbers of results, by appending '/first/last' to the end
        Documentation of functions and more usage
        Study other APIs to see how they handle some of these things
    
    """
  
    #Base Request URL
    baseURL = 'http://open-staging.nysenate.gov/legislation/api'
  
    #Meta data on the state of the wrapper
    supportedVersions = ['1.0']
    supportedCommands = ['bill','committee','search','sponsor']
    supportedFormats = ['xml']#,'csv','json','html']
  
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
    
    def getBillById(self,billid):
        return self._makeRequest('bill',urllib.quote(billid,""))
    
    def searchBySponsor(self,sponsor):
        return self._makeRequest('sponsor',urllib.quote(sponsor,""))
    
    def searchByCommittee(self,committee):
        return self._makeRequest('search',urllib.quote(committee,""))
    
    def searchById(self,billid):
        return self._makeRequest('search',urllib.quote(billid,""))
    
    def searchByKeyword(self,keywordtext):
        return self._makeRequest('search',urllib.quote(keywordtext,""))
    
    #Internal Request mechanism, pretty simple at this point
    def _makeRequest(self,command,argument):
        requestURL = '/'.join([self.baseURL,self.version,self.format,command,argument])
        print requestURL
        request = urllib.urlopen(requestURL)
        return Bill.loadFromXML(request.read())
    

#Protect our testing code. Will only execute if file is directly run
if __name__ == '__main__':
    import inspect
    from time import time
    
    openleg = OpenLegislation()
    start = time()
    bills = openleg.searchByKeyword('healthcare')
    
    print str(time()-start)+' seconds to search.'
    print str(len(bills))+' bills found'
    
    try:
        print 'Inspecting a sample bill'
        for bill in bills:
            for member in bill.__dict__:
                print str(member) + ': ' + str(getattr(bill,member))
            print '\n'
        #for member in inspect.getmembers(bills[0]):
        #    print member
        print '\n\n'
    except IndexError:
        print 'No bills found by search'
        

    
