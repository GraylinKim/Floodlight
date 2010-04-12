# -*- coding: utf-8 -*-
import urllib
from objects.bill import Bill

class OpenLegislation:
    """Provides a simple interface to the open legislation API
    
    Access to legislative data is provided in two central ways: Get and Search. 
    These requests are dependent both on the arguments passed in and the current
    state of the library.
    
    Get requests should be used when you are looking for a single document of a
    single type for which you have unique identification. An example of this 
    would be retrieving bill number S66002.
    
        Get Methods:
            getBillById(billid)
            
    Search requests should be used whenever get requests do not apply. Searches
    may be applied across several types. Search terms may by fuzzy [~,*], apply
    boolean logic [AND,OR], and support ordering of evaluation [()]. Searches 
    can additionally be customized with result ordering. Since searches may
    return a large number of results, pagination occurs. The size of each page 
    is a property of the library and the page nubmer you are requesting is 
    passed in with each request.
    
        Search Methods:
            searchBySponsor(sponsor,pageNumber=1)
            
    Library state is contained in 3 properties: mode, version, and pagesize. 
    These properties have default values of 'object','1.0', and 20 by default.
    The default values can be overridden in the library constructor or through
    direct use of the setMode, setPageSize, and setVersion methods.
    
        Library State Variables:
        
            mode: determines the format of the data returned from user requests
                Available modes: xml, json, csv, html, and object        
                    Xml,json,csv,html return the raw data as retrieved.
                    Object returns objects.py objects preloaded with the data.
            
            version: determines the version used in the when building URLs
                Available versions: 1.0
                    Only one version has been released, this not yet useful.
            
            pagesize: determines the max number of results per page
                Available sizes: natural numbers (integers > 0)
                    There is no known maximum size for this value

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
    
    supportedModes = set(['html','xml','csv','json','object'])

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

    """Need to think more about these    
    def searchByCommittee(self,committee,page='1'):
        return self._makeRequest('search',['bill'],'committee:'+committee,page)
    
    def searchById(self,billid,page='1'):
        return self._makeRequest('search',billid,page)
    
    def searchByKeyword(self,keywordtext,page='1'):
        return self._makeRequest('search',keywordtext,page)
    """
    
    """
        Setter Methods, do the appropriate support checking and lowcase
    """
    def setPageSize(self,pagesize):
        """Assert Valid Page size before setting
        
        >>>openLeg = OpenLegislation()
        >>>openLeg.setPageSize(10)
        >>>print openLeg.pagesize
        10
        
        """
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
        assert request.getcode() == 200, 'Code '+str(request.getcode())+' returned, for url: '+requestURL
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
    import doctest
    #doctest.testmod()


    """
    openLeg = OpenLegislation(mode='xml')
    print openLeg._buildGetURL('bill','S66002','xml')
    print openLeg._buildSearchURL(['bill','vote','action'],'S66002','object',1)
    
    print openLeg.searchBySponsor('alesi')    
    
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
