import optimize
params = {'consumers': 10, 'methods': 3, 'timesteps': 12, 'months_in_timestep': 3, 'emissions_grams': [578.4,0.653,82.8], 'costs_USD':[15,6,5], 'incomes':[25000,75000,125000,175000], 'probabilities':[0.442,0.347,0.145,0.066], 'percent_income':0.0005}
res = optimize.optimize(params)
print('RESULT KEYS:', list(res.keys()))
print('consumer_incomes:', res.get('consumer_incomes'))
print('num_opt_choices:', len(res.get('Optimal_Choices', {})))
