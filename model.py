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


# Create the constraint
# model.Add(x != y)

# Call the solver
# solver = cp_model.CpSolver()
# status = solver.Solve(model)
