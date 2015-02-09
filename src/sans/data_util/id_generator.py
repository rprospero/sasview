'''
An ID generation class that always creates a unique id name/number based
based on a given list.

Created on Oct 9, 2014

@author: jkrzywon
'''

import sys
import random
import string
from random import randint


class IDNumberGenerator():
    """
    Generates a unique id number when called
    """
    
    id_nos_in_use = None
    _id_number = 0
    __id_counter = 0
    
    def __init__(self, starting_point = 0):
        self._reset_counter()
        self.id_nos_in_use = []
        self.set_last_id_number(starting_point)
        
    def assign_id(self):
        """
        Return a unique id number when called
        """
        self.__id_counter += 1
        self._id_number = self.__id_counter
        if self._id_number in self.id_nos_in_use:
            self._id_number = self.assign_id()
        else:
            self.id_nos_in_use.append(self._id_number)
        return self._id_number
    
    def set_last_id_number(self, number = 0):
        """
        Set the last ID number to an arbitrary value
        Convenient way to start at any value or restart at a new value
        """
        if (number not in self.id_nos_in_use):
            self._id_number = number
            self.id_nos_in_use.append(self._id_number)
            
    def randomize_id(self, low = 0, high = sys.maxint):
        """
        Generates a random new starting point for the id number
        """
        #FIXME: If low == high and low in self.id_nos_in_use - infinite loop
        rand_int = randint(low, high)
        if (rand_int in self.id_nos_in_use):
            self.randomize_id(low, high)
        else:
            self._id_number = rand_int
    
    def get_last_id_no(self):
        """
        Get the current value of id_name
        """
        return self._id_number
    
    def _reset_counter(self):
        """
        Resets the counter to 0 for when a new DataManager() object is created
        """
        self.__id_counter = 0
        self._id_number = self.__id_counter
        

class IDNameGenerator(IDNumberGenerator):
    """
    Generates a unique ID name when called
    """
    
    __id_counter = 0
    id_name = ''
    _basename = ''
    id_names_in_use = None
    
    def __init__(self, basename="", zeropoint = 0):
        IDNumberGenerator.__init__(self, zeropoint)
        if (basename != ""):
            self._basename = basename
        else:
            self._basename = ''.join(random.choice(string.ascii_uppercase) \
                                    for _ in range(12))
        self.id_names_in_use = []
        
    def assign_id(self):
        """
        Return a unique id name when called
        """
        IDNumberGenerator.assign_id(self)
        self.id_name = self._basename + str(self.get_last_id_no())
        if self.id_name in self.id_names_in_use:
            self.id_name = self.assign_id()
        else:
            self.id_names_in_use.append(self.id_name)
        return self.id_name
    
    def get_last_id_name(self):
        """
        Returns the last id_name generated
        """
        return self.id_name
    
    def _reset_counter(self):
        """
        Resets the counter and initializes the last known id_name
        """
        IDNumberGenerator._reset_counter(self)
        self.id_name = ''
        
    def get_base_name(self):
        """
        Returns the base string for generating ID names
        """
        return self._basename
        