Usage
=====
Enables clients to easily manipulate catalogues on remote instances of 1248's Pathfinder HyperCat server.

Uses hypercat.py library.

NOTE: This uses urllib2, because it has to run both in GAE and also in raw Python setups, but urllib2 doesn't check HTTPS certificates!

Example
===
Create a catalogue then read it back.

    p = Catalogue("https://dev.1248.io:8002/cats/1248cat", "SECRETKEY")
    h1 = hypercat.hypercat("Dummy test catalogue")
    p.create(h1)

    h2 = p.get()

    assert h1.asJSON() == h2.asJSON()
