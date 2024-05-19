import numpy as np


def print_arr(a):
    print("Array: ", a)


def edit_arr(a, i):
    # this creates a new array, so it doesn't change the outer a
    a = a[:i] + a[i+1:]
    print_arr(a)

    # this doesn't create a new array
    a.append(7)
    print_arr(a)


a = [1, 2, 3, 4, 5, 6]
edit_arr(a,3)

print(a)


