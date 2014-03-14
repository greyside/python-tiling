#Python imports
from decimal import Decimal
from unittest import TestCase

try:
    import dmath
except ImportError:
    dmath = None

from . import BoxGen

class BaseTestCase(TestCase):
    def setUp(self):
        num_class = self.box_gen.num_class
        
        self.num_class = num_class
        
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
                dist = self.box_gen.distance(lat, val1, lat, val2)
            else:
                dist = self.box_gen.distance(val1, 0, val2, 0)
            
            self.assertLess(abs(val1-val2), precision or self.precision, msg='%r and %r are not close enough. About %s %s apart (lat: %s).' % (val1, val2, dist, self.box_gen.unit, lat,))
    
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
        val = self.num_class('33.95')
        
        ret = self.box_gen.fix_lat(val)
        
        self.assertEqual(ret, val)
    
    def test__fix_lat__too_big(self):
        val = self.num_class('90.0001')
        
        ret = self.box_gen.fix_lat(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.box_gen.MAX_LAT)
    
    def test__fix_lat__too_small(self):
        val = self.num_class('-90.0001')
        
        ret = self.box_gen.fix_lat(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.box_gen.MIN_LAT)
    
    def test__fix_lon__not_needed(self):
        val = self.num_class('40.6333')
        
        ret = self.box_gen.fix_lon(val)
        
        self.assertEqual(ret, val)
    
    def test__fix_lon__too_big(self):
        val = self.num_class('180.0001')
        
        ret = self.box_gen.fix_lon(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.num_class('-179.9999'))
    
    def test__fix_lon__too_small(self):
        val = self.num_class('-180.0001')
        
        ret = self.box_gen.fix_lon(val)
        
        self.assertNotEqual(ret, val)
        self.assertEqual(ret, self.num_class('179.9999'))
    
    def test__distance__lax_to_jfk(self):
        # from http://williams.best.vwh.net/avform.htm#Example
        lax = self.num_class('33.95'), self.num_class('-118.4')
        jfk = self.num_class('40.6333'), self.num_class('-73.7833')
        
        d1 = self.box_gen.distance(lax[0], lax[1], jfk[0], jfk[1])
        d2 = self.box_gen.distance(jfk[0], jfk[1], lax[0], lax[1])
        
        self.assertCloseEnough(d1, self.num_class('2467.270176'), precision=1)
        self.assertEqual(d1, d2)
    
    def test__get_box_centerpoint_for_coordinates__zerozero(self):
        box_radius = self.num_class('3')
        lat, lon = self.locations['0-0']
        
        pair = self.box_gen.get_box_centerpoint_for_coordinates(lat, lon, box_radius)
        
        self.assertCloseEnough(pair[0], self.num_class('0.0434488290106'))
        self.assertCloseEnough(pair[1], self.num_class('0.0434488415034'))
    
    def test__get_box_centerpoint_for_coordinates__near_zerozero(self):
        box_radius = self.num_class('3')
        lat, lon = (self.num_class('-0.087'), self.num_class('-0.087'))
        
        pair = self.box_gen.get_box_centerpoint_for_coordinates(lat, lon, box_radius)
        
        self.assertCloseEnough(pair[0], self.num_class('-0.0434488290106')*3)
        self.assertCloseEnough(pair[1], self.num_class('-0.0434488415034')*3)
    
    def test__offset__returns_same_vals(self):
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.box_gen.offset(lat, lon)
        
        self.assertEqual(lat, new_lat)
        self.assertEqual(lon, new_lon)
    
    def test__offset__returns_incremented_vals(self):
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.box_gen.offset(lat, lon, lat_unit_offset=1, lon_unit_offset=1)
        
        self.assertLess(lat, new_lat)
        self.assertLess(lon, new_lon)
    
    def test__offset__returns_decremented_vals(self):
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.box_gen.offset(lat, lon, lat_unit_offset=-1, lon_unit_offset=-1)
        
        self.assertGreater(lat, new_lat)
        self.assertGreater(lon, new_lon)
    
    def test__offset__multiple_transforms(self):
        lat, lon = self.locations['rochester']
        
        new_lat, new_lon = self.box_gen.offset(lat, lon, lat_unit_offset=-3, lon_unit_offset=-3)
        
        new_lat2, new_lon2 = self.box_gen.offset(new_lat, new_lon, lat_unit_offset=3, lon_unit_offset=3)
        
        self.assertCloseEnough(lat, new_lat2, precision=self.num_class('0.0001'))
        self.assertCloseEnough(lon, new_lon2, precision=self.num_class('0.0001'), lat=lat)
    
    def test__offset_pairs_num__same_length_as_original_func(self):
        search_box_radius = self.num_class(5)
        max_box_radius = self.num_class(2)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width, max_box_radius,)
            
            num = self.box_gen.offset_pairs_num(*args)
            pairs = self.box_gen.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__equal_search_and_box_size(self):
        search_box_radius = self.num_class(4)
        max_box_radius = self.num_class(4)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width, max_box_radius,)
            
            num = self.box_gen.offset_pairs_num(*args)
            pairs = self.box_gen.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__box_size_is_divisor_of_search(self):
        search_box_radius = self.num_class(4)
        max_box_radius = self.num_class(2)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width, max_box_radius,)
            
            num = self.box_gen.offset_pairs_num(*args)
            pairs = self.box_gen.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__search_smaller_than_box_size(self):
        search_box_radius = self.num_class(3)
        max_box_radius = self.num_class(4)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width, max_box_radius,)
            
            num = self.box_gen.offset_pairs_num(*args)
            pairs = self.box_gen.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_pairs_num__same_length_as_original_func__bigger_search_box_radius(self):
        search_box_radius = self.num_class(7)
        max_box_radius = self.num_class(2)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            args = (coors[0], coors[1], height, width, max_box_radius,)
            
            num = self.box_gen.offset_pairs_num(*args)
            pairs = self.box_gen.offset_coor_pairs(*args)
            
            self.assertEqual(num, len(pairs))
    
    def test__offset_boxes__nearby_centerpoints_reuse_boxes__rochester(self):
        search_box_radius = self.num_class(7)
        max_box_radius = self.num_class(3)
        
        width = height = search_box_radius * 2
        
        lat1, lon1 = self.locations['rochester']
        
        # 6 miles north, 6 miles east
        lat2, lon2 = self.box_gen.offset(lat1, lon1, lat_unit_offset=6, lon_unit_offset=6)
        
        boxes1 = self.box_gen.offset_boxes(lat1, lon1, height, width, max_box_radius)
        boxes2 = self.box_gen.offset_boxes(lat2, lon2, height, width, max_box_radius)
        
        self.assertEqual(boxes1[8], boxes2[4])
        self.assertEqual(boxes1[7], boxes2[3])
        self.assertEqual(boxes1[5], boxes2[1])
        self.assertEqual(boxes1[4], boxes2[0])
    
    def test__offset_boxes__borders_touch(self):
        search_box_radius = self.num_class(7)
        max_box_radius = self.num_class(2)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            boxes = self.box_gen.offset_boxes(coors[0], coors[1], height, width, max_box_radius)
            
            self.assertBoxesTouch(boxes, 5, 5)
    
    def test__offset_boxes__borders_touch__fewer_boxes(self):
        search_box_radius = self.num_class(7)
        max_box_radius = self.num_class(3)
        
        width = height = search_box_radius * 2
        
        for location_name, coors in self.locations.items():
            boxes = self.box_gen.offset_boxes(coors[0], coors[1], height, width, max_box_radius)
            
            self.assertBoxesTouch(boxes, 3, 3)
    
    def test__offset_boxes__borders_touch__rectangle(self):
        height = self.num_class(13)
        width = self.num_class(5)
        max_box_radius = self.num_class(2)
        
        for location_name, coors in self.locations.items():
            boxes = self.box_gen.offset_boxes(coors[0], coors[1], height, width, max_box_radius)
            
            self.assertBoxesTouch(boxes, 3, 5)

if dmath:
    class DecimalTestCase(BaseTestCase, BaseMethods):
        def setUp(self):
            self.box_gen = BoxGen(num_class=Decimal, math_module=dmath)
            
            super(DecimalTestCase, self).setUp()

class FloatTestCase(BaseTestCase, BaseMethods):
    def setUp(self):
        self.box_gen = BoxGen()
        
        super(FloatTestCase, self).setUp()

