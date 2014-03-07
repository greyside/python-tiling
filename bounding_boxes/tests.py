#Python imports
from decimal import Decimal
import math
from unittest import TestCase

from . import BoxGen

class BaseTestCase(TestCase):
    def setUp(self):
        num_class = self.box_gen.num_class
        
        self.rochester = (num_class('43.1553'), num_class('-77.6090'),)
        self.zerozero  = (num_class('0'), num_class('0'),)
        self.london    = (num_class('51.5171'), num_class('-0.1062'),)
        self.northpole = (num_class('0'), num_class('90'),)
        
        self.precision = num_class('0.0000001')
    
    def assertCloseEnough(self, val1, val2):
        # we actually tend to get equal numbers when using floats, but slightly different decimals
        self.assertLess(abs(val1-val2), self.precision, msg='%s and %s are not close.' % (val1, val2,))
    
    def assertBoxesTouch(self, boxes):
        # geo-order should be:
        # 7-6-8
        # 1-0-2
        # 4-3-5
        
        self.assertCloseEnough(boxes[0][0], boxes[3][2])
        self.assertCloseEnough(boxes[0][1], boxes[1][3])
        self.assertCloseEnough(boxes[0][2], boxes[6][0])
        self.assertCloseEnough(boxes[0][3], boxes[2][1])

class BaseMethods(object):
    def test__offset__returns_same_vals(self):
        lat, lon = self.rochester
        
        new_lat, new_lon = self.box_gen.offset(lat, lon)
        
        self.assertEqual(lat, new_lat)
        self.assertEqual(lon, new_lon)
    
    def test__offset__returns_incremented_vals(self):
        lat, lon = self.rochester
        
        new_lat, new_lon = self.box_gen.offset(lat, lon, lat_mi_offset=1, lon_mi_offset=1)
        
        self.assertLess(lat, new_lat)
        self.assertLess(lon, new_lon)
    
    def test__offset__returns_decremented_vals(self):
        lat, lon = self.rochester
        
        new_lat, new_lon = self.box_gen.offset(lat, lon, lat_mi_offset=-1, lon_mi_offset=-1)
        
        self.assertGreater(lat, new_lat)
        self.assertGreater(lon, new_lon)
    
    def test__offset_pairs_num__same_length_as_original_func__rochester(self):
        lat, lon = self.rochester
        search_box_radius = 5
        max_box_radius = 2
        
        num = self.box_gen.offset_pairs_num(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.offset_coor_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__rochester__high_search_box_radius(self):
        lat, lon = self.rochester
        search_box_radius = 7
        max_box_radius = 2
        
        num = self.box_gen.offset_pairs_num(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.offset_coor_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__origin__high_search_box_radius(self):
        lat, lon = self.zerozero
        search_box_radius = 7
        max_box_radius = 2
        
        num = self.box_gen.offset_pairs_num(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.offset_coor_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__north_pole__high_search_box_radius(self):
        lat, lon = self.northpole
        search_box_radius = 7
        max_box_radius = 2
        
        num = self.box_gen.offset_pairs_num(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.offset_coor_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__london(self):
        lat, lon = self.london
        search_box_radius = 15
        max_box_radius = 2
        
        num = self.box_gen.offset_pairs_num(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.offset_coor_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__offset_boxes__borders_touch__rochester(self):
        lat, lon = self.rochester
        search_box_radius = 7
        max_box_radius = 2
        
        boxes = self.box_gen.offset_boxes(lat, lon, search_box_radius, max_box_radius)
        
        self.assertBoxesTouch(boxes)
    
    def test__offset_boxes__borders_touch__london(self):
        lat, lon = self.london
        search_box_radius = 7
        max_box_radius = 2
        
        boxes = self.box_gen.offset_boxes(lat, lon, search_box_radius, max_box_radius)
        
        self.assertBoxesTouch(boxes)
    
    def test__offset_boxes__borders_touch__northpole(self):
        lat, lon = self.northpole
        search_box_radius = 7
        max_box_radius = 2
        
        boxes = self.box_gen.offset_boxes(lat, lon, search_box_radius, max_box_radius)
        
        self.assertBoxesTouch(boxes)
    
    def test__offset_boxes__borders_touch__zerozero(self):
        lat, lon = self.zerozero
        search_box_radius = 7
        max_box_radius = 2
        
        boxes = self.box_gen.offset_boxes(lat, lon, search_box_radius, max_box_radius)
        
        self.assertBoxesTouch(boxes)

class DecimalTestCase(BaseTestCase, BaseMethods):
    def setUp(self):
        self.box_gen = BoxGen()
        
        super(DecimalTestCase, self).setUp()

class FloatTestCase(BaseTestCase, BaseMethods):
    def setUp(self):
        self.box_gen = BoxGen(num_class=float, math_module=math, quantize=False)
        
        super(FloatTestCase, self).setUp()

