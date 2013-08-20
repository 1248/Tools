#!/usr/bin/env python
#
# HYPERCAT.PY
# Copyright (c) 2013 Pilgrim Beart <pilgrim.beart@1248.io>
# 
# Enables easy creation of valid Hypercat catalogues
# Written to comply with IoT Ecosystems Demonstrator Interoperability Action Plan V1.0 24th June 2013
# As found at http://www.openiot.org/apis
#
##Permission is hereby granted, free of charge, to any person obtaining a copy
##of this software and associated documentation files (the "Software"), to deal
##in the Software without restriction, including without limitation the rights
##to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
##copies of the Software, and to permit persons to whom the Software is
##furnished to do so, subject to the following conditions:
##
##The above copyright notice and this permission notice shall be included in
##all copies or substantial portions of the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
##THE SOFTWARE.
##
## Usage:
##    Create a hypercat object
##    Optionally, add metadata to it with .addRelation()
##    Optionally, add items to the catalogue with .addItem()
##        (an item is either a hypercat or a resource)
##
## Example:
##    h = hypercat("CatalogueContainingOneCatalogueAndOneResource")
##    h2 = hypercat("ChildCatalogue")
##    h.addItem(h2, "http://FIXMEcat")
##    r = resource("resource1", "application/vnd.tsbiot.sensordata+json")
##    h.addItem(r, "http://FIXMEresource")
##    print h.data
##    print h.prettyprint()
##
## See unit tests for more examples

# TODO:
#   4.3.3 Says that it is optional to use isContentType to tag each member of items[]
#   However we treat it as mandatory.
# 
#   Efficiency: In the HyperCat spec, any item can have a relation repeated.
#   For example an item with metadata saying "Pilgrim is_a human" and "Pilgrim is_a man"
#   would repeat "rel" = "is_a" 
#   Therefore we cannot use sets as an efficient way to look-up relations, because set keys have to be unique, so here we iterate.
#   For efficient lookup we could use multisets/bags. Could use a set of lists, but then our .data field wouldn't be a direct representation of the hypercat

import json

# Each Catalogue has a (human-readable) description and a list of metadata about it
# It also contains a list of "items", each of which has an HREF and a list of metadata about it

REL = "rel"
VAL = "val"

# Catalogue structure
CATALOGUE_METADATA  = "item-metadata"    # Name of the array of metadata about the catalogue itself
ITEMS = "items"
HREF = "href"
ITEM_METADATA = "i-object-metadata" # Name of the array of metadata about each item in the catalogue

# Mandatory relations & types
ISCONTENTTYPE_RELATION = "urn:X-tsbiot:rels:isContentType"
CATALOGUE_TYPE = "application/vnd.tsbiot.catalogue+json"
DESCRIPTION_RELATION = "urn:X-tsbiot:rels:hasDescription:en"

# Optional relations & types
SUPPORTS_SEARCH_RELATION = "urn:X-tsbiot:rels:supportsSearch"
SUPPORTS_SEARCH_VAL = "urn:X-tsbiot:search:simple"
HAS_HOMEPAGE_RELATION = "urn:X-tsbiot:rels:hasHomepage"
CONTAINS_CONTENT_TYPE_RELATION = "urn:X-tsbiot:rels:containsContentType"

# We manage Catalogues and Resources as raw Python JSON objects (i.e. we construct them in their final form)

def _values(metadata, rel):
    """Searches a hypercat's metadata to find all relations "rel".
    Returns a list of the values of those relations
    (A list because a rel can occur more than once)"""
    result = []
    for r in metadata:
        if(r[REL] == rel):
            result.append(r[VAL])
    return result

class Base:
    # Functionality common to both Catalogues and Resources
    def __init__(self):
        self.data = {}

    def prettyprint(self):
        """Return hypercat formatted prettily"""
        return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))

class hypercat(Base):
    """Create a valid Hypercat catalogue"""
    # Catalogues must be of type catalogue, have a description, and contain at least an empty array of items

    def __init__(self, description):
        Base.__init__(self)
        assert isinstance(description, basestring), "Description argument must be a string"
        assert description!="", "Description argument cannot be empty"
        # TODO: Check description is ASCII, since JSON can only encode that
        self.data[CATALOGUE_METADATA] = [
            { REL:ISCONTENTTYPE_RELATION, VAL:CATALOGUE_TYPE },
            { REL:DESCRIPTION_RELATION, VAL:description }]
        self.data[ITEMS]=[]

    def addRelation(self, rel, val):
        self.data[CATALOGUE_METADATA] += [{REL:rel, VAL:val}]

    def values(self, rel):
        """Returns a LIST, since HyperCat allows rels to be repeated"""
        return _values(self.data[CATALOGUE_METADATA], rel)
    
    def addItem(self, child, href):
        """Add a new item (a catalogue or resource) as a child of this catalogue"""
        assert isinstance(child, Base), "child must be a hypercat Catalogue or Resource"
        child.data[HREF] = href
        if(CATALOGUE_METADATA in child.data):    # If adding a Catalogue as a child of another Catalogue, change the name of its metadata (because item metadata has a different name than catalogue metadata, for reasons unknown)
            t = child.data[CATALOGUE_METADATA]
            del child.data[CATALOGUE_METADATA]
            child.data[ITEM_METADATA]=t
        if ITEMS in child.data: # Child catalogues can't contain items
            del child.data[ITEMS]
        self.data[ITEMS] += [child.data]

    def description(self):  # 1.0 spec is unclear about whether there can be more than one description. We assume not.
        return self.values(DESCRIPTION_RELATION)[0]

    def items(self):
        return self.data[ITEMS]
    
    def supportsSimpleSearch(self):
        self.addRelation(SUPPORTS_SEARCH_RELATION, SUPPORTS_SEARCH_VAL)

    def hasHomepage(self, url):
        self.addRelation(HAS_HOMEPAGE_RELATION, url)

    def containsContentType(self, contentType):
        self.addRelation(CONTAINS_CONTENT_TYPE_RELATION, contentType)

class resource(Base):
    """Create a valid Hypercat Resource"""
    # Resources must have an href, have a declared type, and have a description
    def __init__(self, description, contentType):
        """contentType must be a string containing an RFC2046 MIME type"""
        Base.__init__(self)
        self.data[ITEM_METADATA] = [
            {REL:ISCONTENTTYPE_RELATION,VAL:contentType},
            {REL:DESCRIPTION_RELATION,VAL:description}]

    def addRelation(self, rel, val):
        self.data[ITEM_METADATA] += [{REL:rel, VAL:val}]

    def values(self, rel):
        """Returns a LIST, since HyperCat allows rels to be repeated"""
        return _values(self.data[ITEM_METADATA], rel)
    
def loads(inputStr):
    """Takes a string and converts it into an internal hypercat object, with some checking"""
    inCat = json.loads(inputStr)
    assert CATALOGUE_TYPE in _values(inCat[CATALOGUE_METADATA], ISCONTENTTYPE_RELATION)
    # Manually copy mandatory fields, to check that they are they, and exclude other garbage
    desc = _values(inCat[CATALOGUE_METADATA], DESCRIPTION_RELATION)[0]  # TODO: We are ASSUMING just one description, which may not be true
    outCat = hypercat(desc)
    for i in inCat[ITEMS]:
        print "Adding item",i
        href = i[HREF]
        contentType = _values(i[ITEM_METADATA], ISCONTENTTYPE_RELATION) [0]
        desc = _values(i[ITEM_METADATA], DESCRIPTION_RELATION) [0]
        r = resource(desc, contentType)
        outCat.addItem(r, href)

    return outCat

# ------ UNIT TESTS ------

def unittest():
    print "Running unit tests"

    print "\nTEST: Create basic empty Catalogue, and render to a string with pretty-printing"
    h = hypercat("Test Catalogue")
    result = h.prettyprint()
    print result
    assert result=="""{
    "item-metadata": [
        {
            "rel": "urn:X-tsbiot:rels:isContentType",
            "val": "application/vnd.tsbiot.catalogue+json"
        },
        {
            "rel": "urn:X-tsbiot:rels:hasDescription:en",
            "val": "Test Catalogue"
        }
    ],
    "items": []
}"""
    
    print "\nTEST: Create a catalogue containing 1 catalogue and 1 resource, held as data"
    h = hypercat("CatalogueContainingOneCatalogueAndOneResource")
    h2 = hypercat("ChildCatalogue")
    print "about to add child catalogue"
    h.addItem(h2, "http://FIXMEcat")
    r = resource("resource1", "application/vnd.tsbiot.sensordata+json")
    print "about to add child resource"
    h.addItem(r, "http://FIXMEresource")
    result = h.data
    print result
    assert result=={'items': [{'i-object-metadata': [{'val': 'application/vnd.tsbiot.catalogue+json', 'rel': 'urn:X-tsbiot:rels:isContentType'}, {'val': 'ChildCatalogue', 'rel': 'urn:X-tsbiot:rels:hasDescription:en'}], 'href': 'http://FIXMEcat'}, {'i-object-metadata': [{'val': 'application/vnd.tsbiot.sensordata+json', 'rel': 'urn:X-tsbiot:rels:isContentType'}, {'val': 'resource1', 'rel': 'urn:X-tsbiot:rels:hasDescription:en'}], 'href': 'http://FIXMEresource'}], 'item-metadata': [{'val': 'application/vnd.tsbiot.catalogue+json', 'rel': 'urn:X-tsbiot:rels:isContentType'}, {'val': 'CatalogueContainingOneCatalogueAndOneResource', 'rel': 'urn:X-tsbiot:rels:hasDescription:en'}]}

    print "\nTEST: Create a fancy Catalogue with optional metadata"
    h2 = hypercat("Fancy Catalogue")
    h2.supportsSimpleSearch()
    h2.hasHomepage("http://www.FIXME.com")
    h2.containsContentType("application/vnd.tsbiot.FIXME+json")
    result = h2.prettyprint()
    print result
    assert result=="""{
    "item-metadata": [
        {
            "rel": "urn:X-tsbiot:rels:isContentType",
            "val": "application/vnd.tsbiot.catalogue+json"
        },
        {
            "rel": "urn:X-tsbiot:rels:hasDescription:en",
            "val": "Fancy Catalogue"
        },
        {
            "rel": "urn:X-tsbiot:rels:supportsSearch",
            "val": "urn:X-tsbiot:search:simple"
        },
        {
            "rel": "urn:X-tsbiot:rels:hasHomepage",
            "val": "http://www.FIXME.com"
        },
        {
            "rel": "urn:X-tsbiot:rels:containsContentType",
            "val": "application/vnd.tsbiot.FIXME+json"
        }
    ],
    "items": []
}"""

    print "\nTEST: Add multiple RELS to a catalogue"
    h = hypercat("cat")
    assert h.values("relation") == []
    h.addRelation("relation","value1")
    h.addRelation("relation","value2")
    assert h.values("relation") == ["value1","value2"]
    print h.prettyprint()

    print "\nTEST: Load a catalogue from a string"
    inString = """{
    "item-metadata": [
        {
            "rel": "urn:X-tsbiot:rels:isContentType",
            "val": "application/vnd.tsbiot.catalogue+json"
        },
        {
            "rel": "urn:X-tsbiot:rels:hasDescription:en",
            "val": "ingestiontestcat"
        }
    ],
    "items": [
        {
            "href": "http://FIXME",
            "i-object-metadata": [
                {
                    "rel": "urn:X-tsbiot:rels:isContentType",
                    "val": "application/vnd.tsbiot.catalogue+json"
                },
                {
                    "rel": "urn:X-tsbiot:rels:hasDescription:en",
                    "val": "resource1"
                }
            ]
        },
        {
            "href": "http://FIXME2",
            "i-object-metadata": [
                {
                    "rel": "urn:X-tsbiot:rels:isContentType",
                    "val": "application/vnd.tsbiot.catalogue+json"
                },
                {
                    "rel": "urn:X-tsbiot:rels:hasDescription:en",
                    "val": "resource2"
                }
            ]
        },
        {
            "href": "http://RESOURCEURL",
            "i-object-metadata": [
                {
                    "rel": "urn:X-tsbiot:rels:isContentType",
                    "val": "resourcecontenttype"
                },
                {
                    "rel": "urn:X-tsbiot:rels:hasDescription:en",
                    "val": "A resource"
                }
            ]
        }
    ]
}"""
    h = loads(inString)
    outString = h.prettyprint()
    assert inString == outString
    print inString
    
    print "\nUnit tests all passed OK"

if __name__ == '__main__':
    # Unit tests
    unittest()

