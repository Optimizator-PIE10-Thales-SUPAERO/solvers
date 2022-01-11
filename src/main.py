import sys
import collections
from ortools.sat.python import cp_model
from Parser import ParserForRequirements as pfr
from Parser import ParserForVisibilities as pfv
from helper import *
from ModelCP import *

def ModelSimple(req_file = './../PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt',
                visib_file = './../PIE_SXS10_data/visibilities_test.txt'):
    parser_req = pfr(req_file)
    parser_visib = pfv(visib_file)

    data_df = parser_req.get_requirements_data()
    data_visib_df = parser_visib.get_visibs_data()

    # parameters
    n_tasks = len(data_df['Task number'])
    list_sats = [int(i.strip('SAT')) for i in data_visib_df.Sat.unique().tolist()]
    list_antennes = [int(i.strip('ANT')) for i in data_visib_df.Ant.unique().tolist()]
    n_antennes = len(list_antennes)

    print("@Requirements are: \n",data_df)
    print("@Visibilities are: \n",data_visib_df)
    print("@list of antennes: \n", list_antennes)

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

    print("\n-->ARGUMENTS<--")
    # print("NON visibility of sat : \n", dict_non_visib)

    # transfer dataframe of requirements and visibilities dataframe to dictionary
    dict_data_df = data_df.to_dict()
    dict_visib_df = data_visib_df.to_dict()
    print("@Requirements dictionary : \n",dict_data_df)
    # print("@Visibility dictionary : \n", dict_visib_df)

    print("-->FINISHED<--\n")
    SimpleSatProgram(model,dict_data_df,dict_non_visib,n_tasks,list_antennes)
    print("==>END MODEL<==\n")

def ModelNominalV1(req_file,visib_file='./../PIE_SXS10_data/visibilities.txt'):
    ModelSimple(req_file,visib_file)

if __name__ == '__main__':
    arguments = sys.argv
    print(arguments)
    if len(arguments) == 1:
        ModelSimple()
    elif len(arguments) == 2:
        ModelNominalV1(arguments[1])
    elif len(arguments) == 3:
        ModelNominalV1(arguments[1],arguments[2])
    else:
        print("Wrong arguments")
