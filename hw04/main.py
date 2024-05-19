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


# condition 1: check, if in current time, the task can be solved before its deadline
def check_missed_deadline(c_new, t_unsched):
    feasable = True
    for task in t_unsched:
        [pi, di] = task[[0, 2]]  # task = [pi, ri, di, id]
        if c_new + pi > di:
            feasable = False
            break
    return feasable


# condition 2: if we could schedule the remaining tasks optimally, the resulting quality should be
# better than our current best solution, otw. it doesn't make sense to search in this tree branch
def check_bounds(c_new, t_unsched, ub):
    p_sum = 0
    min_r = np.inf
    for task in t_unsched:
        [pi, ri] = task[:2]
        min_r = min(min_r, ri)
        p_sum += pi

    lb = max(min_r, c_new) + p_sum

    return lb <= ub


# condition 3: check if all releases of the remaining tasks are after
# the curent time and if yes, we have optimal partial solution
def check_decomposition(c_new, t_unsched):
    r_min = np.inf
    for task in t_unsched:
        r_min = min(r_min, task[1])
    return c_new <= r_min


# condition 4: check if the current solution is optimal by BRTP (block release
# time property) and if yes, we can stop the search for a better solution
def release_time_property(c_new, s_prt):
    if len(s_prt) == 0:
        return True

    r_first = s_prt[0][1]
    r_min = np.inf
    p_sum = 0
    for task in s_prt:
        r_min = min(r_min, task[1])
        p_sum += task[0]
    return (r_first <= r_min) and (c_new == r_first + p_sum)


# compute the quality of the new solution
def get_new_ub(s_new):
    t_cur = 0
    for task in s_new:
        [pi, ri] = task[:2]
        t_cur = max(t_cur, ri) + pi
    return t_cur


def get_ids(tasks):
    ids = []
    for task in tasks:
        ids.append(task[-1])
    return ids


def build_tree(s_arr, s_prt, t_unsched, c):
    global ub
    global found_opt_sol
    global backtrack
    for i, task in enumerate(t_unsched):
        if found_opt_sol or not backtrack:
            break
        t_unsched_new = t_unsched[:i] + t_unsched[i+1:]

        [pi, ri] = task[:2]  # task = [pi, ri, di, id]
        c_new = max(c, ri) + pi
        s_prt_new = s_prt + [task]

        cond_1 = check_missed_deadline(c_new, t_unsched_new)
        cond_2 = check_bounds(c_new, t_unsched_new, ub) or (len(t_unsched_new) == 0)
        cond_3 = check_decomposition(c_new, t_unsched_new) and not (len(t_unsched_new) == 0)
        cond_4 = release_time_property(c_new, s_prt_new)  # exit when optimal solution is found

        # if not cond_1:
        #     print("Pruned by cond 1:", get_ids(s_prt_new))
        # if not cond_2:
        #     print("Pruned by cond 2:", get_ids(s_prt_new))
        # if cond_3:
        #     print("3: Optimal partial sol:", get_ids(s_prt_new))

        if cond_1 and cond_2:
            if len(s_prt_new) == n_tasks:  # we got to the end of the tree
                if cond_4:
                    found_opt_sol = True
                s_arr.append(s_prt_new)
                # ub = min(ub, get_new_ub(s_prt_new))
                ub = min(ub, c_new)
                print("Found new sol with quality: ", get_new_ub(s_prt_new))
            else:
                build_tree(s_arr, s_prt_new, t_unsched_new, c_new)

        # if the partial solution is optimal we just exit the tree after searching its coresp. subtree
        backtrack = backtrack and not cond_3
        # print(backtrack, cond_3)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Default file names
        input_file = "in3.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    ub = 0
    tasks = []
    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        n_tasks = int(input_data[0])
        for id in range(1, n_tasks+1):
            task = list(map(int, input_data[id].split(" ")))
            tasks.append(np.array(task + [id]))
            ub = max(ub, task[2])

    # additional global variables
    found_opt_sol = False
    backtrack = True

    s_arr = []
    s_prt = []
    c_start = 0
    build_tree(s_arr, s_prt, tasks, c_start)

    print(np.array(s_arr))
    print(ub)

    with open(output_file, 'w') as f:
        if not s_arr:
            f.write(f"-1\n")
        else:
            start_times = np.zeros((n_tasks), dtype=int)
            sol_1 = np.array(s_arr[0])

            t_cur = 0
            for task in sol_1:
                [pi, id] = task[[0, 3]]
                start_times[id-1] = t_cur
                t_cur += pi

            for i in range(len(start_times)):
                f.write(f"{start_times[i]}\n")
