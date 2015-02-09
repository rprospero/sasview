'''
All data loaded and manipulated within SasView will be managed and stored
within this package. All plugins should access data from this package.

Created on Oct 1, 2014

@author: jkrzywon
'''

from sans.managers.analysismanager.analysismanager import AnalysisManager
from sans.managers.plotmanager.plotmanager import PlotManager
from sans.managers.savemanager.saveproject import SaveProject

from sans.managers.datamanager.dataset import DataSet
from sans.dataloader.loader import Loader
from sans.data_util.id_generator import IDNameGenerator

DATA_ID_BASE = "DATA_"


class DataManager():
    """
    A centralized manager of all data loaded into SasView. Manages where the
    data is and where it goes.
    """
    
    data_sets = None
    analysis_manager = None
    plot_manager = None
    project_manager = None
    
    def __init__(self):
        # A dictionary mapping data_id : DataSet()
        self.data_sets = {}
        # An id generation tool.
        # TODO: Randomize the base ID name as well?
        self.id_generator = IDNameGenerator(DATA_ID_BASE)
        # Randomize the starting ID number to minimize the chance id names
        # conflict when opening a save file with data already loaded
        self.id_generator.randomize_id()
        self.analysis_manager = AnalysisManager()
        self.plot_manager = PlotManager()
        self.project_manager = SaveProject()
        
    def load_data_file(self, filepath):
        """
        New default method for loading in any data file, including pictures
        via the picture viewer
        
        :param filepath: The path to the file being loaded
        """
        loader = Loader()
        data_list = loader.load(filepath)
        for data in data_list:
            data_id = self.id_generator.assign_id()
            dataset = DataSet(data, data_id)
            self.data_sets[data_id] = dataset
    
    def get_dataset_by_id(self, data_id):
        """
        Returns a dataset with a unique id
        
        :param data_id: The id of the dataset desired
        """
        return self.data_sets.get(data_id)

    def delete_data_set(self, data_id):
        """
        Cleanly removes all references to a DataSet() object
        
        :param data_id: data_id for the dataset to be removed
        """
        data = self.data_sets.get(data_id)
        if data is not None:
            if data_id in self.analysis_manager.data_analysis:
                #TODO: Manage data removal in analysis
                self.analysis_manager.data_analysis.pop(data_id)
            if data_id in self.plot_manager:
                #TODO: Manage data removal on plots
                self.plot_manager.pop(data_id)
            if data_id in self.data_sets:
                del self.data_sets[data_id]
            
    def _flush_data_manager(self):
        """
        Completely destroys all data information in memory
        """
        for data_id in self.data_sets.keys(): 
            self.delete_data_set(data_id)
        self.id_generator._reset_counter()
