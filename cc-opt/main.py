#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import numpy as np
import sys

PRINT = False


opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}

# use the academic licence
with g.Env(params=opts) as env, g.Model(env=env) as m:

    if len(sys.argv) < 3:
        # Default file names
        # input_file = "public/instances/instance_4.txt"
        input_file = "in.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        if len(sys.argv) > 3:
            time_th = sys.argv[3]

    # Model parameters
    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        n_edges = int(input_data[0])

        # adj matrix: adj[i, j] = edge_cost if there is edge from i to j, otw. adj[i, j] = 0
        adj = np.zeros((n_edges, n_edges))   # n_edges > n_vertices
        edges = []
        for i in range(1, n_edges+1):
            [u, v, c] = list(map(int, input_data[i].split(" ")))
            edge = [u-1, v-1, c]
            adj[u-1, v-1] = c
            edges.append(edge)

    n_verts = int(np.array(edges)[:, :2].max() + 1) # max from all u, v in edges
    # edges.sort(reverse=True, key=lambda el: el[2])  # sort by highest cost

    # Model variables
    xs = m.addVars(n_edges, vtype=g.GRB.BINARY)         # 1 if edge i is disabled
    # cs = m.addVars(n_edges, vtype=g.GRB.INTEGER)        # cost of edge i
    top_ord = m.addVars(n_verts, lb=0, vtype=g.GRB.INTEGER)   # topological ordering of vertices

    bigM = 10 * n_verts
    for i in range(n_edges):
        [u, v, c] = edges[i]
        # u [top. lvl. k] -----> v [top. lvl. k-1]
        m.addConstr(top_ord[u] <= top_ord[v] - 0.5 + bigM*xs[i], name="top_ord")

    # Model objective function
    m.setObjective(g.quicksum(xs[i] * edges[i][2] for i in range(n_edges)), sense=g.GRB.MINIMIZE)

    m.optimize()

    # output
    edges_out = []
    total_cost = 0
    for i in range(n_edges):
        if xs[i].X == 1:
            [u, v, c] = edges[i]
            edges_out.append([u+1, v+1])
            total_cost += int(c)

    n_edges = len(edges_out)
    with open(output_file, 'w') as f:
        f.write(f"{total_cost}\n")
        print(total_cost)
        for i in range(n_edges-1):
            f.write(f"{edges_out[i][0]} {edges_out[i][1]}\n")
            print(f"{edges_out[i][0]} {edges_out[i][1]}")
        if n_edges > 0:
            f.write(f"{edges_out[-1][0]} {edges_out[-1][1]}\n")
            print(f"{edges_out[-1][0]} {edges_out[-1][1]}")

    print("----------------")
    for i in range(n_verts):
        print(f"v{i+1}: {int(top_ord[i].X)}")