#!/usr/bin/env python3

import gurobipy as g

# Create empty optimization model.
# In Python, only one environment exists and it is created internally 
# in the Model() constructor. 
model = g.Model()

# Create variables x, y.
x = model.addVar(lb=0, ub=g.GRB.INFINITY, vtype=g.GRB.CONTINUOUS, name="x")
y = model.addVar(lb=0, ub=g.GRB.INFINITY, vtype=g.GRB.CONTINUOUS, name="y")

# Set objective: maximize 32x + 25y
model.setObjective(32*x + 25*y, sense=g.GRB.MAXIMIZE)

# Add constraint: 5x + 4y <= 59
model.addConstr(5*x + 4*y <= 59, "cons1")

# Add constraint: 4x + 3y <= 46
model.addConstr(4*x + 3*y <= 46, "cons2")

# Solve the model.
model.optimize()

# Print the objective and the values of the decision variables in the solution.
print("Optimal objective:", model.objVal)
print("x:", x.x, "y:", y.x)
