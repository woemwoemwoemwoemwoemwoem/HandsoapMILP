import optimize
import pandas as pd

params = {'consumers': 10, 'methods': 3, 'timesteps': 12, 'months_in_timestep': 3, 'emissions_grams': [578.4,0.653,82.8], 'costs_USD':[15,6,5], 'incomes':[25000,75000,125000,175000], 'probabilities':[0.442,0.347,0.145,0.066], 'percent_income':0.0005}
res = optimize.optimize(params)

incomes = res.get('consumer_incomes')
print('sampled incomes:', incomes)

# apply same cut used in graphs.py
bins = [0, 25000, 75000, 125000, 175000, float('inf')]
labels = ['25K', '75K', '125K', '175K', 'Above 175K']
import pandas as pd
s = pd.Series(incomes)
print('binned groups:', pd.cut(s, bins=bins, labels=labels, right=True).value_counts())
