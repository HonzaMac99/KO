import gurobi.*;

public class Example {
	public static void main(String[] args) throws Exception {
     // Create new environment.
		 GRBEnv env = new GRBEnv();

     // Create empty optimization model.
		 GRBModel model = new GRBModel(env);

		 // Create variables x, y.
     // addVar(lowerBound, upperBound, objectiveCoeff, variableType, name)
		 GRBVar x = model.addVar(0.0, GRB.INFINITY, 0.0, GRB.CONTINUOUS, "x");
		 GRBVar y = model.addVar(0.0, GRB.INFINITY, 0.0, GRB.CONTINUOUS, "y");

		 // Set objective: maximize 32x + 25y
		 GRBLinExpr obj = new GRBLinExpr();
		 obj.addTerm(32.0, x);
     obj.addTerm(25.0, y);
		 model.setObjective(obj, GRB.MAXIMIZE);

		 // Add constraint: 5x + 4y <= 59
		 GRBLinExpr cons1 = new GRBLinExpr();
		 cons1.addTerm(5.0, x);
     cons1.addTerm(4.0, y);
     // addConstr(leftHandSide, inequalityType, rightHandSide, name)
		 model.addConstr(cons1, GRB.LESS_EQUAL, 59.0, "cons1");

		 // Add constraint: 4x + 3y <= 46
		 GRBLinExpr cons2 = new GRBLinExpr();
		 cons2.addTerm(4.0, x);
     cons2.addTerm(3.0, y);
		 model.addConstr(cons2, GRB.LESS_EQUAL, 46.0, "cons2");

		 // Solve the model.
		 model.optimize();

     // Print the objective
     // and the values of the decision variables in the solution.
		 System.out.println(x.get(GRB.StringAttr.VarName)+ " " +x.get(GRB.DoubleAttr.X));
		 System.out.println(y.get(GRB.StringAttr.VarName) + " " +y.get(GRB.DoubleAttr.X));
		 System.out.println("Obj: " + model.get(GRB.DoubleAttr.ObjVal));
	}
}
