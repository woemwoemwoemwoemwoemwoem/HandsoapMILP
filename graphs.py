
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# This function takes the dictionary returned by optimize.py
def create_graphs(results):

    # Extract the optimal choices dictionary
    optimal_choices = results['Optimal_Choices']
    
    # Create a list of records (Consumer, Method, Timestep)
    records = []
    for (i, j, k), value in optimal_choices.items():
        records.append({
            'Consumer': i,
            'Method': j,
            'Timestep': k
        })
    
    df = pd.DataFrame(records)
    
    # Create income group mapping
    consumer_income_map = {i: results['consumer_incomes'][i] for i in range(len(results['consumer_incomes']))}
    df['Income'] = df['Consumer'].map(consumer_income_map)
    
    # Define income groups based on incomes array [25000, 75000, 125000, 175000]
    bins = [0, 25000, 75000, 125000, 175000, np.inf]
    labels = ['25K', '75K', '125K', '175K', 'Above 175K']
    # Use right=True so that values equal to the bin edge (e.g., 25000) are included in the lower bin
    df['Income_Group'] = pd.cut(df['Income'], bins=bins, labels=labels, right=True)
    
    # --- Visualization 1: Stacked Bar Chart (Method Percentage by Timestep) ---
    
    plt.figure(figsize=(12, 6))
    
    # Calculate method percentage per timestep
    method_counts_per_timestep = df.groupby(['Timestep', 'Method']).size().reset_index(name='Count')
    total_per_timestep = df.groupby('Timestep').size().reset_index(name='Total')
    method_counts_per_timestep = method_counts_per_timestep.merge(total_per_timestep, on='Timestep')
    method_counts_per_timestep['Percentage'] = (method_counts_per_timestep['Count'] / method_counts_per_timestep['Total']) * 100
    
    # Pivot for stacked bar chart
    pivot_data = method_counts_per_timestep.pivot(index='Timestep', columns='Method', values='Percentage').fillna(0)
    
    # Create stacked bar chart
    pivot_data.plot(kind='bar', stacked=True, figsize=(12, 6), color=['#004D40', '#4CAF50', '#80CBC4'])
    
    plt.title('Method Usage Percentage by Timestep')
    plt.xlabel('Timestep')
    plt.ylabel('Percentage (%)')
    plt.legend(title='Method', labels=['Method 0', 'Method 1', 'Method 2'])
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
    
    # --- Visualization 2: Bar Chart (Average Emissions by Income Group) ---

    plt.figure(figsize=(10, 6))

    emissions_grams = results.get('emissions_grams', [578.4, 0.653, 82.8])  # Default if not in results

    # Calculate emissions for each (consumer,timestep) choice
    df['Emissions'] = df['Method'].map({0: emissions_grams[0], 1: emissions_grams[1], 2: emissions_grams[2]})

    # Sum emissions per consumer across timesteps, then compute average per income group
    per_consumer_emissions = df.groupby('Consumer')['Emissions'].sum().reset_index()

    # Map each consumer to their income group (use the df we already have)
    consumer_groups = df[['Consumer', 'Income_Group']].drop_duplicates(subset=['Consumer']).set_index('Consumer')
    per_consumer_emissions['Income_Group'] = per_consumer_emissions['Consumer'].map(consumer_groups['Income_Group'])

    # Now compute average emissions per consumer by income group
    avg_emissions_by_income = per_consumer_emissions.groupby('Income_Group')['Emissions'].mean().reset_index()

    plt.bar(avg_emissions_by_income['Income_Group'], avg_emissions_by_income['Emissions'], 
        color=['#004D40', '#4CAF50', '#80CBC4', '#00695C', '#004D40'][:len(avg_emissions_by_income)], edgecolor='black', linewidth=1.5)

    plt.title('Average Emissions by Income Group')
    plt.xlabel('Income Group')
    plt.ylabel('Average Emissions per Consumer (grams)')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
    
    # --- Visualization 3: Pie Chart (Method Usage Counts) ---
    
    plt.figure(figsize=(8, 8))
    
    # Count usage of each method
    method_counts = df['Method'].value_counts().sort_index()
    method_labels = [f'Method {i}' for i in method_counts.index]
    
    plt.pie(method_counts.values, labels=method_labels, autopct='%1.1f%%', 
            colors=['#004D40', '#4CAF50', '#80CBC4'], startangle=90)
    
    plt.title('Method Usage Distribution')
    plt.tight_layout()
    plt.show()
    
    print("\n--- Graphs Generated Successfully ---")