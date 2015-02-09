'''
A centralized save project that takes all of the data form the managers,
coordinates them and saves a file with all of the data.

Created on Jan 20, 2015

@author: jkrzywon
'''

from sans.dataloader.cansas_reader import Reader


class SaveProject():
    
    handler = None
    
    def __init__(self):
        self.handler = Reader()
        self.data = None
        
    def save_project(self, filename):
        self.handler.write(filename, self.data)
        