#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import numpy as np
import sys

opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}

def my_callback(model, where):
    # Callback is called when some event occur . The type of event is
    # distinguished using argument ’’where ’ ’.
    # In this case , we want to perform something when an integer
    # solution is found , which corresponds to ’’GRB . Callback . MIPSOL ’’.
    if where == g.GRB.Callback.MIPSOL:
        # TODO : your code here ...

        # Get the value of variable x[i, j] from the solution .
        # You may also pass a list of variables to the method .
        value = model.cbGetSolution(x[i, j])

        # Add lazy constraint to model .
        model.cbLazy(...)

    model.optimize(my_callback)


def get_distances(stripes, n, w, h):
    stripes = np.array(stripes)
    distances = np.ones((n, n)) * np.inf

    for i in range(n):
        for j in range(n):
            # last 3-column of i - first 3-column of j
            distances[i, j] = np.sum(np.abs(stripes[i, :, (w-1)*3:w*3] - stripes[j, :, 0:3]))

    return distances


# use the academic licence
with g.Env(params=opts) as env, g.Model(env=env) as m:
    # model = g.Model()
    # m.Params.lazyConstraints = 1

    # input_file = sys.argv[1]
    # output_file = sys.argv[2]

    # Default file names
    input_file = "in.txt"
    output_file = "out.txt"

    stripes = []

    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        [n, w, h] = list(map(int, input_data[0].split(" ")))

        for i in range(n):
            stripe_map = list(map(int, input_data[i+1].split(" ")))
            stripe = np.array(stripe_map).reshape(h, w*3)
            stripes.append(stripe)

    # Model parameters
    distances = get_distances(stripes, n, w, h)
    print(distances)
    bigM = np.sum(distances)*2

    # Model variables
    xs = {}
    for i in range(n):
        for j in range(n):
            xs[i, j] = m.addVar(vtype=g.GRB.BINARY, name=f"x{i}{j}")
    S = m.addVars(n, lb=0, vtype=g.GRB.INTEGER)


    #TODO: implement the lazy constraints

    # Model constraints
    for i in range(n):
        m.addConstr(xs[i, i] == 0, name=f"v{i}{i}")                                 # no one vertex cycles
        m.addConstr(g.quicksum(xs[i, j] for j in range(n)) == 1, name=f"v{i}_out")  # only one edge out
        m.addConstr(g.quicksum(xs[j, i] for j in range(n)) == 1, name=f"v{i}_in")   # only one edge in

    for i in range(n):
        for j in range(1, n):
            m.addConstr(bigM*(1 - xs[i, j]) + S[j] >= S[i] + distances[i][j], name=f"S{i}{j}")

    # # Model objective function
    m.setObjective(g.quicksum(distances[i][j] * xs[i, j] for j in range(n) for i in range(n)), sense=g.GRB.MINIMIZE)

    m.optimize()

    m.display()
    for i in range(n):
        print(f"S[{i}]: ", S[i].X)

