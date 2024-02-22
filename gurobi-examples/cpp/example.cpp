#include <gurobi_c++.h>
using namespace std;

int main(int argc, char *argv[]) {
    // Create new environment.
    GRBEnv env;

    // Create empty optimization model.
    GRBModel model(env);

		// Create variables x, y.
    // addVar(lowerBound, upperBound, objectiveCoeff, variableType, name)
    GRBVar x = model.addVar(0.0, GRB_INFINITY, 0.0, GRB_CONTINUOUS, "x");
    GRBVar y = model.addVar(0.0, GRB_INFINITY, 0.0, GRB_CONTINUOUS, "y");

    // Set objective: maximize 32x + 25y
    model.setObjective(32*x + 25*y, GRB_MAXIMIZE);

    // Add constraint: 5x + 4y <= 59
    model.addConstr(5*x + 4*y <= 59, "cons1");

    // Add constraint: 4x + 3y <= 46
    model.addConstr(4*x + 3*y <= 46, "cons2");

    // Solve the model.
    model.optimize();

    // Print the objective
    // and the values of the decision variables in the solution.
    cout << "Optimal objective: " << model.get(GRB_DoubleAttr_ObjVal) << endl;
    cout << "x: " << x.get(GRB_DoubleAttr_X) << " ";
    cout << "y: " << y.get(GRB_DoubleAttr_X) << endl;

    return 0;
}
