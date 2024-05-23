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
def construct_path(G, visited, start_id, path, cap):
    global path_sol
    global cap_sol

    visited.append(start_id)

    t_new_id = n_nodes-1
    if start_id != t_new_id:

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

            construct_path(G, visited, node, path_new, cap_new)
            if cap_sol:
                break

        if cap_sol is None:
            for node in nodes_b:
                l_i = G[node, start_id, 0]
                f_i = G[node, start_id, 1]

                path_new = path + [node]
                cap_new = cap + [f_i - l_i]

                construct_path(G, visited, node, path_new, cap_new)
                if cap_sol:
                    break
    else:
        cap_sol = cap
        path_sol = path


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

        s_id = n_nodes-2
        # s_id = 0
        t_id = n_nodes-1

        # will be part of the the extended graph
        s_new_id = n_nodes
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

    G_orig = G.copy()

    # step 1 - compute balances
    G[t_id, s_id, :] = [0, -1, INF]

    enabled = G[:, :, 0] >= 0
    l_in_arr = np.sum(G[:, :, 0]*enabled, axis=0)
    l_out_arr = np.sum(G[:, :, 0]*enabled, axis=1)
    balance_arr = l_in_arr - l_out_arr

    G[:, :, 2][enabled] -= G[:, :, 0][enabled]
    G[:, :, 0][enabled] = 0

    # step 2 - transform to zero lbs, apply balances

    # s_new_id = n_nodes
    # t_new_id = n_nodes + 1
    # n_nodes += 2

    for i, balance in enumerate(balance_arr):
        if balance > 0:
            G[s_new_id, i, :] = [0, -1, balance]
        if balance < 0:
            G[i, t_new_id, :] = [0, -1, -balance]

    # step 3 - initialize the flow
    enabled = G[:, :, 0] == 0
    G[:, :, 1][enabled] = 0

    # step 4 - Ford Fulkerson
    while True:
        path = []
        visited = []
        caps = []  # capacities
        start_id = s_new_id
        path.append(start_id)

        cap_sol = None
        path_sol = None
        construct_path(G, visited, start_id, path, caps)

        cap_sol = cap_sol if cap_sol is not None else []
        path_sol = path_sol if path_sol is not None else []

        print(path_sol)
        if path_sol and cap_sol and min(cap_sol) > 0:
            path_cap = min(cap_sol)
            for i in range(len(path)-1):
                u_id = path[i]
                v_id = path[i+1]

                if G[u_id, v_id, 0] < 0:
                    G[v_id, u_id, 1] -= path_cap  # edge goes backwards
                else:
                    G[u_id, v_id, 1] += path_cap  # edge goes forwards
        else:
            break

    partial_result = G[:, :, 1] + G_orig[:, :, 0]

    # step 5 - initialize flow of the original graph
    G = G_orig[:-2, :-2, :]
    G[:, :, 1] = partial_result[:-2, :-2]

    # step 6 - Ford Fulkerson again
    while True:
        path = []
        visited = []
        capacities = []

        start_id = s_id
        path.append(start_id)
        construct_path(G, visited, start_id, path, capacities)

        if path and capacities and min(capacities) > 0:
            cap_min = min(capacities)
            for i in range(len(path)-1):
                u_id = path[i]
                v_id = path[i+1]

                if G[u_id, v_id, 0] < 0:
                    G[v_id, u_id, 1] -= cap_min
                else:
                    G[u_id, v_id, 1] += cap_min
        else:
            break

    v_min = G[n_cust:n_cust + n_prod, -1, 1]
    products = G[0:n_cust, n_cust:n_cust + n_prod, 1]
    products[products < 0] = 0
    v_computed = np.sum(G[0:n_cust, n_cust:n_cust + n_prod, 1], axis=0)
    if np.all(v_computed >= v_min):
        result = G[0:n_cust, n_cust:n_cust + n_prod, 1]
    else:
        result = None

    with open(output_file, 'w') as f:
        if result is None:
            f.write(f"-1\n")
        else:
            for r in result:
                # Get the indices where the value is equal to 1
                indices = np.where(r == 1)[0] + 1
                if indices.size != 0:
                    f.write(' '.join(map(str, indices)) + '\n')

