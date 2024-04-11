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


# use the academic licence
with g.Env(params=opts) as env, g.Model(env=env) as m:
    # model = g.Model()

    if len(sys.argv) < 3:
        # Default file names
        input_file = "in.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    stripes = []

    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        # [n, w, h] = list(map(int, input_data[0].split(" ")))
        n = int(input_data[0])

        for i in range(1, n+1):
            data = input_data[i]
            c = ord(data[0])
            r = int(data[1])
            pos = [r, c]

    # Model parameters
    # bigM = np.sum(distances)*20

    # Model variables
    xs = m.addVars(n+1, n+1, vtype=g.GRB.BINARY)

    # Model constraints
    m.addConstrs(xs[i, i] == 0 for i in range(n+1))                                   # no one vertex cycles

    # Model objective function
    # m.setObjective(g.quicksum(distances[i, j] * xs[i, j] for i in range(n+1) for j in range(n+1)), sense=g.GRB.MINIMIZE)

    # for i in range(n+1):
    #     for j in range(1, n+1):
    #         m.addConstr(bigM*(1 - xs[i, j]) + S[j] >= S[i] + distances[i, j], name=f"S{i}{j}")

    m.optimize()

    ordering = []
    v_start = 0
    v_next = [i for i in range(n+1) if xs[v_start, i].X > 0.5][0]
    ordering.append(v_next)
    while v_next != 0:
        v_next = [i for i in range(n+1) if xs[v_next, i].X > 0.5][0]
        ordering.append(v_next)

    print("Ordering:", ordering[:-1])

    with open(output_file, 'w') as f:
        for i in range(len(ordering)-1):
            f.write(f"{ordering[i]} ")


    if __name__ == "__main__":
        ...



