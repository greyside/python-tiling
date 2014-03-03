#Python imports
from decimal import Decimal
import dmath
import itertools
import logging

VERSION = (0, 1, 0)

__version__ = "".join([".".join(map(str, VERSION[0:3])), "".join(VERSION[3:])])

#TODO: make sure to handle wrap around 0 and 180 degrees

class BoxGen(object):
    # NM == Nautical Mile
    KM_PER_MILE  = '1.609344'
    NM_PER_LAT   = '60.00721'
    NM_PER_LONG  = '60.10793'
    MILES_PER_NM = '1.15078'
    
    
    def __init__(self,
          num_class=Decimal,
          math_module=dmath,
          coordinate_decimal_places=7,
          radius_decimal_places=3,
          quantize=True
        ):
        self.num_class = num_class
        self.math_module = math_module
        self.coordinate_decimal_places = coordinate_decimal_places
        self.radius_decimal_places = radius_decimal_places
        self.quantize = quantize
        
        self.half = num_class('0.5')
        
        self.coordinate_quantizer = num_class('0.1') ** self.coordinate_decimal_places
        self.radius_quantizer = num_class('0.1') ** self.radius_decimal_places
        
        self.ceil = math_module.ceil
        self.floor = math_module.floor
        self.cos = math_module.cos
        self.sin = math_module.sin
        self.pi = math_module.pi() if callable(math_module.pi) else math_module.pi
        
        self.RAD = self.pi / num_class('180.0')
        
        self.KM_PER_MILE  = num_class(self.KM_PER_MILE)
        self.NM_PER_LAT   = num_class(self.NM_PER_LAT)
        self.NM_PER_LONG  = num_class(self.NM_PER_LONG)
        self.MILES_PER_NM = num_class(self.MILES_PER_NM)
        
        #frequently used math fragment
        self._rangePartial = self.MILES_PER_NM * num_class('60.0')
    
    def get_box_centerpoint_for_coordinates(self, lat, lon, box_radius):
        floor = self.floor
        half = self.half
        coordinate_quantizer = self.coordinate_quantizer
        _rangePartial = self._rangePartial
        
        latWidth = 2 * box_radius / _rangePartial
        
        lat = (floor(lat/latWidth) + half) * latWidth
        
        lonWidth = 2 * box_radius / (self.cos(lat * self.RAD) * _rangePartial)
        
        lon = (floor(lon/lonWidth) + half) * lonWidth
        
        
        if self.quantize:
            lat = lat.quantize(coordinate_quantizer)
            lon = lon.quantize(coordinate_quantizer)
        
        return lat, lon
    
    def calc_distance(self, lat1, lon1, lat2, lon2):
        """
        Caclulate distance between two lat lons in NM
        """
        cos = self.cos
        RAD = self.RAD
        
        yDistance = (lat2 - lat1) * self.NM_PER_LAT
        xDistance = (cos(lat1 * RAD) + cos(lat2 * RAD)) * (lon2 - lon1) * (self.NM_PER_LONG / 2)
        
        distance = (xDistance**2 + yDistance**2).sqrt()
        
        return distance * self.MILES_PER_NM
    
    def calc_miles_box(self, lat, lon, radius):
        """
        Returns two lat/lon pairs as (lat1, lon2, lat2, lon2) which define a box that
        surrounds a circle of radius of the given amount in miles.
        """
        _rangePartial = self._rangePartial
        
        latRange = radius / _rangePartial
        lonRange = radius / (self.cos(lat * self.RAD) * _rangePartial)
        
        return (lat - latRange, lon - lonRange, lat + latRange, lon + lonRange,)
    
    def calc_offset(self, lat, lon, lat_mi_offset=0, lon_mi_offset=0):
        _rangePartial = self._rangePartial
        
        latRange = lat_mi_offset / _rangePartial
        lonRange = lon_mi_offset / (self.cos(lat * self.RAD) * _rangePartial)
        
        return lat + latRange, lon + lonRange
    
    #TODO: could be useful for testing, turning center points to bounding boxes and back
#    def calc_bounding_box_center_point(point_pairs):
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
    
    def calc_coor_offset_pairs(self, latitude, longitude, search_box_radius, max_box_radius):
        offsets = set()
        tmp_offset = 0
        
        while tmp_offset < search_box_radius:
            offsets.add(tmp_offset)
            offsets.add(-tmp_offset)
            tmp_offset += max_box_radius * 2
        
        offset_pairs = itertools.product(offsets, repeat=2)
        pairs = []
        
        calc_offset = self.calc_offset
        coordinate_quantizer = self.coordinate_quantizer
        quantize = self.quantize
        
        for lat_mi_offset, lon_mi_offset in offset_pairs:
            lat, lon = calc_offset(latitude, longitude, lat_mi_offset, lon_mi_offset)
            
            if quantize:
                lat = lat.quantize(coordinate_quantizer)
                lon = lon.quantize(coordinate_quantizer)
            
            pairs.append((lat, lon,))
        
        return pairs
    
    def calc_num_offset_pairs(self, latitude, longitude, search_box_radius, max_box_radius):
        # this function proceeds a little differently since it's not assembling a set
        # (0 and -0 only gets stored once)
        num = (2 * self.ceil(self.num_class(search_box_radius) / (2 * self.num_class(max_box_radius)))) - 1
        return num**2

