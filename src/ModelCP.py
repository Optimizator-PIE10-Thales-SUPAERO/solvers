import collections
from ortools.sat.python import cp_model

from parser import ParserForRequirements as pfr
from parser import ParserForVisibilities as pfv

model = cp_model.CpModel()
dict_visib = {}
dict_non_visib = {}
        
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
    # print(d_ants)
    return d_ants


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
    # Creates the model.
    # [START model]
    model = cp_model.CpModel()
    # [END model]

    # number of variables : tasks * antennes

    # bounds for time
    upper_bound = 10000
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
            interval_var = model.NewIntervalVar(start=start_var,size=size_var, end=end_var,name="interval"+suffix)

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


    # Contraint 1 : pour chaque tache
    for task_id in intervals_in_task :
        model.Add(sum([i.end - i.start for i in intervals_in_task[task_id]]) == 100) 
        # TODO : 100 -> duration        
        

    # Contraint 2 : pour chaque antenne
    for antenne_id in intervals_in_antenne:
        model.AddNoOverlap(intervals_in_antenne[antenne_id])

    # Contraint 3: pour chaque position dans le matrix
    for task_id in range(n_tasks):
        for antenne_id in range(n_antennes):
            if (task_id,antenne_id) in dict_non_visib.keys():
                list_intervals = dict_non_visib[task_id,antenne_id]
                for s,e in list_intervals:
                    model.Add(variables_matrix[task_id,antenne_id].start > e or variables_matrix[task_id,antenne_id].end < s ) 
                
                # TODO : to verify if it works for fixed start, end, interval
                # model.AddNoOverlap(list_intervals)

    # [END constraints]

    # Creates a solver and solves the model.
    # [START solve]
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    solution_printer = VarArraySolutionPrinter(variables_matrix)
    # [END solve]
    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_printer.solution_count())


if __name__ == '__main__':
    parser_req = pfr('./../PIE_SXS10_data/nominal/scenario_10SAT_nominal_example.txt')
    parser_visib = pfv('./../PIE_SXS10_data/visibilities.txt')

    data_df = parser_req.get_requirements_data()
    data_visib_df = parser_visib.get_visibs_data()

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

    # add element
    for i in range(len(data_visib_df)):
        dict_visib[data_visib_df["Sat"][i],data_visib_df["Ant"][i]].append((data_visib_df['Start'][i],data_visib_df['End'][i]))

    get_dict_non_visib(dict_visib)

    SimpleSatProgram(3,10)

    # for sat in list_sat:
    #     #name = data_df['Satellite'][i]

    #     # data visib for each satelite in the list
    #     data_visib = data_visib_df[data_visib_df['Sat']==sat]
    #     print(data_visib)

    #     # organize one dictionary for each ant
    #     d_ant_tmp = get_dict_ant_for_sat(data_visib)
    #     ID = int(name.strip('SAT'))
    #     priority = data_df['Priority'][i]
    #     eariest = int(data_df['Eariest'][i])
    #     latest = int(data_visib_df['Latest'][i])