"""Simple solve."""
from abc import abstractproperty
from datetime import time
from os import X_OK
from ortools.sat.python import cp_model
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

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
    [data_df, data_visib_df] = extraire('./PIE_SXS10_data/nominal/scenario_10SAT_nominal_with_oneoff1.txt','./PIE_SXS10_data/visibilities.txt')
    # Creates the variables.
    tache_nombre = len(data_df)
    antenne_nombre = len(data_visib_df["Ant"].drop_duplicates())
    x = data_visib_df.copy()
    x.loc[:,'End']= data_visib_df['End'].astype(int)
    time_limit_right_all = int(x['End'].max());

    # two kinds of list to save the ts
    ts_list_2d_par_tache = []
    ts_dict_2d_par_antenne = {}
    duration_ts_dict_2d_par_antenne = {}
    ts_list = []
    ts_bool_ge = []
    ts_bool_le = []
    obj_var_tache_list = []

    # 创建根据不同的antenne而生成不同的tache所对应的list
    for index,vis in data_visib_df.iterrows():
        antenne_name = str(vis['Sat'])+':'+ str(vis['Ant'])
        if antenne_name not in ts_dict_2d_par_antenne:
            ts_ant_list = []
            duration_ts_list = []
            x_ts = {antenne_name:ts_ant_list}
            ts_dict_2d_par_antenne.update(x_ts)
            x_duration = {antenne_name:duration_ts_list}
            duration_ts_dict_2d_par_antenne.update(x_duration)
            
    
    # 针对每个任务，加入visibilite的条件限制
    for index_tache,tache in data_df.iterrows():
        ts_list = []
        antennes = [ants for ants in data_visib_df[data_visib_df["Sat"]==str(tache["Satellite"])]["Ant"].drop_duplicates()]
        nb_antenne = len(antennes)
        # Pour chaque antenne, creer un variable de ts
        ts_bool_and_list = []
        ts_bool_negative_list = []
        for ant in antennes:
            # 计算antenne_name 用于寻找合适list
            antenne_name = str(tache["Satellite"])+':'+ str(ant)
            # 取tache和visiblite的需要使用的值
            visibilities = data_visib_df[(data_visib_df["Sat"]==str(tache["Satellite"])) & (data_visib_df["Ant"]==str(ant))]
            temp_depart_limit = int(tache["Earliest"])
            temp_end_limit = int(tache["Latest"])
            duration = int(tache["Duration"])
            # 对于每一行，我们创造一个ts用于定义其初始位置， 并且创建一个interval用于添加 Nooverlap条件
            ts = model.NewIntVar(-1,temp_end_limit-duration, "Start time-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            te = model.NewIntVar(-1,temp_end_limit, "End time-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            ts_bool_negative = model.NewBoolVar("t_bool_negative: Tache: %s, Ant: %s" % (tache["Task number"],ant))
            # interval = model.NewIntervalVar(ts, duration, te, "Interval -> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            # ts_valide = model.NewIntVar(-1,temp_end_limit-duration, "ts_valid-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant))
            # b = model.NewBoolVar("t_bool_valid: Tache: %s, Ant: %s" % (tache["Task number"],ant))
            # model.Add(ts!=(-1)).OnlyEnforceIf(b)
            # model.Add(ts_valide = ts).OnlyEnforceIf(b)
            ts_dict_2d_par_antenne[antenne_name].append(ts)
            duration_ts_dict_2d_par_antenne[antenne_name].append(duration)
            # print (ts_dict_2d_par_antenne[antenne_name])
            ts_list.append(ts)
            model.Add(ts==-1).OnlyEnforceIf(ts_bool_negative)
            ts_bool_negative_list.append(ts_bool_negative)

            # 添加一个任务的最早的开始时间和最晚的开始时间
            # model.Add(ts<=(temp_end_limit-duration))
            list_union = []
            bool_sup = model.NewBoolVar("bool_sup-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
            model.Add(ts>=temp_depart_limit).OnlyEnforceIf(bool_sup)
            ts_bool_not_equal_1 = model.NewBoolVar("ts_bool_not_equal_1-> Tache : %s, Sat: %s, Ant: %s" % (tache["Task number"],tache["Satellite"], ant)) 
            model.Add(ts==-1).OnlyEnforceIf(ts_bool_not_equal_1)
            list_union.append(bool_sup)
            list_union.append(ts_bool_not_equal_1)
            model.Add(sum(list_union) == 1)

        # 添加天线可用的条件 visibilite
            temp_union = []
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
                model.Add(sum(tmp_ts)==2).OnlyEnforceIf(ts_bool_and)
                temp_union.append(ts_bool_and)
                ts_bool_and_list.append(ts_bool_and)
            model.Add(sum(temp_union)<=1)

        # 添加每个任务只能被传输一次的限制
        model.Add(sum(ts_bool_and_list)==1)
        model.Add(sum(ts_bool_negative_list)==(nb_antenne-1))
        ts_list_2d_par_tache.append(ts_list)  
        obj_var_chaque_tache = model.NewIntVar(0, time_limit_right_all, 'obj_max')
        model.AddMaxEquality(obj_var_chaque_tache, ts_list)
        obj_var_tache_list.append(obj_var_chaque_tache)

    # 添加同一antenne不能同时传输两个tache的限制
    # 该种方式出现运算问题，尝试换一种方式
    for key in ts_dict_2d_par_antenne:
        if len(ts_dict_2d_par_antenne[key])>=2:
            ts_list = ts_dict_2d_par_antenne[key]
            duration_list = duration_ts_dict_2d_par_antenne[key]

            for i in range(len(ts_dict_2d_par_antenne[key])):
                ts_bool_equal_1 = model.NewBoolVar("intersect: %s"% str(ts_list[i]))
                
                model.Add(ts_list[i]==-1).OnlyEnforceIf(ts_bool_equal_1)
                
                for j in range(i+1,len(ts_dict_2d_par_antenne[key])):
                    # print (j)
                    # ts_bool_or = model.NewBoolVar("intersect: %s"% str(ts_list[i]))
                    temp_bool_union = []
                    bool_smaller = model.NewBoolVar("smaller")
                    bool_bigger = model.NewBoolVar("bigger")
                    model.Add((ts_list[i]+duration_list[i])<=ts_list[j]).OnlyEnforceIf(bool_smaller)
                    model.Add(ts_list[i]>=ts_list[j] +duration_list[j]).OnlyEnforceIf(bool_bigger)
                    temp_bool_union.append(bool_smaller)
                    temp_bool_union.append(bool_bigger)
                    temp_bool_union.append(ts_bool_equal_1)
                    model.Add(sum(temp_bool_union)==1)

    obj_var = model.NewIntVar(0, time_limit_right_all, 'valeur maximum des variables de decision')

    model.AddMaxEquality(obj_var, obj_var_tache_list)
    model.Minimize(sum(obj_var_tache_list))
   # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Maximum of objective function: {solver.ObjectiveValue()}\n')
        # for tsl in ts_list_2d_par_tache:
        #     for ts in tsl:
        #         print('%s = %i' % (str(ts),solver.Value(ts)))
        #     print()
        for key in ts_dict_2d_par_antenne:
            for ts in ts_dict_2d_par_antenne[key]:
                print('%s = %i' % (str(ts),solver.Value(ts)))
            # print()
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


    # cmap = plt.get_cmap('gnuplot')
    # sats = data_visib_df["Sat"].drop_duplicates().to_list()
    # colors = [cmap(i) for i in np.linspace(0, 1, len(sats))]
    # # print (colors)
    # sat_ant_names = {}
    # i = 0
    # for index, vis in data_visib_df.iterrows():
    #     tempstr = str(vis['Sat']) +":" +str(vis['Ant'])
    #     if not (tempstr in sat_ant_names.keys()):
    #         sat_ant_name = {tempstr:i}
    #         sat_ant_names.update(sat_ant_name)
    #         i = i+1
    # for index, vis in data_visib_df.iterrows():
    #     tempstr = str(vis['Sat']) +":" +str(vis['Ant'])
    #     X = [int(vis['Start']), int(vis['End'])]
    #     Y = [sat_ant_names[tempstr], sat_ant_names[tempstr]]
    #     plt.plot(X,Y,color=colors[sats.index(vis["Sat"])])

    # # plt.ylim([-1, 16])
    # # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
    # # labels = [ant for ant in ant_list]
    # # plt.legend(lines, labels, loc='upper right',ncol = 4)
    # plt.show()



if __name__ == '__main__':
    main()