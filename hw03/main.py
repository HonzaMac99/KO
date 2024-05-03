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

    G = {}
    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        [n_cust, n_prod] = list(map(int, input_data[0].split(" ")))
        G["s"] = []

        for i in range(n_cust):
            ci = f"c{i+1}"
            cust_info = list(map(int, input_data[i+1].split(" ")))
            l_i, u_i = cust_info[:2]
            G["s"].append([ci, l_i, -1, u_i])
            cust_prods = cust_info[2:]
            for p in cust_prods:
                pi = f"p{p}"
                e = [pi, 0, -1, 1]
                G[ci] = G[ci] + [e] if ci in G else [e]
        demands = list(map(int, input_data[-1].split(" ")))
        for i, d in enumerate(demands):
            pi = f"p{i+1}"
            G[pi] = [["t", d, -1, np.inf]]

    # init step 1
    G["t"] = [["s", 0, -1, np.inf]]

    # init step 2




    ordering = []
    with open(output_file, 'w') as f:
        for i in range(len(ordering)-1):
            f.write(f"{ordering[i]} ")

    if __name__ == "__main__":
        ...

