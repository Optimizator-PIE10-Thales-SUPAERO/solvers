"""Simple solve."""
from ortools.sat.python import cp_model
import pandas as pd

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
    infinity = 100000000
    # Creates the model.
    [data_df, data_visib_df] = extraire('./PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt','./PIE_SXS10_data/visibilities.txt')

    # Creates the variables.
    var_upper_bound = 10000000
    tache_nombre = len(data_df)
    list_antenne_taches = []
    # Le parcours des taches
    for index_tache in data_df.index:
        # print("Total income in "+ data_df["Task number"][i]+ " is:"+str(data_df["Satellite"][i]))
        sub_data_visib_df = data_visib_df[ data_visib_df.Sat == str(data_df["Satellite"][index_tache]) ]
        sub_data_visib_df = sub_data_visib_df.drop_duplicates(subset=['Ant'])
        # print (sub_data_visib_df["Ant"][j])
        ant_nombre = len(sub_data_visib_df)
        for ant in sub_data_visib_df["Ant"]:
            time_list = []
            # Creer des variables necessaire
            for tache in range(tache_nombre):
                time_list.append(model.NewIntVar(0, infinity, f'x[{str(data_df["Task number"][tache])},{str(ant)},{str(data_df["Satellite"][tache])}]'))
                time_list.append(model.NewIntVar(0, infinity, f'y[{str(data_df["Task number"][tache])},{str(ant)},{str(data_df["Satellite"][tache])}]'))
                len_timelist = len(time_list)

                # ajouter les contriantes de la duree d'excution
                yy = time_list[len_timelist-2]
                xx = time_list[len_timelist-1]
                model.Add(
                     yy-xx <= int(data_df["Duration"][tache])
                )
                model.Add(
                     yy-xx >= 0
                )
                nume = model.NewIntVar(0, 10000000, 'numerator')
                model.Add(nume == yy-xx )
                division = model.NewIntVar(0, 10000000, 'division')
                model.AddModuloEquality(division, nume, int(data_df["Duration"][tache]))
                model.Add(
                    division == 0
                )

                # model.Add(
                #             ((time_list[len(time_list)-2]- time_list[len(time_list)-1]) == int(data_df["Duration"][tache]))|
                #             ((time_list[len(time_list)-2]- time_list[len(time_list)-1]) == 0)
                #         )

            # ajouter les contraintes de la visibilite des antennes
            sub_data_visib_df_ant = data_visib_df[ data_visib_df.Ant == ant]
            sub_data_visib_df_ant_sat = sub_data_visib_df_ant [ data_visib_df.Sat == str(data_df["Satellite"][index_tache])]
            sub_data_visib_df_ant_sat['Start'] =  sub_data_visib_df_ant_sat['Start'].astype('int')
            sub_data_visib_df_ant_sat['End'] =  sub_data_visib_df_ant_sat['End'].astype('int')
            sub_data_visib_df_ant_sat = sub_data_visib_df_ant_sat.sort_values(by='Start',ascending=True)


            for index_visibilite in range(len(sub_data_visib_df_ant_sat)-1):
                print (int(sub_data_visib_df_ant_sat.iloc[index_visibilite+1].at['Start']))
                if (sub_data_visib_df_ant_sat.iloc[index_visibilite].at['End'] < sub_data_visib_df_ant_sat.iloc[index_visibilite+1].at['Start']):
                    for j in range(tache_nombre):
                        #  
                        model.Add(
                            (time_list[2*j+1] <= sub_data_visib_df_ant_sat.iloc[index_visibilite].at['End']) |
                            (time_list[2*j]   >= sub_data_visib_df_ant_sat.iloc[index_visibilite+1].at['Start'])
                        )
            list_antenne_taches.append(time_list)
            # ajouter les contraintes de superposition
            for i in range(ant_nombre):
                for j in range(ant_nombre):
                    if (i!=j):
                        model.Add(
                                (time_list[2*i]  >= (time_list[2*j+1])) | 
                                (time_list[2*i+1] <= time_list[2*j])
                                ) 
            
        list_antenne_taches_len = len(list_antenne_taches)
        # ajouter les contraintes de unicite d'execution
        for i in range (tache_nombre):
            model.Add(
                        sum(list_antenne_taches[j][2*i+1]- time_list[j][2*i]
                                for j in range(list_antenne_taches_len)) == data_df["duration"][i]
                     )
                # x = model.NewIntVar(0, solver.infinity(), 'x'+str(k))       
                # byinfinity = solver.infinity()
                # x = {}
                # for j in range(data['num_vars']):
                #     x[j] = solver.IntVar(0, infinity, 'x[%i]' % j)
    # for tache in data_df:
        
        # for ant in tache.Satellite:
            
        
    # x = model.NewIntVar(0, var_upper_bound, '')
    # y = model.NewIntVar(0, var_upper_bound, 'y')
    # z = model.NewIntVar(0, var_upper_bound, 'z')

    # # Creates the constraints.
    # model.Add(2 * x + 7 * y + 3 * z <= 50)
    # model.Add(3 * x - 5 * y + 7 * z <= 45)
    # model.Add(5 * x + 2 * y - 6 * z <= 37)

    # model.Maximize(2 * x + 2 * y + 3 * z)

    # # Creates a solver and solves the model.
    # solver = cp_model.CpSolver()
    # status = solver.Solve(model)

    # if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    #     print(f'Maximum of objective function: {solver.ObjectiveValue()}\n')
    #     print(f'x = {solver.Value(x)}')
    #     print(f'y = {solver.Value(y)}')
    #     print(f'z = {solver.Value(z)}')
    # else:
    #     print('No solution found.')

    # # Statistics.
    # print('\nStatistics')
    # print(f'  status   : {solver.StatusName(status)}')
    # print(f'  conflicts: {solver.NumConflicts()}')
    # print(f'  branches : {solver.NumBranches()}')
    # print(f'  wall time: {solver.WallTime()} s')


if __name__ == '__main__':
    main()