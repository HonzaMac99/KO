#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import numpy as np
import sys

PRINT = False


def in_cycles(cycles, u, v):
    for cycle in cycles:
        if u in cycle:
            idx = cycle.index(u)
            if cycle[(idx+1) % len(cycle)] == v:
                return True


# using dfs to find all paths from start to end
def dfs(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            new_paths = dfs(graph, node, end, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths


def extend_graph(graph, edge):
    u, v, c = edge
    if u not in graph:
        graph[u] = []
    if v not in graph:
        graph[v] = []
    graph[u].append(v)


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
        # input_file = "public/instances/instance_4.txt"
        input_file = "in.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        if len(sys.argv) > 3:
            time_th = sys.argv[3]

    # Model parameters
    bigM = 10000
    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        n = int(input_data[0])

        # adj matrix: adj[i, j] = edge_cost if there is edge from i to j, otw. adj[i, j] = 0
        adj = np.zeros((n, n))
        edges = []
        graph = {}
        for i in range(1, n+1):
            [u, v, c] = list(map(int, input_data[i].split(" ")))
            edge = [u-1, v-1, c]
            adj[u-1, v-1] = c
            edges.append(edge)
            extend_graph(graph, edge)

    edges.sort(reverse=True, key=lambda el: el[2])  # sort by highest cost

    # Model variables
    xs = m.addVars(n, n, vtype=g.GRB.BINARY)  # is there an edge [i, j]
    # cs = m.addVars(n, n, vtype=g.GRB.INTEGER)  # cost of edge [i, j]

    # cycles = []
    for i in range(n):
        [u, v, c] = edges.pop(0)
        # if in_cycles(cycles, u, v):
        #     continue
        new_cycles = dfs(graph, v, u)
        # disable all cycles
        for cycle in new_cycles:
            c_len = len(cycle)
            m.addConstr(g.quicksum(xs[cycle[i], cycle[i+1]] for i in range(c_len-1)) + xs[cycle[-1], cycle[0]] <= c_len-1, name="cycle")
            if PRINT:
                for i in range(c_len-1):
                    print(cycle[i]+1, cycle[i+1]+1)
                print(cycle[-1]+1, cycle[0]+1)
                print()
        # cycles.extend(new_cycles)

    # cannot set xs to 1 if there is no edge to be enabled
    for i in range(n):
        for j in range(n):
            m.addConstr(xs[i, j] <= adj[i, j], name="edge")

    # Model objective function
    m.setObjective(g.quicksum(xs[i, j] * adj[i, j] for i in range(n) for j in range(n)), sense=g.GRB.MAXIMIZE)

    m.optimize()

    # output
    edges_out = []
    total_cost = 0
    for j in range(n):
        for i in range(n):
            e_cost = adj[i, j]
            if xs[i, j].X == 0 and e_cost != 0:
                edges_out.append([i+1, j+1])
                total_cost += int(e_cost)

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


    # for i in range(n):
    #     for j in range(n):
    #         print(int(xs[i, j].X * adj[i, j]), end=" ")
    #     print()
    # print()
