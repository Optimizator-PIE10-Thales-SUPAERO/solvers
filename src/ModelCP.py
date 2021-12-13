import collections
from ortools.sat.python import cp_model

<<<<<<< HEAD
import parser 
import SatClass
import TaskClass
import AntClass

model = cp_model.CpModel() 
     
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
=======
from parser import ParserForRequirements as pfr
from parser import ParserForVisibilities as pfv

model = cp_model.CpModel()
dict_visib = {}
dict_non_visib = {}

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

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

def get_dict_non_visib(dict_visib):
    
    for element in dict_visib:
        list_no_sort = dict_visib[element]
        list_sort = sorted(list_no_sort)
        for i in range(len(list_sort)):
            if i == 0: 
                dict_non_visib[element] = [(-1,list_sort[i][0]-1)]
            else:
                dict_non_visib[element].append((list_sort[i-1][1]+1,list_sort[i][0]-1))
            i += 1 # increase the index
    #print(dict_non_visib)
    return dict_non_visib


def SimpleSatProgram(n_tasks,n_antennes):
    """ CP-SAT example to showcase calling the solver."""

    print("\n================START MODEL=================\n")
    # Creates the model.
    # [START model]
    model = cp_model.CpModel()
    # [END model]

    # number of variables : tasks * antennes

    # bounds for time
    upper_bound = 1175490
    lower_bound = 0

    # Creates the variables.
    # [START variables]
    num_vals = n_tasks*n_antennes

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                            'start job index duration')

    # Creates job intervals and add to the corresponding lists.
    variables_matrix = {}
    intervals_in_antenne = collections.defaultdict(list)
    intervals_in_task = collections.defaultdict(list)

    dict_by_task = {}
    
    for task_id in range(n_tasks):
        list_task = []
        for antenne_id in range(n_antennes):
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

    print("--------------MODEL PARAMETERS-------------")
    # print("intervals in each task ", intervals_in_task)
    print("variables matrix : ", variables_matrix)


    print("---------------CONTRAINTS----------------")

    print("Contraint1: duration for each task")
    # Contraint 1 : pour chaque tache
    for task_id in intervals_in_task :
        print(intervals_in_task[task_id])
        model.Add(sum([i.end - i.start for i in intervals_in_task[task_id]]) == 3000) 
        # TODO : 100 -> duration
        
>>>>>>> 3f803aebde46d759f7dbec86378cdbda584c3284

    print("Contraint2: No overlap for all intervals of each antenne")
    # Contraint 2 : pour chaque antenne
    for antenne_id in intervals_in_antenne:
        print(intervals_in_antenne[antenne_id])
        model.AddNoOverlap(intervals_in_antenne[antenne_id])

    # Contraint 3: pour chaque position dans le matrix
    print("Contraint3: No overlap for interval variable and non-visib intervals (not variables) ")
    for task_id in range(n_tasks):
        for antenne_id in range(n_antennes):
            if (task_id+1,antenne_id+1) in dict_non_visib.keys():
                list_intervals = dict_non_visib[task_id+1,antenne_id+1]
                print(list_intervals)
                for s,e in list_intervals:
                    t1_bool = model.NewBoolVar("t1_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    t2_bool = model.NewBoolVar("t2_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    # First Try
                    model.Add(variables_matrix[task_id,antenne_id].start > e).OnlyEnforceIf(t1_bool)
                    model.Add(variables_matrix[task_id,antenne_id].end < s).OnlyEnforceIf(t2_bool)

                    # Another method
                    t1_bool_and = model.NewBoolVar("t1_and_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    t2_bool_and = model.NewBoolVar("t2_and_"+str(task_id)+str(antenne_id)+str(s)+str(e))
                    model.Add(t1_bool_and==1).OnlyEnforceIf(t1_bool)
                    model.Add(t2_bool_and==1).OnlyEnforceIf(t2_bool)
                    tmp_t1_t2 = []
                    tmp_t1_t2.append(t1_bool_and)
                    tmp_t1_t2.append(t2_bool_and)
                    model.Add(sum(tmp_t1_t2) == 1)
                # TODO : to verify if it works for fixed start, end, interval
                # model.AddNoOverlap(list_intervals)

    # [END constraints]

    # Creates a solver and solves the model.
    # [START solve]
    solver = cp_model.CpSolver()
    # solver.parameters.enumerate_all_solutions = True
    solution_printer = VarArraySolutionPrinter(intervals_in_antenne)
    status = solver.Solve(model,solution_printer)
    # [END solve]

<<<<<<< HEAD
if __name__ == 'main':
    parser_req = parser.ParserForRequirements('./../PIE_SXS10_data/nominal/scenario_10SAT_nominal1.txt')
    parser_visib = parser.ParserForVisibilities('./../PIE_SXS10_data/visibilities.txt')
=======
#    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#        print('Status = %s' % solver.StatusName(status))
#        print('Number of solutions found: %i' % solution_printer.solution_count())
#    else:
#        print('No solution found.')

    print('\nStatistics')
    print(f'  status   : {solver.StatusName(status)}')
    print(f'  conflicts: {solver.NumConflicts()}')
    print(f'  branches : {solver.NumBranches()}')
    print(f'  wall time: {solver.WallTime()} s')


if __name__ == '__main__':
    parser_req = pfr('./../PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt')
    parser_visib = pfv('./../PIE_SXS10_data/visibilities_test.txt')
>>>>>>> 3f803aebde46d759f7dbec86378cdbda584c3284

    data_df = parser_req.get_requirements_data()
    data_visib_df = parser_visib.get_visibs_data()

<<<<<<< HEAD

=======
    # print(data_df)
    # print(data_visib_df)
>>>>>>> 3f803aebde46d759f7dbec86378cdbda584c3284

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

    # construct the matrix for visib
    # initialize
    for i in range(len(data_visib_df)):
        dict_visib[data_visib_df["Sat"][i],data_visib_df["Ant"][i]] = []

    print("========================")
    print("Initialization for the matrix of visibility")
    print(dict_visib)
    # add element
    for i in range(len(data_visib_df)):
        dict_visib[data_visib_df["Sat"][i],data_visib_df["Ant"][i]].append((data_visib_df['Start'][i],data_visib_df['End'][i]))

    print("========================")
    print("After add elements : \n", dict_visib)

    dict_non_visib = get_dict_non_visib(dict_visib)

    # change keys for dict_non_visib
    oldkeys = dict_non_visib.keys()
    for sat,ant in list(oldkeys):
        sat_id = int(sat.replace("SAT",""))
        ant_id = int(ant.replace("ANT",""))
        new_key = (sat_id,ant_id)
        dict_non_visib[new_key] = dict_non_visib.pop((sat,ant))

    print("========================")
    print("NON visibility of sat : \n", dict_non_visib)

    SimpleSatProgram(3,3)

