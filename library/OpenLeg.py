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
    
    Supports two types of requests. Get Requests and Search Requests.
    
    Get Requests are appropriate when you already know what 1 specific thing
    you are looking for.
    
    Search Requests are appropriate when you want to return a collection of
    result documents
    
    USAGE:
        openleg = OpenLegislation(version='1.0',mode='object')
        bills = openleg.searchbysponsor('alesi') //Returns the list of Bill type
    
    TODO:
        Returning varied numbers of results, by appending '/first/last' to the end
        Documentation of functions and more usage
    
    """
  
    #Base Request URL used in _build(.*)URL requests below
    baseURL = 'http://open-staging.nysenate.gov/legislation'
  
    #Meta data on the state of the library
    supportedVersions = ['1.0','1']    
    
    #need different type support because they have different type support :(
    supportedGetTypes = set(['meeting','transcript','calendar','bill'])
    supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
    #The object mode returns our classes
    supportedModes = set(['xml','csv','json','object'])

    #Class defaults
    defaultMode = 'object'
    defaultVersion = '1.0'
    defaultPageSize = 20
    objectDataType = 'json'
    
    def __init__(self,
                mode=defaultMode,
                version=defaultVersion,
                pagesize=defaultPageSize):
        """Provide defaults for ease of use"""
        self.setVersion(version)
        self.setMode(mode)
        self.setPageSize(pagesize)
    
    """
        Get Methods
    """
    def getBillById(self,billid):
        return self._makeRequest('get','bill',billid)
    
    """
        Searching Methods
    """
    def searchBySponsor(self,sponsor,page='1'):
        return self._makeRequest('search',['bill'],'sponsor:'+sponsor,page)
    
    def searchByCommittee(self,committee,page='1'):
        return self._makeRequest('search',['bill'],'committee:'+committee,page)
    
    def searchById(self,billid,page='1'):
        return self._makeRequest('search',billid,page)
    
    def searchByKeyword(self,keywordtext,page='1'):
        return self._makeRequest('search',keywordtext,page)
    
    """
        Setter Methods, do the appropriate support checking and lowcase
    """
    def setPageSize(self,pagesize):
        """Assert Valid Page size before setting"""
        assert pagesize>0 and pagesize<100,'Pagesize ('+str(pagesize)+') must be between 1 and 100'
        self.pagesize = pagesize
        
    def setMode(self,mode):
        """Assert supported mode before setting"""
        assert mode.lower() in self.supportedModes,'Mode '+mode+' is not supported'
        self.mode = mode.lower()
    
    def setVersion(self,version):
        """Assert supported version before setting"""
        assert version.lower() in self.supportedVersions, 'Version '+version+' is not supported'
        self.version = version.lower()
        
    """
        Request methods, build the correct URL, get the data and return it
    """
    #Internal Request mechanism, pretty simple at this point
    def _makeRequest(self,rtype,otype,term,pageNum=1):
        """Executes the request and processes the data returned"""
        
        #Determine the correct data format
        assert rtype.lower() in ['search','get'], "Invalid request type (use search or get)"
        if self.mode == 'object':
            mode = self.objectDataType
        else:
            mode = self.mode
            
        #Build the appropriate URL request string
        if rtype.lower()=='search':
            requestURL = self._buildSearchURL(otype,term,mode,pageNum)
        else:
            requestURL = self._buildGetURL(otype,term,mode)
            
        #Open the request and get the data
        request = urllib.urlopen(requestURL)
        data = request.read()
        
        #Objectify the data if necessary
        if self.mode == 'object':
            return data#Bill.loadFromXML(data)
        else:
            return data
        
    def _buildSearchURL(self, objects, term, mode, pageNum):
        """The Search URL is used to retrieve collections of documents"""
        
        #Assert valid object filters and pageNums
        assert set(objects).issubset(self.supportedSearchTypes), 'invalid types specified'
        assert pageNum>0, 'pageNum must be positive integer'
        
        #Embed each type in otype:<type> string, logically combine
        otype_filter = ' OR '.join(['otype:'+object for object in objects])
        #Combine filter and search text to form the term
        term = '('+otype_filter+') AND ('+urllib.quote_plus(term)+')'
        
        #Pair the arguments up in a dictionary
        args = {
            'term':term,
            'pageIdx':pageNum,
            'pageSize':self.pagesize,
            'format':mode
        }
        #Embed each arg in the key value pair, and join with &. Should I urllib quote this?
        args = '&'.join([key+'='+str(value) for key,value in args.iteritems()])
        
        #Join the different parts into a final URL, mark arguments with a ?
        return '/'.join( [self.baseURL,'search','?'+args] )
        
    def _buildGetURL(self,otype,oid,mode):
        """The Get URL is used to retrieve specific document types"""
        
        #Check for valid object type
        assert otype in self.supportedGetTypes, str(otype)+' is invalid type'
            
        #Join the differentparts into a final URL, quote their oid input
        return '/'.join( [self.baseURL,'api',self.version,mode,otype,urllib.quote_plus(oid)] )



#Protect our testing code. Will only execute if file is directly run
if __name__ == '__main__':
    openLeg = OpenLegislation(mode='xml')
    print openLeg._buildGetURL('bill','S66002','xml')
    print openLeg._buildSearchURL(['bill','vote','action'],'S66002','object',1)
    
    print openLeg.searchBySponsor('alesi')
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
