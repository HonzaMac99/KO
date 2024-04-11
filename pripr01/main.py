#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def load_values(path2file):
    with open(path2file, 'r') as f:
        info = [int(x) for x in f.readline().split()]
        N = info[0]
        M =info[1]
        T =info[2]
        L =info[3]
        P =info[4]
        lines = f.readlines()
        c = []
        for line in lines[:M]:
            c.append([0] + [int(x) for x in line.split()] + [0])
        p = []
        for line in lines[M:]:
            p.append(int(line))
    return N,M,T,L,P,c,p

def modeling(N,M,T,L,P,c,p):
    """
    Example of code:
    m.addConstr(a[x-1,y,"E"] + a[x+1,y,"W"] + a[x,y-1,"S"] + a[x,y+1,"N"] == 1)
    x = model.addVars(8, 8, lb=0,vtype=g.GRB.BINARY, name='x')
    model.setObjective(x.sum(), sense=g.GRB.MAXIMIZE)
    sum....getvalue .getValue()
    """

    m = g.Model()
    t = m.addVars(M,N+2,["connected","not connected"],vtype=g.GRB.BINARY, name="t")
    price = m.addVars(M, N + 2, ["connected", "not connected"], vtype=g.GRB.INTEGER, name="price")
    c_connected = [[i - L for i in elem] for elem in c]
    for x in range(0,M):
        if x in p:
            m.addConstr(t.sum(x,"*","*") == 0)
        for y in range(1,N+1):
            m.addConstr(t.sum(x, y, "*") <= 1)
            m.addConstr(price[x,y,"connected"] == c_connected[x][y])
            m.addConstr(price[x,y,"not connected"] == c[x][y])
            m.addConstr(5 * (1-t.sum(x, y, "*")) >= t[x,y+1,"not connected"])

    m.addConstr(t.sum() <= T)
    m.addConstr(t.sum("*",0,"*") == 0)
    m.addConstr(t.sum("*",N+1, "*") == 0)

    m.setObjective(g.quicksum(t[i,j,pos] * price[i,j,pos] for i in range(M)
                              for j in range(N+2) for pos in ["connected","not connected"]),sense=g.GRB.MAXIMIZE)

    m.optimize()
    result1 = int(m.objVal)
    result2 = []

    for y in range(1, N + 1):
        for x in range(0, M):
            if t.sum(x, y, "*").getValue() > 0.5:
                result2.append([y-1,x])
    return result1,result2

def write_results(path2file, l1, l2):
    with open(path2file, "w") as f:
        f.write(f"{l1}\n")
        for res in l2:
            f.write(' '.join(map(str, res)))
            f.write("\n")
        f.close()


def save_result(road,path2file):
    with open(path2file,"w") as f:
        f.write(' '.join(map(str,road)))
        f.close()

if __name__ == '__main__':
    # path2in_file = sys.argv[1]
    # path2out_file = sys.argv[2]
    path2in_file = "in.txt"
    path2out_file = "out.txt"

    N,M,T,L,P,c,p = load_values(path2in_file)
    r1,r2 = modeling(N,M,T,L,P,c,p)
    write_results(path2out_file,r1,r2)

