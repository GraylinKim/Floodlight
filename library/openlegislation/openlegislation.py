# -*- coding: utf-8 -*-
import urllib
import re
#from objects import Bill
    
class OpenLegislation:
    """Provides a simple interface to the open legislation API
    
    Access to legislative data is provided in two central ways: Get and Search. 
    Both types of methods return OpenLegislationQuery classes which provide
    simple methods for handling complex queries. These classes are constructed
    with both on the arguments passed in and the current state of the library.
    
    Get requests should be used when you are looking for a single document of a
    single type for which you have unique identification. An example of this 
    would be retrieving bill number S66002.
    
        Get Methods:
            getBill(billId)
            getMeeting(committee,number,session)
            getTranscript(transcriptNumber)
            
    Search requests should be used whenever get requests do not apply. Searches
    may be applied across several types. Search terms may by fuzzy [~,*], apply
    boolean logic [AND,OR], and support ordering of evaluation [()]. Searches 
    can additionally be customized with result ordering (not yet supported).
    
        Search Methods:
            
            search(searchString,types=[],sponsor=None,committee=None)
            searchFullText(searchString,types=[],sponsor=None,committee=None)
            searchMemo(searchString,types=[],sponsor=None,committee=None)
    
        Search String:
            
            Search Strings in open legislation support set logic [AND,OR],
            logical grouping [()], exact matching [""], wildcards [*], and fuzzy
            matching [~]. Example usage and results below:
            
            TODO: Add Examples
            
            
        Optional Arguments
        
            types: describes the document type for get queries or a list of
            types to include for search queries.
                default: []
                Available types: bill,vote,action,transcript,meeting,calendar
            
            sponsor: restricts result to bills sponsored by the named senator.
                default: None
                Notes: sponsors are identfied by last name.
            
            committee: restricts results to documents associated with the named
            committee.
                default: None
                

                        
    Library state is contained in 2 properties: version, and pagesize. 
    These properties have default values of '1.0', and 20 by default.
    The default values can be overridden in the library constructor or through
    direct use of the setPageSize, and setVersion methods.
    
        Library State Variables:
            
            version: determines the version used in the when building URLs
                Available versions: 1.0
                    Only one version has been released, this not yet useful.
            
            pagesize: determines the max number of results per page
                Available sizes: natural numbers (integers > 0)
                    There is no known maximum size for this value

    """
    
    #Note: Calendars are not supported because they are not yet stable
    supportedGetTypes = set(['meeting','transcript','bill'])
    supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
    supportedVersions = [1.0]
    objectDataType = 'json'
    
    def __init__(self,version='1.0',pagesize=20):
        """Provide defaults for ease of use"""
        self.setVersion(version)
        self.setPageSize(pagesize)
    
    def getBill(self,billId):
        return OpenLegislationQuery('get',billId,'bill',None,None,self.pagesize,self.version)
        
    def getMeeting(self,committee,number,session):
        assert number>0, 'Meeting number must be natural number (integer > 0)'
        assert re.match('\d{4}-\d{4}',session), 'Invalid session '+str(session)
        meetingId = '-'.join(['meeting',str(committee),str(number),str(session)])
        return OpenLegislationQuery('get',meetingid,'meeting',None,None,self.pagesize,self.version)
        
    def getTranscript(self,transcriptId):
        return OpenLegislationQuery('get',transcriptId,'transcript',None,None,self.pagesize,self.version)
        
    def search(self,string,types=[],sponsor=None,committee=None):
        return OpenLegislationQuery('search',string,types,sponsor,committee,self.pagesize,self.version)
        
    def searchFullText(self,string,types=[],sponsor=None,committee=None):
        string = 'full:('+string+')'
        return OpenLegislationQuery('search',string,types,sponsor,committee,self.pagesize,self.version)
    
    def searchMemo(self,string,types=[],sponsor=None,committee=None):
        string = 'memo:('+string+')'
        return OpenLegislationQuery('search',string,types,sponsor,committee,self.pagesize,self.version)
    
    def setPageSize(self,pagesize):
        """Assert Valid Page size before setting"""
        assert pagesize>0 and pagesize<100,'Pagesize ('+str(pagesize)+') must be between 1 and 100'
        self.pagesize = pagesize
    
    def setVersion(self,version):
        """Assert supported version before setting"""
        assert float(version) in self.supportedVersions,'Version '+str(version)+' is not supported'
        self.version = version.lower()

class OpenLegislationQuery:
    """Holds all the query parameters. Used to construct URLs and make requests.
    
    Queries contain the logic for both constructing queries from parameters and
    executing those queries. It is not recommended that you construct queries on
    your own. Instead you should use the available OpenLegislation methods which
    will gnerate the queries for you. This ensures meaningful and accurate
    queries are produced. Queries have the following elements:
    
        qtype: determines the kind of query that you wish to execute
            Available qtypes: get, search
        
        string: identifies the document to get; contains the search text
            Available Modifiers: AND, OR, (), *, ~, ""
            Notes: See detailed explanation under searchString in the
            OpenLegislation documentation above
            
        Optional Parameters (and their defaults)
        
            types: describes the document type for get queries or a
            list of types to include for search queries.
                default: []
                Available types: bill,vote,action,transcript,meeting,calendar
            
            sponsor: restricts result to bills sponsored by the named senator.
                default: None
                Notes: sponsors are identfied by last name.
            
            committee: restricts results to documents associated with the
            named committee.
                default: None

            pagesize: the number of results returned with each request
                default: 20
                Available sizes: 0 < pagesize < unknown
                
            version: the version of the API to query with (for compatibility)
                default: 1.0
                Available versions: 1.0
    
    Queries are executed by calling a method corresponding to the format you 
    wish to retrieve the data in and indicating the page number to retrieve. In
    some cases the data returned will change depending on the mode chosen due to
    inconsistencies in Open Legislation. The following modes are available:
        
        xml(page=1) - Returns the data in XML format
        json(page=1) - Returns the data in JSON format
        csv(page=1)  - Returns the data in CSV format
        html(page=1) - Returns the data in HTML format
        object(page=1) - Returns the data preloaded into objects for convenience

    Since searches may return a large number of results, pagination occurs. The
    size of each page is typically a property of the library passed in during 
    query creation but can also be changed on a query basis through the pagesize
    parameter.
    
    """
    baseURL = 'http://open-staging.nysenate.gov/legislation'
    supportedGetTypes = set(['meeting','transcript','bill'])
    supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
    supportedModes = set(['html','xml','csv','json','object'])
    
    def __init__(self,qtype,string,types=[],sponsor=None,committee=None,pagesize=20,version=1.0):
        qtype = qtype.lower()
        assert qtype=='get' or qtype=='search',
            "Invalid query type ("+qtype+"). Use 'get' or 'set'"
        assert qtype=='search' or not types==[],
            "Get requests must have a type specified"
            
        self.qtype = qtype
        self.string = string
        self.type = str(types) if qtype == 'get' else set(types)
        self.sponsor = sponsor
        self.committee = committee
        self.pagesize = pagesize
        self.version = version
        
    def url(self,mode,page=1):
        #Adjust mode when objects are being returned
        mode = 'json' if mode == 'object' else mode
        assert page>0, 'Page number must be greater than zero'
        
        func = self._getURL if self.qtype=='get' else self._searchURL
        return self.func(mode,page)
        
    def _getURL(self,mode,page):
        assert self.type in self.supportedGetTypes, self.type +' is invalid type'
        string = urllib.quote_plus(self.string)
        url =  '/'.join( [self.baseURL,'api',self.version,mode,'get',string] )
         
    def _searchURL(self,mode,page):
        assert self.type.issubset(self.supportedSearchTypes),
            'invalid search types specified: '+' ,'.join(self.type)
        
        #Build full search term with optional committee,sponsor, and types
        prefix = ""
        if self.committee:
            committee = 'committee:'+self.committee
            prefix = prefix+' AND '+committee if prefix else committee
        if self.sponsor:
            sponsor = 'sponsor:'+self.sponsor
            prefix = prefix+' AND '+sponsor if prefix else sponsor
        if otype_filter:
            otypes = ' OR '.join(['otype:'+object for object in self.type])
            prefix = prefix+' AND ('+otypes+')' if prefix else '('+otypes+')'
        if self.string:
            term = self.string if not prefix else prefix+' AND ('+self.string+')'
        else:
            term = prefix
        
        #Embed each arg in the key value pair, and join with &.
        args = '&'.join([
            key+'='+str(value) for key,value in {
                'term':urllib.quote_plus(term),
                'pageIdx':page,
                'pageSize':self.pagesize,
                'format':mode
            }.iteritems()
        ])
        
        #Join the pieces into a final URL, mark arguments with a ?
        url =  '/'.join( [self.baseURL,'search','?'+args] )
    
    def __getattr__(self,name):
        if not name.lower() in self.supportedModes:
            raise AttributeError
            
        def execute(page=1):
            requestURL = self.url(name.lower(),page)
            request = urllib.urlopen(requestURL)
            assert request.getcode() == 200, 'Code '+str(request.getcode())+' returned, for url: '+requestURL
            data = request.read()
            
            # TODO: Object creation and loading
            if name == 'object':
                return data#Bill.loadFromXML(data)
            else:
                return data
                
        return execute

#Protect our testing code. Will only execute if file is directly run
if __name__ == '__main__':
    
    openLeg = OpenLegislation()
    results = [
        openLeg.search('jobs~ AND benefits~',sponsor='ALESI',types=['bill']).url('object'),
        openLeg.search('healthcare OR medicare',committee='AGING',types=['vote']).url('xml'),
        openLeg.searchFullText('tax cuts~',types=['bill']).url('json')
    ]
    for url in [urllib.unquote_plus(url) for url in results]:
        print url
        
    print openLeg.search('healthcare OR medicare',committee='AGING',types=['vote']).xml()

