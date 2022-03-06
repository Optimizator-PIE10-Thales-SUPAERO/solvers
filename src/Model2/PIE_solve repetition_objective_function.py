"""Simple solve."""
from abc import abstractproperty
from datetime import time
from os import X_OK
from tkinter import S
from ortools.sat.python import cp_model
import pandas as pd
import matplotlib.pyplot as pltW
import numpy as np
import matplotlib.patches as mpatches
import xlwt
from pathlib import Path
import datetime as dt
import plotly
import plotly.express as px


# This function aims to save the data calculated from ortools into a excel file
def write_file(solver, visibility, ts_dict_2d_par_antenne, duration_ts_dict_2d_par_antenne, data_output_path):

    book = xlwt.Workbook(encoding='utf-8')
    sheet1 = book.add_sheet(u'datasheet', cell_overwrite_ok=True)

    sheet1.write(0, 0, 'Task') 
    sheet1.write(0, 1, 'Start')  
    sheet1.write(0, 2, 'Finish')
    sheet1.write(0, 3, 'Name')
    sheet1.write(0, 4, 'Color')
    sheet1.write(0, 5, 'Opacity')
    sheet1.write(0, 6, 'Information')
    i = 1
    sat_ant_list = []
    antname_index = 0
    for key in ts_dict_2d_par_antenne:
        duation_list = duration_ts_dict_2d_par_antenne[key]
        j = 0
        for ts in ts_dict_2d_par_antenne[key]:
            satlite = key.split(":")[0]
            antname = key.split(":")[1]
            if ((key not in sat_ant_list) and ((len(ts_dict_2d_par_antenne[key]) != 0)and (solver.Value(ts)!=-1))):
                antname_index = antname_index +1
                sub_df = visibility[(visibility.Sat ==satlite)&(visibility.Ant==antname)]
                for index,vis in sub_df.iterrows():
                        sheet1.write(i, 0, key)
                        sheet1.write(i, 1, int(vis['Start']))
                        sheet1.write(i, 2, int(vis['End']))
                        sheet1.write(i, 3, str(index) + " "+ satlite + " " + antname)
                        sheet1.write(i, 4, antname_index*5)
                        sheet1.write(i, 5, 0.05)
                        sheet1.write(i, 6, "Start Time="+str(vis['Start'])+ "; End Time: " + str(vis['End']))
                        i = i+1
            if (len(ts_dict_2d_par_antenne[key]) != 0):
                if (solver.Value(ts)!=-1):
                    sheet1.write(i, 0, key)
                    sheet1.write(i, 1, solver.Value(ts))
                    sheet1.write(i, 2, int(solver.Value(ts))+ int(duation_list[j]))
                    sheet1.write(i, 3, str(ts))
                    sheet1.write(i, 4, antname_index*5)
                    sheet1.write(i, 5, 1)
                    sheet1.write(i, 6, "Start Time="+str(solver.Value(ts))+ "; End Time: " + str(int(solver.Value(ts))+ int(duation_list[j])))
                    i = i + 1
            j = j + 1
    book.save(data_output_path)

# This function aims to create gantt diagarm with the input excel file
def gantt_diagram(input_path):
    EXCEL_FILE = Path.cwd() / input_path
    # Read Dataframe from Excel file
    df = pd.read_excel(EXCEL_FILE)
    # Assign Columns to variables
    tasks = df["Task"]
    start = df["Start"]
    reference = dt.datetime(2022,1,1,0,0)
    datetime_series_s = start.astype('timedelta64[s]') + reference
    time_series_s = pd.to_datetime(datetime_series_s, unit='s')
    finish = df["Finish"]
    datetime_series_e = finish.astype('timedelta64[s]') + reference
    time_series_e = pd.to_datetime(datetime_series_e, unit='s')
    color = df["Color"]
    opacity = df ["Opacity"]
    information = df["Name"]
    # Create Gantt Chart
    fig = px.timeline(
        df, x_start=time_series_s, x_end=time_series_e, y=tasks, color=color, title="Task Overview", opacity = opacity, hover_name = information
    )
    # Upade/Change Layout
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title_font_size=42, font_size=18, title_font_family="Arial")

    # Interactive Gantt
    # fig = ff.create_gantt(df)
    # Save Graph and Export to HTML
    plotly.offline.plot(fig, filename="Task_Overview_Gantt.html")

# This function aims to extract data from the official files that include satlite and visibility constraints
def extraire (task_path, visibility_path):
    # extraire des taches
    header = ["Task number","Satellite","Priority","Duration","Earliest","Latest","Repetitive","Number occ","Min time lag","Max time lag"]
    with open(task_path) as f:
        lines = f.readlines()
    data_i = []
    for i in range(3,len(lines)):
        data_i.append(lines[i].strip().split())
    data_df = pd.DataFrame(data_i,columns=header) # data frame for nominal data
    with open(visibility_path) as f:
        visibs = f.readlines()
    header_visibs = []
    data_visibs = []
    for i in range(len(visibs)):
        if i == 0:
            header_visibs = visibs[i].strip().split()
        else:
            data_visibs.append(visibs[i].strip().split())
    data_visib_df = pd.DataFrame(data_visibs,columns=header_visibs)
    return [data_df, data_visib_df]

# data_input : [taskfile, visibilityfile]
# data_output_path : path string
def Solver_PIE(data_input_path, data_output_path):
    """Minimal CP-SAT example to showcase calling the solver."""
#  ----------------------------------Initialisation----------------------------------------------- #
    # Create model
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    # Get data from file
    [data_df, data_visib_df] = extraire(data_input_path[0],data_input_path[1])

    # Creates the variables.
    data_visib_df_copy = data_visib_df.copy()
    data_visib_df_copy.loc[:,'End']= data_visib_df['End'].astype(int)
    data_visib_df_copy.loc[:,'Start'] = data_visib_df['Start'].astype(int)
    time_limit_right_all = int(data_visib_df_copy['End'].max());

    # different kinds of list to save the ts (Find corresponding ts more efficiently)
    ts_list_2d_par_tache = []
    ts_dict_2d_par_antenne = {}
    duration_ts_dict_2d_par_antenne = {}   # Need to save duartion because we need this information to add corresponding constarints
    ts_list = []
    obj_var_tache_list = []    # To calculate the score of the objective function
    priority_list_par_tache =[]
    # Initialisation of different list of ts according to different antenne in different satellite
    for _,vis in data_visib_df.iterrows():
        antenne_name = str(vis['Sat'])+':'+ str(vis['Ant'])
        if antenne_name not in ts_dict_2d_par_antenne:
            ts_ant_list = []
            duration_ts_list = []
            x_ts = {antenne_name:ts_ant_list}
            ts_dict_2d_par_antenne.update(x_ts)
            x_duration = {antenne_name:duration_ts_list}
            duration_ts_dict_2d_par_antenne.update(x_duration)


# ----------------------------------Create decision variables--------------------------------------- #     
    # For every task in the tasklist
    for _,tache in data_df.iterrows():
        ts_list = []
        antennes = [ants for ants in data_visib_df[data_visib_df["Sat"]==str(tache["Satellite"])]["Ant"].drop_duplicates()]
        nb_antenne = len(antennes)
        ts_bool_and_list = []
        ts_bool_negative_list = []
        temp_depart_limit = int(tache["Earliest"])
        temp_end_limit = int(tache["Latest"])
        duration = int(tache["Duration"])
        N = int(tache["Repetitive"])
        priority = int(tache["Priority"])
        min_time_lag = int(tache["Min time lag"])
        max_time_lag = int(tache["Max time lag"])
        repetition = int((temp_end_limit - temp_depart_limit)/(duration+min_time_lag))
        # repetition = 10 # set the maximux repetition 

        if (N == 1):
            ts_max_list = []
            ts_list_repetition_total = []
            for i in range(repetition):
                ts_list_repetition = []
                ts_list_repetition_total.append(ts_list_repetition)
                ts_bool_negative_list_repetition = []
                ts_bool_repetition_union_list = []
                
                for ant in antennes:
                    # Choose antenna to put ts
                    antenne_name = str(tache["Satellite"])+':'+ str(ant)
                    ts = model.NewIntVar(-1, temp_end_limit-duration, "Repetition task: %s ,ant: %s, Start time-> Tache: %s, Sat: %s, Ant: %s" % (str(i+1),str(ant), tache["Task number"],tache["Satellite"],  ant))
                    ts_bool_negative = model.NewBoolVar("t_bool_negative: Tache repetition: %s, Ant: %s" % (tache["Task number"], ant))
                    ts_bool_negative_list_repetition.append(ts_bool_negative)
                    # append every list the corresponding values
                    ts_dict_2d_par_antenne[antenne_name].append(ts)
                    duration_ts_dict_2d_par_antenne[antenne_name].append(duration)
                    ts_list_repetition.append(ts)
                    model.Add(ts==-1).OnlyEnforceIf(ts_bool_negative)  
                    # Add start time constarint for the repetition constraint
                    # Add the earliest start time of a task: if the ts == -1, we neglige the start time constarint
                    list_union = []
                    bool_after = model.NewBoolVar("bool_after-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
                    model.Add(ts >= temp_depart_limit).OnlyEnforceIf(bool_after)           
                    list_union.append(bool_after)
                    list_union.append(ts_bool_negative)
                    model.Add(sum(list_union)==1)

                    visibilities = data_visib_df[(data_visib_df["Sat"]==str(tache["Satellite"])) & (data_visib_df["Ant"]==str(ant))]
                    # Add visibility constarints for the created ts
                    temp_union = []
                    for index_vis,vis in visibilities.iterrows():
                        ts_bool_ge  = model.NewBoolVar("t_bool_ge: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        ts_bool_le  = model.NewBoolVar("t_bool_le: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        ts_bool_and = model.NewBoolVar("t_bool_and: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        tmp_ts = []
                        tmp_ts.append(ts_bool_ge)
                        tmp_ts.append(ts_bool_le)
                        model.Add(ts <= (int(vis['End'])-duration)).OnlyEnforceIf(ts_bool_le)  
                        model.Add(ts >= int(vis['Start'])).OnlyEnforceIf(ts_bool_ge)
                        model.Add(sum(tmp_ts)==2).OnlyEnforceIf(ts_bool_and)
                        temp_union.append(ts_bool_and)
                        ts_bool_repetition_union_list.append(ts_bool_and)
                    model.Add(sum(temp_union)<=1) # Means in all visibility interval, the task created could only be executed less one time. 
                model.Add(sum(ts_bool_repetition_union_list)<=1)
                model.Add(sum(ts_bool_negative_list_repetition)>=(nb_antenne-1))
                model.Add(sum(ts_bool_repetition_union_list) +sum(ts_bool_negative_list_repetition) ==nb_antenne)
                ts_list_2d_par_tache.append(ts_list_repetition)
                ts_ant_max = model.NewIntVar(-1, time_limit_right_all, 'obj_max')
                model.AddMaxEquality(ts_ant_max ,ts_list_repetition)
                ts_max_list.append(ts_ant_max)

            # min time lag and max time lag
            for i in range(len(ts_max_list)):
                bool_negative_i = model.NewBoolVar("t_bool_i: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                bool_min_time_lag =  model.NewBoolVar("bool_min_time_lag: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                bool_max_time_lag =  model.NewBoolVar("bool_max_time_lag: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                model.Add(ts_max_list[i]==-1).OnlyEnforceIf(bool_negative_i)
                for j in range(i+1,len(ts_max_list)):
                    union_union_list = []
                    union_list = []
                    and_list = []
                    bool_or = model.NewBoolVar("t_bool_or: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                    bool_negative_j = model.NewBoolVar("t_bool_j: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                    # bool_and = model.NewBoolVar("t_bool_or: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                    model.Add(ts_max_list[j]==-1).OnlyEnforceIf(bool_negative_j)
                    union_list.append(bool_negative_i)
                    union_list.append(bool_negative_j)
                    model.Add(sum(union_list)==1).OnlyEnforceIf(bool_or)
                    union_union_list.append(bool_or)
                    ts_abs_diff1 = model.NewIntVar(-time_limit_right_all, time_limit_right_all, 'obj_max')
                    ts_abs_diff2 = model.NewIntVar(-time_limit_right_all, time_limit_right_all, 'obj_max')
                    ts_abs = model.NewIntVar(-time_limit_right_all, time_limit_right_all, 'obj_max')
                    # min time lag (ts[i]==-1 or ts[j]==-1) or abs(ts[i]-ts[j])>=min time lag
                    model.Add(ts_abs_diff1==(ts_max_list[i]-ts_max_list[j]))
                    model.Add(ts_abs_diff2==(ts_max_list[j]-ts_max_list[i]))
                    model.AddMaxEquality(ts_abs,[ts_abs_diff1,ts_abs_diff2])
                    model.Add(ts_abs>=min_time_lag).OnlyEnforceIf(bool_min_time_lag)
                    # model.Add(ts_abs<=max_time_lag+duration).OnlyEnforceIf(bool_max_time_lag)
                    and_list.append(bool_min_time_lag)
                    # and_list.append(bool_max_time_lag)
                    # model.Add(sum(and_list)==2).OnlyEnforceIf(bool_and)
                    union_union_list.append(bool_min_time_lag)
                    model.Add(sum(union_union_list)==1)

                    # Add max time lag
                    if j > 0:
                        bool_non_negative_i = model.NewBoolVar("t_bool_i: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        model.Add(ts_max_list[i]>= 0).OnlyEnforceIf(bool_non_negative_i)
                        bool_non_negative_j = model.NewBoolVar("bool_non_negative_j: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        model.Add(ts_max_list[j]>= 0).OnlyEnforceIf(bool_non_negative_i)
                        union_list = []
                        and_list = []
                        and_and_list = []
                        union_union_list = []
                        union_list.append(bool_negative_i)
                        and_list.append(bool_non_negative_i)
                        # bool_leq = model.NewBoolVar("bool_leq: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        bool_non_negative_j_1 = model.NewBoolVar("bool_non_negative_j_1: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        bool_negative_j_1 =  model.NewBoolVar("bool_negative_j_1: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        bool_and_and = model.NewBoolVar("bool_and_and: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        bool_union_union = model.NewBoolVar("bool_union_union: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        bool_and = model.NewBoolVar("bool_and: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                        ## add max time lag
                        ## a[i] = -1
                        ## ou
                        ## a[i] != -1  and [  a[j+1]  = -1
                        ##                 [  a[j+1] != -1 and a[j] = -1 and abs(a[i]-a[j+1]) >= (max time lag + duration)
                        model.Add(ts_max_list[j-1]== -1).OnlyEnforceIf(bool_negative_j_1)
                        # model.Add(ts_max_list[i]< ts_max_list[j+1]).OnlyEnforceIf(bool_leq)
                        model.Add(ts_max_list[j-1]>= 0).OnlyEnforceIf(bool_non_negative_j_1)

                        and_and_list.append(bool_non_negative_j)
                        and_and_list.append(bool_negative_j_1)
                        model.Add(ts_abs<=max_time_lag+duration).OnlyEnforceIf(bool_max_time_lag)
                        and_and_list.append(bool_max_time_lag)
                        model.Add(sum(and_and_list)==3).OnlyEnforceIf(bool_and_and)

                        union_union_list.append(bool_negative_j)
                        union_union_list.append(bool_and_and)
                        model.Add(sum(union_union_list)==1).OnlyEnforceIf(bool_union_union)

                        and_list.append(bool_union_union)
                        and_list.append(bool_non_negative_i)
                        model.Add(sum(and_list)==2).OnlyEnforceIf(bool_and)

                        union_list.append(bool_negative_i)
                        union_list.append(bool_and)
                        model.Add(sum(union_list)==1)

        else:
            for ant in antennes:
                antenne_name = str(tache["Satellite"])+':'+ str(ant)
                visibilities = data_visib_df[(data_visib_df["Sat"]==str(tache["Satellite"])) & (data_visib_df["Ant"]==str(ant))]
                # Define variables for every task and add "latest time" constraint
                ts = model.NewIntVar(-1,temp_end_limit-duration, "Start time-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
                ts_bool_negative = model.NewBoolVar("t_bool_negative: Tache: %s, Ant: %s" % (tache["Task number"],ant))

                # append every list the corresponding values
                ts_dict_2d_par_antenne[antenne_name].append(ts)
                duration_ts_dict_2d_par_antenne[antenne_name].append(duration)
                ts_list.append(ts)
                model.Add(ts==-1).OnlyEnforceIf(ts_bool_negative)   
                ts_bool_negative_list.append(ts_bool_negative)
                # Add start time constarint for this ts
                # Add the earliest start time of a task: if the ts == -1, we neglige the start time constarint
                list_union = []
                bool_sup = model.NewBoolVar("bool_sup-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
                model.Add(ts>=temp_depart_limit).OnlyEnforceIf(bool_sup)
                ts_bool_not_equal_1 = model.NewBoolVar("ts_bool_not_equal_1-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
                model.Add(ts==-1).OnlyEnforceIf(ts_bool_not_equal_1)
                list_union.append(bool_sup)
                list_union.append(ts_bool_not_equal_1)
                model.Add(sum(list_union)==1)

            # Add visibility constarints for the created ts
                temp_union = []
                for index_vis,vis in visibilities.iterrows():
                    ts_bool_ge = model.NewBoolVar("t_bool_ge: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                    ts_bool_le = model.NewBoolVar("t_bool_le: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                    ts_bool_and = model.NewBoolVar("t_bool_and: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                    tmp_ts = []
                    tmp_ts.append(ts_bool_ge)
                    tmp_ts.append(ts_bool_le)
                    model.Add(ts<=(int(vis['End'])-duration)).OnlyEnforceIf(ts_bool_le)  
                    model.Add(ts>=int(vis['Start'])).OnlyEnforceIf(ts_bool_ge)
                    model.Add(sum(tmp_ts)==2).OnlyEnforceIf(ts_bool_and)
                    temp_union.append(ts_bool_and)
                    ts_bool_and_list.append(ts_bool_and)
                model.Add(sum(temp_union)<=1) # Means in all visibility interval, the task created could only be executed less one time. 
            model.Add(sum(ts_bool_and_list)==1) # Means in all visibility interval, the task created could only be executed only one time in all antenna. 
            model.Add(sum(ts_bool_negative_list)==(nb_antenne-1)) # Count non negative value and make sure this could be 1
            ts_list_2d_par_tache.append(ts_list)
            priority_list_par_tache.append(priority)
            if N==1:
                for i in len(ts_list_repetition_total):
                    obj_var_chaque_tache = model.NewIntVar(0, time_limit_right_all, 'obj_max')
                    model.AddMaxEquality(obj_var_chaque_tache, ts_list_repetition_total[i])
                    obj_var_tache_list.append(obj_var_chaque_tache)
            else:
                obj_var_chaque_tache = model.NewIntVar(0, time_limit_right_all, 'obj_max')
                model.AddMaxEquality(obj_var_chaque_tache, ts_list)
                obj_var_tache_list.append(obj_var_chaque_tache)     

    # Add the "limitation that the same antenne cannot transmit two tache at the same time" constraint 
    ts_ant_list = []
    duration_ant_list = []
    sat_list_temp = []
    for key in ts_dict_2d_par_antenne:
        ts_list_TEMP = ts_dict_2d_par_antenne[key]
        duration_list_TEMP = duration_ts_dict_2d_par_antenne[key]
        satlite = key.split(":")[0]
        if (satlite not in sat_list_temp):
            sat_list_temp.append(satlite)
            ts_list = []
            duration_list = []
            ts_ant_list.append(ts_list)
            duration_ant_list.append(duration_list)
        sat_index = sat_list_temp.index(satlite)
        for ts_temp in ts_list_TEMP:
            ts_ant_list[sat_index].append(ts_temp)
        for duration_temp in duration_list_TEMP:
            duration_ant_list[sat_index].append(duration_temp)
    
    for sat in sat_list_temp:
        sat_index = sat_list_temp.index(sat)
        ts_list = ts_ant_list[sat_index]
        duration_list = duration_ant_list[sat_index]

        if (len(ts_list)==0):
            continue
        for i in range(len(ts_list)):
            ts_bool_equal_1 = model.NewBoolVar("ts_bool_equal_1: %s"% str(ts_list[i]))
            model.Add(ts_list[i]==-1).OnlyEnforceIf(ts_bool_equal_1)
            for j in range(i+1,len(ts_list)):
                temp_bool_union = []
                bool_smaller = model.NewBoolVar("smaller")
                bool_bigger = model.NewBoolVar("bigger")
                model.Add((ts_list[i]+duration_list[i])<=ts_list[j]).OnlyEnforceIf(bool_smaller)
                model.Add(ts_list[i]>=ts_list[j] +duration_list[j]).OnlyEnforceIf(bool_bigger)
                temp_bool_union.append(bool_smaller)
                temp_bool_union.append(bool_bigger)
                temp_bool_union.append(ts_bool_equal_1)
                model.Add(sum(temp_bool_union)==1)

    model.Maximize(sum([int(1 / priority_list_par_tache[i]*1000) for i in range(len(obj_var_tache_list))]))

   # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print results on terminal
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Maximum of objective functionW: {solver.ObjectiveValue()}\n')
        
    print('\nStatistics')
    print(f'  status   : {solver.StatusName(status)}')
    print(f'  conflicts: {solver.NumConflicts()}')
    print(f'  branches : {solver.NumBranches()}')
    print(f'  wall time: {solver.WallTime()} s')
    # Export data from list to excel
    write_file(solver, data_visib_df, ts_dict_2d_par_antenne, duration_ts_dict_2d_par_antenne, data_output_path)

    # Read data form excel and draw it in 
    gantt_diagram(data_output_path)
def main():
    """Minimal CP-SAT example to showcase calling the solver."""
    Solver_PIE(["./PIE_SXS10_data/nominal/test_data.txt","./PIE_SXS10_data/visibilities.txt"], 'Solution Data.xls')

if __name__ == '__main__':
    main()
