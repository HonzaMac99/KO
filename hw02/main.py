#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import numpy as np
import sys

LAZY_CS = False

opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}


def find_one_tour(edges):
    tour = []
    tour.append(edges[0])
    start = edges[0][0]
    temp = edges[0][1]
    edges.remove(tour[0])

    while True:
        for edge in edges:
            if edge[0] == temp:
                tour.append(edge)
                if edge[1] != start:
                    temp = edge[1]
                    edges.remove(edge)
                    break
                else:
                    edges.remove(edge)
                    return tour, edges


def find_shortest_tour(edges):
    shortest_tour = []
    while len(edges) > 1:
        tour, edges = find_one_tour(edges)
        if len(shortest_tour) == 0:
            shortest_tour = tour
        else:
            if len(tour) < len(shortest_tour):
                shortest_tour = tour
    return shortest_tour


def ParseInputFile(file):
    with open(file) as f:
        temp = f.readlines()
    lines = []
    for line in temp:
        lines.append(map(int, line.split(" ")))
    return lines


def add_subtour_cstr(model, where):
    # Callback is called when some event occur . The type of event is
    # distinguished using argument ’’where ’ ’.
    # In this case , we want to perform something when an integer
    # solution is found , which corresponds to ’’GRB.Callback.MIPSOL ’’.
    if where == g.GRB.callback.MIPSOL:
        # make a list of edges selected in the solution
        selected = []
        for i in range(n+1):
            # Get the value of variable x[i, j] from the solution .
            # You may also pass a list of variables to the method .
            sol = model.cbGetSolution([model._xs[i, j] for j in range(n+1)])
            selected += [(i,j) for j in range(n+1) if sol[j] > 0.5]
        # find the shortest cycle in the selected edge list
        tour = find_shortest_tour(selected)
        if len(tour) < n:
            # add a subtour elimination constraint
            expr = 0
            for i in range(len(tour)):
                expr += model._xs[tour[i][0], tour[i][1]]
            # Add lazy constraint to model .
            model.cbLazy(expr <= len(tour)-1)


def get_distances(stripes, n, w, h):
    stripes = np.array(stripes)
    distances = np.ones((n+1, n+1)) * np.sum(stripes)*10

    for i in range(n+1):
        distances[0, i] = 0

    for i in range(n):
        for j in range(n):
            # dist = [last 3-column of i] - [first 3-column of j]
            distances[i+1, j+1] = np.sum(np.abs(stripes[i, :, (w-1)*3:w*3] - stripes[j, :, 0:3]))

    return distances


# use the academic licence
with g.Env(params=opts) as env, g.Model(env=env) as m:
    # model = g.Model()

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
    bigM = np.sum(distances)*20

    # Model variables

    # xs = {}
    # for i in range(n):
    #     for j in range(n):
    #         xs[i, j] = m.addVar(vtype=g.GRB.BINARY, name=f"x{i}{j}")
    xs = m.addVars(n+1, n+1, vtype=g.GRB.BINARY)

    S = m.addVars(n+1, lb=0, vtype=g.GRB.INTEGER)


    #TODO: implement the lazy constraints

    # Model constraints
    for i in range(n+1):
        m.addConstr(xs[i, i] == 0, name=f"v{i}{i}")                                 # no one vertex cycles
        m.addConstr(g.quicksum(xs[i, j] for j in range(n+1)) == 1, name=f"v{i}_out")  # only one edge out
        m.addConstr(g.quicksum(xs[j, i] for j in range(n+1)) == 1, name=f"v{i}_in")   # only one edge in

    LAZY_CS = False
    if LAZY_CS:
        m.setObjective(g.quicksum(distances[i, j] * xs[i, j] for j in range(n+1) for i in range(n+1)), sense=g.GRB.MINIMIZE)
        m._xs = xs
        m.Params.lazyConstraints = 1
        m.optimize(add_subtour_cstr)

        a = np.zeros((n+1, n+1))
        for i in range(n+1):
            for j in range(n+1):
                a[i, j] = xs[i, j].X
        print(a)

    # solve it by the classic constraints (there may be too many for the model!)
    else:
        for i in range(n+1):
            for j in range(1, n+1):
                m.addConstr(bigM*(1 - xs[i, j]) + S[j] >= S[i] + distances[i, j], name=f"S{i}{j}")

        # # Model objective function
        m.setObjective(g.quicksum(distances[i, j] * xs[i, j] for j in range(n+1) for i in range(n+1)), sense=g.GRB.MINIMIZE)

        m.optimize()
        # m.display()

        a = np.zeros((n+1, n+1))
        for i in range(n+1):
            for j in range(n+1):
                a[i, j] = xs[i, j].X
        print(a)


        values = np.zeros(n+1)
        for i in range(n+1):
            print(f"S[{i}]: ", S[i].X)
            values[i] = S[i].X

        ordering = values[1:].argsort().argsort()
        print("Ordering:", ordering+1)


        # original image
        image = np.zeros((h, w*n, 3))
        for i in range(n):
            stripe = stripes[i].reshape(h, w, 3)
            image[:, w*i:w*(i+1), :] = stripe / 255

        plt.imshow(image)
        plt.show()


        # corrected image
        image = np.zeros((h, w*n, 3))
        for i in range(n):
            idx = ordering[i]
            stripe = stripes[idx].reshape(h, w, 3)
            image[:, w*i:w*(i+1), :] = stripe / 255

        plt.imshow(image)
        plt.show()


