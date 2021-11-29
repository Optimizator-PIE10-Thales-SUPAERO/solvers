import collections
from ortools.sat.python import cp_model

from parser import ParserForRequirements as pfr
from parser import ParserForVisibilities as pfv
import SatClass
import TaskClass
import AntClass
        
def get_dict_ant_for_sat(data_visib):
    d_ants = {}
    for i in range(len(data_visib['Ant'])) :
        name = data_visib['Ant'][i]
        ID = int(name.strip('ANT'))
        start = int(data_visib['Start'][i])
        end = int(data_visib['End'][i])
        if ID in d_ants:
            count = len(d_ants[ID])
            d_ants[ID].append(model.NewIntervalVar(start,end-start,end,str(count+1)))
        else:
            d_ants[ID] = []
            d_ants[ID].append(model.NewIntervalVar(start,end-start,end,str(1)))
    return d_ants


if __name__ == 'main':
    parser_req = pfv('./../PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt')
    parser_visib = pfr('./../PIE_SXS10_data/visibilities.txt')

    data_df = parser_req.get_requirements_data()
    data_visib_df = parser_visib.get_visibs_data()

    model = cp_model.CpModel()

    # construct objects of Ant
    d_ants = {}
    all_sats = []

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

    # create sat objects
    # consider only one file
    d_sats = {}
    for sat in parser_req.list_sat:
        name = data_df['Satellite'][i]
        data_visib = data_visib_df[data_visib_df['Sat']==name]
        d_ant_tmp = get_dict_ant_for_sat(data_visib)
        ID = int(name.strip('SAT'))
        priority = data_df['Priority'][i]
        eariest = int(data_df['Eariest'][i])
        latest = int(data_visib_df['Latest'][i])