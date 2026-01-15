# Salary Dataset Analysis Tools

Simple tools for cleaning and analyzing salary survey data.

## Requirements

- Python 3.x
- pandas
- matplotlib

Install dependencies:
```bash
pip install pandas matplotlib
```

## Usage

### Step 1: Clean the Data

Run the cleanup script to prepare your data:

```bash
python Cleanup.py
```

This will:
- Remove duplicates and outliers
- Standardize country names and currency codes
- Split data into separate files by currency
- Create `cleaned_data_*.csv` files for each currency

### Step 2: Analyze the Data

Run the analytics tool:

```bash
python Analytics.py
```

Follow the interactive menu to:
1. Choose an analysis type:
   - Salary Benchmarking by Job Title
   - Age vs Salary Analysis
   - Geographic Salary Analysis
   - Cross-Currency Comparison
   - Bonus Analysis
   - Summary Statistics
2. Select a dataset if applicable (USD, EUR, GBP, etc. or ALL currencies)

3. View results (automatically saved to `results_*/` folders)

## Files Generated

- `cleaned_data_*.csv` - Cleaned datasets split by currency
- `cleaned_data_all.csv` - Complete cleaned dataset
- `results_*/` - Analysis results organized by currency
- `*.png` - Charts and visualizations

## Notes

- The cleanup script uses 3 standard deviations to remove statistical outliers
- Analytics converts all currencies to USD for fair comparison when analyzing ALL currencies
- Results are automatically saved with timestamps
- It's not really built to have the saving disabled, but it's possible if you edit a lot of the script
- Dataset taken from https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/edit?resourcekey=&gid=1625408792#gid=1625408792 Survey given at https://www.askamanager.org/2021/04/how-much-money-do-you-make-4.html 

## Known improvements that could be made

- The Cleanup file uses a JSON Format to help with the typos and other issues present in the dataset, like having Unitedd States VS United states. This could be a separate JSON File that is edited so the Cleanup.py file can be more readable. The same with the Currency conversions for the Analytics.py file
- This could be made into a web application that sorts the data and contains all of the analytics, instead of having to run two separate python files, but this shows the process of cleaning up the dataset to remove jobs with titles like "bum" that earns $10,000,000 USD a year that's an obvious outlier and bad data.
- The Analytics script logic assumes whenever you are running scripts you are in the DataSet_Cleanup folder, if you are not you'll get errors and it won't work
