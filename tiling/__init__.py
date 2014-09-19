from __future__ import division

#Python imports
import itertools
import logging
import math

VERSION = (0, 1, 0)

__version__ = "".join([".".join(map(str, VERSION[0:3])), "".join(VERSION[3:])])

#TODO: make sure to handle 0, 180, and -180 degrees

class Tiler(object):
    def __init__(self, geo_helper, max_tile_wh):
        """
        max_tile_wh - the max width/height of a tile
        """
        self.geo_helper = geo_helper
        
        self.max_tile_wh = self.geo_helper.num_class(max_tile_wh)
        # the max_box_radius is half the height of the tile
        self.max_tile_radius = self.max_tile_wh / 2
    
    def get_box_centerpoint_for_coordinates(self, lat, lon):
        """
        Normalizes a location to the nearest tile center point.
        """
        tile_radius = self.max_tile_radius
        geo_helper = self.geo_helper
        floor = geo_helper.floor
        half = geo_helper.half
        _range_partial = geo_helper._range_partial
        
        lat_width = geo_helper.offset_lat(2 * tile_radius)
        
        lat_offset = floor(lat/lat_width) + half
        
        lat = geo_helper.fix_lat(lat_offset * lat_width)
        
        lon_width = 2 * tile_radius / (geo_helper.cos(lat * geo_helper.RAD) * _range_partial)
        
        lon_offset = floor(lon/lon_width) + half
        
        lon = geo_helper.fix_lon(lon_offset * lon_width)
        
        return lat, lon
    
    def offset_coor_pairs(self, latitude, longitude, height, width):
        # we normalize lat, lon here before calcing offsets, and then we normalize
        # the lat, lon offset pairs later. Just doing it on the pairs should work,
        # but at certain extreme coors tiny differences emerge that cause an offset
        # to get nromalized to the wrong tile.
        max_tile_radius = self.max_tile_radius
        max_tile_wh = self.max_tile_wh
        
        latitude, longitude = self.get_box_centerpoint_for_coordinates(latitude, longitude)
        
        height_offsets = set()
        width_offsets = set()
        
        tmp_height_offset = 0
        tmp_width_offset = 0
        
        # since the offsets represent tile center points, the boxes generated
        # from those points will include an area up to max_tile_radius away.
        height_offset_needed = (height / 2) - max_tile_radius
        width_offset_needed = (width / 2) - max_tile_radius
        
        while True:
            height_offsets.add(tmp_height_offset)
            height_offsets.add(-tmp_height_offset)
            
            if tmp_height_offset < height_offset_needed:
                tmp_height_offset += max_tile_wh
            else:
                break
        
        while True:
            width_offsets.add(tmp_width_offset)
            width_offsets.add(-tmp_width_offset)
            
            if tmp_width_offset < width_offset_needed:
                tmp_width_offset += max_tile_wh
            else:
                break
        
        height_offsets = sorted(height_offsets)
        width_offsets = sorted(width_offsets)
        
        offset_pairs = itertools.product(height_offsets, width_offsets)
        pairs = []
        
        offset = self.geo_helper.offset
        
        for lat_unit_offset, lon_unit_offset in offset_pairs:
            lat, lon = offset(latitude, longitude, lat_unit_offset, lon_unit_offset)
            
            # normalize coordinates. boxes north and south of center box will be slightly shifted
            # FIXME: this hack works in most cases, but there are instances where the boxes on diff latitudes will be too drastically shifted from the center box, especially as we get further from the center box, plus we may end up fetching more boxes than are really needed. A better solution would be to get the center box for each latitude needed, then work sideways from each of those, fetching east/west adjacent boxes as needed. This will also help avoid us fetching extra boxes in cases where the original search coords are near the edge of the center box, and adjacent boxes near the opposite edge aren't needed.
            lat, lon = self.get_box_centerpoint_for_coordinates(lat, lon)
            
            pairs.append((lat, lon,))
        
        return pairs
    
    def offset_pairs_num(self, latitude, longitude, height, width):
        max_tile_radius = self.max_tile_radius
        ceil = self.geo_helper.ceil
        # this function proceeds a little differently since it's not assembling a set
        # (0 and -0 only gets stored once)
        width_offset_needed = (width / 2) - max_tile_radius
        height_offset_needed = (height / 2) - max_tile_radius
        
        max_box_wh = max_tile_radius * 2
        
        num_boxes_wide = (2*ceil((width_offset_needed / max_box_wh)) + 1)
        num_boxes_high = (2*ceil((height_offset_needed / max_box_wh)) + 1)
        
        return num_boxes_wide * num_boxes_high
    
    def offset_boxes(self, latitude, longitude, height, width):
        max_tile_radius = self.max_tile_radius
        pairs = self.offset_coor_pairs(latitude, longitude, height, width)
        box_func = self.geo_helper.box
        
        boxes = []
        
        for pair_latitude, pair_longitude in pairs:
            box = box_func(pair_latitude, pair_longitude, max_tile_radius)
            boxes.append(box)
        
        return boxes

class GeoHelper(object):
    UNIT_MI = 'mi' # Miles
    UNIT_NM = 'nm' # Nautical Mile
    UNIT_KM = 'km' # Kilometers
    
    KM_PER_MI  = '1.609344'
    MI_PER_NM  = '1.150779'
    
    NM_PER_LAT = '60.00721'
    NM_PER_LON = '60.10793'
    
    
    #TODO: allow choice between mi/km in constructor
    def __init__(self,
          unit=UNIT_MI,
          num_class=float,
          math_module=math,
          
        ):
        self.num_class = num_class
        self.math_module = math_module
        
        self.half = num_class('0.5')
        
        self.ceil = math_module.ceil
        self.floor = math_module.floor
        self.cos = math_module.cos
        self.sin = math_module.sin
        self.pi = math_module.pi() if callable(math_module.pi) else math_module.pi
        
        self.RAD = self.pi / num_class('180.0')
        
        self.unit = unit
        
        self.MAX_LAT = num_class('90')
        self.MIN_LAT = num_class('-90')
        self.MAX_LON = num_class('180')
        self.MIN_LON = num_class('-180')
        
        self.KM_PER_MI  = num_class(self.KM_PER_MI)
        self.NM_PER_LAT = num_class(self.NM_PER_LAT)
        self.NM_PER_LON = num_class(self.NM_PER_LON)
        self.MI_PER_NM  = num_class(self.MI_PER_NM)
        self.KM_PER_NM  = self.MI_PER_NM * self.KM_PER_MI
        
        if unit == self.UNIT_MI:
            self.units_per_nm = self.MI_PER_NM
        elif unit == self.UNIT_KM:
            self.units_per_nm = self.KM_PER_NM
        else:
            # Default to nautical miles
            self.units_per_nm = num_class('1')
        
        # frequently used math fragment
        self._range_partial = self.units_per_nm * num_class('60.0')
    
    def tiler(self, max_tile_wh):
        """
        max_tile_wh - the max width/height of a tile
        """
        return Tiler(self, max_tile_wh)
    
    def fix_lat(self, val):
        if val > self.MAX_LAT:
            return self.MAX_LAT
        if val < self.MIN_LAT:
            return self.MIN_LAT
        return val
    
    def fix_lon(self, val):
        if val > self.MAX_LON:
            return self.MIN_LON + (val % self.MAX_LON)
        if val < self.MIN_LON:
            return self.MAX_LON + (val % self.MIN_LON)
        return val
    
    def distance(self, lat1, lon1, lat2, lon2):
        """
        Caclulate distance between two lat lons in units.
        """
        #WARNING: can't get a sufficiently accurate result, off by about a mile
        math = self.math_module
        sin = math.sin
        cos = math.cos
        asin = math.asin
        sqrt = math.sqrt
        pi = self.pi
        
        # from http://williams.best.vwh.net/avform.htm#Example
        lat1 = lat1*pi/180
        lon1 = abs(lon1*pi/180)
        lat2 = lat2*pi/180
        lon2 = abs(lon2*pi/180)
        
        d = 2*asin(sqrt((sin((lat1-lat2)/2))**2+cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2))**2))
        return (d*180*60/pi) * self.units_per_nm
    
    def offset_lat(self, unit_offset=0):
        lat_range = unit_offset / self._range_partial
        return lat_range
    
    def offset_lon(self, lat, unit_offset=0):
        lon_range = (unit_offset / self._range_partial) / (self.cos(lat * self.RAD))
        return lon_range
    
    def offset(self, lat, lon, lat_unit_offset=0, lon_unit_offset=0):
        lat_range = self.offset_lat(
            unit_offset=lat_unit_offset,
        )
        
        # move to new latitude before adjusting east/west position
        new_lat = self.fix_lat(lat + lat_range)
        
        lon_range = self.offset_lon(
            new_lat,
            unit_offset=lon_unit_offset
        )
        return new_lat, self.fix_lon(lon + lon_range)
    
    def rectangle(self, lat, lon, height, width):
        # NOTE: these "rectangles" will be wider at the bottom than the top if
        # north of the equator, or vice versa if south. It's a necessary evil,
        # since if they were the same width top and bottom there's be gaps and
        # overlap between rectangles.
        
        lat_range = self.offset_lat(
            unit_offset=height/2
        )
        
        lon_range = self.offset_lon(
            lat,
            unit_offset=width/2
        )
        
        ret = self.fix_lat(lat + lat_range), self.fix_lon(lon + lon_range), self.fix_lat(lat - lat_range), self.fix_lon(lon - lon_range)
        return ret
    
    def box(self, lat, lon, radius):
        """
        Returns two lat/lon pairs as (lat-south, lon-west, lat-north, lon-east)
        which define a box that surrounds a circle of radius of the given amount
        in the specified units.
        """
        l = radius * 2
        return self.rectangle(lat, lon, l, l)
    
    #TODO: could be useful for testing, turning center points to tiles and back
#    def tile_center_point(point_pairs):
#        #just averaging should be fine for now
#        length = len(point_pairs)
#        
#        lat = self.num_class('0.0')
#        lon = self.num_class('0.0')
#        
#        for pair in point_pairs:
#            lat += self.num_class(pair[0])
#            lon += self.num_class(pair[1])
#        
#        return lat/length, lon/length
    
    def filter_radius(self, iterable, latitude, longitude, radius, coor_func=None):
        """
        Filter out results not in a circular radius.
        """
        
        for item in iterable:
            p_lat, p_lon = item if not coor_func else coor_func(item)
            if self.distance(p_lat, p_lon, latitude, longitude) < radius:
                yield p_lat, p_lon
    
    def filter_rectangle(self, iterable, latitude, longitude, height, width, coor_func=None):
        """
        Filter out results not in a rectangle.
        """
        lat_north, lon_east, lat_south, lon_west = self.rectangle(latitude, longitude, height, width)
        
        for item in iterable:
            p_lat, p_lon = item if not coor_func else coor_func(item)
            #TODO: handle wrap around
            if lat_south <= p_lat <= lat_north and lon_west < p_lon < lon_east:
                yield p_lat, p_lon

