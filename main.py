import graphs
import optimize

# Create dictionary of parameters
print("is this working")
params = {'consumers': 10, 
            'methods': 3, 
            'timesteps': 8,
            'soap_purchase_per_yr': 4,
            'emissions_grams': [578.4, 0.653, 82.8],
            'costs_USD': [15,6,5],
            'incomes':[25000, 75000, 125000, 175000],
            'probabilities': [0.442, 0.347, 0.145, 0.066],
            'percent_income': 0.001
            }

results = optimize.optimize(params)

graphs.create_graphs(results)