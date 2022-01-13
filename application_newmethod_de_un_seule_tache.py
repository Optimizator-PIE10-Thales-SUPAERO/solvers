"""Simple solve."""
from abc import abstractproperty
from datetime import time
from os import X_OK
from ortools.sat.python import cp_model
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self,ts_list):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__ts_list = ts_list
        self.__solution_count = 0
        self.__start_time = time.time()
    
    def solution_count(self):
            return self.__solution_count

    def on_solution_callback(self):
        current_time = time.time()
        print('Solution %i, time = %f s' %
            (self.__solution_count, current_time - self.__start_time))
        self.__solution_count += 1

        all_temp_depart = range(len(self.__ts_list))
        for i in all_temp_depart:
            print(f'x = {self.__ts_list[i]}')

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



def main():
    """Minimal CP-SAT example to showcase calling the solver."""
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    # Creates the model.
    [data_df, data_visib_df] = extraire('./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt','./PIE_SXS10_data/visibilities.txt')
    # Creates the variables.
    tache_nombre = len(data_df)
    antenne_nombre = len(data_visib_df["Ant"].drop_duplicates())
    x = data_visib_df.copy()
    x.loc[:,'End']= data_visib_df['End'].astype(int)
    time_limit_right_all = int(x['End'].max());

    # two kinds of list to save the ts
    ts_list_2d_par_tache = []
    ts_dict_2d_par_antenne = {}
    ts_list = []
    ts_bool_ge = []
    ts_bool_le = []
    obj_var_tache_list = []

    # 创建根据不同的antenne而生成不同的tache所对应的list
    for index,vis in data_visib_df.iterrows():
        antenne_name = str(vis['Sat'])+':'+ str(vis['Ant'])
        if antenne_name not in ts_dict_2d_par_antenne:
            ts_ant_list = []
            x = {antenne_name:ts_ant_list}
            ts_dict_2d_par_antenne.update(x)
    
    # 针对每个任务，加入visibilite的条件限制
    for index_tache,tache in data_df.iterrows():
        ts_list = []
        antennes = [ants for ants in data_visib_df[data_visib_df["Sat"]==str(tache["Satellite"])]["Ant"].drop_duplicates()]
        # Pour chaque antenne, creer un variable de ts
        ts_bool_and_list = []
        for ant in antennes:
            # 计算antenne_name 用于寻找合适list
            antenne_name = str(tache["Satellite"])+':'+ str(ant)
            # 取tache和visiblite的需要使用的值
            visibilities = data_visib_df[(data_visib_df["Sat"]==str(tache["Satellite"])) & (data_visib_df["Ant"]==str(ant))]
            time_limit_right_ant = int(tache['Latest'])
            time_limit_left_ant  = int(tache['Earliest'])
            duration = int(tache["Duration"])
            # 对于每一行，我们创造一个ts用于定义其初始位置， 并且创建一个interval用于添加 Nooverlap条件
            ts = model.NewIntVar(time_limit_left_ant-1,time_limit_right_ant-duration, "Start time-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            te = model.NewIntVar(time_limit_left_ant-1,time_limit_right_ant-duration, "End time-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            interval = model.NewIntervalVar(ts, duration, te, "Interval -> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            ts_dict_2d_par_antenne[antenne_name].append(interval)
            # print (ts_dict_2d_par_antenne[antenne_name])
            ts_list.append(ts)

            # 添加一个任务的最早的开始时间和最晚的开始时间
            temp_depart_limit = int(tache["Earliest"])
            temp_end_limit = int(tache["Latest"])
            model.Add(ts<=(temp_end_limit-duration))
            model.Add(ts>=temp_depart_limit)

            # 添加天线可用的条件 visibilite
            # temp_union = []
            ts_bool_ant = model.NewBoolVar("t_bool_ant: Tache: %s, Ant: %s" % (tache["Task number"],ant))
            for index_vis,vis in visibilities.iterrows():
                # print (vis['Start'] + " "+ vis['End'])
                ts_bool_ge = model.NewBoolVar("t_bool_ge: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                ts_bool_le = model.NewBoolVar("t_bool_le: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                ts_bool_and = model.NewBoolVar("t_bool_and: Ant: %s, Vis_index: %s" % (ant,str(index_vis)))
                tmp_ts = []
                tmp_ts.append(ts_bool_ge)
                tmp_ts.append(ts_bool_le)
                model.Add(ts<=(int(vis['End'])-duration)).OnlyEnforceIf(ts_bool_le)  
                model.Add(ts>=int(vis['Start'])).OnlyEnforceIf(ts_bool_ge)
                model.Add(ts_bool_and==1).OnlyEnforceIf(tmp_ts)
                # temp_union.append(ts_bool_and)
                ts_bool_and_list.append(ts_bool_and)
            # model.Add(sum(temp_union)==1)
        
        # 添加每个任务只能被传输一次的限制
        print (len(ts_bool_and_list))
        model.Add(sum(ts_bool_and_list)==1)
        ts_list_2d_par_tache.append(ts_list)  
        obj_var_chaque_tache = model.NewIntVar(0, time_limit_right_all, 'chaque tache des variables de decision')
        model.AddMaxEquality(obj_var_chaque_tache, ts_list)
        obj_var_tache_list.append(obj_var_chaque_tache)

    # 添加同一antenne不能同时传输两个tache的限制
    for key in ts_dict_2d_par_antenne:
        # print (len(ts_dict_2d_par_antenne[key]))
        if len(ts_dict_2d_par_antenne[key])>=2:
            model.AddNoOverlap(ts_dict_2d_par_antenne[key])
    obj_var = model.NewIntVar(0, time_limit_right_all, 'valeur maximum des variables de decision')

    model.Maximize(obj_var)
   # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Maximum of objective function: {solver.ObjectiveValue()}\n')
        for tsl in ts_list_2d_par_tache:
            for ts in tsl:
                print('%s = %i' % (str(ts),solver.Value(ts)))
            print()
        # for key in ts_dict_2d_par_antenne:
        #     print('%s = %i' % (str(ts_dict_2d_par_antenne[key]),solver.Value(ts_dict_2d_par_antenne[key])))
    else:
        print('No solution found.')

    # Statistics.
    print('\nStatistics')
    print(f'  status   : {solver.StatusName(status)}')
    print(f'  conflicts: {solver.NumConflicts()}')
    print(f'  branches : {solver.NumBranches()}')
    print(f'  wall time: {solver.WallTime()} s')


    cmap = plt.get_cmap('gnuplot')
    sats = data_visib_df["Sat"].drop_duplicates().to_list()
    colors = [cmap(i) for i in np.linspace(0, 1, len(sats))]
    # print (colors)
    sat_ant_names = {}
    i = 0
    for index, vis in data_visib_df.iterrows():
        tempstr = str(vis['Sat']) +":" +str(vis['Ant'])
        if not (tempstr in sat_ant_names.keys()):
            sat_ant_name = {tempstr:i}
            sat_ant_names.update(sat_ant_name)
            i = i+1
    for index, vis in data_visib_df.iterrows():
        tempstr = str(vis['Sat']) +":" +str(vis['Ant'])
        X = [int(vis['Start']), int(vis['End'])]
        Y = [sat_ant_names[tempstr], sat_ant_names[tempstr]]
        plt.plot(X,Y,color=colors[sats.index(vis["Sat"])])

    # plt.ylim([-1, 16])
    # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
    # labels = [ant for ant in ant_list]
    # plt.legend(lines, labels, loc='upper right',ncol = 4)
    plt.show()



if __name__ == '__main__':
    main()