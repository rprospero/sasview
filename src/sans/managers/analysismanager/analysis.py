'''
All forms of data analysis should be sent here to better manage saving states
and saving each individual analysis.

The attributes of each Analysis are what is saved by saveproject and
saveanalysis. 

Created on Jan 15, 2015

@author: jkrzywon
'''

import logging

FROZEN_ANALYSIS = "The analysis has been locked and cannot be modified."


class Analysis():
    """
    A class to store attributes related to each analysis that 
    can be modified and/or updated by a perspective.
    """
    
    attributes = None
    frozen = None
    perspective = None
    data_id = []
    
    def __init__(self, attrs, perspec):
        if attrs == None:
            self.attributes = {}
        elif isinstance(attrs, {}):
            self.attributes = attrs
        else:
            self.attributes = None
        self.frozen = False
        if perspec == None:
            self.perspective = ""
        else:
            self.perspective = perspec
        
    def set_attribute(self, attribute, value):
        """
        Sets a single attribute value for the given analysis
        
        :param attribute: The attribute name
        :param value: The attribute value.
        """
        if self.frozen == False:
            self.attributes[attribute] = value
        else:
            logging.info(FROZEN_ANALYSIS)
        
    def get_attribute_by_name(self, attribute):
        """
        Returns the value for the given attribute of the current analysis
        
        :param attribute: The attribute name the value of is desired
        """
        return self.attributes.get(attribute)
        
    def get_all_attributes(self):
        """
        Returns a dictionary of all attributes
        """
        return self.attributes
        
    def check_if_frozen(self):
        """
        A check to see if the analysis is frozen.
        """
        return self.frozen
    
    def freeze_analysis(self):
        """
        Locks the analysis so it cannot be modified. Useful for making sure a 
        fit isn't overwritten.
        """
        self.frozen = True
        return self.frozen
        
    def unfreeze_analysis(self):
        """
        Unlocks the analysis so it can be modified again.
        """
        self.frozen = False
        return self.frozen