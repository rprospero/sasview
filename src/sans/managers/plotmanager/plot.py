'''
A data-only plot manager in order to separate the data and gui.

This class defines the basics of a plot as shown within SasView. The major 
aspects of the plot will be defined within the gui, but the parameters will
be stored and accessed from here. A plot should only be created through the
plot manager to be sure all plots are housed and accessed through the plot
repository.

Created on Jan 20, 2015

@author: jkrzywon
'''

PLOT_X_SIZE = 20
PLOT_Y_SIZE = 20
PLOT_X_START = 25
PLOT_Y_START = 25
PLOT_MIN_X = 0.008
PLOT_MAX_X = 0.500
PLOT_MIN_Y = 0
PLOT_MAX_Y = 100000


class Plot():
    """
    A Plot() is any object that can be visualized within SasView. This class
    stores information on what data is plotted together as well as relative 
    size and position of the plot within the window.
    
    This class should not include any way to visualize the data, only the data
    that is included in the plot.
    """
    
    # A unique ID to differentiate each plot from one another
    plot_id = None
    # The position of a plot is relative to the upper left corner of the main
    # SasView window, in percent of the size of the open window.
    position_x = 0
    position_y = 0
    # The size of a plot is the size of the plot window relative to the area
    # plots can be displayed. 
    size_x = 0
    size_y = 0
    #
    # Minimum and maximum values displayed on each axis at last update
    x_min = 0
    x_max = 0
    y_min = 0
    y_max = 0
    # Data is a list of data_id's for each DataSet() displayed on the plot
    data = None
    # Analysis is a list of analysis_id for each Analysis() displayed
    analysis = None
    
    def __init__(self, plot_id, data, analysis, attributes):
        self.plot_id = plot_id
        # Manage data ID value(s)
        if (isinstance(data, [])):
            self.data = data
        elif (isinstance(data, "")):
            self.data = [data]
        # TODO: Check data plot parameters - if none, create unique color and
        # shape for each new data set
        self.data = data
        
        for data_set in data:
            data_object = data_set.get_data()
            x_min = data_object.x_min
            x_max = data_object.x_max
            y_min = data_object.y_min
            y_max = data_object.y_max
            
        
        # Handle analysis ID value(s)
        if (isinstance(analysis, [])):
            analysis = analysis
        elif (isinstance(analysis, "")):
            analysis = [analysis]
        self.analysis = analysis
        
        # Handle plot attribute(s)
        # TODO: If no minimum values given, determine min and maxes from data
        # TODO: Create constants for each of these strings
        if (isinstance(attributes, {})):
            self.position_x = attributes.get("position_x", PLOT_X_START)
            self.position_y = attributes.get("position_y", PLOT_Y_START)
            self.size_x = attributes.get("size_x", PLOT_X_SIZE)
            self.size_y = attributes.get("size_y", PLOT_Y_SIZE)
            self.x_max = attributes.get("x_min", PLOT_MIN_X)
            
    def on_close_plot(self):
        """
        When the plot is closed, the reference to the plot should be destroyed
        """
        plot_manager = PlotManager()
        plot_manager.close_plot(self.plot_id)
        
    def add_data(self, data_id):
        """
        To be called when adding a DataSet to an existing plot window
        """
        #TODO: Add warning if plotting the same DataSet() to a plot twice
        self.data.append(data_id)