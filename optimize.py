import gurobipy as gp
from gurobipy import GRB
import numpy as np

def optimize(params):

    # Extract parameter values
    consumers = params["consumers"]
    methods = params["methods"]
    timesteps = params["timesteps"]
    emissions_grams = params["emissions_grams"]
    costs_USD = ["costs_USD"]
    incomes = ["incomes"]
    probabilities = ["probabilities"]
    percent_income = ["percent_income"]

    # Create distribution of incomes
    consumer_incomes = np.random.choice(incomes, size=consumers, p=probabilities)

    # Create optimization model
    m = gp.Model("Handsoap")
    m.Params.LogToConsole = 1
    
    # Indices 
    consumer = range(1,consumers+1)
    method = range(1,methods+1)
    timestep = range(1,timesteps+1)

    # Everything after this is copy and pasted from a past homework problem, don't use:

    '''
    # Decision variables
    X = m.addVars(individual, lb=0, name="X")
    Y = m.addVars(bottle, individual, lb=1, vtype=GRB.INTEGER, name="Y")
    
    # Objective function
    m.setObjective(0*sum(Y.values()) + 0*sum(X.values()), GRB.MAXIMIZE)
    
    # Constraints
    
    # All individuals get the same amount
    m.addConstr(X[1] == X[2])
    m.addConstr(X[2] == X[3])
    
    # Amount of wine for each individual
    for j in individual:
        m.addConstr(X[j] == Y[1,j] + 0.5 * Y[2,j])
    
    # There is 7 of each type of bottle
    for i in bottle: 
        m.addConstr(sum(Y[i,j] for j in individual) == 7)
    
    # Each individual gets 7 bottles
    for j in individual:
        m.addConstr(sum(Y[i,j] for i in bottle) == 7)
    
    m.optimize()
    
    print("obj_func = ", m.objVal)
    for v in m.getVars():
    '''