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



