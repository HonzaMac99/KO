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


# condition 1
def check_missed_deadline(c, tasks_unsched):
    feasable = True
    for task in tasks_unsched:
        [pi, ri, di, id] = task
        if c + pi > di:
            feasable = False
            break

    return feasable


# condition 2
def check_bounds(c, tasks_unsched, ub):
    if len(tasks_unsched) == 0:
        return True
    pi_sum = 0
    min_r = np.inf
    for task in tasks_unsched:
        [pi, ri] = task[:2]
        min_r = min(min_r, ri)
        pi_sum += pi

    lb = max(min_r, c) + pi_sum

    return lb <= ub


# condition 3
def release_time_property(c, tasks_unsched):
    ri_min = np.inf
    for task in tasks_unsched:
        ri = task[1]
        ri_min = min(ri_min, ri)
    return c <= ri_min


def build_tree(sol_arr, sol_partial, tasks_unsched, c, ub):
    found_sol = False
    for i, task in enumerate(tasks_unsched):
        tasks_unsched_new = tasks_unsched[:i] + tasks_unsched[i+1:]

        [pi, ri] = task[:2]  # [pi, ri, di, id]
        c_new = pi + max(c, ri)

        cond_1 = check_missed_deadline(c_new, tasks_unsched_new)
        cond_2 = check_bounds(c_new, tasks_unsched_new, ub)

        if cond_1 and cond_2:
            sol_p_new = sol_partial + [task]
            if len(sol_p_new) == n_tasks:  # we got to the leave
                found_sol = True
                sol_arr.append(sol_p_new)
                break
            found_sol = build_tree(sol_arr, sol_p_new, tasks_unsched_new, c_new, ub)
    return found_sol


if __name__ == "__main__":

    if len(sys.argv) < 3:
        # Default file names
        input_file = "in.txt"
        output_file = "out.txt"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    ub = 0
    tasks = []
    with open(input_file, 'r') as f:
        input_data = f.read().split("\n")
        n_tasks = int(input_data[0])
        for i in range(n_tasks):
            task_desc = list(map(int, input_data[i+1].split(" ")))
            tasks.append(task_desc + [i+1])
            ub = max(ub, task_desc[2])

    sol_arr = []
    sol_found = build_tree(sol_arr, [], tasks, 0, ub)

    print(np.array(sol_arr))

    with open(output_file, 'w') as f:
        if len(sol_arr) >= 1:
            sol_1 = np.array(sol_arr[0])

            start_times = np.zeros((n_tasks), dtype=int)

            t_cur = 0
            for task in sol_1:
                [pi, ri, di, id] = task
                start_times[id-1] = t_cur
                t_cur += pi

            for i in range(len(start_times)):
                f.write(f"{start_times[i]}\n")
        else:
            f.write(f"-1\n")

