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

    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        # [n, w, h] = list(map(int, input_data[0].split(" ")))
        n_rooks = int(input_data[0])
        rooks_poses = []

        for i in range(1, n_rooks+1):
            data = input_data[i]
            r = int(data[1])-1
            c = ord(data[0])-97
            rooks_poses.append([r, c])

    # Model parameters
    b_len = 8
    # bigM = np.sum(distances)*20

    # Model variables
    xs = m.addVars(b_len, b_len, vtype=g.GRB.BINARY)  # is knight

    # Model constraints
    for i, rook_pos in enumerate(rooks_poses):
        r, c = rook_pos
        m.addConstr(xs[r, c] == 0, name=f"rook{i+1}")
        m.addConstrs(xs[r, i] == 0 for i in range(b_len))
        m.addConstrs(xs[i, c] == 0 for i in range(b_len))
        # m.addConstr(xs.sum(r, "*") == 0)
        # m.addConstr(xs.sum("*", c) == 0)

    # no mutually attacking knights
    idxs = np.array([[1, -2], [2, -1], [2, 1], [1, 2],
                     [-1, 2], [-2, 1], [-2, -1], [-1, -2]])
    for i in range(b_len):
        for j in range(b_len):
            for k in range(idxs.shape[0]):
                i_new = i + idxs[k, 0]
                j_new = j + idxs[k, 1]
                if 0 <= i_new < b_len and 0 <= j_new < b_len:
                    m.addConstr(xs[i, j] + xs[i_new, j_new] <= 1, name=f"knight_{i}{j}")

    # # examples
    # for i in range(n+1):
    #     for j in range(1, n+1):
    #         m.addConstr(bigM*(1 - xs[i, j]) + S[j] >= S[i] + distances[i, j], name=f"S{i}{j}")
    # m.setObjective(g.quicksum(distances[i, j] * xs[i, j] for i in range(n+1) for j in range(n+1)), sense=g.GRB.MINIMIZE)



    # Model objective function
    m.setObjective(g.quicksum(xs[i, j] for i in range(b_len) for j in range(b_len)), sense=g.GRB.MAXIMIZE)

    m.optimize()

    for i in range(b_len-1, -1, -1):
        for j in range(b_len):
            if [i, j] in rooks_poses:
                print("R", end=" ")
            elif xs[i, j].X == 1:
                print("K", end=" ")
            else:
                print("-", end=" ")
        print("")
    print("")

    knight_poses = []
    for i in range(b_len):
        for j in range(b_len):
            if xs[i, j].X == 1:
                pos = chr(j+97) + str(i+1)  # <--- ch: v prohozeni i a j
                knight_poses.append(pos)

    n_knights = len(knight_poses)
    print(n_knights)
    for i in range(n_knights):
        print(knight_poses[i])

    with open(output_file, 'w') as f:
        f.write(f"{n_knights}\n")
        for i in range(n_knights-1):
            f.write(f"{knight_poses[i]}\n")
        if n_knights > 0:
            f.write(f"{knight_poses[-1]}")

