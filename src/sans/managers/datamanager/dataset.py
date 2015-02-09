"""
Base data set package for handling an individual data (1D or 2D) object and all 
theories and plots the data set is present in.

Created on Sep 29, 2014

@author: jkrzywon
"""

from sans.dataloader.data_info import Data1D
from sans.dataloader.data_info import Data2D
import logging
from types import NoneType
from types import StringType

DATA_TYPES = {
              Data1D : Data1D,
              Data2D : Data2D,
              None : NoneType,
              Exception : BaseException,
              'Other' : StringType
              }
BAD_DATA_MSG = "The data sent to DataSet is in an unexpected format."


class ImproperDataTypeException(Exception):
    """
    An exception thrown when creating a DataSet() object with improper data
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class DataSet():
    """
    DataSet() data are meant to be immutable. Perspectives and plots can and
    should be modified as the dataset is sent to various theories
    """
    __data_id = None
    __data = None
    datatype = None
    plot_attributes = None
     
    def __init__(self, data = None, id_no = None):
        self.__data_id = id_no
        self.__data = data
        if data:
            if isinstance(data, Data1D):
                self.datatype = DATA_TYPES.get(Data1D)
            elif isinstance(data, Data2D):
                self.datatype = DATA_TYPES.get(Data2D)
            elif data == None:
                self.datatype = DATA_TYPES.get(None)
            elif isinstance(data, Exception):
                self.datatype = DATA_TYPES.get(Exception)
                logging.error(str(data))
            else:
                self.datatype = DATA_TYPES.get('Other')
                raise ImproperDataTypeException(BAD_DATA_MSG)
        self.plot_attributes = {}
    
    def __str__(self):
        """
        Formats the DataSet() into a human-readable string object.
        """
        string = "DataSet - id:{0}".format(self.__data_id)
        string += ""
        string += str(self.__data)
        
#         Commented out until the plot and analysis managers are finalized
#         if len(self.analyses) > 0:
#             string += ""
#             string += "Perspectives the data is present in:"
#             for theory in self.theories:
#                 string += "\tPerspective: {0}".format(theory.type)
#                 string += "\t\tInfo:{0}".format(theory.attributes)
#         if len(self.plots) > 0:
#             string += ""
#             string += "Plots the data is present in:"
#             for plot in self.plots:
#                 string += "\Plot: {0}".format(plot.name)
#                 string += "\t\tInfo:{0}".format(plot.attributes)

        return string
    
    def get_id(self):
        """
        Returns the data_id for the DataSet()
        """
        return self.__data_id
    
    def get_data(self):
        """
        Returns the data - the data should NEVER be modified
        """
        return self.__data
    
    def set_plot_attribs(self, attribs):
        """
        Sets the plotting attributes to create continuity between data and
        plotting
        """
        self.plot_attributes = attribs
        return self.get_plot_attribs()
        
    def get_plot_attribs(self):
        """
        Returns the plotting attributes when a plot requests them
        """
        return self.plot_attributes
    
#     Commented out until location of perspectives and plots is finalized
#     def send_to_perspective(self, perspective):
#         """
#         Adds a perspective to the list of theories the DataSet() object
#         has been handled by
#         
#         :param perspective: The perspective handling the DataSet() and
#             associated meta data. The object should have __str__ and to_xml
#             methods.
#         """
#         self.analyses.append(perspective)
#         
#     def add_to_plot(self, plot):
#         """
#         Adds a plot to the list of plots the DataSet() is currently plotted in
#         
#         :param plot: A Plot() the DataSet() is newly plotted in
#         """
#         self.plots.append(plot)
#         
#     def remove_from_plot(self, plot):
#         """
#         Tells the DataSet() object the data is no longer displayed in the plot
#         
#         :param plot: The Plot() the DataSet() was removed from
#         """
#         if plot in self.plots:
#           self.plots.remove(plot)
