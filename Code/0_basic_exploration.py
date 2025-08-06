import pandas as pd
import matplotlib.pyplot as plt
import glob

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import pandas as pd


import os
import pandas as pd
import matplotlib.pyplot as plt
import os
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Read all files into DataFrames
file_paths = glob.glob("../Data/Speeches/speeches_by_central_bank/*/*.csv")  # Adjust file extension if needed
print(f"Files found: {file_paths}")
dataframes = [pd.read_csv(file,sep='\t') for file in file_paths]
os.makedirs('../Output/plots/Aggregated_plots', exist_ok=True)
os.makedirs('../Output/csvs/Aggregated_csvs', exist_ok=True)
# Step 2: Calculate all variables in the DataFrames
for i, df in enumerate(dataframes):
    print(f"Variables in dataset {i + 1}: {list(df.columns)}")

# Step 3: Calculate the total number of speeches
total_speeches = sum(len(df) for df in dataframes)
print(f"Total number of speeches: {total_speeches}")

# Step 4: Plot number of speeches against year
all_data = pd.concat(dataframes, ignore_index=True)
all_data['date']=all_data['Date']

all_data['nWords'] = all_data['text'].str.replace('\n',' ').str.split().str.len()  # Assuming 'text' column contains the speech text





if 'nWords' in all_data.columns and 'CentralBank' in all_data.columns:
    # Determine the order of CentralBanks by the maximum nWords
    central_bank_order = all_data.groupby('CentralBank')['nWords'].mean().sort_values(ascending=False).index

    # Create a boxplot of nWords for each CentralBank with sorted x-axis
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        data=all_data, 
        x='CentralBank', 
        y='nWords', 
        order=central_bank_order,  # Sort x-axis by max nWords
        palette='tab20'
    )
    plt.xlabel('Central Bank')
    plt.yscale('log')  # Use log scale for better visibility of distributions
    plt.ylabel('Number of Words (nWords)')
    plt.title('Distribution of nWords by Central Bank (Sorted by Max nWords)')
    plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to fit everything
    plt.savefig('../Output/plots/Aggregated_plots/Number_of_words_by_bank_sorted.png', bbox_inches='tight')
    plt.show()
else:
    print("Required columns ('nWords' and 'CentralBank') not found in the dataset.")

#all_data['nWords'# = pd.to_datetime(all_data['date'], errors='coerce')  # Handle invalid dates



if 'date' in all_data.columns and 'CentralBank' in all_data.columns:
    # Convert 'date' to datetime and extract the year
    all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')  # Handle invalid dates
    all_data['year'] = all_data['date'].dt.year

    # Determine the order of CentralBanks by the maximum nWords
    central_bank_order = all_data.groupby('CentralBank')['nWords'].mean().sort_values(ascending=False).index

    # Group by CentralBank and year, then count speeches
    speeches_by_bank_year = all_data.groupby(['year', 'CentralBank']).size().unstack(fill_value=0)

    # Reorder columns in the same order as central_bank_order
    speeches_by_bank_year = speeches_by_bank_year[central_bank_order]

    # Define a colormap with the same order as the central banks
    colormap = ListedColormap(plt.cm.tab20.colors[:len(central_bank_order)])

    # Plot stacked bar chart
    speeches_by_bank_year.plot(
        kind='bar', 
        stacked=True, 
        figsize=(12, 8), 
        color=colormap.colors
    )
    plt.xlabel('Year')
    plt.ylabel('Number of Speeches')
    plt.title('Number of Speeches by Central Bank and Year (Stacked)')
    plt.legend(
        title='Central Bank', 
        labels=central_bank_order, 
        bbox_to_anchor=(1.05, 1), 
        loc='upper left'
    )
    plt.tight_layout()  # Adjust layout to fit legend
    
    plt.savefig('../Output/plots/Aggregated_plots/speeches_by_bank_year_stacked_sorted.png', bbox_inches='tight')
    plt.show()
else:
    print("Required columns ('date', 'CentralBank', and 'nWords') not found in the dataset.")



# Ensure the required columns exist
if {'CentralBank', 'date', 'nWords'}.issubset(all_data.columns):
    # Standardize the column name
    all_data.rename(columns={'nWords': 'charCount'}, inplace=True)

    # Convert 'date' to datetime and extract the year
    all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')
    all_data['year'] = all_data['date'].dt.year

    # Create output directories
    os.makedirs('../Output/csvs/Dissagregated_csvs', exist_ok=True)
    os.makedirs('../Output/plots/Dissagregated_plots', exist_ok=True)

    # Initialize a list to store aggregate summary data
    aggregate_summary = []

    # Group by CentralBank
    for central_bank, group in all_data.groupby('CentralBank'):
        # Calculate total number of speeches
        total_speeches = len(group)

        # Calculate summary statistics for character count
        char_stats = group['charCount'].agg(['mean', 'median', 'min', 'max', 'std']).to_dict()

        # Calculate minimum and maximum year
        min_year = group['year'].min()
        max_year = group['year'].max()

        # Create a DataFrame for the CSV
        csv_data = {
            'Variable': ['Total Speeches', 'Mean Char Count', 'Median Char Count', 'Min Char Count', 'Max Char Count', 'SD Char Count', 'Min Year', 'Max Year'],
            'Value': [total_speeches, char_stats['mean'], char_stats['median'], char_stats['min'], char_stats['max'], char_stats['std'], min_year, max_year]
        }
        csv_df = pd.DataFrame(csv_data)

        # Save the CSV
        csv_path = f'../Output/csvs/Dissagregated_csvs/{central_bank}_summary.csv'
        csv_df.to_csv(csv_path, index=False)

        # Append summary data to the aggregate list
        aggregate_summary.append({
            'CentralBank': central_bank,
            'Total Speeches': total_speeches,
            'Mean Char Count': char_stats['mean'],
            'Median Char Count': char_stats['median'],
            'Min Char Count': char_stats['min'],
            'Max Char Count': char_stats['max'],
            'SD Char Count': char_stats['std'],
            'Min Year': min_year,
            'Max Year': max_year
        })

        # Create a plot of number of speeches per year
        speeches_per_year = group.groupby('year').size()
        plt.figure(figsize=(10, 6))
        speeches_per_year.plot(kind='bar', color='skyblue')
        plt.title(f'Number of Speeches per Year - {central_bank}')
        plt.xlabel('Year')
        plt.ylabel('Number of Speeches')
        plt.tight_layout()

        # Save the plot
        plot_path = f'../Output/plots/Dissagregated_plots/{central_bank}_speeches_per_year.png'
        plt.savefig(plot_path)
        plt.close()

    # Create an aggregate CSV with all summaries
    aggregate_df = pd.DataFrame(aggregate_summary)
    aggregate_csv_path = '../Output/csvs/Aggregated_summary.csv'
    aggregate_df.to_csv(aggregate_csv_path, index=False)

    print("CSV files, plots, and the aggregate summary have been successfully generated in the 'output' directory.")
else:
    print("Required columns ('CentralBank', 'date', 'nWords') not found in the dataset.")




# Ensure the required columns exist
if {'CentralBank', 'date', 'charCount'}.issubset(all_data.columns):
    # Standardize the column name
    #all_data.rename(columns={'nWords': 'charCount'}, inplace=True)

    # Convert 'date' to datetime and extract the year
    all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')
    all_data['year'] = all_data['date'].dt.year

    # Rename specified central banks to "FED"
    fed_banks = [
        'Federal Reserve Bank of Atlanta',
        'Federal Reserve Bank of Boston',
        'Federal Reserve Bank of Chicago',
        'Federal Reserve Bank of Cleveland',
        'Federal Reserve Bank of Dallas',
        'Federal Reserve Bank of Kansas City',
        'Federal Reserve Bank of New York',
        'Federal Reserve Bank of Philadelphia',
        'Federal Reserve Bank of Richmond',
        'Federal Reserve Bank of San Francisco',
        'Federal Reserve Bank of St Louis',
        'Board of Governors of the Federal Reserve'
    ]
    ecb_banks =[
        'European Central Bank',
        'Austrian National Bank',
 'Bank of Estonia',
 'Bank of Finland',
 'Bank of France',
 'Bank of Greece',
 'Bank of Italy',
 'Bank of Latvia',
 'Bank of Lithuania',
 'Bank of Portugal',
 'Bank of Slovenia',
 'Bank of Spain',
 'Central Bank of Cyprus',
 'Central Bank of Ireland',
 'Central Bank of Luxembourg',
 'Central Bank of Malta',
 'Croatian National Bank',
 'De Nederlandsche Bank',
 'Deutsche Bundesbank',
 'National Bank of Belgium',
 'National Bank of Slovakia'


    ]

    other_eu = [
        #'Central Bank of Iceland',
    'National Bank of Romania',
    'National Bank of Poland',
    'National Bank of Denmark',
    'Czech National Bank',
    'Bulgarian National Bank',
    'Central Bank of Hungary',
    'Sveriges Riksbank',
    ]
    all_data['RenamedCentralBank'] = all_data['CentralBank'].replace(fed_banks, 'FED').replace(ecb_banks, 'ECB').replace(other_eu, 'Other EU CB')

    # Create output directories
    #os.makedirs('../Output/csvs/Aggregated_csvs', exist_ok=True)
    os.makedirs('../Output/plots/Aggregated_plots', exist_ok=True)

    # Initialize a list to store aggregate summary data
    aggregate_summary = []

    # Group by RenamedCentralBank
    for central_bank, group in all_data.groupby('RenamedCentralBank'):
        # Calculate total number of speeches
        total_speeches = len(group)

        # Calculate summary statistics for character count
        char_stats = group['charCount'].agg(['mean', 'median', 'min', 'max', 'std']).to_dict()

        # Calculate minimum and maximum year
        min_year = group['year'].min()
        max_year = group['year'].max()

        # Create a DataFrame for the CSV
        csv_data = {
            'Variable': ['Total Speeches', 'Mean Char Count', 'Median Char Count', 'Min Char Count', 'Max Char Count', 'SD Char Count', 'Min Year', 'Max Year'],
            'Value': [total_speeches, char_stats['mean'], char_stats['median'], char_stats['min'], char_stats['max'], char_stats['std'], min_year, max_year]
        }
        csv_df = pd.DataFrame(csv_data)

        # Save the CSV
        csv_path = f'../Output/csvs/Dissagregated_csvs/{central_bank}_summary.csv'
        csv_df.to_csv(csv_path, index=False)

        # Append summary data to the aggregate list
        aggregate_summary.append({
            'CentralBank': central_bank,
            'Total Speeches': total_speeches,
            'Mean Char Count': char_stats['mean'],
            'Median Char Count': char_stats['median'],
            'Min Char Count': char_stats['min'],
            'Max Char Count': char_stats['max'],
            'SD Char Count': char_stats['std'],
            'Min Year': min_year,
            'Max Year': max_year
        })

        

    # Create an aggregate CSV with all summaries
    aggregate_df = pd.DataFrame(aggregate_summary)
    aggregate_csv_path = '../Output/csvs/Aggregated_summary_with_FED.csv'
    aggregate_df.to_csv(aggregate_csv_path, index=False)

    print("Renamed central banks, aggregated CSVs, and plots have been successfully generated in the 'output' directory.")
else:
    print("Required columns ('CentralBank', 'date', 'charCount') not found in the dataset.")



if 'date' in all_data.columns and 'RenamedCentralBank' in all_data.columns:
    # Convert 'date' to datetime and extract the year
    all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')  # Handle invalid dates
    all_data['year'] = all_data['date'].dt.year

    # Determine the order of CentralBanks by the maximum nWords
    central_bank_order = all_data.groupby('RenamedCentralBank')['charCount'].mean().sort_values(ascending=False).index

    # Group by CentralBank and year, then count speeches
    speeches_by_bank_year = all_data.groupby(['year', 'RenamedCentralBank']).size().unstack(fill_value=0)

    # Reorder columns in the same order as central_bank_order
    speeches_by_bank_year = speeches_by_bank_year[central_bank_order]

    # Define a colormap with the same order as the central banks
    colormap = ListedColormap(plt.cm.tab20.colors[:len(central_bank_order)])

    # Plot stacked bar chart
    speeches_by_bank_year.plot(
        kind='bar', 
        stacked=True, 
        figsize=(12, 8), 
        color=colormap.colors
    )
    plt.xlabel('Year')
    plt.ylabel('Number of Speeches')
    plt.title('Number of Speeches by Central Bank and Year (Stacked)')
    plt.legend(
        title='Central Bank', 
        labels=central_bank_order, 
        bbox_to_anchor=(1.05, 1), 
        loc='upper left'
    )
    plt.tight_layout()  # Adjust layout to fit legend
    
    plt.savefig('../Output/plots/Aggregated_plots/speeches_by_bank_year_stacked_sorted_with_FED.png', bbox_inches='tight')
    plt.show()
else:
    print("Required columns ('date', 'RenamedCentralBank', and 'nWords') not found in the dataset.")





if 'date' in all_data.columns and 'Language' in all_data.columns:
    # Convert 'date' to datetime and extract the year
    all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')  # Handle invalid dates
    all_data['year'] = all_data['date'].dt.year

    # Determine the order of CentralBanks by the maximum nWords
    central_bank_order = all_data.groupby('Language')['charCount'].mean().sort_values(ascending=False).index

    # Group by CentralBank and year, then count speeches
    speeches_by_bank_year = all_data.groupby(['year', 'Language']).size().unstack(fill_value=0)

    # Reorder columns in the same order as central_bank_order
    speeches_by_bank_year = speeches_by_bank_year[central_bank_order]

    # Define a colormap with the same order as the central banks
    colormap = ListedColormap(plt.cm.tab20.colors[:len(central_bank_order)])

    # Plot stacked bar chart
    speeches_by_bank_year.plot(
        kind='bar', 
        stacked=True, 
        figsize=(12, 8), 
        color=colormap.colors
    )
    plt.xlabel('Year')
    plt.ylabel('Number of Speeches')
    plt.title('Number of Speeches by Language and Year (Stacked)')
    plt.legend(
        title='Central Bank', 
        labels=central_bank_order, 
        bbox_to_anchor=(1.05, 1), 
        loc='upper left'
    )
    plt.tight_layout()  # Adjust layout to fit legend
    
    plt.savefig('../Output/plots/Aggregated_plots/speeches_by_language_year_stacked_sorted_with_FED.png', bbox_inches='tight')
    plt.show()
else:
    print("Required columns ('date', 'RenamedCentralBank', and 'nWords') not found in the dataset.")


all_data
