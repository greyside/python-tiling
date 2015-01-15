=============
python-tiling
=============

.. image:: https://travis-ci.org/greyside/python-tiling.svg?branch=master
    :target: https://travis-ci.org/greyside/python-tiling
.. image:: https://coveralls.io/repos/greyside/python-tiling/badge.png?branch=master
    :target: https://coveralls.io/r/greyside/python-tiling?branch=master

Generates a set of adjacent tiles, which can be used for organizing DB results in a cache.

-----
Usage
-----

::

    from tiling import GeoHelper
    
    geo_helper = GeoHelper()
    
    # get coordinates 1 mile north and 1 mile east of the passed in coordinates.
    new_lat, new_lon = geo_helper.offset(43, -77, lat_unit_offset=1, lon_unit_offset=1)
    
    # get a Tiler instance that generates tiles 3 miles wide and 3 miles high.
    tiler = geo_helper.tiler(3)
    
    # get tiles for the 5mi X 6mi box around the provided coordinates
    # boxes is a list of tuples, each tuple has 4 elements:
    # (north_latitude, east_longitude, south_latitude, west_longitude,).
    # The list is ordered west to east, north to south.
    boxes = tiler.offset_boxes(43, -77, 5, 6)
    
    
    # other examples
    metric_geo_helper = GeoHelper(unit=GeoHelper.UNIT_KM)
    
    from decimal import Deci*mal
    import dmath
    
    decimal_geo_helper = GeoHelper(num_class=Decimal, math_module=dmath)

----------------
Example Use Case
----------------

::

    # Let's say you have 2 users request a list of stores in a 5 mile radius of their location.
    # user 1 is at 43, -77, user 2 is at 43.01, -77.01
    
    geo_helper = GeoHelper()
    
    # use whatever tile size you want, here we use 2mi X 2mi
    tiler = geo_helper.tiler(2)
    
    # 5mi radius = 10mi high and 10mi wide
    boxes1 = tiler.offset_boxes(43, -77, 10, 10)
    
    # you can use boxes1 to construct cache keys and pull your results from a
    # cache instead of the database. Then when user 2's request is served:
    boxes2 = tiler.offset_boxes(43.01, -77.01, 10, 10)
    
    # even though the 2 users are at different coordinates, because they're
    # really close, boxes2 will be the same tiles as boxes1, so you can reuse
    # the same set of cached data for any nearby coordinates.

----------
Copyrights
----------

This software was orginally written for my client Mark Smillie, who has given me, Seán Hayes, permission to open source it under a BSD license. I continued development on it while working for another client, Sudo, Inc.

* Mark Smillie [https://twitter.com/msmillie] - Orignal Owner
* Seán Hayes [http://seanhayes.name/] - Author, Maintainer
* Sudo, Inc. [http://gosudo.com/] - Contributor

---------------------
Notes/Further Reading
---------------------

* http://williams.best.vwh.net/avform.htm
* http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates

Right now we calc boxes the "wrong way", though it's compensated for in other ways. It might be nice to eventually offer other ways to split up the earth's surface.

* https://github.com/GoogleCloudPlatform/appengine-24hrsinsf-python/blob/master/geobox.py

