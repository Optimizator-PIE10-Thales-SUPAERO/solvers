# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 10:33:27 2021

@author: Ange
"""
import pandas as pd
import numpy as np

# open nominal files
# example of one nominal file
with open('./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt') as f:
    lines = f.readlines()

# list of sat
list_sat = lines[1].strip().split('\t')

# requirements for each task
data_i = []
for i in range(3,len(lines)):
    data_i.append(lines[i].strip().split())
    
# header for tasks' requirements
header = ["Task number","Satellite","Priority","Duration","Earliest","Latest","Repetitive","Number occ","Min time lag","Max time lag"]

# data frame for nominal data
data_df = pd.DataFrame(data_i,columns=header) 
print("data_df : \n", data_df)
list_tasks = data_df["Task number"].values.tolist()

# open visibility files
with open('./PIE_SXS10_data/visibilities.txt') as f:
    visibs = f.readlines()
    
header_visibs = []
data_visibs = []
for i in range(len(visibs)):
    if i == 0:
        header_visibs = visibs[i].strip().split()
    else:
        data_visibs.append(visibs[i].strip().split())


#creating the visibilities dataframe
data_visib_df = pd.DataFrame(data_visibs,columns=header_visibs)
print("visibilities between satellites and antennas : \n", data_visib_df)
list_ant = data_visib_df["Ant"].unique().tolist()
print("list of antennas : ", list_ant)







