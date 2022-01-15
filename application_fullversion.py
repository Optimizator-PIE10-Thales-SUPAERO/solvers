"""Simple solve."""
from abc import abstractproperty
from datetime import time
from os import X_OK
from ortools.sat.python import cp_model
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import xlwt
from pathlib import Path
import pandas as pd
import plotly
import plotly.express as px
import plotly.figure_factory as ff

def write_file(solver, ts_dict_2d_par_antenne, duration_ts_dict_2d_par_antenne, data_output_path):

    book = xlwt.Workbook(encoding='utf-8')
    sheet1 = book.add_sheet(u'datasheet', cell_overwrite_ok=True)

    sheet1.write(0, 0, 'Task') 
    sheet1.write(0, 1, 'Start')  
    sheet1.write(0, 2, 'Finish')
    sheet1.write(0, 3, 'name')
    sheet1.write(0, 4, 'Resource')
    i = 1
    for key in ts_dict_2d_par_antenne:
        duation_list = duration_ts_dict_2d_par_antenne[key]
        j = 0
    for ts in ts_dict_2d_par_antenne[key]:
            sheet1.write(i, 0, key)
            if (len(ts_dict_2d_par_antenne[key]) != 0):
                if (solver.Value(ts)!=-1):
                    sheet1.write(i, 1, solver.Value(ts))
                    sheet1.write(i, 2, int(solver.Value(ts))+ int(duation_list[j]))
                    sheet1.write(i, 3, str(ts))
                    sheet1.write(i, 4, "Black")
                    i = i + 1
            j = j + 1
    book.save('Solution Data.xls')

#  Pour extraire des donnees
def extraire (task_path, visibility_path):
    # extraire des taches
    header = ["Task number","Satellite","Priority","Duration","Earliest","Latest","Repetitive","Number occ","Min time lag","Max time lag"]
    with open(task_path) as f:
        lines = f.readlines()
    data_i = []
    for i in range(3,len(lines)):
        data_i.append(lines[i].strip().split())
    data_df = pd.DataFrame(data_i,columns=header) # data frame for nominal data
    # donnne des visibility
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

# version: "simple" or "complex"S
# data_input : [taskfile, visibilityfile]
# data_output_path : path string
def Solver_PIE(version, data_input_path, data_output_path):
    """Minimal CP-SAT example to showcase calling the solver."""

    # input correctness inspection
    if  not((version == "simple")or (version == "complex")):
        print ("The input of your function is illegal")
        return None

    # Create model
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    [data_df, data_visib_df] = extraire(data_input_path[0],data_input_path[1])
    # Creates the variables.
    x = data_visib_df.copy()
    x.loc[:,'End']= data_visib_df['End'].astype(int)
    time_limit_right_all = int(x['End'].max());

    # different kinds of list to save the ts
    ts_list_2d_par_tache = []
    ts_dict_2d_par_antenne = {}
    duration_ts_dict_2d_par_antenne = {}
    ts_list = []
    priority_list = []
    obj_var_tache_list = []

    # Create different list of ts according to different antenne in different satellite
    for index,vis in data_visib_df.iterrows():
        antenne_name = str(vis['Sat'])+':'+ str(vis['Ant'])
        if antenne_name not in ts_dict_2d_par_antenne:
            ts_ant_list = []
            duration_ts_list = []
            x_ts = {antenne_name:ts_ant_list}
            ts_dict_2d_par_antenne.update(x_ts)
            x_duration = {antenne_name:duration_ts_list}
            duration_ts_dict_2d_par_antenne.update(x_duration)
            
    
    # For every task in the tasklist
    for index_tache,tache in data_df.iterrows():
        ts_list = []
        antennes = [ants for ants in data_visib_df[data_visib_df["Sat"]==str(tache["Satellite"])]["Ant"].drop_duplicates()]
        nb_antenne = len(antennes)
        # for every task, create a different ts for different antenne
        ts_bool_and_list = []
        ts_bool_negative_list = []   # for calculate the -1 times
        for ant in antennes:
            # Get useful value from dataframe
            antenne_name = str(tache["Satellite"])+':'+ str(ant)
            visibilities = data_visib_df[(data_visib_df["Sat"]==str(tache["Satellite"])) & (data_visib_df["Ant"]==str(ant))]
            temp_depart_limit = int(tache["Earliest"])
            temp_end_limit = int(tache["Latest"])
            duration = int(tache["Duration"])
            N = int(tache["Repetitive"]) +1
            priority = int(tache["Priority"])

            # Define variables for every task
            ts = model.NewIntVar(-1,temp_end_limit-duration, "Start time-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            ts_bool_negative = model.NewBoolVar("t_bool_negative: Tache: %s, Ant: %s" % (tache["Task number"],ant))

            # append every list the corresponding values
            ts_dict_2d_par_antenne[antenne_name].append(ts)
            duration_ts_dict_2d_par_antenne[antenne_name].append(duration)
            ts_list.append(ts)
            priority_list.append(priority)
            model.Add(ts==-1).OnlyEnforceIf(ts_bool_negative)
            ts_bool_negative_list.append(ts_bool_negative)

            # Add the earliest start time of a task: if the ts == -1, we neglige the start time constarint
            list_union = []
            bool_sup = model.NewBoolVar("bool_sup-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
            model.Add(ts>=temp_depart_limit).OnlyEnforceIf(bool_sup)
            ts_bool_not_equal_1 = model.NewBoolVar("ts_bool_not_equal_1-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
            model.Add(ts==-1).OnlyEnforceIf(ts_bool_not_equal_1)
            list_union.append(bool_sup)
            list_union.append(ts_bool_not_equal_1)
            model.Add(sum(list_union) == 1)

        # visibility constarints
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
            if version == "simple":
                model.Add(sum(temp_union)<=1) # <= means two ts repetitive could be arranged to 1 visibility interval, but the maximum sum(temp_union) is equal to transfertimes
            if version == "complex":
                model.Add(sum(temp_union)<=N)
        # Add priority task transfer order limit
        if version == "complex":
            for i in range(len(ts_list)):
                pri_ts = priority_list[i]
                for j in range(i+1, len(ts_list)):
                    temp_union_pri = []
                    ts_bool_equal_1 = model.NewBoolVar("tempvar_bool_not_equal-1")
                    model.Add(ts_list[i]==-1).OnlyEnforceIf(ts_bool_equal_1)
                    ts_bool_pri = model.NewBoolVar("tempvar_bool_priority")
                    if (pri_ts<priority_list[j]):
                        model.Add(ts[i]<ts[j]).OnlyEnforceIf(ts_bool_pri)
                    if (pri_ts>priority_list[j]):
                        model.Add(ts[i]>ts[j]).OnlyEnforceIf(ts_bool_pri)
                    temp_union_pri.append(ts_bool_equal_1)
                    temp_union_pri.append(ts_bool_pri)
                    model.Add(sum(temp_union_pri)==1)

        # Add a limit that each task can only be transferred N times
        if version == "simple":
            model.Add(sum(ts_bool_and_list)<=1)
            model.Add(sum(ts_bool_negative_list)==(nb_antenne-1))
        if version == "complex":
            model.Add(sum(ts_bool_and_list)<=N)
            model.Add(sum(ts_bool_negative_list)==(nb_antenne-N)) # <= means two ts repetitive could be arranged to 1 visibility interval, but the maximum sum(temp_union) is equal to transfertimes
               
        model.Add(sum(ts_bool_and_list)<=N)
        model.Add(sum(ts_bool_negative_list)==(nb_antenne-N))
        ts_list_2d_par_tache.append(ts_list)  
        obj_var_chaque_tache = model.NewIntVar(0, time_limit_right_all, 'obj_max')
        model.AddMaxEquality(obj_var_chaque_tache, ts_list)
        obj_var_tache_list.append(obj_var_chaque_tache)

    # Add the limitation that the same antenne cannot transmit two tache at the same time
    for key in ts_dict_2d_par_antenne:
        if len(ts_dict_2d_par_antenne[key])>=2:
            ts_list = ts_dict_2d_par_antenne[key]
            duration_list = duration_ts_dict_2d_par_antenne[key]

            for i in range(len(ts_dict_2d_par_antenne[key])):
                ts_bool_equal_1 = model.NewBoolVar("intersect: %s"% str(ts_list[i]))
                model.Add(ts_list[i]==-1).OnlyEnforceIf(ts_bool_equal_1)
                
                for j in range(i+1,len(ts_dict_2d_par_antenne[key])):
                    temp_bool_union = []
                    bool_smaller = model.NewBoolVar("smaller")
                    bool_bigger = model.NewBoolVar("bigger")
                    model.Add((ts_list[i]+duration_list[i])<=ts_list[j]).OnlyEnforceIf(bool_smaller)
                    model.Add(ts_list[i]>=ts_list[j] +duration_list[j]).OnlyEnforceIf(bool_bigger)
                    temp_bool_union.append(bool_smaller)
                    temp_bool_union.append(bool_bigger)
                    temp_bool_union.append(ts_bool_equal_1)
                    model.Add(sum(temp_bool_union)==1)

    # Define the objectif variables to find the best solution Min(Max(ts))
    obj_var = model.NewIntVar(0, time_limit_right_all, 'valeur maximum des variables de decision')
    model.AddMaxEquality(obj_var, obj_var_tache_list)
    model.Minimize(sum(obj_var_tache_list))

   # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print results on terminal
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Maximum of objective function: {solver.ObjectiveValue()}\n')
        # print solution by task
        for tsl in ts_list_2d_par_tache:
            for ts in tsl:
                print('%s = %i' % (str(ts),solver.Value(ts)))
            print()

    # Export data from list to excel
    write_file(solver, ts_dict_2d_par_antenne, duration_ts_dict_2d_par_antenne, data_output_path)

    # Visualisation part
    # Draw Diagrame from excel file
    # EXCEL_FILE = Path.cwd() / "Solution Data.xls"
    # df = pd.read_excel(EXCEL_FILE)
    # colors = {'Green': 'rgb(0, 153, 51)',
    #       'Black': 'rgb(0, 0, 0)'}
    # name = df["name"]
    # # Create Gantt Chart
    # fig = ff.create_gantt(
    #     df, colors=colors, index_col='Resource', title="Task Overview"
    # )
    # fig.show()

    # EXCEL_FILE = Path.cwd() / "Solution Data.xls"
    # df = pd.read_excel(EXCEL_FILE)
    # tasks = df["Task"]
    # start = df["Start"]
    # finish = df["Finish"]
    # colors = {'Green': 'rgb(0, 153, 51)',
    #       'Black': 'rgb(0, 0, 0)'}

    # fig = px.timeline(
    #     df, x_start=start, x_end=finish, y=tasks, color=colors, title="Task Overview"
    # )

    # Upade/Change Layout
    # fig.update_yaxes(autorange="reversed")
    # fig.update_layout(title_font_size=42, font_size=18, title_font_family="Arial")

    # Interactive Gantt
    # fig = ff.create_gantt(df)

    # Save Graph and Export to HTML
    # plotly.offline.plot(fig, filename="Task_Overview_Gantt.html")
    # Upade/Change Layout
    # fig.update_yaxes(autorange="reversed")
    # fig.update_layout(title_font_size=42, font_size=18, title_font_family="Arial")

    # Interactive Gantt
    # fig = ff.create_gantt(df)

    # Save Graph and Export to HTML
    # plotly.offline.plot(fig, filename="Task_Overview_Gantt.html")


def main():
    """Minimal CP-SAT example to showcase calling the solver."""
    Solver_PIE("complex", ["./PIE_SXS10_data/nominal/scenario_10SAT_nominal_with_oneoff1.txt","./PIE_SXS10_data/visibilities.txt"], 'Solution Data.xls')

if __name__ == '__main__':
    main()