from helper import *

"""
To check the periods of each task
"""
def Period_Checker(dict_req, dict_res):
    print('Checking periods of each task.')
    
    for i in dict_req['Task number']:
        task = dict_req['Task number'][i]
        duration = dict_req['Duration'][i]
        data_in_task = dict_res[task]
        duration_res = 0;
        for data in data_in_task:
            duration_res = data['end'] - data['start']
        if duration_res >0 and not duration_res == duration:
            return False
        # print(duration_res)
    return True

"""
To check the visibilities of pairs of sat-ant.
"""
def VisibChecker(dict_visib,dict_res):
    print('Checking requirements of visibilities.')
    
    for task in dict_res:
        for element in dict_res[task]:
            sat = element['satellite']
            ant = element['antenne']
            if element['end'] == element['start']:
                continue
            else:
                list_visibility = dict_visib[sat,ant]
                flag = False
                for s,e in list_visibility:
                    if s <= element['start'] and e >= element['end']:
                        # print(s,e)
                        flag = True
                if not flag:
                    print(list_visibility)
                    print(element['start'],element['end'])
                    return False
    return True

"""
TODO:To check the requirements for each antenne
"""
def Antenne_Checker(list_ant,dict_res):
    print('Checking the requirements for each antenne')
    return True


"""
TODO:To check the requirements for each satellite
"""
def Satellite_Checker(list_sat,dict_res):
    print('Checking the requirements for each satellite')
    return True


"""
TODO:To check the priorities
"""
def Priority_Checker(dict_req, dict_res):
    print('Checking the priorities')
    return True



def CheckerInOne(dict_visib,dict_req, list_sat,list_ant, dict_res):
    if not Period_Checker(dict_req,dict_res):
        print('Checking periods failed.')
        return False
    elif not VisibChecker(dict_visib,dict_res):
        print('Checking visiblities failed.')
        return False
    elif not Antenne_Checker(list_ant,dict_res):
        print('Checking antennes failed.')
        return False
    elif not Satellite_Checker(list_sat,dict_res):
        print('Checking satellites failed.')
        return False
    elif not Priority_Checker(dict_req,dict_res):
        print('Checking priorities failed.')
        return False
    else:
        print('Everything is ok!')
        return True
