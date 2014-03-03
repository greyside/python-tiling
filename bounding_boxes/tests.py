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

class BaseMethods(object):
    def test__calc_offset__returns_same_vals(self):
        lat, lon = self.rochester
        
        new_lat, new_lon = self.box_gen.calc_offset(lat, lon)
        
        self.assertEqual(lat, new_lat)
        self.assertEqual(lon, new_lon)
    
    def test__calc_offset__returns_incremented_vals(self):
        lat, lon = self.rochester
        
        new_lat, new_lon = self.box_gen.calc_offset(lat, lon, lat_mi_offset=1, lon_mi_offset=1)
        
        self.assertLess(lat, new_lat)
        self.assertLess(lon, new_lon)
    
    def test__calc_offset__returns_decremented_vals(self):
        lat, lon = self.rochester
        
        new_lat, new_lon = self.box_gen.calc_offset(lat, lon, lat_mi_offset=-1, lon_mi_offset=-1)
        
        self.assertGreater(lat, new_lat)
        self.assertGreater(lon, new_lon)
    
    def test__calc_num_offset_pairs__same_length_as_original_func__rochester(self):
        lat, lon = self.rochester
        search_box_radius = 5
        max_box_radius = 2
        
        num = self.box_gen.calc_num_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.calc_coor_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__calc_num_offset_pairs__same_length_as_original_func__rochester__high_search_box_radius(self):
        lat, lon = self.rochester
        search_box_radius = 7
        max_box_radius = 2
        
        num = self.box_gen.calc_num_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.calc_coor_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__calc_num_offset_pairs__same_length_as_original_func__origin__high_search_box_radius(self):
        lat, lon = self.zerozero
        search_box_radius = 7
        max_box_radius = 2
        
        num = self.box_gen.calc_num_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.calc_coor_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__calc_num_offset_pairs__same_length_as_original_func__north_pole__high_search_box_radius(self):
        lat, lon = self.northpole
        search_box_radius = 7
        max_box_radius = 2
        
        num = self.box_gen.calc_num_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.calc_coor_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))
    
    def test__calc_num_offset_pairs__same_length_as_original_func__london(self):
        lat, lon = self.london
        search_box_radius = 15
        max_box_radius = 2
        
        num = self.box_gen.calc_num_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        pairs = self.box_gen.calc_coor_offset_pairs(lat, lon, search_box_radius, max_box_radius)
        
        self.assertEqual(num, len(pairs))

class DecimalTestCase(BaseTestCase, BaseMethods):
    def setUp(self):
        self.box_gen = BoxGen()
        
        super(DecimalTestCase, self).setUp()

class FloatTestCase(BaseTestCase, BaseMethods):
    def setUp(self):
        self.box_gen = BoxGen(num_class=float, math_module=math, quantize=False)
        
        super(FloatTestCase, self).setUp()

