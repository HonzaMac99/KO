#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import numpy as np
import sys

LAZY_CS = True

opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}


def get_tour(edges):
    tour = []
    e_start = edges[0]
    v_start, v_next = e_start

    tour.append(e_start)
    edges.remove(e_start)

    found_tour = False
    while not found_tour:
        for e in edges:
            if e[0] == v_next:
                v_next = e[1]

                tour.append(e)
                edges.remove(e)

                if v_next == v_start:
                    found_tour = True
                break

    return tour, edges


def get_shortest_tour(edges):
    shortest_tour = []
    min_len = np.inf
    while len(edges) > 1:
        tour, edges = get_tour(edges)
        if min_len > len(tour):             # <--- note: did mistake here
            min_len = len(tour)
            shortest_tour = tour
    return shortest_tour


def add_subtour_cstr(model, where):
    # Callback is called when some event occur. The type of event is
    # distinguished using argument ’’where’’.
    # In this case , we want to perform something when an integer
    # solution is found , which corresponds to ’’GRB.Callback.MIPSOL ’’.
    if where == g.GRB.callback.MIPSOL:
        # Get the value of variable xs[i, j] from the solution.
        # You may also pass a list of variables to the method.
        val = model.cbGetSolution([model._xs[i, j] for i in range(n+1) for j in range(n+1)])
        # print(np.array(val).reshape(n+1, n+1))

        # make a list of edges that were enabled in the xs
        es_active = [(i, j) for i in range(n+1) for j in range(n+1) if val[i*(n+1) + j] > 0.5]
        # es_active = np.array(es_active)

        # find the shortest cycle in the edge list
        tour = get_shortest_tour(es_active)
        tour_len = len(tour)

        # Add lazy constraint to model that eliminates the subtour --> one of the xs in the tour must be 0
        if tour_len < n+1:
            model.cbLazy(g.quicksum(model._xs[tour[i]] for i in range(tour_len)) <= tour_len-1)


def get_distances(stripes, n, w, h):
    stripes = np.array(stripes)
    distances = np.zeros((n+1, n+1))

    for i in range(n+1):
        distances[0, i] = 0

    for i in range(n):
        for j in range(n):
            # dist = [last 3-column of i] - [first 3-column of j]
            distances[i+1, j+1] = np.sum(np.abs(stripes[i, :, -3:] - stripes[j, :, 0:3]))

    return distances


def print_var_arr(model_var, n):
    a = np.zeros((n+1, n+1))
    for i in range(n+1):
        for j in range(n+1):
            a[i, j] = model_var[i, j].X
    print(a)


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
    xs = m.addVars(n+1, n+1, vtype=g.GRB.BINARY)
    if not LAZY_CS:
        S = m.addVars(n+1, lb=0, vtype=g.GRB.INTEGER)  # for naive approach


    # Model constraints
    for i in range(n+1):
        m.addConstr(xs[i, i] == 0, name=f"v{i}{i}")                                   # no one vertex cycles
        # m.addConstr(xs[i, 0] == 0, name=f"v{i}{0}")                                   # no return to dummy vertex
        m.addConstr(g.quicksum(xs[i, j] for j in range(n+1)) == 1, name=f"v{i}_out")  # only one edge out
        m.addConstr(g.quicksum(xs[j, i] for j in range(n+1)) == 1, name=f"v{i}_in")   # only one edge in

    # Model objective function
    m.setObjective(g.quicksum(distances[i, j] * xs[i, j] for i in range(n+1) for j in range(n+1)), sense=g.GRB.MINIMIZE)

    if LAZY_CS:
        m._xs = xs
        m.Params.lazyConstraints = 1
        m.optimize(add_subtour_cstr)
    else:
        # naive approach w all constraints (there may be too many for the model!!)
        for i in range(n+1):
            for j in range(1, n+1):
                m.addConstr(bigM*(1 - xs[i, j]) + S[j] >= S[i] + distances[i, j], name=f"S{i}{j}")
        m.optimize()

        for i in range(n+1):
            print(f"S[{i}]: ", S[i].X)

    print_var_arr(xs, n)

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

        # plot the original image
        image = np.zeros((h, w*n, 3))
        for i in range(n):
            stripe = stripes[i].reshape(h, w, 3)
            image[:, w*i:w*(i+1), :] = stripe / 255

        plt.imshow(image)
        plt.show()


        # plot the corrected image
        image = np.zeros((h, w*n, 3))
        for i in range(n):
            idx = ordering[i]-1
            stripe = stripes[idx].reshape(h, w, 3)
            image[:, w*i:w*(i+1), :] = stripe / 255

        plt.imshow(image)
        plt.show()


