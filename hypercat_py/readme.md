Usage
=====

Servers:

- Create an empty hypercat catalogue
- Optionally, add metadata to describe it
- Optionally, add items to the catalogue
	- an item is either a hypercat or a resource
- Output it as JSON, either minimally or prettyprinted
- Find a specific part of a catalogue hierarchy

Clients:

- Load and validate a hypercat

Example - HyperCat server
-------------------------
<pre>
We'll create a HyperCat catalogue with 2 items in it:
      h
     / \
    h2  r
</pre>

    import hypercat
    
    # Create a catalogue
    h = hypercat.hypercat("CatalogueContainingOneCatalogueAndOneResource")
    
    # Create a second catalogue, and add it as a child of the first
    h2 = hypercat.hypercat("ChildCatalogue")
    h.addItem(h2, "http://FIXMEcat")
    
    # Create a resource, and add it as another child of the first catalogue
    r = hypercat.resource("resource1", "application/vnd.tsbiot.sensordata+json")
    h.addItem(r, "http://FIXMEresource")
    
    # Print the raw JSON of the catalogue, and then with human-friendly formatting
    print h.asJSON()
    print h.prettyprint()
 
_OUTPUT_

<pre>
{
    "item-metadata": [
        {
            "rel": "urn:X-tsbiot:rels:isContentType",
            "val": "application/vnd.tsbiot.catalogue+json"
        },
        {
            "rel": "urn:X-tsbiot:rels:hasDescription:en",
            "val": "CatalogueContainingOneCatalogueAndOneResource"
        }
    ],
    "items": [
        {
            "href": "http://FIXMEcat",
            "i-object-metadata": [
                {
                    "rel": "urn:X-tsbiot:rels:isContentType",
                    "val": "application/vnd.tsbiot.catalogue+json"
                },
                {
                    "rel": "urn:X-tsbiot:rels:hasDescription:en",
                    "val": "ChildCatalogue"
                }
            ]
        },
        {
            "href": "http://FIXMEresource",
            "i-object-metadata": [
                {
                    "rel": "urn:X-tsbiot:rels:isContentType",
                    "val": "application/vnd.tsbiot.sensordata+json"
                },
                {
                    "rel": "urn:X-tsbiot:rels:hasDescription:en",
                    "val": "resource1"
                }
            ]
        }
    ]
}
</pre>

  
Example - HyperCat Client
-------------------------
	h = hypercat.loads(inString)	# Read-in and validate HyperCat
	print "Metadata is ",h.metadata

How this module works
=====================
According to the spec, each Catalogue has a (human-readable) description and a list of metadata about it.
It also contains a list of "items", and each item has an HREF and a list of metadata about it.
An item can be any kind of resource, including another catalogue.

So conceptually, catalogues can have many levels of hierarchy (i.e. a catalogue can contain a catalogue which contains a catalogue and so on).
(Catalogues don't just have to be trees either, they can be graphs, contain loops etc.)
And clients of this module will often want to declare full catalogue structures several levels deep, i.e. build their entire hierarchy in one go.

But according to the 1.0 spec only one level of Catalogue can be output at a time,
i.e. getting a catalogue will declare its child catalogues, but not its grand-children
(to see the grand-children, you'd have to get the child catalogue)

A further complication is some asymmetry in how attributes are declared when a catalogue is the parent, vs. when it is the child

To deal with this, within this module we maintain a universal base class for every hypercat object.
Then during output, we ignore grand-children, and modify attributes as necessary.

Released as Open Source
=======================

Copyright (c) 2013 Pilgrim Beart &lt;firstname.lastname@1248.io&gt;
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
