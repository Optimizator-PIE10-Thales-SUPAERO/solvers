# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 10:44:40 2021

@author: Ange
"""
#Import the parser file
exec(open("parser.py").read())

# Import the libraries
import collections
from ortools.sat.python import cp_model

#Define the parameters
T = []

# Declare the model
model = cp_model.CpModel()


# Create the variables
num_vals = len(list_tasks)
int_tasks = [model.IntervalVar(size = data_df["Duration"]0, num_vals - 1, 'int_task')

# Create one interval variable per job operation
job_operations = [[interval_var(size=DURATION[j][m], name='O{}-{}'.format(j,m)) for m in range(NB_MACHINES)] for j in range(NB_JOBS)]

# Create the constraint
# model.Add(x != y)

# Call the solver
# solver = cp_model.CpSolver()
# status = solver.Solve(model)
