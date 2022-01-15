"""Simple solve."""
from ortools.sat.python import cp_model
import pandas as pd


model = cp_model.CpModel()

t1 = model.NewIntVar(12, 20, "t1")
t1_bool_ge = model.NewBoolVar("t1_bool_ge")
t1_bool_le = model.NewBoolVar("t1_bool_le")
t1_bool_and =  model.NewBoolVar("t1_bool_and")
tmp_t1 = []
tmp_t1.append(t1_bool_ge)
tmp_t1.append(t1_bool_le)
model.Add(t1 >= 15).OnlyEnforceIf(t1_bool_ge) # t1 >=12
model.Add(t1 <= 16).OnlyEnforceIf(t1_bool_le) # t1 <= 15
model.Add(sum(tmp_t1)==2).OnlyEnforceIf(t1_bool_and) # (t1 >=12)&&(t1 <= 15)

t2 = model.NewIntVar(12, 20, "t2")
t2_bool_ge = model.NewBoolVar("t2_bool_ge")
model.Add(t2_bool_ge ==1)
t2_bool_le = model.NewBoolVar("t2_bool_le")
t2_bool_and =  model.NewBoolVar("t2_bool_and")
tmp_t2 = []
tmp_t2.append(t2_bool_ge)
tmp_t2.append(t2_bool_le)
model.Add(t2 >= 11).OnlyEnforceIf(t2_bool_ge) # t2 >=16
model.Add(t2 <= 11).OnlyEnforceIf(t2_bool_le) # t2 <= 18
model.Add(sum(tmp_t2)==2).OnlyEnforceIf(t2_bool_and) #(t2 >=16) && (t2 <=18)

ts = model.NewIntVar(-1,1, "Start time-> Tache ")
te = model.NewIntVar(-1,1, "End time-> Tache ")
interval = model.NewIntervalVar(ts, 1, te,"HELLO")        
tmp_t1_t2 = []
tmp_t1_t2.append(t2_bool_and)
tmp_t1_t2.append(t1_bool_and)
model.Add(sum(tmp_t1_t2)==1) #((t1 >=12)&&(t1 <= 15))||((t2 >=16) && (t2 <=18))

solver = cp_model.CpSolver()
status = solver.Solve(model)

print('\nStatistics')
print(f'  status   : {solver.StatusName(status)}')
print(f'  conflicts: {solver.NumConflicts()}')
print(f'  branches : {solver.NumBranches()}')
print(f'  wall time: {solver.WallTime()} s')
print('%s = %i' % (str(t2_bool_ge),solver.Value(t2_bool_ge)))
print('%s = %i' % (str(t1),solver.Value(t1)))
print('%s = %i' % (str(t2),solver.Value(t2)))