from __future__ import division

#Python imports
from decimal import Decimal
import itertools
import logging

try:
    import dmath
except ImportError:
    dmath = None

VERSION = (0, 1, 0)

__version__ = "".join([".".join(map(str, VERSION[0:3])), "".join(VERSION[3:])])

#TODO: make sure to handle wrap around 0 and 180 degrees

class BoxGen(object):
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
          num_class=Decimal,
          math_module=dmath,
          coordinate_decimal_places=7,
          radius_decimal_places=3
        ):
        self.num_class = num_class
        self.math_module = math_module
        self.coordinate_decimal_places = coordinate_decimal_places
        self.radius_decimal_places = radius_decimal_places
        
        self.half = num_class('0.5')
        
        self.ceil = math_module.ceil
        self.floor = math_module.floor
        self.cos = math_module.cos
        self.sin = math_module.sin
        self.pi = math_module.pi() if callable(math_module.pi) else math_module.pi
        
        self.RAD = self.pi / num_class('180.0')
        
        self.unit = unit
        
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
    
    def get_box_centerpoint_for_coordinates(self, lat, lon, box_radius):
        """
        Normalizes a location to the nearest bounding box center point.
        """
        floor = self.floor
        half = self.half
        _range_partial = self._range_partial
        
        lat_width = self.offset_lat(2 * box_radius)
        
        lat = (floor(lat/lat_width) + half) * lat_width
        
        lon_width = 2 * box_radius / (self.cos(lat * self.RAD) * _range_partial)
        
        lon = (floor(lon/lon_width) + half) * lon_width
        
        return lat, lon
    
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
        new_lat = lat + lat_range
        
        lon_range = self.offset_lon(
            new_lat,
            unit_offset=lon_unit_offset
        )
        return new_lat, lon + lon_range
    
    def units_rectangle(self, lat, lon, width, height):
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
        
        return lat + lat_range, lon + lon_range, lat - lat_range, lon - lon_range
    
    def units_box(self, lat, lon, radius):
        """
        Returns two lat/lon pairs as (lat-south, lon-west, lat-north, lon-east)
        which define a box that surrounds a circle of radius of the given amount
        in the specified units.
        """
        l = radius * 2
        return self.units_rectangle(lat, lon, l, l)
    
    #TODO: could be useful for testing, turning center points to bounding boxes and back
#    def bounding_box_center_point(point_pairs):
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
    
    def offset_coor_pairs(self, latitude, longitude, width, height, max_box_radius):
        """
        max_box_radius - the max size of a bounding box
        """
        #FIXME: points north and south of this lat and lon are not normalized
        width_offsets = set()
        height_offsets = set()
        
        # the max_box_radius is actually half the height of the box, hence *2
        max_box_wh = max_box_radius * 2
        
        tmp_width_offset = 0
        tmp_height_offset = 0
        
        # since the offsets represent bounding box center points, the boxes generated
        # form those points will include an area up to max_box_radius away.
        width_offset_needed = (width / 2) - max_box_radius
        height_offset_needed = (height / 2) - max_box_radius
        
        while True:
            width_offsets.add(tmp_width_offset)
            width_offsets.add(-tmp_width_offset)
            
            if tmp_width_offset < width_offset_needed:
                tmp_width_offset += max_box_wh
            else:
                break
        
        while True:
            height_offsets.add(tmp_height_offset)
            height_offsets.add(-tmp_height_offset)
            
            if tmp_height_offset < height_offset_needed:
                tmp_height_offset += max_box_wh
            else:
                break
        
        offset_pairs = itertools.product(sorted(width_offsets), sorted(height_offsets))
        pairs = []
        
        offset = self.offset
        
        for lat_unit_offset, lon_unit_offset in offset_pairs:
            
            lat, lon = offset(latitude, longitude, lat_unit_offset, lon_unit_offset)
            
            # normalize coordinates. boxes north and south of center box will be slightly shifted
            # FIXME: this hack works in most cases, but there are instances where the boxes on diff latitudes will be too drastically shifted from the center box, especially as we get further from the center box, plus we may end up fetching more boxes than are really needed. A better solution would be to get the center box for each latitude needed, then work sideways from each of those, fetching east/west adjacent boxes as needed. This will also help avoid us fetching extra boxes in cases where the original search coords are near the edge of the center box, and adjacent boxes near the opposite edge aren't needed.
            lat, lon = self.get_box_centerpoint_for_coordinates(lat, lon, max_box_radius)
            
            pairs.append((lat, lon,))
        
        return pairs
    
    def offset_pairs_num(self, latitude, longitude, width, height, max_box_radius):
        # this function proceeds a little differently since it's not assembling a set
        # (0 and -0 only gets stored once)
        width_offset_needed = (width / 2) - max_box_radius
        height_offset_needed = (height / 2) - max_box_radius
        
        max_box_wh = max_box_radius * 2
        
        num_boxes_wide = (2*self.ceil((width_offset_needed / max_box_wh)) + 1)
        num_boxes_high = (2*self.ceil((height_offset_needed / max_box_wh)) + 1)
        
        return num_boxes_wide * num_boxes_high
    
    def offset_boxes(self, latitude, longitude, width, height, max_box_radius):
        pairs = self.offset_coor_pairs(latitude, longitude, width, height, max_box_radius)
        
        boxes = []
        
        for pair_latitude, pair_longitude in pairs:
            box = self.units_box(pair_latitude, pair_longitude, max_box_radius)
            boxes.append(box)
        
        return boxes
    
    def filter_radius(self, iterable, latitude, longitude, radius, coor_func=None):
        """
        Filter out results not in a circular radius.
        """
        
        for item in iterable:
            p_lat, p_lon = item if not coor_func else coor_func(item)
            if self.distance(p_lat, p_lon, latitude, longitude) < radius:
                yield p_lat, p_lon
    
    def filter_rectangle(self, iterable, latitude, longitude, width, height, coor_func=None):
        """
        Filter out results not in a rectangle.
        """
        lat_north, lon_east, lat_south, lon_west = self.units_rectangle(latitude, longitude, width, height)
        
        for item in iterable:
            p_lat, p_lon = item if not coor_func else coor_func(item)
            #TODO: handle wrap around
            if lat_south <= p_lat <= lat_north and lon_west < p_lon < lon_east:
                yield p_lat, p_lon

