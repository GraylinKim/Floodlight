# -*- coding: utf-8 -*-
import urllib
from xml.dom import minidom

class Bill:
    """Represents the bills as maintained by Open Legislation
    
    """
    
    @staticmethod
    def loadFromXML(xml):
        """Loads a list of bills from an XML string or minidom class
        
        Converts into into minidom and pulls the bill data out of the root node
        Crawls the minidom for each bill's data
        Build the bills list to return to user
        
        """
        try:
            dom = minidom.parseString(xml)
        except TypeError as inst:
            if isinstance(xml,minidom):
                dom = xml
            else:
                raise inst
        
        bills = list()
        
        #Get the bill nodes from the docket and construct Bills one by one   
        elements = dom.getElementsByTagName('bill')
        for element in elements:
            bill = Bill()
            
            #billID,year,title,sponsor,lawSection are currently bill attributes
            bill.id = element.getAttribute('billId')
            bill.year = element.getAttribute('year')
            bill.title = element.getAttribute('title')
            bill.sponsor = element.getAttribute('sponsor')
            bill.law_section = element.getAttribute('lawSection')
            
            #ordering insensitive processing of sub node values
            #"" value if empty (no child nodes)
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
                elif 'text' == child.nodeName.lower():
                    try:
                        bill.text = child.firstChild.nodeValue
                    except AttributeError:
                        bill.text = ""
                elif 'cosponsors' == child.nodeName.lower():
                    try:
                        bill.cosponsors = list()
                        cosponsors = element.getElementsByTagName('cosponsors')
                        #Cosponsors is a nested list, loop the second level here
                        for cosponsor in cosponsors.item(0).childNodes:
                            bill.cosponsors.append(cosponsor.firstChild.nodeValue)
                    except AttributeError:
                        bill.cosponsors = list()
                #endif
            #endfor
            bills.append(bill)
        return bills

    def __str__(self):
        return 'Bill ' + str(bill.id) + ': ' + str(bill.title)


class OpenLegislation:
    """Provides a simple interface to the open legislation API
    
    USAGE:
        openleg = OpenLegislation(version='1.0',mode='object')
        bills = openleg.searchbysponsor('alesi') //Returns the list of Bill type
    
    TODO:
        Returning varied numbers of results, by appending '/first/last' to the end
        Documentation of functions and more usage
    
    """
  
    #Base Request URL
    baseURL = 'http://open-staging.nysenate.gov/legislation/api'
  
    #Meta data on the state of the library
    supportedVersions = ['1.0','1']
    supportedCommands = ['bill','committee','search','sponsor']
    # 'processed' format returns data processed into classes
    supportedModes = ['xml','csv','json','object']
    
    defaultMode = 'object'
    defaultVersion = '1.0'
    defaultPageSize = 20
    
    def __init__(self,
                mode=defaultMode,
                version=defaultVersion,
                pagesize=defaultPageSize):
        """Provide defaults for ease of use"""
        self.setVersion(version)
        self.setMode(mode)
        self.setPageSize(pagesize)
        
    def setPageSize(self,pagesize):
        """Assert Valid Page size before setting"""
        assert(pagesize>0 and pagesize<100),'Pagesize ('+str(pagesize)+') must be between 1 and 100'
        self.pagesize = pagesize
        
    def setMode(self,mode):
        """Assert supported mode before setting"""
        assert (mode in self.supportedModes),'Mode '+mode+' is not supported'
        self.mode = mode
    
    def setVersion(self,version):
        """Assert supported version before setting"""
        assert (version in self.supportedVersions), 'Version '+version+' is not supported'
        self.version = version
    
    def getBillById(self,billid):
        return self._makeRequest('bill',billid)
    
    def searchBySponsor(self,sponsor,page='1'):
        return self._makeRequest('sponsor',sponsor,page)
    
    def searchByCommittee(self,committee,page='1'):
        return self._makeRequest('search',committee,page)
    
    def searchById(self,billid,page='1'):
        return self._makeRequest('search',billid,page)
    
    def searchByKeyword(self,keywordtext,page='1'):
        return self._makeRequest('search',keywordtext,page)
    
    def _buildURL(self,command,argument,page):
        """Detects current mode and builds the appropriate request URL"""
        #All user input must be quoted to ensure safe html encoding
        argument = urllib.quote_plus(argument,"") 
        
        #object construction currently requires XML
        if self.mode == 'object':
            mode = 'xml'
        else:
            mode = self.mode
        
        return '/'.join([self.baseURL,self.version,mode,command,argument,str(page),str(self.pagesize)])
        
    #Internal Request mechanism, pretty simple at this point
    def _makeRequest(self,command,argument,page):
        """Executes the request and processes the data returned"""
        requestURL = self._buildURL(command,argument,page)
        print requestURL
        request = urllib.urlopen(requestURL)
        data = request.read()
        
        if self.mode == 'object':
            return Bill.loadFromXML(data)
        return data



#Protect our testing code. Will only execute if file is directly run
if __name__ == '__main__':
    import inspect
    from time import time
    
    openleg = OpenLegislation(pagesize=30)
    start = time()
    bills1 = openleg.searchByKeyword('healthcare',2)
    print len(bills1)
    """
    print str(time()-start)+' seconds to search.'
    print str(len(bills))+' bills found'
    
    try:
        print 'Inspecting a sample bill'
        for bill in bills:
            for member in bill.__dict__:
                print str(member) + ': ' + str(getattr(bill,member))
            print '\n'
        print '\n\n'
    except IndexError:
        print 'No bills found by search'
    """

    
