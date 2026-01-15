import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Column name constants (from the cleanup script)
SALARY_COL = "what is your annual salary? (you'll indicate the currency in a later question. if you are part-time or hourly, please enter an annualized equivalent -- what you would earn if you worked the job 40 hours a week, 52 weeks a year.)"
AGE_COL = "how old are you?"
JOB_TITLE_COL = "job title"
COUNTRY_COL = "what country do you work in?"
CURRENCY_COL = "please indicate the currency"
BONUS_COL = "how much additional monetary compensation do you get, if any (for example, bonuses or overtime in an average year)? please only include monetary compensation here, not the value of benefits."

# Exchange rates to USD (approx)
EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.164,
    'GBP': 1.343,
    'CAD': 0.720,
    'AUD_NZD': 0.668,  # Using AUD rate
    'INR': 0.0111,  
    'PHP': 0.0175,  
    'BRL': 0.200,  
    'ILS': 0.274,  
    'PLN': 0.250,  
    'SGD': 0.776,  
    'MYR': 0.247,  
    'CNY': 0.143,  
    'CHF': 1.250,
    'JPY': 0.006,
    'HKD': 0.128,
    'SEK': 0.095,
    'ZAR': 0.056,
    'NOK': 0.099,
    'TZS': 0.00043
}

# Map countries to their local currencies for 'OTHER' entries
COUNTRY_CURRENCY_MAP = {
    'India': 0.0111,  # INR
    'Philippines': 0.0175,  # PHP
    'Brazil': 0.200,  # BRL
    'Israel': 0.274,  # ILS
    'Poland': 0.250,  # PLN
    'Singapore': 0.776,  # SGD
    'Malaysia': 0.247,  # MYR
    'China': 0.143,  # CNY
    'Tanzania': 0.00043,  # TZS
}

class SalaryAnalytics:
    def __init__(self, data_dir='.'):
        self.data_dir = data_dir
        self.current_df = None
        self.current_currency = None
        self.last_result = None
    
    def _get_exchange_rate(self, row):
        #Get the appropriate exchange rate for a row, handling OTHER currency
        currency = row[CURRENCY_COL]
        if currency == 'OTHER':
            # Use country-based rate for OTHER currencies
            country = row[COUNTRY_COL]
            return COUNTRY_CURRENCY_MAP.get(country, 1.0)
        return EXCHANGE_RATES.get(currency, 1.0)
        
    def get_available_currencies(self):
        #Get list of available currency datasets
        currencies = []
        for currency in EXCHANGE_RATES.keys():
            if currency == 'OTHER':
                continue
            file_path = os.path.join(self.data_dir, f'cleaned_data_{currency}.csv')
            if os.path.exists(file_path):
                currencies.append(currency)
        
        # Check for ALL dataset
        if os.path.exists(os.path.join(self.data_dir, 'cleaned_data_all.csv')):
            currencies.append('ALL')
        
        return sorted(currencies)
    
    def select_dataset(self):
        #Interactive dataset selection
        available = self.get_available_currencies()
        
        if not available:
            print("\n✗ No datasets found! Please run the cleanup script first.")
            return False
        
        print("\n" + "="*80)
        print(" SELECT DATASET")
        print("\nAvailable datasets:")
        for i, currency in enumerate(available, 1):
            print(f"  {i}. {currency}")
        print("  0. Cancel")
        
        try:
            choice = int(input("\nEnter your choice: ").strip())
            if choice == 0:
                return False
            if 1 <= choice <= len(available):
                currency = available[choice - 1]
                return self._load_data(currency)
            else:
                print("\n✗ Invalid choice")
                return False
        except ValueError:
            print("\n✗ Invalid input")
            return False
    
    def _load_data(self, currency):
        #Internal method to load data
        try:
            if currency == 'ALL':
                file_path = os.path.join(self.data_dir, 'cleaned_data_all.csv')
            else:
                file_path = os.path.join(self.data_dir, f'cleaned_data_{currency}.csv')
            
            self.current_df = pd.read_csv(file_path)
            self.current_currency = currency
            print(f"\n✓ Loaded {len(self.current_df):,} records for {currency}")
            return True
        except Exception as e:
            print(f"\n✗ Error loading data: {e}")
            return False
    
    def salary_benchmarking(self, top_n=10):
        #Analyze salary statistics by job title
        if self.current_df is None:
            print("Please load data first!")
            return
        
        print(f"\n{'='*80}")
        print(f"SALARY BENCHMARKING BY JOB TITLE ({self.current_currency})")
        print(f"{'='*80}\n")
        
        stats = self.current_df.groupby(JOB_TITLE_COL)[SALARY_COL].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('min', 'min'),
            ('max', 'max'),
            ('std', 'std')
        ]).round(2)
        
        # Filter to jobs with at least 5 responses for statistical significance
        stats = stats[stats['count'] >= 5]
        stats = stats.sort_values('median', ascending=False).head(top_n)
        
        result = f"Top {top_n} Jobs by Median Salary\n"
        result += f"Currency: {self.current_currency}\n"
        result += f"Note: All salary amounts shown are in {self.current_currency}\n\n"
        result += stats.to_string()
        
        print(result)
        self.last_result = ("Salary Benchmarking", result)
        
        return stats
    
    def age_salary_analysis(self):
        #Analyze relationship between age and salary
        if self.current_df is None:
            print("Please load data first!")
            return
        
        print(f"\n{'='*80}")
        print(f"AGE vs SALARY ANALYSIS ({self.current_currency})")
        print(f"{'='*80}\n")
        
        # If analyzing ALL currencies, convert to USD for fair comparison
        if self.current_currency == 'ALL' and CURRENCY_COL in self.current_df.columns:
            df_copy = self.current_df.copy()
            df_copy['salary_usd'] = df_copy.apply(
                lambda row: row[SALARY_COL] * self._get_exchange_rate(row), 
                axis=1
            )
            
            age_stats = df_copy.groupby(AGE_COL)['salary_usd'].agg([
                ('count', 'count'),
                ('median', 'median'),
                ('mean', 'mean')
            ]).round(2)
            
            age_stats = age_stats.sort_index()
            
            result = f"Salary Statistics by Age Group\n"
            result += f"Currency: USD (converted from multiple currencies)\n"
            result += f"Note: All salary amounts have been converted to USD for fair comparison\n"
            result += age_stats.to_string()
            
            chart_title = 'Median Salary by Age Group (USD - Converted)'
        else:
            # Single currency analysis - use raw values
            age_stats = self.current_df.groupby(AGE_COL)[SALARY_COL].agg([
                ('count', 'count'),
                ('median', 'median'),
                ('mean', 'mean')
            ]).round(2)
            
            age_stats = age_stats.sort_index()
            
            result = f"Salary Statistics by Age Group\n"
            result += f"Currency: {self.current_currency}\n"
            result += f"Note: All salary amounts shown are in {self.current_currency}\n\n"
            result += age_stats.to_string()
            
            chart_title = f'Median Salary by Age Group ({self.current_currency})'
        
        print(result)
        self.last_result = ("Age vs Salary", result)
        
        # Create chart of information
        try:
            plt.figure(figsize=(12, 6))
            age_stats['median'].plot(kind='bar', color='steelblue')
            plt.title(chart_title)
            plt.xlabel('Age Group')
            plt.ylabel('Median Salary')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.data_dir, f'age_salary_{self.current_currency}.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Chart saved to: {chart_path}")
            plt.close()
        except Exception as e:
            print(f"\n✗ Could not create visualization: {e}")
        
        return age_stats
    
    def geographic_analysis(self, top_n=15):
        #Analyze salaries by country/location
        if self.current_df is None:
            print("Please load data first!")
            return
        
        print(f"\n{'='*80}")
        print(f"GEOGRAPHIC SALARY ANALYSIS ({self.current_currency})")
        print(f"{'='*80}\n")
        
        # If analyzing ALL currencies, convert to USD for fair comparison
        if self.current_currency == 'ALL' and CURRENCY_COL in self.current_df.columns:
            df_copy = self.current_df.copy()
            df_copy['salary_usd'] = df_copy.apply(
                lambda row: row[SALARY_COL] * self._get_exchange_rate(row), 
                axis=1
            )
            
            geo_stats = df_copy.groupby(COUNTRY_COL)['salary_usd'].agg([
                ('count', 'count'),
                ('median', 'median'),
                ('mean', 'mean')
            ]).round(2)
            
            # Filter to countries with at least 10 responses
            geo_stats = geo_stats[geo_stats['count'] >= 10]
            geo_stats = geo_stats.sort_values('median', ascending=False).head(top_n)
            
            result = f"Top {top_n} Countries by Median Salary\n"
            result += f"Currency: USD (converted from multiple currencies)\n"
            result += f"Note: All salary amounts have been converted to USD for fair comparison\n"
            result += f"Note: Excludes 'OTHER' currency entries (INR, PHP, BRL, etc.) due to small sample size\n\n"
            result += geo_stats.to_string()
        else:
            # Single currency analysis - use raw values
            geo_stats = self.current_df.groupby(COUNTRY_COL)[SALARY_COL].agg([
                ('count', 'count'),
                ('median', 'median'),
                ('mean', 'mean')
            ]).round(2)
            
            # Filter to countries with at least 10 responses
            geo_stats = geo_stats[geo_stats['count'] >= 10]
            geo_stats = geo_stats.sort_values('median', ascending=False).head(top_n)
            
            result = f"Top {top_n} Countries by Median Salary\n"
            result += f"Currency: {self.current_currency}\n"
            result += f"Note: All salary amounts shown are in {self.current_currency}\n\n"
            result += geo_stats.to_string()
        
        print(result)
        self.last_result = ("Geographic Analysis", result)
        
        return geo_stats
    
    def cross_currency_comparison(self):
        #Compare salaries across all currencies (converted to USD)
        print(f"\n{'='*80}")
        print(f"CROSS-CURRENCY SALARY COMPARISON (Converted to USD)")
        print(f"{'='*80}\n")
        
        all_currency_data = []
        
        for currency in EXCHANGE_RATES.keys():
            file_path = os.path.join(self.data_dir, f'cleaned_data_{currency}.csv')
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    df['salary_usd'] = df[SALARY_COL] * EXCHANGE_RATES[currency]
                    df['original_currency'] = currency
                    all_currency_data.append(df)
                except Exception as e:
                    print(f"Could not load {currency}: {e}")
        
        if not all_currency_data:
            print("No currency data found!")
            return
        
        combined = pd.concat(all_currency_data, ignore_index=True)
        
        currency_stats = combined.groupby('original_currency')['salary_usd'].agg([
            ('count', 'count'),
            ('median', 'median'),
            ('mean', 'mean')
        ]).round(2)
        
        currency_stats = currency_stats.sort_values('median', ascending=False)
        
        result = "Salary Statistics by Original Currency\n"
        result += "Currency: USD (all values converted)\n"
        result += "Note: All original currency salaries have been converted to USD using current exchange rates\n\n"
        result += currency_stats.to_string()
        
        print(result)
        self.last_result = ("Cross-Currency Comparison", result)
        
        return currency_stats
    
    def bonus_analysis(self):
        #Analyze bonus/additional compensation patterns#
        if self.current_df is None:
            print("Please load data first!")
            return
        
        print(f"\n{'='*80}")
        print(f"BONUS & ADDITIONAL COMPENSATION ANALYSIS ({self.current_currency})")
        print(f"{'='*80}\n")
        
        if BONUS_COL not in self.current_df.columns:
            print("Bonus data not available in this dataset")
            return
        
        # Convert bonus column to numeric
        bonus_data = pd.to_numeric(self.current_df[BONUS_COL], errors='coerce').fillna(0)
        
        # If analyzing ALL currencies, convert to USD for fair comparison
        if self.current_currency == 'ALL' and CURRENCY_COL in self.current_df.columns:
            df_copy = self.current_df.copy()
            df_copy['bonus_numeric'] = bonus_data
            df_copy['bonus_usd'] = df_copy.apply(
                lambda row: row['bonus_numeric'] * self._get_exchange_rate(row), 
                axis=1
            )
            bonus_data = df_copy['bonus_usd']
            
            result = f"Bonus Statistics\n"
            result += f"Currency: USD (converted from multiple currencies)\n"
            result += f"Note: All bonus amounts have been converted to USD for fair comparison\n\n"
        else:
            result = f"Bonus Statistics\n"
            result += f"Currency: {self.current_currency}\n"
            result += f"Note: All bonus amounts shown are in {self.current_currency}\n\n"
        result += f"Total respondents: {len(bonus_data):,}\n"
        result += f"Respondents with bonus: {(bonus_data > 0).sum():,} ({(bonus_data > 0).sum() / len(bonus_data) * 100:.1f}%)\n"
        result += f"Median bonus (all): {bonus_data.median():,.2f} {self.current_currency}\n"
        result += f"Median bonus (if >0): {bonus_data[bonus_data > 0].median():,.2f} {self.current_currency}\n"
        result += f"Mean bonus (all): {bonus_data.mean():,.2f} {self.current_currency}\n"
        result += f"Max bonus: {bonus_data.max():,.2f} {self.current_currency}\n"
        
        print(result)
        self.last_result = ("Bonus Analysis", result)
        
        return bonus_data
    
    def summary_statistics(self):
        #Generate overall summary statistics
        if self.current_df is None:
            print("Please load data first!")
            return
        
        print(f"\n{'='*80}")
        print(f"SUMMARY STATISTICS ({self.current_currency})")
        print(f"{'='*80}\n")
        
        result = f"Dataset Overview\n"
        result += f"Currency: {self.current_currency}\n\n"
        result += f"Total records: {len(self.current_df):,}\n"
        result += f"Unique job titles: {self.current_df[JOB_TITLE_COL].nunique():,}\n"
        result += f"Unique countries: {self.current_df[COUNTRY_COL].nunique():,}\n\n"
        
        # Find the row with maximum salary
        max_salary_idx = self.current_df[SALARY_COL].idxmax()
        max_salary_country = self.current_df.loc[max_salary_idx, COUNTRY_COL]
        max_salary_job = self.current_df.loc[max_salary_idx, JOB_TITLE_COL]
        max_salary_value = self.current_df[SALARY_COL].max()
        
        result += f"Salary Statistics (all amounts in {self.current_currency}):\n"
        result += f"  Minimum: {self.current_df[SALARY_COL].min():,.2f} {self.current_currency}\n"
        result += f"  25th percentile: {self.current_df[SALARY_COL].quantile(0.25):,.2f} {self.current_currency}\n"
        result += f"  Median: {self.current_df[SALARY_COL].median():,.2f} {self.current_currency}\n"
        result += f"  Mean: {self.current_df[SALARY_COL].mean():,.2f} {self.current_currency}\n"
        result += f"  75th percentile: {self.current_df[SALARY_COL].quantile(0.75):,.2f} {self.current_currency}\n"
        result += f"  Maximum: {max_salary_value:,.2f} {self.current_currency} ({max_salary_job} from {max_salary_country})\n"
        result += f"  Standard deviation: {self.current_df[SALARY_COL].std():,.2f} {self.current_currency}\n"
        
        print(result)
        self.last_result = ("Summary Statistics", result)
        
        return result
    
    def save_last_result(self):
        #Save the last analysis result to a text file in currency-specific folder
        if not self.last_result:
            return
        
        # Create currency-specific folder
        currency_folder = os.path.join(self.data_dir, f'results_{self.current_currency}')
        try:
            os.makedirs(currency_folder, exist_ok=True)
        except Exception as e:
            print(f"\n✗ Error creating folder: {e}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title, content = self.last_result
        safe_title = title.replace(" ", "_").replace("/", "_")
        filename = os.path.join(currency_folder, f'{safe_title}_{timestamp}.txt')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write(f"{title.upper()} - {self.current_currency}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
                f.write("\n")
            
            print(f"\nResults automatically saved to: {os.path.basename(currency_folder)}/{os.path.basename(filename)}")
            return filename
        except Exception as e:
            print(f"\n✗ Error saving results: {e}")
            return None


def display_menu():
    #Display the main menu
    print("\n" + "="*80)
    print(" SALARY DATA ANALYTICS")
    print("="*80)
    print("\n[Analysis Options]")
    print("  1. Salary Benchmarking by Job Title")
    print("  2. Age vs Salary Analysis")
    print("  3. Geographic Salary Analysis")
    print("  4. Cross-Currency Comparison")
    print("  5. Bonus & Additional Compensation Analysis")
    print("  6. Summary Statistics")
    print("\n[Other]")
    print("  q. Quit")
    print("\n" + "="*80)


def run_analysis_with_dataset(analytics, analysis_func, needs_dataset=True):
    #Helper function to run analysis with dataset selection and save option
    # Select dataset if needed
    if needs_dataset:
        if not analytics.select_dataset():
            return
    
    # Run the analysis
    try:
        analysis_func()
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        return
    
    # Auto-save results
    analytics.save_last_result()


def main():
    analytics = SalaryAnalytics()
    
    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == '1':
            run_analysis_with_dataset(analytics, analytics.salary_benchmarking)
        
        elif choice == '2':
            run_analysis_with_dataset(analytics, analytics.age_salary_analysis)
        
        elif choice == '3':
            run_analysis_with_dataset(analytics, analytics.geographic_analysis)
        
        elif choice == '4':
            run_analysis_with_dataset(analytics, analytics.cross_currency_comparison, needs_dataset=False)
        
        elif choice == '5':
            run_analysis_with_dataset(analytics, analytics.bonus_analysis)
        
        elif choice == '6':
            run_analysis_with_dataset(analytics, analytics.summary_statistics)
        
        elif choice == 'q':
            print("\nGoodbye")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
