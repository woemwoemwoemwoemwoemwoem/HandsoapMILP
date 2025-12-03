import gurobipy as gp
from gurobipy import GRB
import numpy as np

def optimize(params):

    # Extract parameter values
    consumers = params['consumers']
    methods = params['methods']
    timesteps = params['timesteps']
    # number of soap purchases per year (optional; default 4)
    soap_purchase_per_yr = params.get('soap_purchase_per_yr', 4)
    emissions_grams = params['emissions_grams']
    costs_USD = params['costs_USD']
    incomes = params['incomes']
    probabilities = params['probabilities']
    percent_income = params['percent_income']

    # Create distribution of incomes
    # Ensure each income group appears at least once (useful for small 'consumers')
    if consumers <= len(incomes):
        # If consumers fewer or equal to income categories, just take the first `consumers` incomes
        consumer_incomes = np.array(incomes[:consumers])
    else:
        # Pre-assign one consumer to each income level to guarantee representation
        base = list(incomes)
        remaining = consumers - len(base)
        if remaining > 0:
            extra = list(np.random.choice(incomes, size=remaining, p=probabilities))
        else:
            extra = []
        consumer_incomes = np.array(base + extra)
        np.random.shuffle(consumer_incomes)

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

    # Method affordability constraints: method can only be used if percent_income * income >= cost per use
    for i in consumer:
        for j in method:
            for k in timestep:
                m.addConstr(X[i,j,k] * costs_USD[j] <= percent_income * consumer_incomes[i] / soap_purchase_per_yr)
    
    m.optimize()

    # Create results dictionary
    results = {}
    # Always include the sampled incomes and emissions parameters so downstream code mirrors inputs
    results['consumer_incomes'] = consumer_incomes
    results['emissions_grams'] = emissions_grams
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
        
        # Print consumer-level optimal solution summary
        print("\n" + "="*100)
        print("OPTIMAL SOLUTION SUMMARY BY CONSUMER")
        print("="*100)
        print(f"{'Consumer':<10} {'Income ($)':<15} {'Emissions (g)':<15} {'Method 0':<10} {'Method 1':<10} {'Method 2':<10}")
        print("-"*100)
        
        # Calculate per-consumer statistics
        consumer_stats = {}
        
        for consumer_id in consumer:
            consumer_stats[consumer_id] = {
                'income': consumer_incomes[consumer_id],
                'emissions': 0.0,
                'method_counts': [0, 0, 0]
            }
        
        # Aggregate data from optimal choices
        for (i, j, k), value in optimal_choices.items():
            consumer_stats[i]['emissions'] += emissions_grams[j]
            consumer_stats[i]['method_counts'][j] += 1
        
        # Print each consumer's solution
        for consumer_id in sorted(consumer_stats.keys()):
            stats = consumer_stats[consumer_id]
            print(f"{consumer_id:<10} ${stats['income']:<14.2f} {stats['emissions']:<14.2f} {stats['method_counts'][0]:<10} {stats['method_counts'][1]:<10} {stats['method_counts'][2]:<10}")
        
        print("="*100 + "\n")
        print(f"Objective (total emissions): {m.objVal}")
        
    elif m.status == GRB.INFEASIBLE:
        results['Error'] = 'Model is Infeasible'
    else:
        results['Error'] = f'Optimization failed with status: {m.status}'

    return results