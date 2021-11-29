import pandas as pd

class ParserForRequirements():
    # open nominal files
    # example of one nominal file
    def __init__(self, filename):
        """
        Initializes the parser
        """
        self.filename = filename
        self.lines = None
        self.header =["Task number","Satellite","Priority","Duration","Earliest","Latest","Repetitive","Number occ","Min time lag","Max time lag"]
    
    def open_file(self):
        with open(self.filename) as f:
            self.lines = f.readlines()
        return self.lines;
    
    def read_list_sat(self):
        #'./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt'

        list_sat = self.lines[1].strip().split('\t')
        return list_sat

    def get_requirements_data(self):
        # requirements for each task
        self.lines = self.read_list_sat(self)
        data_i = []
        for i in range(3,len(self.lines)):
            data_i.append(self.lines[i].strip().split())
        
        data_df = pd.DataFrame(data_i,columns=self.header)
        return data_df

class ParserForVisibilities():
    # open visibility files
    def __init__(self, filename):
        """
        Initializes the parser
        """
        self.filename = filename
        self.visibs = None
        self.header_visibs = []
        self.data_visibs = []
    
    def open_file(self):
        with open(self.filename) as f:
            self.visibs = f.readlines()
        return self.visibs;

    def get_visibs_data(self):
        for i in range(len(self.visibs)):
            if i == 0:
                self.header_visibs = self.visibs[i].strip().split()
            else:
                self.data_visibs.append(self.visibs[i].strip().split())
        data_visib_df = pd.DataFrame(self.data_visibs,columns=self.header_visibs)
        return data_visib_df


    



