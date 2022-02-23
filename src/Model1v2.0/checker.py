from helper import *
from Gantt import *

"""
To check the periods of each task
"""
def Period_Checker(dict_req, dict_res):
    print('Checking periods of each task.')
    
    """ commit temporary
    for i in dict_req['Task number']:
        task_id = dict_req['Task number'][i]
        duration = dict_req['Duration'][i]
        data_in_task = dict_res[task_id]
        duration_res = 0;
        for data in data_in_task:
            duration_res = data['end'] - data['start']
        if duration_res >0 and duration_res<duration or duration_res > duration:
            return False
        # print(duration_res)
    """
    GanttForTask(dict_res)
    return True

"""
To check the requirements for each antenne
"""
def Antenne_Checker(list_ant,dict_res):
    print('Checking the requirements for each antenne')
    return True


"""
To check the requirements for each satellite
"""
def Satellite_Checker(list_sat,dict_res):
    print('Checking the requirements for each satellite')
    return True


"""
To check the priorities
"""
def Priority_Checker(dict_req, dict_res):
    print('Checking the priorities')
    return True



def CheckerInOne(dict_req, list_sat,list_ant, dict_res):
    if not Period_Checker(dict_req,dict_res):
        print('Checking periods failed.')
    elif not Antenne_Checker(list_ant,dict_res):
        print('Checking antennes failed.')
    elif not Satellite_Checker(list_sat,dict_res):
        print('Checking satellites failed.')
    elif not Priority_Checker(dict_req,dict_res):
        print('Checking priorities failed.')
    else:
        print('Everything is ok!')
