
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
        # Since we only stored values where X = 1 (value > 0.5), we just need the indices.
        # j is the method index (1, 2, 3), which maps to the list of methods.
        records.append({
            'Consumer': i,
            'Method': f'Method {j}',
            'Timestep': k
        })
        
    df = pd.DataFrame(records)
    
    # Count the number of consumers choosing each method at each timestep
    method_counts = df.groupby(['Timestep', 'Method']).size().reset_index(name='Count')
    
    # Calculate the total number of consumers per timestep (should be constant: 100)
    total_consumers = df['Consumer'].nunique()
    
    # Calculate the percentage
    method_counts['Percentage'] = (method_counts['Count'] / total_consumers) * 100
    
    # --- Visualization 1: Stacked Bar Chart (Method Adoption Over Time) ---
    
    plt.figure(figsize=(12, 6))
    
    # Pivot the data for easy plotting
    pivot_df = method_counts.pivot(index='Timestep', columns='Method', values='Percentage').fillna(0)
    
    # Ensure columns are in order
    method_cols = [f'Method {j}' for j in sorted(df['Method'].str.split().str[-1].astype(int).unique())]
    pivot_df = pivot_df[method_cols]

    pivot_df.plot(kind='bar', stacked=True, color=['#004D40', '#4CAF50', '#80CBC4'], ax=plt.gca())
    
    plt.title('Method Adoption Percentage Over Timesteps')
    plt.xlabel('Timestep')
    plt.ylabel('Percentage of Consumers (%)')
    plt.xticks(rotation=0)
    plt.legend(title='Method')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    # --- Visualization 2: Analysis by Income (Example) ---
    
    # This visualization requires mapping the consumer choices back to their income group.
    
    # 1. Create a dictionary to map Consumer ID (1-100) to their Income
    consumer_income_map = {i + 1: results['consumer_incomes'][i] for i in range(len(results['consumer_incomes']))}
    
    # 2. Add income data to the main choices DataFrame
    df['Income'] = df['Consumer'].map(consumer_income_map)
    
    # 3. Define income groups (e.g., Low, Medium, High)
    bins = [0, 50000, 150000, np.inf] # Example bins
    labels = ['Low Income', 'Medium Income', 'High Income']
    df['Income_Group'] = pd.cut(df['Income'], bins=bins, labels=labels, right=False)
    
    # Calculate average method usage per income group
    income_method_usage = df.groupby(['Income_Group', 'Method']).size().reset_index(name='Total_Usage')
    
    # Calculate the total number of choices per income group (normalize)
    total_choices_per_group = income_method_usage.groupby('Income_Group')['Total_Usage'].transform('sum')
    income_method_usage['Percentage'] = (income_method_usage['Total_Usage'] / total_choices_per_group) * 100
    
    # --- Visualization 2: Grouped Bar Chart (Method Usage by Income) ---
    
    plt.figure(figsize=(10, 6))
    import seaborn as sns
    sns.barplot(x='Income_Group', y='Percentage', hue='Method', data=income_method_usage, palette=['#004D40', '#4CAF50', '#80CBC4'])
    
    plt.title('Method Usage Distribution by Consumer Income Group')
    plt.xlabel('Income Group')
    plt.ylabel('Percentage of Total Choices in Group (%)')
    plt.legend(title='Method')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
    
    print("\n--- Graphs Generated Successfully ---")