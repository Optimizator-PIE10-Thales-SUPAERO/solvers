import pandas as pd

class ParserForRequirements():
    # open nominal files
    # example of one nominal file
    def __init__(self, filename):
        """
        Initializes the parser
        """
        self.filename = filename
        # self.lines = []
        self.header =["Task number","Satellite","Priority","Duration","Earliest","Latest","Repetitive","Number occ","Min time lag","Max time lag"]
    
    def open_file(self):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines;
    
    def read_list_sat(self):
        #'./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt'
        self.lines = self.open_file()
        list_sat = [int(i.strip('SAT')) for i in self.lines[1].strip().split('\t')]
        return list_sat

    def get_requirements_data(self):
        # requirements for each task
        self.lines = self.open_file()
        data_i = []
        for i in range(3,len(self.lines)):
            data_i.append(self.lines[i].strip().split())
        # print(data_i)

        data_df = pd.DataFrame(data_i,columns=self.header)
        data_df[["Priority","Duration","Earliest",
                "Latest","Repetitive","Number occ",
                "Min time lag","Max time lag"]] = data_df[["Priority","Duration","Earliest",
                                                            "Latest","Repetitive","Number occ",
                                                            "Min time lag","Max time lag"]].astype(int)
        return data_df

class ParserForVisibilities():
    # open visibility files
    def __init__(self, filename):
        """
        Initializes the parser
        """
        self.filename = filename
        #self.visibs = []
        self.header_visibs = []
        self.data_visibs = []
    
    def open_file(self):
        with open(self.filename) as f:
            self.visibs = f.readlines()
        return self.visibs;

    def get_visibs_data(self):
        self.visibs = self.open_file()
        for i in range(len(self.visibs)):
            if i == 0:
                self.header_visibs = self.visibs[i].strip().split()
            else:
                self.data_visibs.append(self.visibs[i].strip().split())
        data_visib_df = pd.DataFrame(self.data_visibs,columns=self.header_visibs)
        data_visib_df[["Start","End"]] = data_visib_df[["Start","End"]] .astype(int)
        return data_visib_df


    



