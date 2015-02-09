import unittest
from sans.managers.datamanager.datamanager import DataManager
from sans.data_util.singleton import Singleton
from io import __metaclass__


class datamanager(unittest.TestCase):
    
    def setUp(self):
        self.datamanager = DataManager()
        self.file1 = "ISIS_1_0.xml"
        self.file2 = "ISIS_1_1.xml"
        # Do not load the 2nd data file immediately
        self.datamanager.load_data_file(self.file1)
        
    def test_datamanager_get_and_set(self):
        """
        Test the basic functionality of the DataManager() class
        """
        self.last_id = self.datamanager.id_generator.get_last_id_name()
        self.last_data_set = self.datamanager.get_dataset_by_id(self.last_id)
        self.assertTrue(self.last_data_set)
        self.assertTrue(len(self.datamanager.data_sets) == 1)
        self.datamanager.delete_data_set(self.last_id)
        self.last_data_set = self.datamanager.get_dataset_by_id(self.last_id)
        self.assertFalse(self.last_data_set)
        self.assertTrue(len(self.datamanager.data_sets) == 0)
        self.datamanager.load_data_file(self.file2)
        self.last_id = self.datamanager.id_generator.get_last_id_name()
        self.last_data_set = self.datamanager.get_dataset_by_id(self.last_id)
        self.assertTrue(self.last_data_set)
        self.datamanager._flush_data_manager()
        self.assertFalse(self.datamanager.get_dataset_by_id(self.last_id))
        self.assertTrue(len(self.datamanager.data_sets) == 0)
    

if __name__ == '__main__':
    unittest.main()   