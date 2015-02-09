'''
Created on Jan 15, 2015

@author: jkrzywon
'''

from sans.data_util.id_generator import IDNameGenerator

ANALYSIS_ID_BASE = "ANALYSIS_"


class AnalysisManager():
    """
    A centralized repository of all analyses performed by SasView
    """
    
    analyses = None
    
    def __init__(self):
        # A dictionary mapping analysis_id : Analysis()
        self.analyses = {}
        # A dictionary mapping data_id : [analysis_id]
        self.data_analysis = {}
        # An id generation tool.
        self.id_generator = IDNameGenerator(ANALYSIS_ID_BASE)
        
    def set_analysis(self, dataid, analysis):
        """
        A public method to add an analysis to the manager
        """
        a_id = self.id_generator.assign_id()
        self.link_data_to_analysis(dataid, a_id)
        self.analyses[a_id] = analysis
    
    def get_analysis_by_id(self, analysis_id):
        """
        A public method to get an existing analysis.
          Returns false if the id does not exist.
        """
        return self.analyses.get(analysis_id)
        
    def link_data_to_analysis(self, dataid, a_id):
        """
        A public method to ensure each analysis is linked to a dataset
        """
        analysis_list = self.data_analysis.get(dataid)
        if (isinstance(analysis_list, [])):
            analysis_list.append(a_id)
        elif(isinstance(analysis_list, None)):
            analysis_list = [a_id]
        else:
            pass
        self.data_analysis[dataid] = analysis_list