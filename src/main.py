import collections
from ortools.sat.python import cp_model
from parser import ParserForRequirements as pfr
from parser import ParserForVisibilities as pfv
from helper import *
from ModelCP import *

if __name__ == '__main__':
    parser_req = pfr('./../PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt')
    parser_visib = pfv('./../PIE_SXS10_data/visibilities_test.txt')

    data_df = parser_req.get_requirements_data()
    data_visib_df = parser_visib.get_visibs_data()

    print("Requirements are: \n",data_df)
    # print(data_visib_df)

    # construct objects of Ant
    d_ants = {}
    all_sats = []
    dict_visib = {}

    print("\n==>START MODEL<==\n")
    # Creates the model.
    # [START model]
    model = cp_model.CpModel()
    # [END model]

    for i in range(len(data_visib_df['Ant'])) :
        name = data_visib_df['Ant'][i]
        ID = int(name.strip('ANT'))
        start = int(data_visib_df['Start'][i])
        end = int(data_visib_df['End'][i])
        if ID in d_ants:
            count = len(d_ants[ID])
            d_ants[ID].append(model.NewIntervalVar(start,end-start,end,str(count+1)))
        else:
            d_ants[ID] = []
            d_ants[ID].append(model.NewIntervalVar(start,end-start,end,str(1)))

    # construct the matrix for visib
    # initialize
    for i in range(len(data_visib_df)):
        dict_visib[data_visib_df["Sat"][i],data_visib_df["Ant"][i]] = []

    print("-->Initialization for the matrix of visibility<--")
    # print(dict_visib)
    # add element
    for i in range(len(data_visib_df)):
        dict_visib[data_visib_df["Sat"][i],data_visib_df["Ant"][i]].append((data_visib_df['Start'][i],data_visib_df['End'][i]))

    print("-->FINISED<--")
    # print("After add elements : \n", dict_visib)

    dict_non_visib = get_dict_non_visib(dict_visib)

    # change keys for dict_non_visib
    oldkeys = dict_non_visib.keys()
    for sat,ant in list(oldkeys):
        sat_id = int(sat.replace("SAT",""))
        ant_id = int(ant.replace("ANT",""))
        new_key = (sat_id,ant_id)
        dict_non_visib[new_key] = dict_non_visib.pop((sat,ant))

    # print("\n========================")
    # print("NON visibility of sat : \n", dict_non_visib)

    SimpleSatProgram(model,dict_non_visib,3,3)
    print("==>END MODEL<==\n")
