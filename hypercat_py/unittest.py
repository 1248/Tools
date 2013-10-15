# UNITTEST.PY
# Copyright (c) 2013 Pilgrim Beart <firstname.lastname@1248.io>
# 
# Simple unit-tests for hypercat.py
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

import hypercat

def unittest():
    print "Running unit tests"

    print "\nTEST: Create minimal empty Catalogue, and render to a string, minimally, then with pretty-printing"
    h = hypercat.Hypercat("")

    s = h.asJSONstr()
    print s
    assert s=="""{"item-metadata":[{"rel":"urn:X-tsbiot:rels:isContentType","val":"application/vnd.tsbiot.catalogue+json"},{"rel":"urn:X-tsbiot:rels:hasDescription:en","val":""}],"items":[]}"""

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
            "val": ""
        }
    ],
    "items": []
}"""

    print "\nTEST: Create a catalogue containing 1 catalogue and 1 resource, held as data"
    h = hypercat.Hypercat("CatalogueContainingOneCatalogueAndOneResource")
    h2 = hypercat.Hypercat("ChildCatalogue")
    print "about to add child catalogue"
    h.addItem(h2, "http://FIXMEcat")
    r = hypercat.Resource("resource1", "application/vnd.tsbiot.sensordata+json")
    print "about to add child resource"
    h.addItem(r, "http://FIXMEresource")
    result = h.asJSON()
    print result
    print h.prettyprint()
    assert result=={'items': [{'i-object-metadata': [{'val': 'application/vnd.tsbiot.catalogue+json', 'rel': 'urn:X-tsbiot:rels:isContentType'}, {'val': 'ChildCatalogue', 'rel': 'urn:X-tsbiot:rels:hasDescription:en'}], 'href': 'http://FIXMEcat'}, {'i-object-metadata': [{'val': 'application/vnd.tsbiot.sensordata+json', 'rel': 'urn:X-tsbiot:rels:isContentType'}, {'val': 'resource1', 'rel': 'urn:X-tsbiot:rels:hasDescription:en'}], 'href': 'http://FIXMEresource'}], 'item-metadata': [{'val': 'application/vnd.tsbiot.catalogue+json', 'rel': 'urn:X-tsbiot:rels:isContentType'}, {'val': 'CatalogueContainingOneCatalogueAndOneResource', 'rel': 'urn:X-tsbiot:rels:hasDescription:en'}]}

    print "\nTEST: Create a catalogue 2 deep (and output each level)"
    h1 = hypercat.Hypercat("Top")
    h2 = hypercat.Hypercat("Middle")
    h3 = hypercat.Hypercat("Bottom")
    h1.addItem(h2, "http://FIXMEcat2")
    h2.addItem(h3, "http://FIXMEcat3")
    print "Top:"
    print h1.asJSON()
    print h1.prettyprint()
    print "Middle:"
    print h2.asJSON()
    print h2.prettyprint()
    print "Bottom:"
    print h3.asJSON()
    print h3.prettyprint()

    print "\nTEST: Creating more than 2 levels of catalogue, then outputting different levels"
    h1 = hypercat.Hypercat("Top")
    h1.addRelation("name","top")
    h2 = hypercat.Hypercat("Middle")
    h2.addRelation("name","middle")
    h3 = hypercat.Hypercat("Bottom")
    h3.addRelation("name","bottom")
    h1.addItem(h2, "http://FIXMEcat2")
    h2.addItem(h3, "http://FIXMEcat3")

    print "Find top catalogue:"
    hN = h1.findByPath("name", "/")
    print hN.prettyprint()
    assert hN.values("name")[0] == "top"

    print "Find middle catalogue:"
    hN = h1.findByPath("name", "/middle/")
    print hN.prettyprint()
    assert hN.values("name")[0] == "middle"

    print "Find bottom catalogue:"
    hN = h1.findByPath("name", "/middle/bottom")
    print hN.prettyprint()
    assert hN.values("name")[0] == "bottom"

    print "\nTEST: Create a fancy Catalogue with optional metadata"
    h2 = hypercat.Hypercat("Fancy Catalogue")
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
    h = hypercat.Hypercat("cat")
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
    h = hypercat.loads(inString)
    outString = h.prettyprint()
    assert inString == outString
    print inString
    
    print "\nUnit tests all passed OK"

if __name__ == "__main__":
    unittest()
