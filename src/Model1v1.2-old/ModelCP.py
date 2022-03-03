import collections
import math
from ortools.sat.python import cp_model

"""Print intermediate solutions."""
"""
class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s=%i' % (v, self.Value(v)), end=' ')
        print()

    def solution_count(self):
        return self.__solution_count
"""

"""First Version Model"""
def SimpleSatProgram(model,dict_data,dict_non_visib,n_tasks,list_sats,list_antennes):
    """ CP-SAT example to showcase calling the solver."""

    # number of variables : tasks * antennes
    n_antennes = len(list_antennes)
    # bounds for time
    upper_bound = 1175490
    lower_bound = 0
    # duration
    dict_duration = dict_data['Duration']
    # priorities collections
    dict_priorities = dict_data['Priority']
    # reperitive collections
    dict_repetitive = dict_data['Repetitive']
    dict_occ = dict_data['Number occ']
    print(dict_data['Duration'])

    # satellites
    dict_satellites = dict_data['Satellite']

    # min lag and max lag
    dict_min_lag = dict_data['Min time lag']
    dict_max_lag = dict_data['Max time lag']

    dict_max_repetive = {}
    for key in dict_duration:
        if dict_occ[key] == -1:
            dict_max_repetive[key] = math.floor(upper_bound/(dict_duration[key]+25200))
        else:
            dict_max_repetive[key] = 1
    print("@dict_max_repetive:\n",dict_max_repetive)

    # seperate the tasks by satellites
    groups = collections.defaultdict(list)
    for task_id in dict_satellites:
        groups[dict_satellites[task_id]].append(task_id)
    print("@groups by satellites",groups)



    # Creates the variables.
    # [START variables]
    num_vals = n_tasks*n_antennes

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', ['stack','height'])
    rep_type = collections.namedtuple('rep_type', ['start','end','interval'])
   

    # Creates job intervals and add to the corresponding lists.
    variables_matrix = {}

    # variables for repetitive
    variables_rep = {}

    # time in each task in rep_type
    dict_occ_task = collections.defaultdict(list)

    # Note that, here the index of task is related to the position, instead of real ID
    for task_id in range(n_tasks):
        list_task = []
        # variables of repetitive
        rep = model.NewIntVar(1,dict_max_repetive[task_id],'rep_%i'%task_id)
        variables_rep[task_id] = rep
        for antenne_id in list_antennes:
            suffix = '_%i_%i' % (task_id, antenne_id)
            list_rep_var = []
            for rep_id in range(dict_max_repetive[task_id]):
                start_var = model.NewIntVar(lower_bound, upper_bound, 'start' + suffix)
                end_var = model.NewIntVar(lower_bound, upper_bound, 'end' + suffix)
                size_var = model.NewIntVar(lower_bound, upper_bound, 'size' + suffix)
                interval_var = model.NewIntervalVar(start=start_var,size=size_var, end=end_var,name="interval"+suffix) # size is a variable not a constant here, more complex

                rep_var = rep_type(start=start_var,end=end_var,interval=interval_var)
                # list_rep_var.append(rep_var)
                variables_matrix[task_id,antenne_id,rep_id] = rep_var

    # [END variables]

    # Creates the constraints.
    # [START constraints]

    print("\n-->MODEL PARAMETERS<--")
    # print("intervals in each task ", intervals_in_task)
    # print("variables matrix : ", variables_matrix)
    
    print("-->CONTRAINTS<--")

    print("Constraint1: No overlap for all intervals of each task/satellite")
    # Constraint 1 : pour chaque tache
    # Constraint 1.5 : pour chaque satellite (include constraint1)

    for sat_id in list_sats :
        sat_name = "SAT"+str(sat_id)
        all_time_in_sat = []
        for task_id in groups[sat_name]:
            for antenne_id in list_antennes:
                for rep_id in range(dict_max_repetive[task_id]):
                    ele = variables_matrix[task_id,antenne_id,rep_id]
                    all_time_in_sat.append(ele.interval)
                    dict_occ_task[task_id].append(ele)
        model.AddNoOverlap(all_time_in_sat)

    print("Contraint2: No overlap for all intervals of each antenne")
    # Contraint 2 : pour chaque antenne
    for antenne_id in list_antennes:
        # print(intervals_in_antenne[antenne_id])
        """
        model.AddNoOverlap(intervals_in_antenne[antenne_id])
        """
        all_time_in_antenne = []
        for task_id in range(n_tasks):
            for rep_id in range(dict_max_repetive[task_id]):
                ele = variables_matrix[task_id,antenne_id,rep_id]
                all_time_in_antenne.append(ele.interval)
        model.AddNoOverlap(all_time_in_antenne)

    # Contraint 3: pour chaque position dans le matrix
    print("Contraint3: No overlap for interval variable and non-visib intervals (not variables) ")
    for task_id in range(n_tasks):
        for antenne_id in list_antennes:
            if (task_id+1,antenne_id) in dict_non_visib.keys():
                list_intervals = dict_non_visib[task_id+1,antenne_id]
                # print(list_intervals)
                for s,e in list_intervals:
                    for rep_id in range(dict_max_repetive[task_id]):
                        time = variables_matrix[task_id,antenne_id,rep_id]
                        t1_bool = model.NewBoolVar("t1_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                        t2_bool = model.NewBoolVar("t2_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                        # First Try
                        model.Add(time.start > e).OnlyEnforceIf(t1_bool)
                        model.Add(time.end < s).OnlyEnforceIf(t2_bool)

                        t1_bool_and = model.NewBoolVar("t1_and_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                        t2_bool_and = model.NewBoolVar("t2_and_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                        model.Add(t1_bool_and==1).OnlyEnforceIf(t1_bool)
                        model.Add(t2_bool_and==1).OnlyEnforceIf(t2_bool)
                        tmp_t1_t2 = []
                        tmp_t1_t2.append(t1_bool_and)
                        tmp_t1_t2.append(t2_bool_and)
                        model.Add(sum(tmp_t1_t2) == 1)

    # Contraint 4: Repetition is consider and each duration is fixed
    # pour tous les antennes de chaque tâche, il y a qu'un interval qui a une durée et les autres sont null.
    print("Constraint4: The duration and repetition requirements ")
    for task_id in range(n_tasks):
        tmp_c2 = []
        duration = int(dict_duration[task_id])
        list_duration = []
        for rep_id in range(dict_max_repetive[task_id]):
            bool_in_each_occ = []
            for antenne_id in list_antennes:
                time = variables_matrix[task_id,antenne_id,rep_id]
                t_bool = model.NewBoolVar("t_c2_"+str(task_id) + str(antenne_id) + str(rep_id))
                model.Add((time.end - time.start) == duration).OnlyEnforceIf(t_bool)
                list_duration.append(time.end-time.start)
                tmp_c2.append(t_bool)
                bool_in_each_occ.append(t_bool)
            model.Add(sum(bool_in_each_occ) == 1) # each occ/rep, there is only one antenne lancé
        model.Add(sum(tmp_c2) == variables_rep[task_id]) # sum of occ is equal to variable rep
        model.Add(sum(list_duration) == duration * variables_rep[task_id]) # sum of duration is equal to required duration * variable rep

    # Constraint 5: time margin between interval used should be bounded by min lag and max lag
    print("(ignore for now) Contraint5: Time margin between interval used should be bounded by min lag and max lag")
    
    '''
    for task_id in range(n_tasks):
        min_lag = dict_min_lag[task_id]
        max_lag = dict_max_lag[task_id]
        tmp_list_occ = dict_occ_task[task_id]
        for i in range(len(tmp_list_occ)):
            for j in range(i+1,len(tmp_list_occ)):
                e1 = tmp_list_occ[i]
                e2 = tmp_list_occ[j]
                bool_var1 = model.NewBoolVar("b_c5_1"+str(task_id)+str(i)+str(j))
                bool_var2 = model.NewBoolVar("b_c5_2"+str(task_id)+str(i)+str(j))
                bool_var3 = model.NewBoolVar("b_c5_3"+str(task_id)+str(i)+str(j))
                bool_var4 = model.NewBoolVar("b_c5_4"+str(task_id)+str(i)+str(j))
    
                model.Add(e1.start == e1.end).OnlyEnforceIf(bool_var1)
                model.Add(e2.start == e2.end).OnlyEnforceIf(bool_var2)
                model.Add(e1.end <= e2.start - min_lag).OnlyEnforceIf(bool_var3)
                model.Add(e1.end >= e2.start - max_lag).OnlyEnforceIf(bool_var3)
                model.Add(e2.end <= e1.start - min_lag).OnlyEnforceIf(bool_var4)
                model.Add(e2.end >= e1.start - max_lag).OnlyEnforceIf(bool_var4)
    
                tmp_bool_list = [bool_var1,bool_var2,bool_var3,bool_var4]
                model.Add(sum(tmp_bool_list) >= 1)
    '''

    print("-->FINISED<--")
    # [END constraints]

    # [START objective]
    # obj_var = model.NewIntVar(lower_bound,upper_bound,'objective') # CP solver is limited to Integer
    # objective 1 : min max end time of all tasks

    """
    model.AddMaxEquality(obj_var,[
        variables_matrix[task_id,antenne_id].end
        for task_id in range(n_tasks) for antenne_id in list_antennes
    ])

    model.Minimize(obj_var)
    """

    # objective 2: max score := 1/priority * 1000 * repetitives
    model.Maximize(sum([int(1 / dict_priorities[task_id] * 1000) * variables_rep[task_id] 
                        for task_id in range(n_tasks)]))
    
    # [END objective]

    # Creates a solver and solves the model.
    # [START solve]
    solver = cp_model.CpSolver()
    # solver.parameters.enumerate_all_solutions = True
    # solution_printer = VarArraySolutionPrinter(intervals_in_antenne)
    # status = solver.Solve(model,solution_printer)
    # [END solve]

    # DISPLAY THE RESULTS
    status = solver.Solve(model)

    # Pour 0 conflits [TO FIX]
#    while(solver.NumConflicts()>0):
#       status = solver.Solve(model)

    print('\n-->Statistics<--')
    print(f'  status   : {solver.StatusName(status)}')
    print(f'  conflicts: {solver.NumConflicts()}')
    print(f'  branches : {solver.NumBranches()}')
    print(f'  wall time: {solver.WallTime()} s')
    print("-->FINISED<--")

    # OUTPUT
    # Named tuple to manipulate solution information.
    
    assigned_antennes_type = collections.namedtuple('assigned_antennes_type',
                                            'start end task antenne occ')

    # create one list of assigned intervals for each task:
    assigned_intervals = collections.defaultdict(list)
    for task_id in range(n_tasks):
        for antenne_id in list_antennes:
            for rep_id in range(dict_max_repetive[task_id]):
                time = variables_matrix[task_id,antenne_id,rep_id]
                assigned_intervals[task_id].append(
                    assigned_antennes_type(start=solver.Value(time.start),
                                           end=solver.Value(time.end),
                                           task=task_id,
                                           antenne=antenne_id,
                                           occ=rep_id
                    )
                )
    

    assigned_repetition = []
    for task_id in range(n_tasks):
        assigned_repetition.append(solver.Value(variables_rep[task_id]))

    print("@assigned repetition for each task:\n",assigned_repetition)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#        print('Status = %s' % solver.StatusName(status))
#        print('Number of solutions found: %i' % solution_printer.solution_count())
        output = ''
        return_dict = collections.defaultdict(list)
        for task_id in range(n_tasks):
            sol_line_antennes = dict_data['Task number'][task_id] + ':  \n'
            sol_line = ''
            for assign in assigned_intervals[task_id]:
                dict_task = {}
                sat_name = "SAT%i" % list_sats[assign.task]
                ant_name = 'ANT%i' % assign.antenne
                occ_name = 'OCC%i' % assign.occ

                start = assign.start
                end = assign.end

                if(assign.start != assign.end):
                    name = sat_name + '_' + ant_name + '_' + occ_name
                    # Add spaces to output align columns
                    sol_line += '%-20s' %name
                    sol_tmp = '[%i,%i]' % (start, end)
                    # Add spaces to output align columns
                    sol_line += '%-15s\n' % sol_tmp



                # create return structure
                dict_task['satellite'] = sat_name
                dict_task['antenne'] = ant_name
                dict_task['start'] = start
                dict_task['end'] = end
                return_dict[dict_data['Task number'][task_id]].append(dict_task)
            
            sol_line += '\n'
            output += sol_line_antennes
            output += sol_line
        with open('result.txt', 'w') as f:
            f.write(output)
        print('\n-->RESULTS<--')
        print(f'Optimal score : {solver.ObjectiveValue()}')
        # print(output)
        # print(return_dict)
        print('-->FINISHED<--\n')
        return return_dict
    else:
        print('No solution found.')



