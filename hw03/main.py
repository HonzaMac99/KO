#!/usr/bin/env python3
import gurobipy as g
import matplotlib.pyplot as plt
import numpy as np
import sys

np.set_printoptions(linewidth=500)


opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}

# enum node types
S_TYPE = 0
C_TYPE = 1
P_TYPE = 2
T_TYPE = 3
INF = 10000


# function for dfs search
def construct_path(G, start_id, end_id, path, cap, visited):
    global path_sol
    global cap_sol

    visited.append(start_id)

    if start_id != end_id:

        # check the forward connections
        nodes_f = np.where(G[start_id, :, 2] >= 0)[0]
        visited_f = np.isin(nodes_f, visited)
        nodes_f = nodes_f[~visited_f]

        # there must be empty room for some more flow
        empty = G[start_id, nodes_f, 1] < G[start_id, nodes_f, 2]
        nodes_f = nodes_f[empty]

        # check the backward connections
        nodes_b = np.where(G[:, start_id, 2] >= 0)[0]
        visited_b = np.isin(nodes_b, visited)
        nodes_b = nodes_b[~visited_b]

        # there must be empty room for lowering the flow
        empty = G[nodes_b, start_id, 1] > G[nodes_b, start_id, 0]
        nodes_b = nodes_b[empty]

        for node in nodes_f:
            u_i = G[start_id, node, 2]
            f_i = G[start_id, node, 1]

            path_new = path + [node]
            cap_new = cap + [u_i - f_i]

            construct_path(G, node, end_id, path_new, cap_new, visited)
            if cap_sol:
                break

        if not cap_sol:
            for node in nodes_b:
                l_i = G[node, start_id, 0]
                f_i = G[node, start_id, 1]

                path_new = path + [node]
                cap_new = cap + [f_i - l_i]
                construct_path(G, node, end_id, path_new, cap_new, visited)
                if cap_sol:
                    break
    else:
        cap_sol = cap
        path_sol = path


def ford_fulkerson(G, start_id, end_id):
    global cap_sol
    global path_sol

    new_sols = True
    while new_sols:
        cap_sol = []
        path_sol = []
        construct_path(G, start_id, end_id, [start_id], [], [])

        print(path_sol)
        # print(cap_sol)
        if path_sol and cap_sol and min(cap_sol) > 0:
            path_cap = min(cap_sol)
            for i in range(len(path_sol)-1):
                u_id = path_sol[i]
                v_id = path_sol[i+1]

                if G[u_id, v_id, 0] < 0:
                    G[v_id, u_id, 1] -= path_cap  # edge goes backwards
                else:
                    G[u_id, v_id, 1] += path_cap  # edge goes forwards
        else:
            new_sols = False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Default file names
        input_file = "in.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        [n_cust, n_prod] = list(map(int, input_data[0].split(" ")))
        n_nodes = n_cust + n_prod + 2

        # s_id = 0
        s_id     = n_nodes - 2
        t_id     = n_nodes - 1

        s_new_id = n_nodes       # will be part of the extended graph
        t_new_id = n_nodes + 1
        n_nodes += 2

        G = np.ones((n_nodes, n_nodes, 3)) * -1   # * -INF

        for i in range(n_cust):
            c_id = i
            cust_info = list(map(int, input_data[i+1].split(" ")))
            l_i, u_i = cust_info[:2]
            G[s_id, c_id, :] = [l_i, -1, u_i]
            cust_prods = cust_info[2:]
            for p in cust_prods:
                p_id = n_cust + p-1
                G[c_id, p_id] = [0, -1, 1]
        demands = list(map(int, input_data[-1].split(" ")))
        for i, v in enumerate(demands):
            p_id = n_cust + i
            G[p_id, t_id, :] = [v, -1, INF]

    # G_orig = G.copy()


    # step 1 - add t-s connection and compute balances
    G[t_id, s_id, :] = [0, -1, INF]
    enabled = G[:, :, 0] >= 0
    l_in_arr = np.sum(G[:, :, 0]*enabled, axis=0)
    l_out_arr = np.sum(G[:, :, 0]*enabled, axis=1)
    balance_arr = l_in_arr - l_out_arr


    # step 2 - transform to zero lbs, apply balances
    for i, balance in enumerate(balance_arr):
        if balance > 0:
            G[s_new_id, i, :] = [0, -1, balance]
        if balance < 0:
            G[i, t_new_id, :] = [0, -1, -balance]
    G_orig = G.copy()

    G[:, :, 2][enabled] -= G[:, :, 0][enabled]
    G[:, :, 0][enabled] = 0


    # step 3 - initialize the flow
    enabled = G[:, :, 0] == 0
    G[:, :, 1][enabled] = 0


    # step 4 - Ford Fulkerson
    ford_fulkerson(G, s_new_id, t_new_id)

    partial_result = G[:, :, 1] + G_orig[:, :, 0]
    print(partial_result)

    # step 5 - initialize flow of the original graph
    G = G_orig[:-2, :-2, :]
    G[:, :, 1] = partial_result[:-2, :-2]


    # step 6 - Ford Fulkerson again
    a = G[:, :, 1].copy()
    ford_fulkerson(G, s_id, t_id)
    b = G[:, :, 1].copy()

    v_min = G[n_cust:(n_cust+n_prod), -1, 1]
    products = G[:n_cust, n_cust:(n_cust+n_prod), 1]
    products[products < 0] = 0   # neg. number means no products chosen
    v_computed = np.sum(products, axis=0)

    # feasibility criterion
    if np.all(v_computed >= v_min):
        result = products
    else:
        result = []
    print(result)


    # step 7 - saving
    with open(output_file, 'w') as f:
        if not list(result):
            f.write(f"-1\n")
        else:
            for row in result:
                idxs = np.where(row == 1)[0]  # Get the indices where the value is equal to 1
                if idxs.size != 0:
                    print(' '.join(map(str, idxs+1)))
                    f.write(' '.join(map(str, idxs+1)) + '\n')

    print("Done.")