import gurobipy as gp

opts = {
    "WLSACCESSID": "62cd638b-d118-4fc1-b04d-624506c02ad3",
    "WLSSECRET":   "ddcd167a-cacc-47c0-a2d9-634e5fea9fec",
    "LICENSEID":   2481370,
}

# use the academic licence
with gp.Env(params=opts) as env, gp.Model(env=env) as model:
    # Formulate problem

    # Example input
    S = [100, 50, 50, 50, 20, 20, 10]

    # TODO: implement the model and find the solution

    model = gp.Model()

    xs = model.addVars(len(S), vtype=gp.GRB.BINARY)

    model.addConstr(sum(xs[i] * S[i] for i in range(len(S))) == 
                    sum((1 - xs[i]) * S[i] for i in range(len(S))))

    model.optimize()

    if model.status == gp.GRB.OPTIMAL:
        for i in range(len(S)):
            if xs[i].X > 0.5:
                print(f"x{i} {xs[i].X}")
    

