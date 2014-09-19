#Python imports
from decimal import Decimal
import math
from unittest import TestCase

try:
    import dmath
except ImportError:
    dmath = None

from . import GeoHelper

class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        num_class = cls.num_class
        cls.geo_helper = GeoHelper(num_class=num_class, math_module=cls.math_module)
        cls.tiler_4 = cls.geo_helper.tiler('4')
        cls.tiler_6 = cls.geo_helper.tiler('6')
        cls.tiler_8 = cls.geo_helper.tiler('8')
    
    def setUp(self):
        self.tiler = None
        
        num_class = self.num_class
        
        #TODO: handle international date line
        self.locations = {
            'rochester': (num_class('43.1553'), num_class('-77.6090'),),
            'london'   : (num_class('51.5171'), num_class('-0.1062'),),
            '1-1' : (num_class('1'), num_class('1'),),
            '10-10' : (num_class('10'), num_class('10'),),
             
            'equator'  : (num_class('0'), num_class('90'),),
            '0-0' : (num_class('0'), num_class('0'),),#also on the equator
            '0-1' : (num_class('0'), num_class('1'),),
#            'intldateline'  : (num_class('180'), num_class('0'),),
#            'intldateline2'  : (num_class('-180'), num_class('0'),),
#            'nearnorthpole': (num_class('89.9999'), num_class('0'),),
#            'nearsouthpole': (num_class('-89.9999'), num_class('0'),),
#            'northpole': (num_class('90'), num_class('0'),),
#            'southpole': (num_class('-90'), num_class('0'),),
        }
        
        self.precision = num_class('0.000001')
    
    def assertCloseEnough(self, val1, val2, lat=None, precision=None):
        try:
            self.assertEqual(val1, val2)
        except AssertionError:
            # give a rough estimate of the magnitude of the difference
            if lat is not None:
                dist = self.geo_helper.distance(lat, val1, lat, val2)
            else:
                dist = self.geo_helper.distance(val1, 0, val2, 0)
            
            self.assertLess(abs(val1-val2), precision or self.precision, msg='%r and %r are not close enough. About %s %s apart (lat: %s).' % (val1, val2, dist, self.geo_helper.unit, lat,))
    
    def assertBoxesTouch(self, boxes, nwidth, nheight):
        box_len = len(boxes)
        
        self.assertEqual(box_len, nwidth * nheight)
        # geo-order should be:
        # 6-7-8
        # 3-4-5
        # 0-1-2
        
        max_row_pos = nwidth - 1
        
#        for i, box in enumerate(boxes):
#            print i, i % nwidth, box      
        for i, box in enumerate(boxes):
            
            n_idx = i+nwidth
            e_idx = i+1
            s_idx = i-nwidth
            w_idx = i-1
            
            row_pos = i % nwidth
            
            if n_idx < box_len:
                self.assertCloseEnough(box[0], boxes[n_idx][2])
            if not row_pos == max_row_pos:
                self.assertCloseEnough(box[1], boxes[e_idx][3], lat=box[0])
            if s_idx > nwidth:
                self.assertCloseEnough(box[2], boxes[s_idx][0])
            if not row_pos == 0:
                self.assertCloseEnough(box[3], boxes[w_idx][1], lat=box[0])

class BaseMethods(object):
    def test__fix_lat__not_needed(self):
        self.tiler = self.tiler_4
        
        val = self.num_class('33.95')
        
        ret = self.geo_helper.fix_lat(val)
        
        self.assertEqual(ret, val)
    
    def test__fix_lat__too_big(self):
        self.tiler = self.tiler_4
        
        val = self.num_class('90.0001')
        
        ret = self.geo_helper.fix_lat(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.geo_helper.MAX_LAT)
    
    def test__fix_lat__too_small(self):
        self.tiler = self.tiler_4
        
        val = self.num_class('-90.0001')
        
        ret = self.geo_helper.fix_lat(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.geo_helper.MIN_LAT)
    
    def test__fix_lon__not_needed(self):
        self.tiler = self.tiler_4
        
        val = self.num_class('40.6333')
        
        ret = self.geo_helper.fix_lon(val)
        
        self.assertEqual(ret, val)
    
    def test__fix_lon__too_big(self):
        self.tiler = self.tiler_4
        
        val = self.num_class('180.0001')
        
        ret = self.geo_helper.fix_lon(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.num_class('-179.9999'))
    
    def test__fix_lon__too_small(self):
        self.tiler = self.tiler_4
        
        val = self.num_class('-180.0001')
        
        ret = self.geo_helper.fix_lon(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.num_class('179.9999'))
    
    def test__distance__lax_to_jfk(self):
        self.tiler = self.tiler_4
        
        # from http://williams.best.vwh.net/avform.htm#Example
        lax = self.num_class('33.95'), self.num_class('-118.4')
        jfk = self.num_class('40.6333'), self.num_class('-73.7833')
        
        d1 = self.geo_helper.distance(lax[0], lax[1], jfk[0], jfk[1])
        d2 = self.geo_helper.distance(jfk[0], jfk[1], lax[0], lax[1])
        
        self.assertCloseEnough(d1, self.num_class('2467.270176'), precision=1)
        self.assertEqual(d1, d2)
    
    def test__get_box_centerpoint_for_coordinates__zerozero(self):
        self.tiler = self.tiler_6
        
        lat, lon = self.locations['0-0']
        
        pair = self.tiler.get_box_centerpoint_for_coordinates(lat, lon)
        
        self.assertCloseEnough(pair[0], self.num_class('0.0434488290106'))
        self.assertCloseEnough(pair[1], self.num_class('0.0434488415034'))
    
    def test__get_box_centerpoint_for_coordinates__near_zerozero(self):
        self.tiler = self.tiler_6
        
        lat, lon = (self.num_class('-0.087'), self.num_class('-0.087'))
        
        pair = self.tiler.get_box_centerpoint_for_coordinates(lat, lon)
        
        self.assertCloseEnough(pair[0], self.num_class('-0.0434488290106')*3)
        self.assertCloseEnough(pair[1], self.num_class('-0.0434488415034')*3)
    
    def test__offset__returns_same_vals(self):
        self.tiler = self.tiler_4
        
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.geo_helper.offset(lat, lon)
        
        self.assertEqual(lat, new_lat)
        self.assertEqual(lon, new_lon)
    
    def test__offset__returns_incremented_vals(self):
        self.tiler = self.tiler_4
        
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.geo_helper.offset(lat, lon, lat_unit_offset=1, lon_unit_offset=1)
        
        self.assertLess(lat, new_lat)
        self.assertLess(lon, new_lon)
    
    def test__offset__returns_decremented_vals(self):
        self.tiler = self.tiler_4
        
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.geo_helper.offset(lat, lon, lat_unit_offset=-1, lon_unit_offset=-1)
        
        self.assertGreater(lat, new_lat)
        self.assertGreater(lon, new_lon)
    
    def test__offset__multiple_transforms(self):
        self.tiler = self.tiler_4
        
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.geo_helper.offset(lat, lon, lat_unit_offset=-3, lon_unit_offset=-3)
        
        new_lat2, new_lon2 = self.geo_helper.offset(new_lat, new_lon, lat_unit_offset=3, lon_unit_offset=3)
        
        self.assertCloseEnough(lat, new_lat2, precision=self.num_class('0.0001'))
        self.assertCloseEnough(lon, new_lon2, precision=self.num_class('0.0001'), lat=lat)
    
    def test__offset_pairs_num__same_length_as_original_func(self):
        self.tiler = self.tiler_4
        
        search_box_radius = self.num_class(5)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width,)
            
            num = self.tiler.offset_pairs_num(*args)
            pairs = self.tiler.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__equal_search_and_box_size(self):
        self.tiler = self.tiler_4
        
        search_box_radius = self.num_class(4)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width,)
            
            num = self.tiler.offset_pairs_num(*args)
            pairs = self.tiler.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__box_size_is_divisor_of_search(self):
        self.tiler = self.tiler_4
        
        search_box_radius = self.num_class(4)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width,)
            
            num = self.tiler.offset_pairs_num(*args)
            pairs = self.tiler.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__search_smaller_than_box_size(self):
        self.tiler = self.tiler_4
        
        search_box_radius = self.num_class(3)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width,)
            
            num = self.tiler.offset_pairs_num(*args)
            pairs = self.tiler.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__bigger_search_box_radius(self):
        self.tiler = self.tiler_4
        
        search_box_radius = self.num_class(7)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width,)
            
            num = self.tiler.offset_pairs_num(*args)
            pairs = self.tiler.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_boxes__nearby_centerpoints_reuse_boxes__rochester(self):
        self.tiler = self.tiler_6
        
        search_box_radius = self.num_class(7)
        
        width = height = search_box_radius * 2
        
        lat1, lon1 = self.locations['rochester']
        
        # 6 miles north, 6 miles east
        lat2, lon2 = self.geo_helper.offset(lat1, lon1, lat_unit_offset=6, lon_unit_offset=6)
        
        boxes1 = self.tiler.offset_boxes(lat1, lon1, height, width,)
        boxes2 = self.tiler.offset_boxes(lat2, lon2, height, width,)
        
        self.assertEqual(boxes1[8], boxes2[4])
        self.assertEqual(boxes1[7], boxes2[3])
        self.assertEqual(boxes1[5], boxes2[1])
        self.assertEqual(boxes1[4], boxes2[0])
    
    def test__offset_boxes__borders_touch(self):
        self.tiler = self.tiler_4
        
        search_box_radius = self.num_class(7)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            boxes = self.tiler.offset_boxes(coors[0], coors[1], height, width)
            
            self.assertBoxesTouch(boxes, 5, 5)
    
    def test__offset_boxes__borders_touch__fewer_boxes(self):
        self.tiler = self.tiler_6
        
        search_box_radius = self.num_class(7)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            boxes = self.tiler.offset_boxes(coors[0], coors[1], height, width)
            
            self.assertBoxesTouch(boxes, 3, 3)
    
    def test__offset_boxes__borders_touch__rectangle(self):
        self.tiler = self.tiler_4
        
        height = self.num_class(13)
        width = self.num_class(5)
        
        for location_name, coors in self.locations.items():
            boxes = self.tiler.offset_boxes(coors[0], coors[1], height, width,)
            
            self.assertBoxesTouch(boxes, 3, 5)

if dmath:
    class DecimalTestCase(BaseTestCase, BaseMethods):
        num_class = Decimal
        math_module = dmath

class FloatTestCase(BaseTestCase, BaseMethods):
    num_class = float
    math_module = math

