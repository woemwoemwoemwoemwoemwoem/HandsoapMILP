import gurobipy as gp
from gurobipy import GRB
import numpy as np

def optimize(params):

    # Extract parameter values
    consumers = params['consumers']
    methods = params['methods']
    timesteps = params['timesteps']
    months_in_timestep = params['months_in_timestep']
    emissions_grams = params['emissions_grams']
    costs_USD = params['costs_USD']
    incomes = params['incomes']
    probabilities = params['probabilities']
    percent_income = params['percent_income']

    # Calculate number of years modeled
    years = (months_in_timestep * timesteps) / 12

    # Create distribution of incomes
    consumer_incomes = np.random.choice(incomes, size=consumers, p=probabilities)

    # Create optimization model
    m = gp.Model('Handsoap')
    m.Params.LogToConsole = 1
    
    # Indices 
    consumer = range(0,consumers)
    method = range(0,methods)
    timestep = range(0,timesteps)

    # Decision variables
    X = m.addVars(consumer, method, timestep, vtype=GRB.BINARY, name='X')
    
    # Objective function
    m.setObjective(emissions_grams[0]*gp.quicksum(X[i,0,k] for i in consumer for k in timestep) 
                   + emissions_grams[1]*gp.quicksum(X[i,1,k] for i in consumer for k in timestep) 
                   + emissions_grams[2]*gp.quicksum(X[i,2,k] for i in consumer for k in timestep) , GRB.MINIMIZE)
    
    # Constraints
    
    # Only one method used at each timestep
    for i in consumer:
        for k in timestep:
            m.addConstr(gp.quicksum(X[i,j,k] for j in method) == 1)
    
    # Method 2 can only be used if method 1 was used before
    for i in consumer:
        for k in timestep:
            m.addConstr(X[i,1,k] <= gp.quicksum(X[i,0,s] for s in range(0,k)))

    # Income constraints
    for i in consumer:
          m.addConstr(gp.quicksum(costs_USD[j]*X[i,j,k] for j in method for k in timestep) <= percent_income*consumer_incomes[i]*years)
    
    m.optimize()

    # Create results dictionary
    results = {}
    if m.status == GRB.OPTIMAL:
        results['Optimal_Emissions'] = m.objVal
        optimal_choices = {
            (i, j, k): X[i, j, k].X 
            for i in consumer 
            for j in method 
            for k in timestep 
            if X[i, j, k].X > 0.5
        }
        results['Optimal_Choices'] = optimal_choices
        results['consumer_incomes'] = consumer_incomes
        
    elif m.status == GRB.INFEASIBLE:
        results['Error'] = 'Model is Infeasible'
    else:
        results['Error'] = f'Optimization failed with status: {m.status}'

    return results