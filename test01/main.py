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
        # input_file = "in.txt"
        input_file = "public/instances/instance_4.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        [N, M, D, S, R] = list(map(int, input_data[0].split(" ")))
        c_vals = list(map(int, input_data[1].split(" ")))
        rock_poses = []
        for i in range(2, R+2):
            data = list(map(int, input_data[i].split(" ")))
            r, c = data[1], data[0]
            rock_poses.append([r, c])

    # Model parameters
    b_len = 8
    # bigM = np.sum(distances)*20

    # Model variables
    xs = m.addVars(M, N, vtype=g.GRB.BINARY)  # is there a dam on [i, j]
    cs = m.addVars(M, N, vtype=g.GRB.INTEGER)  # power produced at [i, j]

    print("Adding constraints")
    # Model constraints
    m.addConstr(xs.sum() <= D, name="Max_dams")

    # Max dams on one stream lvl
    for i in range(M):
        m.addConstr(g.quicksum(xs[i, j] for j in range(N)) <= S, name=f"s_lvl{i}")

    # Dams cannot be on rocks
    for i, rock_pos in enumerate(rock_poses):
        r, c = rock_pos
        m.addConstr(xs[r, c] == 0, name=f"rock{i+1}")

    # Lowering the current
    bigM = 10000
    for i in range(M):
        for j in range(N):
            current = c_vals[j]
            for k in range(1, 4):  # k = 1, 2, 3
                if (i-k) < 0:
                    break
                current -= (4-k) * xs[i-k, j]
            m.addConstr(cs[i, j] <= current, name="max_c")  # <--- ch: '==' cond makes it infeas.
            m.addConstr(cs[i, j] <= xs[i, j] * bigM, name="max_c")
            # also possible:
            # m.addCosntr(cs[i, j] <= c_vals[j] * xs[i, j]

    # # Production is 0 only when xs[i, j] is 0
    # bigM = 100
    # for i in range(M):
    #     for j in range(N):
    #         m.addConstr(cs[i, j] <= xs[i, j] * bigM, name=f"prod{i}{j}")

    # Model objective function
    m.setObjective(cs.sum(), sense=g.GRB.MAXIMIZE)

    m.optimize()

    # # Debugging
    # for i in range(b_len-1, -1, -1):
    #     for j in range(b_len):
    #         if [i, j] in rooks_poses:
    #             print("R", end=" ")
    #         elif xs[i, j].X == 1:
    #             print("K", end=" ")
    #         else:
    #             print("-", end=" ")
    #     print("")
    # print("")

    # output
    dam_poses = []
    for j in range(N):
        for i in range(M):
            if xs[i, j].X == 1:
                dam_poses.append([j, i])

    opt_production = int(cs.sum().getValue())
    n_dams = len(dam_poses)
    with open(output_file, 'w') as f:
        f.write(f"{opt_production}\n")
        print(opt_production)
        for i in range(n_dams-1):
            f.write(f"{dam_poses[i][0]} {dam_poses[i][1]}\n")
            print(f"{dam_poses[i][0]} {dam_poses[i][1]}")
        if n_dams > 0:
            f.write(f"{dam_poses[-1][0]} {dam_poses[-1][1]}\n")
            print(f"{dam_poses[-1][0]} {dam_poses[-1][1]}")

