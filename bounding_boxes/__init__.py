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
        
        lat_width = 2 * box_radius / _range_partial
        
        lat = (floor(lat/lat_width) + half) * lat_width
        
        lon_width = 2 * box_radius / (self.cos(lat * self.RAD) * _range_partial)
        
        lon = (floor(lon/lon_width) + half) * lon_width
        
        return lat, lon
    
    def distance(self, lat1, lon1, lat2, lon2):
        """
        Caclulate distance between two lat lons in units.
        """
        cos = self.cos
        RAD = self.RAD
        
        yDistance = (lat2 - lat1) * self.NM_PER_LAT
        xDistance = (cos(lat1 * RAD) + cos(lat2 * RAD)) * (lon2 - lon1) * (self.NM_PER_LON / 2)
        
        distance = (xDistance**2 + yDistance**2).sqrt()
        
        return distance * self.units_per_nm
    
    def units_rectangle(self, lat, lon, width, height):
        _range_partial = self._range_partial
        
        latRange = height / _range_partial
        #FIXME: this likely has gaps and/or overlaps. A more accurate method might involve unit offsets from (0, 0)
        lonRange = width / (self.cos(lat * self.RAD) * _range_partial)
        
        return (lat - latRange, lon - lonRange, lat + latRange, lon + lonRange,)
    
    def units_box(self, lat, lon, radius):
        """
        Returns two lat/lon pairs as (lat-south, lon-west, lat-north, lon-east)
        which define a box that surrounds a circle of radius of the given amount
        in the specified units.
        """
        return self.units_rectangle(lat, lon, radius, radius)
    
    def offset(self, lat, lon, lat_mi_offset=0, lon_mi_offset=0):
        _range_partial = self._range_partial
        
        latRange = lat_mi_offset / _range_partial
        lonRange = lon_mi_offset / (self.cos(lat * self.RAD) * _range_partial)
        
        return lat + latRange, lon + lonRange
    
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
    
    def offset_coor_pairs(self, latitude, longitude, search_box_radius, max_box_radius):
        """
        search_box_radius - the total radius to be searched
        max_box_radius - the max size of a bounding box
        """
        offsets = set()
        tmp_offset = 0
        
        while tmp_offset < search_box_radius:
            offsets.add(tmp_offset)
            offsets.add(-tmp_offset)
            # the max_box_radius is actually half the width of the box, hence *2
            tmp_offset += max_box_radius * 2
        
        offset_pairs = itertools.product(offsets, repeat=2)
        pairs = []
        
        offset = self.offset
        
        for lat_unit_offset, lon_unit_offset in offset_pairs:
            lat, lon = offset(latitude, longitude, lat_unit_offset, lon_unit_offset)
            
            pairs.append((lat, lon,))
        
        return pairs
    
    def offset_pairs_num(self, latitude, longitude, search_box_radius, max_box_radius):
        # this function proceeds a little differently since it's not assembling a set
        # (0 and -0 only gets stored once)
        num = (2 * self.ceil(self.num_class(search_box_radius) / (2 * self.num_class(max_box_radius)))) - 1
        return num**2
    
    def offset_boxes(self, latitude, longitude, search_box_radius, max_box_radius):
        pairs = self.offset_coor_pairs(latitude, longitude, search_box_radius, max_box_radius)
        
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
        lat_south, lon_west, lat_north, lon_east = self.units_rectangle(latitude, longitude, width, height)
        
        for item in iterable:
            p_lat, p_lon = item if not coor_func else coor_func(item)
            #TODO: handle wrap around
            if lat_south <= p_lat <= lat_north and lon_west < p_lon < lon_east:
                yield p_lat, p_lon

