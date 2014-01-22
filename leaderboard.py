#!/usr/bin/env python
#
#     LEADERBOARD.PY
# (c) 2014 Pilgrim Beart, 1248 Ltd.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Demo code
# ----
# Using only standard Python 2.7 libraries, we:
# 1) Read a HyperCat API (http://www.openiot.org/apis)
# 2) Crawl the hierarchy exhaustively looking for contents of a particular type
#   (in this case Energy, a standard SenML type held in Joules)
#   (limitation: Catalogues must form a closed hierarchy, not an open or cyclic graph)
# 3) Return a ranked leaderboard of the previous day's results
#

import urllib2, base64, json, time

HYPERCAT_URL = "http://geras.1248.io/share/5ab6d8kw8t/armhome/cat"
HYPERCAT_KEY = ">>INSERT_KEY_HERE<<"

def loadJSON(uri, key=None):
    # Loads a HyperCat catalogue from a remote server, as a JSON string
    # URI must be fully-specified, i.e. "https://fred.com/cat" or "http://127.0.0.1:9087/cat"
    # As per the HyperCat spec, the access <key>, if any, is passed as the Basic Auth username 
    
    if(key!=None):
        # The following approach to constructing Basic Auth should work
        # even if the site doesn't send back a 401 in response to a non-auth request
        request = urllib2.Request(uri)
        base64string = base64.encodestring(key+":"+"")[:-1]  # Remove trailing \n
        request.add_header("Authorization", "Basic %s" % base64string)
        f = urllib2.urlopen(request, timeout=600)    # 60 seconds is max timeout allowed by GAE in foreground (but if testing locally we can get longer)
    else:
        f = urllib2.urlopen(uri, timeout=600)
        
    return json.loads(f.read())

CONTENT_TYPE_IS = 'urn:X-tsbiot:rels:isContentType'
CATALOGUE = 'application/vnd.tsbiot.catalogue+json'
SENML = 'application/senml+json'

SENML_UNITS_IS = 'urn:X-senml:u'
ENERGY = 'J'

SUPPORTS_QUERY = 'urn:X-tsbiot:rels:supports:query'
OPENIOT = 'urn:X-tsbiot:query:openiot:v1'

def hasRel(metadataList, rel, val):
    # Hypercat metadata consists of a list of pairs [(rel=R,val=V), ...]
    # We return True if we find a matching pair
    m = [ (x) for x in metadataList if x['rel']==rel and x['val']==val ]
    return m != []

def isQueryable(metadata, datatype):
    # Does this Resource support time-series queries?
    return  (hasRel(metadata, CONTENT_TYPE_IS, SENML) and
            hasRel(metadata, SENML_UNITS_IS, datatype) and
            hasRel(metadata, SUPPORTS_QUERY, OPENIOT))

def previousDay():
    # As epoch-seconds
    t = int(time.time())
    (d,d,d,h,m,s,d,d,d) = time.gmtime(t)
    start = t - s - m*60 - h*60*60 - 86400  # Find start of previous whole day
    end = start + 86400
    return (start,end)

def senmlValueAtTime(senml,t):
    # Extract the value of a SenML time series at a particular time
    d = [ (x["v"]) for x in senml["e"] if x['t']==t ]
    return d[0] if d else None
 
def getEnergySeries(href, key, metadata):
    # Get the last 24 hours, as 1-hour rollups
    (start,end) = previousDay()
    data = loadJSON(href+"?start="+str(start)+"&end="+str(end)+"&interval=1h&rollup=avg", key)
    # We asked for a full day of hours, but actually all we care about are Hour 0 and Hour 23
    # This is because we're dealing with Total-Energy-To-Date values, not Power values,
    # so what goes on between the last and first hour is irrelevant detail.
    try:
        kWh = (senmlValueAtTime(data, end-3600) - senmlValueAtTime(data, start)) / 3600000 # Convert a full day's consumption from Joules to kiloWatthours
    except:
        kWh = None
    return (href, kWh)

def crawl(url, key, datatype, fn):
    # Returns a list of values resulting from calling <fn> on every queryable leaf
    cat = loadJSON(url, key)
    result = []
    for (href,metadata) in map(lambda x: (x["href"],x["i-object-metadata"]), cat["items"]):
        if hasRel(metadata, CONTENT_TYPE_IS, CATALOGUE):
            result += crawl(href, key, datatype, fn)
        else:   # Resource
            if isQueryable(metadata, datatype):
                result += [fn(href, key, metadata)]
    return result

def getLeaderboard():
    L = crawl(HYPERCAT_URL, HYPERCAT_KEY, ENERGY, getEnergySeries)
    L = [ (x) for x in L if "MeterReader" in x[0] and x[1] and x[1]!= 0 ] # Keep only Meter Readers with valid values
    L.sort(key = lambda x : x[1], reverse=True)    # Sort on Energy, highest first
    L = [ (x[0].split("home/")[1].split("/")[0], "%0.2f" % x[1]) for x in L ] # Pluck just the ARM Home number from the long HREF string, and round kWh to 2 decimal places
    return L    
    
if __name__ == '__main__':
    gL = getLeaderboard()
    print json.dumps(gL, indent=4, separators=(',', ': '))
