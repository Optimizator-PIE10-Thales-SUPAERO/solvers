import collections
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
def SimpleSatProgram(model,dict_data,dict_non_visib,n_tasks,list_antennes):
    """ CP-SAT example to showcase calling the solver."""

    # number of variables : tasks * antennes
    n_antennes = len(list_antennes)
    # bounds for time
    upper_bound = 1175490
    lower_bound = 0

    # Creates the variables.
    # [START variables]
    num_vals = n_tasks*n_antennes

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_antennes_type = collections.namedtuple('assigned_antennes_type',
                                            'start end task antenne')

    # Creates job intervals and add to the corresponding lists.
    variables_matrix = {}

    # time periods in each antenne
    intervals_in_antenne = collections.defaultdict(list)

    # time periods in each task
    intervals_in_task = collections.defaultdict(list)

    dict_by_task = {}

    # Note that, here the index of task is related to the position, instead of real ID
    for task_id in range(n_tasks):
        list_task = []
        for antenne_id in list_antennes:
            suffix = '_%i_%i' % (task_id, antenne_id)
            start_var = model.NewIntVar(lower_bound, upper_bound, 'start' + suffix)
            end_var = model.NewIntVar(lower_bound, upper_bound, 'end' + suffix)
            size_var = model.NewIntVar(lower_bound, upper_bound, 'size' + suffix)
            interval_var = model.NewIntervalVar(start=start_var,size=size_var, end=end_var,name="interval"+suffix) # size is a variable not a constant here, more complex

            variables_matrix[task_id,antenne_id] = task_type(start=start_var,end=end_var,interval=interval_var)
            intervals_in_antenne[antenne_id].append(interval_var)
            intervals_in_task[task_id].append(task_type(start=start_var,end=end_var,interval=interval_var))
            list_task.append(interval_var)
            #list_line.append(model.NewIntervalVar(start=start_var,end=end_var,name="interval"+suffix))
        #list_variables.append(list_task)
        dict_by_task[task_id] = list_task
    # [END variables]

    # Creates the constraints.
    # [START constraints]

    print("\n-->MODEL PARAMETERS<--")
    # print("intervals in each task ", intervals_in_task)
    # print("variables matrix : ", variables_matrix)
    
    print("-->CONTRAINTS<--")

    print("Contraint1: duration for each task")
    print("Contraint2: No overlap for all intervals of each task/satellite")
    # Contraint 1 : pour chaque tache
    for task_id in intervals_in_task :
        # print(intervals_in_task[task_id])
        model.Add(sum([i.end - i.start for i in intervals_in_task[task_id]]) == int(dict_data['Duration'][task_id]))
        # Contraint 2 : pour chaque satellite
        model.AddNoOverlap([i.interval for i in intervals_in_task[task_id]])


    print("Contraint3: No overlap for all intervals of each antenne")
    # Contraint 3 : pour chaque antenne
    for antenne_id in intervals_in_antenne:
        # print(intervals_in_antenne[antenne_id])
        model.AddNoOverlap(intervals_in_antenne[antenne_id])

    # Contraint 4: pour chaque position dans le matrix
    print("Contraint4: No overlap for interval variable and non-visib intervals (not variables) ")
    for task_id in range(n_tasks):
        for antenne_id in list_antennes:
            if (task_id+1,antenne_id) in dict_non_visib.keys():
                list_intervals = dict_non_visib[task_id+1,antenne_id]
                # print(list_intervals)
                for s,e in list_intervals:
                    t1_bool = model.NewBoolVar("t1_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    t2_bool = model.NewBoolVar("t2_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    # First Try
                    model.Add(variables_matrix[task_id,antenne_id].start > e).OnlyEnforceIf(t1_bool)
                    model.Add(variables_matrix[task_id,antenne_id].end < s).OnlyEnforceIf(t2_bool)

                    t1_bool_and = model.NewBoolVar("t1_and_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    t2_bool_and = model.NewBoolVar("t2_and_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    model.Add(t1_bool_and==1).OnlyEnforceIf(t1_bool)
                    model.Add(t2_bool_and==1).OnlyEnforceIf(t2_bool)
                    tmp_t1_t2 = []
                    tmp_t1_t2.append(t1_bool_and)
                    tmp_t1_t2.append(t2_bool_and)
                    model.Add(sum(tmp_t1_t2) == 1)


    print("-->FINISED<--")
    # [END constraints]

    # [START objective]
    obj_var = model.NewIntVar(lower_bound,upper_bound,'objective')
    # sat_id = int(dict_data['Satellite'][task_id].strip('SAT'))
    model.AddMaxEquality(obj_var,[
        variables_matrix[task_id,antenne_id].end
        for task_id in range(n_tasks) for antenne_id in list_antennes
    ])
    model.Minimize(obj_var)
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

    print('\n-->Statistics<--')
    print(f'  status   : {solver.StatusName(status)}')
    print(f'  conflicts: {solver.NumConflicts()}')
    print(f'  branches : {solver.NumBranches()}')
    print(f'  wall time: {solver.WallTime()} s')
    print("-->FINISED<--")

    # create one list of assigned intervals for each task:
    assigned_intervals = collections.defaultdict(list)
    for task_id in range(n_tasks):
        for antenne_id in list_antennes:
            assigned_intervals[task_id].append(
                assigned_antennes_type(start=solver.Value(
                    variables_matrix[task_id,antenne_id].start),
                                       end=solver.Value(
                                           variables_matrix[task_id,antenne_id].end),
                                       task=task_id,
                                       antenne=antenne_id
                )
            )

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#        print('Status = %s' % solver.StatusName(status))
#        print('Number of solutions found: %i' % solution_printer.solution_count())
        output = ''
        for task_id in range(n_tasks):
            sol_line_antennes = dict_data['Task number'][task_id] + ':  '
            sol_line = '        '
            for intervals in assigned_intervals[task_id]:
                # name = 'task_%i_antenne_%i' % (intervals.task,intervals.antenne)
                name = dict_data['Satellite'][intervals.task] + '_' + 'ANT%i' % intervals.antenne
                # Add spaces to output align columns
                sol_line_antennes += '%-15s' %name

                start = intervals.start
                end = intervals.end
                sol_tmp = '[%i,%i]' % (start, end)

                # Add spaces to output align columns
                sol_line += '%-15s' % sol_tmp
            sol_line += '\n'
            sol_line_antennes += '\n'
            output += sol_line_antennes
            output += sol_line
        print('\n-->RESULTS<--')
        print(f'Optimal time usage : {solver.ObjectiveValue()}')
        print(output)
        print('-->FINISHED<--\n')
    else:
        print('No solution found.')



