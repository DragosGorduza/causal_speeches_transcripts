# Data Exploration and Visualization

This document provides an overview of the visualizations created for exploring the dataset. The visualizations include a stacked bar chart of speeches by central bank and year, as well as a box-and-whisker plot of the number of words (`nWords`) for each central bank.

---

## 1. Stacked Bar Chart: Number of Speeches by Central Bank and Year

The stacked bar chart below shows the number of speeches delivered by each central bank, grouped by year. Each bar represents a year, and the segments within the bar represent the contributions of individual central banks.

### Code:
```python
if 'date' in all_data.columns and 'CentralBank' in all_data.columns:
    # Convert 'date' to datetime and extract the year
    all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')  # Handle invalid dates
    all_data['year'] = all_data['date'].dt.year

    # Group by CentralBank and year, then count speeches
    speeches_by_bank_year = all_data.groupby(['year', 'CentralBank']).size().unstack(fill_value=0)

    # Plot stacked bar chart
    speeches_by_bank_year.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='tab20')
    plt.xlabel('Year')
    plt.ylabel('Number of Speeches')
    plt.title('Number of Speeches by Central Bank and Year (Stacked)')
    plt.legend(title='Central Bank', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()  # Adjust layout to fit legend
    
    plt.savefig('../Figures/speeches_by_bank_year_stacked.png', bbox_inches='tight')
    plt.show()
```

## 2. Box-and-Whisker Plot: ### Distribution of nWords by Central Bank
The box-and-whisker plot below shows the distribution of the number of words (nWords) for each central bank. This visualization helps identify the spread, median, and potential outliers in the word counts for speeches delivered by each central bank.

Code:
```python
if 'nWords' in all_data.columns and 'CentralBank' in all_data.columns:
    # Create a boxplot of nWords for each CentralBank
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=all_data, x='CentralBank', y='nWords', palette='Set2')
    plt.xlabel('Central Bank')
    plt.ylabel('Number of Words (nWords)')
    plt.title('Distribution of nWords by Central Bank')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to fit everything
    plt.show()
else:
    print("Required columns ('nWords' and 'CentralBank') not found in the dataset.")
```
