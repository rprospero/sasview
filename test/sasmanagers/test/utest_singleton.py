import unittest
from sans.data_util.id_generator import IDNameGenerator
from sans.data_util.id_generator import IDNumberGenerator
from sans.data_util.singleton import Singleton
from io import __metaclass__


class id_generator(unittest.TestCase):
    
    def setUp(self):
        self.idnumber = IDNumberGenerator()
        self.idname = IDNameGenerator()
        
    def test_id_numbers(self):
        self.idnumber.assign_id()
        self.last_id = self.idnumber.get_last_id_no()
        self.idnumber_new = IDNumberGenerator()
        self.new_id_last = self.idnumber_new.get_last_id_no()
        self.assertTrue(self.last_id == self.new_id_last)
        for x in xrange(10000):
            self.idnumber.assign_id()
        for x in xrange(999):
            self.idnumber_new.assign_id()
        self.assertTrue(self.idnumber.get_last_id_no() == \
                        self.idnumber_new.get_last_id_no())
        self.assertTrue(self.idnumber.get_last_id_no() == 11000)
        self.idnumber.randomize_id()
        self.assertFalse(self.idnumber.get_last_id_no() == 11000)


class singleton(unittest.TestCase):
    
    def setUp(self):
        self.singleton = singleton_counter_test()
    
    def test_create_singelton(self):
        self.assertTrue(self.singleton.counter == 1)
        self.singleton.tickup()
        self.assertTrue(self.singleton.counter == 2)
        self.singleton = singleton_counter_test()
        self.assertTrue(self.singleton.counter == 2)
        for x in xrange(98):
            self.singleton.tickup()
        self.assertTrue(self.singleton.counter == 100)
        self.singleton = singleton_counter_test()
        self.assertTrue(self.singleton.counter == 100)
        
        
class singleton_counter_test():
    
    __metaclass__ = Singleton
    
    counter = 0
    
    def __init__(self):
        self.counter = 1
        
    def tickup(self):
        self.counter = self.counter + 1
        
    def tickdown(self):
        if (self.counter > 1):
            self.counter = self.counter - 1
        else:
            self.counter = 1


if __name__ == '__main__':
    unittest.main()   