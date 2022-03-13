import sys
import argparse
import collections
from ortools.sat.python import cp_model
from Parser import ParserForRequirements as pfr
from Parser import ParserForVisibilities as pfv
from helper import *
from ModelCP import *
from checker import CheckerInOne as check
from Gantt import *
import parse
from os import listdir
from os.path import isfile, join

def ModelSimple(setOccurrence,req_file = './PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt',
                visib_file = './PIE_SXS10_data/visibilities_test.txt',flag_nostore=False,flag_nooccurrence=False):
    parser_req = pfr(req_file)
    parser_visib = pfv(visib_file)

    data_df = parser_req.get_requirements_data()
    data_visib_df = parser_visib.get_visibs_data()

    # parameters
    n_tasks = len(data_df['Task number'])
    """
    get sats and ants from visib_file
    """
    list_sats_visib = [int(i.strip('SAT')) for i in data_visib_df.Sat.unique().tolist()]
    list_antennes_visib = [int(i.strip('ANT')) for i in data_visib_df.Ant.unique().tolist()]
    dict_sat_ants = collections.defaultdict(list) 
    for i in range(len(data_visib_df)):
        if data_visib_df.Ant[i] not in dict_sat_ants[data_visib_df.Sat[i]]:
            dict_sat_ants[data_visib_df.Sat[i]].append(data_visib_df.Ant[i])

    n_antennes_visib = len(list_antennes_visib)

    print("@Visibilities are: \n",data_visib_df)
    # print("@Satellite and all its visiable antennes: \n",dict_sat_ants)

    """
    get sats and ants according to requirements
    """
    list_sats_names = data_df.Satellite.unique().tolist()
    list_sats = [int(i.strip('SAT')) for i in list_sats_names]
    # list_sats = parser_req.read_list_sat()
    list_antennes = []
    for sat in list_sats_names:
        if sat in dict_sat_ants:
            list_antennes = list_antennes + dict_sat_ants[sat]
    list_antennes = [int(i.strip('ANT')) for i in unique(list_antennes)]
    n_antennes = len(list_antennes)

    print("@Requirements are: \n",data_df)
    print("@list of satellites: \n",list_sats)
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

    '''
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
    '''

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

    # change keys for dict_non_visib, from str to int, from name to id
    oldkeys = dict_non_visib.keys()
    for sat,ant in list(oldkeys):
        sat_id = int(sat.replace("SAT","")) # or int(sat.strip("SAT"))
        ant_id = int(ant.replace("ANT",""))
        new_key = (sat_id,ant_id)
        dict_non_visib[new_key] = dict_non_visib.pop((sat,ant))

    print("\n-->ARGUMENTS<--")
    # print("NON visibility of sat : \n", dict_non_visib)

    # transfer dataframe of requirements and visibilities dataframe to dictionary
    dict_data_df = data_df.to_dict()
    # dict_visib_df = data_visib_df.to_dict()
    print("@Requirements dictionary : \n",dict_data_df)
    # print("@Visibility dictionary : \n", dict_visib)

    print("-->FINISHED<--\n")

    results,time = SimpleSatProgram(model,dict_data_df,dict_non_visib,n_tasks,list_sats,list_antennes,req_file,setOccurrence,flag_nostore,flag_nooccurrence)
    print("==>END MODEL<==\n")
    return dict_visib, dict_data_df,list_sats,list_antennes,results,time

def ModelNominalV1(req_file,setOccurrence,flag_nooccurrence,visib_file='./PIE_SXS10_data/visibilities.txt'):
    print("req file",req_file)
    return ModelSimple(setOccurrence,req_file,visib_file,flag_nooccurrence=flag_nooccurrence)

def TestForDiffNombreSat(list_req_file,flag_nooccurrence,setOccurrence,visib_file='./PIE_SXS10_data/visibilities.txt'):
    list_time = []
    for req_file in list_req_file:
        print("req file",req_file)
        dict_visib,dict_req,list_sats,list_ants,dict_res,time = ModelSimple(setOccurrence,req_file,visib_file,flag_nostore=True,flag_nooccurrence=flag_nooccurrence)
        list_time.append(time)
    print("@ list of execution time :",list_time)
    print(" The average time is:",sum(list_time)/len(list_req_file))


"""
define the options of main function
"""
parser_arg = argparse.ArgumentParser(description='Modèle Matriciel')
parser_arg.add_argument("-g", "--TestForGroupScenario", help="If you want to run the model for a group of scenarios", action="store_true" )
parser_arg.add_argument("-no", "--NoOccurrence", help="If you want to run the model without considering the repetition", action="store_true" )
parser_arg.add_argument("-n",'--SetOccurrence',nargs='?',help="(optional) Set the max time of repetion manully",type=int, default=-1)
parser_arg.add_argument('--p', help="Test files path", nargs="?",default='./PIE_SXS10_data/nominal/random_sample/10/')
parser_arg.add_argument('--r', help="Requirements file", nargs="?",default='./PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt')
parser_arg.add_argument("--v", help="Visibility file",nargs="?", default="./PIE_SXS10_data/visibilities.txt")

if __name__ == '__main__':
    '''
    arguments = sys.argv
    '''
    arguments = parser_arg.parse_args()
    print(arguments)
    dict_res = {}
    dict_req = {}
    dict_visib = {}
    list_sats = []
    list_ants = []
    filename = ""
    flag_nooccurrence = True if arguments.NoOccurrence else False

    if arguments.TestForGroupScenario:
        path = arguments.p
        onlyfiles = [arguments.p+f for f in listdir(path) if isfile(join(path, f))]
        TestForDiffNombreSat(onlyfiles,flag_nooccurrence,arguments.SetOccurrence, arguments.v)
        sys.exit(0)
    else:
        if arguments.r == './PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt':
            dict_visib,dict_req,list_sats,list_ants,dict_res,time = ModelSimple(arguments.SetOccurrence,flag_nooccurrence=flag_nooccurrence)
            filename = './PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt'
        else:
            filename = arguments.r
            dict_visib,dict_req,list_sats,list_ants,dict_res,time = ModelNominalV1(filename,arguments.SetOccurrence,flag_nooccurrence,arguments.v)
    print("==>START CHECKING<==")
    # print(dict_req)
    # print("-->results are<--")
    # print(dict_res)
    if check(dict_visib,dict_req,list_sats,list_ants,dict_res):
        parsed = parse.parse('./PIE_SXS10_data/{}/{}.txt',filename)
        plan_data_name = 'results/'+parsed[1]+'.xls'
        write_file(dict_visib,dict_res,dict_req,plan_data_name)
        fig_name = 'results/'+parsed[1]+'.png'
        fig_name2 = 'results/'+parsed[1]+'_T.png'
        GanttPlan(plan_data_name)
        GanttForTask(dict_res,fig_name)
        GanttForAntenne(dict_res,dict_req,fig_name2)
    print("==>END CHECKING<==")
