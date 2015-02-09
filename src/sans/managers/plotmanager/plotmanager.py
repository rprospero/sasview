'''
A centralized plot manager to handle each plot saved, loaded and created within
SasView. All visualization should be done separately, but the gui should 

Created on Jan 20, 2015

@author: jkrzywon
'''

from sans.managers.plotmanager.plot import Plot
from sans.data_util.id_generator import IDNameGenerator

PLOT_X_SIZE = 20
PLOT_Y_SIZE = 20
PLOT_X_START = 25
PLOT_Y_START = 25
PLOT_ID_BASE = "PLOT_"


class PlotManager():
    """
    A singleton to manage all Plot()s that are open within SasView. Only 
    attributes of the plots are stored here. Any method to visualize the plots
    and data should be separate from this manager to keep data management and
    gui separate.
    """
    
    plots = None
    data_plots = None
    analysis_plots = None
    last_pos_x = 0
    last_pos_y = 0
    last_size_x = 0
    last_size_y = 0
    next_pos_x = 0
    next_pos_y = 0
    id_generator = None
    
    def __init__(self):
        # Plot.plot_id : Plot
        self.plots = {}
        # DataSet.data_id : Plot.plot_id
        self.data_plots = {}
        # Analysis.analysis_id : Plot.plot_id
        self.analysis_plots = {}
        # Left edge of the last opened plot window
        self.last_pos_x = PLOT_X_START
        # Top edge of the last opened plot window
        self.last_pos_y = PLOT_Y_START
        # Left-to-right size, in percent, of the last plot window opened
        self.last_size_x = 0
        # Top-to-bottom size, in percent, of the last plot window opened
        self.last_size_y = 0
        self.set_next_position()
        self.id_generator = IDNameGenerator(PLOT_ID_BASE)
        self.id_generator.randomize_id()
        
    def add_plot(self, datasets, analyses):
        '''
        Create a new plot. Attempt to tile the plots with no overlap if
        possible. If overlap, stagger the next set of plots.
        '''
        plot_id = self.id_generator
        attr = {
                "position_x" : self.next_pos_x,
                "position_y" : self.next_pos_y,
                "size_x" : PLOT_X_SIZE,
                "size_y" : PLOT_Y_SIZE,
                }
        plot = Plot(plot_id, datasets, analyses, attr)
        if plot:
            self.link_data_to_plot(datasets, plot_id)
            self.plots[plot_id] = plot
        
    def set_next_position(self):
        '''
        Define the starting position of the net plot to open
        '''
        self.next_pos_x = self.last_pos_x + self.last_size_x
        self.next_pos_y = self.last_pos_y + self.last_size_y
        if ((self.next_pos_x + PLOT_X_SIZE > 100) or \
                    (self.next_pos_y + PLOT_Y_SIZE > 100)):
            # If the plot would be outside the window size, stagger from the
            # first window opened
            self.next_pos_x = PLOT_X_START + 5
            self.next_pos_y = PLOT_Y_START + 5
            
    def link_data_to_plot(self, datasets, plot_id):
        """
        Link each DataSet instance to each Plot instance
        """
        for data_id in datasets:
            if not self.data_plots[data_id]:
                self.data_plots[data_id] = [plot_id]
            elif self.data_plots[data_id] and \
                    not self.data_plots[data_id].get(plot_id):
                plots = self.data_plots[data_id].append(plot_id)
                self.data_plots[data_id] = plots
    
    def close_plot(self, plot_id):
        """
        Remove the plot from the manager when the plot window is closed
        """
        self.plots.pop(plot_id)
        # TODO: Handle other managers, each data_if, etc.
        