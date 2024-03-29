#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import sys

opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}


def plot_shifts(x_start):
    num_shifts = [sum([x_start[k % 24] for k in range(i - 7, i + 1)]) for i in range(24)]
    margin = 0.2
    width = 0.3
    plt.figure(figsize=(8, 4))
    plt.bar([h + margin for h in range(24)], d, width=width, color='green')
    plt.bar([h + margin + width for h in range(24)], num_shifts, width=width, color='yellow')
    plt.xlabel("hour")
    plt.legend(['demand', 'number shifts'], ncol=2, bbox_to_anchor=(0.8, 1.1))
    plt.xlim(0, 24)
    plt.ylim(0, max(num_shifts + d) + 1)
    plt.xticks(range(24), [i % 24 for i in range(24)])
    plt.grid()
    plt.show()


# use the academic licence
with g.Env(params=opts) as env, g.Model(env=env) as m:
    # model = gp.Model()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # # Default input parameters
    # d = [6, 6, 6, 6, 6, 8, 9, 12, 18, 22, 25, 21, 21, 20, 18, 21, 21, 24, 24, 18, 18, 18, 12, 8]
    # e = [3, 3, 3, 3, 3, 4, 4,  6,  9, 11, 12, 10, 10, 10,  9, 10, 10, 12, 12,  9,  9,  9,  6, 4]
    # D = 2

    # # Default file names
    # input_file = "in.txt"
    # output_file = "out.txt"

    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        d = list(map(int, input_data[0].split(" ")))
        e = list(map(int, input_data[1].split(" ")))
        D = int(input_data[2])

    # shifts array for entire week
    w = d * 5 + e * 2

    # Model variables
    zs = m.addVars(len(w), vtype=g.GRB.INTEGER, name=[f"z{i}" for i in range(len(w))])
    xs = m.addVars(len(w), vtype=g.GRB.INTEGER, name=[f"x{i}" for i in range(len(w))])

    # Model constraints
    # m.addConstrs(d[i] <= g.quicksum(xs[(i-j) % len(d)] for j in range(8)) for i in range(len(d)))
    m.addConstrs(w[i] - g.quicksum(xs[(i-j) % len(w)] for j in range(8))        <= zs[i] for i in range(len(w)))
    m.addConstrs(       g.quicksum(xs[(i-j) % len(w)] for j in range(8)) - w[i] <= zs[i] for i in range(len(w)))
    m.addConstrs(w[i] - g.quicksum(xs[(i-j) % len(w)] for j in range(8))        <= D     for i in range(len(w)))

    # Model objective function
    # m.setObjective(xs.sum(), sense=g.GRB.MINIMIZE)
    m.setObjective(zs.sum(), sense=g.GRB.MINIMIZE)

    m.optimize()

    # if m.status == g.GRB.OPTIMAL:
    #     ...

    # m.display()
    # plot_shifts([xs[i].x for i in range(len(d))])
    with open(output_file, 'w') as f:
        zs_sum = int(sum(zs[i].X for i in range(len(zs))))
        f.write(f"{zs_sum}\n")
        for i in range(len(xs)-1):
            xi = int(xs[i].X)
            f.write(f"{xi} ")
        xi = int(xs[len(xs)-1].X)
        f.write(f"{xi}")


