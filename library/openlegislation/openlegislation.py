# -*- coding: utf-8 -*-
import urllib
import re
from objects import Bill

class OpenLegislation:
    """Provides a simple interface to the open legislation API
    
    Access to legislative data is provided in two central ways: Get and Search. 
    These requests are dependent both on the arguments passed in and the current
    state of the library.
    
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
    can additionally be customized with result ordering. Since searches may
    return a large number of results, pagination occurs. The size of each page 
    is a property of the library and the page nubmer you are requesting is 
    passed in with each request.
    
        Search Methods:
            
            search(searchString,pageNumber=1)
            advancedSearch(types,searchString,pageNumber=1)
            
            and
        
            <Find Specific then Search Methods>
            searchSponsor(sponsor,types,searchString,pageNumber=1)
            searchMemo(exactMatch,types,searchString,pageNumber=1)
            searchFullText(exactMatch,types,searchString,pageNumber=1)
            searchCommittee(committee,types,searchString,pageNumber=1)
            
            and
            
            <Generic Search Methods>
            searchActions(searchString,pageNumber=1)
            searchBills(searchString,pageNumber=1)
            searchCalendars(searchString,pageNumber=1)
            searchMeetings(searchString,pageNumber=1)
            searchTranscripts(searchString,pageNumber=1)
            searchVotes(searchString,pageNumber=1)
            
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

    """
    
    #Base Request URL used in _build(.*)URL requests below
    baseURL = 'http://open-staging.nysenate.gov/legislation'
    
    #Note: Calendars are not supported because they are not yet stable
    supportedGetTypes = set(['meeting','transcript','bill'])
    supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
    supportedModes = set(['html','xml','csv','json','object'])
    objectDataType = 'json'
    supportedVersions = [1]
    
    searchbills = {
        'FullText'  :'full',
        'Memo'      :'memo',
        'Sponsor'   :'sponsor',
    }
    searchotypes = {
        'Actions'    :'action',
        'Bills'      :'bill',
        'Calendars'  :'calendar',
        'Meetings'   :'meeting',
        'Transcripts':'transcript',
        'Votes'      :'vote',
    }
    
    def __init__(self,mode='object',version='1.0',pagesize=20):
        """Provide defaults for ease of use"""
        self.setVersion(version)
        self.setMode(mode)
        self.setPageSize(pagesize)
    
    """
        Get Methods
    """
    def getBill(self,billId):
        return self._makeRequest('get','bill',billId)
        
    def getMeeting(self,committee,number,session):
        assert number>0, 'Meeting number must be natural number (integer > 0)'
        assert re.match('\d{4}-\d{4}',session), 'Invalid session '+str(session)
        meetingId = '-'.join(['meeting',str(committee),str(number),str(session)])
        return self._makeRequest('get','meeting',meetingId)
        
    def getTranscript(self,transcriptId):
        return self._makeRequest('get','transcript',transcriptId)
        
    """
        Search Methods
    """
    def search(self,string,types=[],sponsor=None,committee=None,page=1):
        string = '('+string+')'
        string = string if sponsor=None else string+' AND sponsor:'+sponsor
        string = string if committee=None else string+' AND committee:'+committee
        return self._makeRequest('search',types,text,page)
        
    def searchFullText(self,string,types=[],sponsor=None,committee=None,page=1):
        string = 'full:('+string+')'
        string = string if sponsor=None else string+' AND sponsor:'+sponsor
        string = string if committee=None else string+' AND committee:'+committee
        return self._makeRequest('search',types,string,page)
    
    def searchMemo(self,string,types=[],sponsor=None,committee=None,page=1):
        string = 'memo:('+string+')'
        string = string if sponsor=None else string+' AND sponsor:'+sponsor
        string = string if committee=None else string+' AND committee:'+committee
        return self._makeRequest('search',types,string,page)
        
    def __getattr__(self,name):
        """Generates some search methods"""
        matches = re.match('search(.*)$',name)
        if matches:
            subject = matches.group(1)
            #If they specify a type without otype, do it this way
            if subject in set(self.searchbills.keys()):
                def custom_search(match,searchString,page='1'):
                    text = self.searchbills[subject]+':"'+match+'"'
                    if searchString:
                        text = text+' AND ('+searchString+')'
                    return self._makeRequest('search',types,text,page)
                return custom_search
            
            #If they specify an otype, do it this way
            elif subject in set(self.searchotypes.keys()):
                def custom_search(searchString,page='1'):
                    return self._makeRequest('search',[self.searchotypes[subject]],searchString,page)
                return custom_search
                
            #Else its not a valid request
            else:
                raise AttributeError, 'No attribute: '+name
        else:
            raise AttributeError, 'No attribute: '+name
        
    """
        Request methods, build the correct URL, get the data and return it
    """
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
        
        return requestURL  
                  
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
        if term:
            term = '('+otype_filter+') AND ('+urllib.quote_plus(term)+')'
        else:
            term = (otype_filter)
        
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
        assert int(float(version)) in self.supportedVersions,'Version '+str(version)+' is not supported'
        self.version = version.lower()



#Protect our testing code. Will only execute if file is directly run
if __name__ == '__main__':
    import doctest
    #doctest.testmod()
    
    openLeg = OpenLegislation()
    results = [
        '-------------------------',
        ' Specific Search Queries ',
        '-------------------------',
        openLeg.searchSponsor('ALESI',['bill'],'jobs~ AND benefits~'),
        openLeg.searchCommittee('AGING',['vote'],"healthcare OR medicare"),
        openLeg.searchFullText('tax',['bill'],'cuts~'),
        ' ------------------------',
        ' Generic Search Queries ',
        ' ------------------------',
        openLeg.searchActions('REFERRED TO FINANCE'),
        openLeg.searchBills('health* AND cut*'),
        openLeg.searchVotes('banking~'),
        openLeg.searchTranscripts('tabled OR failed'),
    ]
    for url in [urllib.unquote_plus(url) for url in results]:
        print url
