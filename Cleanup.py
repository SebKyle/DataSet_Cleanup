import pandas as pd
import numpy as np

def clean_dataset(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)
    
    print(f"Original dataset: {len(df):,} rows")
    
    # Remove duplicates
    original_count = len(df)
    df.drop_duplicates(inplace=True)
    print(f"Removed {original_count - len(df):,} duplicates")
    
    # Standardize column names to lowercase first
    df.columns = [col.lower() for col in df.columns]
    
    # Convert salary column from text to numeric
    salary_col = 'what is your annual salary? (you\'ll indicate the currency in a later question. if you are part-time or hourly, please enter an annualized equivalent -- what you would earn if you worked the job 40 hours a week, 52 weeks a year.)'
    if salary_col in df.columns:
        df[salary_col] = pd.to_numeric(df[salary_col].astype(str).str.replace(',', ''), errors='coerce')
    
    # Handle the bonus/additional compensation column
    bonus_col = 'how much additional monetary compensation do you get, if any (for example, bonuses or overtime in an average year)? please only include monetary compensation here, not the value of benefits.'
    if bonus_col in df.columns:
        df[bonus_col] = df[bonus_col].fillna(0)
    
    # For REQUIRED fields, drop rows where they're missing
    required_fields = [
        'how old are you?',
        'job title',
        salary_col,
        'please indicate the currency',
        'what country do you work in?'
    ]
    
    before_required = len(df)
    for field in required_fields:
        if field in df.columns:
            if field == salary_col:
                # Drop if salary is NaN or 0
                df = df[df[field].notna() & (df[field] > 0)]
            else:
                # Drop if empty or whitespace only
                df = df[df[field].notna() & (df[field].astype(str).str.strip() != '')]
    
    print(f"Removed {before_required - len(df):,} rows with missing required fields")
    
    # Remove statistical outliers using 3 standard deviations
    before_outliers = len(df)
    if salary_col in df.columns:
        mean_salary = df[salary_col].mean()
        std_salary = df[salary_col].std()
        upper_limit = mean_salary + (3 * std_salary)
        lower_limit = mean_salary - (3 * std_salary)
        
        # Keep only salaries within 3 standard deviations
        df = df[(df[salary_col] >= max(0, lower_limit)) & (df[salary_col] <= upper_limit)]
        print(f"Removed {before_outliers - len(df):,} statistical outliers (beyond 3 std devs)")
        print(f"  Salary range kept: {max(0, lower_limit):,.2f} to {upper_limit:,.2f}")
    
    # For OPTIONAL fields, don't fill missing values
    
    # Standardize currency values (handle variations)
    currency_col = 'please indicate the currency'
    if currency_col in df.columns:
        df[currency_col] = df[currency_col].str.strip().str.upper()
        # Standardize USD and GBP 
        currency_mapping = {
            'US': 'USD',
            'DOLLARS': 'USD',
            'US DOLLAR': 'USD',
            'POUND': 'GBP',
            'POUNDS': 'GBP'
        }
        df[currency_col] = df[currency_col].replace(currency_mapping)
    
    # Standardize OTHER currency specifications (handle full names and variations)
    other_currency_col = 'if "other," please indicate the currency here: '
    if other_currency_col in df.columns:
        # Strip whitespace first
        df[other_currency_col] = df[other_currency_col].str.strip()
        
        # Create case-insensitive mapping for OTHER currency codes
        other_currency_mapping_lower = {
            'philippine peso': 'PHP',
            'philippine pesos': 'PHP',
            'php (philippine peso)': 'PHP',
            'php philippine peso': 'PHP',
            'indian rupees': 'INR',
            'indian rupee': 'INR',
            'rupees': 'INR',
            'inr (indian rupee)': 'INR',
            'mexican peso': 'MXN',
            'mexican pesos': 'MXN',
            'peso mexicano': 'MXN',
            'norwegian kroner': 'NOK',
            'norwegian kroner (nok)': 'NOK',
            'polish złoty': 'PLN',
            'polish zloty': 'PLN',
            'pln (polish zloty)': 'PLN',
            'pln (zwoty)': 'PLN',
            'złoty': 'PLN',
            'zloty': 'PLN',
            'american dollars': 'USD',
            'us dollar': 'USD',
            'us dollars': 'USD',
            'australian dollars': 'AUD',
            'aud australian': 'AUD',
            'australian dollar': 'AUD',
            'thai baht': 'THB',
            'baht': 'THB',
            'korean won': 'KRW',
            'krw (korean won)': 'KRW',
            'rmb (chinese yuan)': 'CNY',
            'china rmb': 'CNY',
            'chinese yuan': 'CNY',
            'yuan': 'CNY',
            'rmb': 'CNY',
            'israeli shekels': 'ILS',
            'israeli shekel': 'ILS',
            'ils (shekel)': 'ILS',
            'nis (new israeli shekel)': 'ILS',
            'new israeli shekel': 'ILS',
            'ils/nis': 'ILS',
            'shekel': 'ILS',
            'shekels': 'ILS',
            'nis': 'ILS',
            'br$': 'BRL',
            'brl (r$)': 'BRL',
            'brazilian real': 'BRL',
            'argentine peso': 'ARS',
            'argentinian peso': 'ARS',
            'argentinian peso (ars)': 'ARS',
            'peso argentino': 'ARS',
            'danish kroner': 'DKK',
            'danish krone': 'DKK',
            'taiwanese dollars': 'TWD',
            'taiwanese dollar': 'TWD',
            'taiwan dollar': 'TWD',
            'singapore dollara': 'SGD',
            'singapore dollars': 'SGD',
            'pesos colombianos': 'COP',
            'colombian peso': 'COP',
            'croatian kuna': 'HRK',
            'kuna': 'HRK',
            'czech crowns': 'CZK',
            'czech crown': 'CZK',
            'equity': '',  # Invalid currency
        }
        
        # Apply mapping using lowercase comparison
        df[other_currency_col] = df[other_currency_col].apply(
            lambda x: other_currency_mapping_lower.get(str(x).lower().strip(), str(x).strip().upper()) 
            if pd.notna(x) and str(x).strip() != '' else x
        )
    
    # Standardize country names (handle variations)
    country_col = 'what country do you work in?'
    if country_col in df.columns:
        # Strip whitespace and normalize multiple spaces
        df[country_col] = df[country_col].str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Create case-insensitive mapping by converting keys to lowercase
        country_mapping_lower = {
            'us': 'United States',
            'usa': 'United States',
            'u.s.': 'United States',
            'u.s.a.': 'United States',
            'u.s': 'United States',
            'united states': 'United States',
            'united states of america': 'United States',
            'the united states': 'United States',
            'united state': 'United States',
            'united sates': 'United States',
            'united stares': 'United States',
            'united stated': 'United States',
            'united stateds': 'United States',
            'united statees': 'United States',
            'united statea': 'United States',
            'united statesp': 'United States',
            'united statew': 'United States',
            'united statss': 'United States',
            'united stattes': 'United States',
            'united statues': 'United States',
            'united status': 'United States',
            'united statws': 'United States',
            'united sttes': 'United States',
            'unitedstates': 'United States',
            'united state of america': 'United States',
            'united sates of america': 'United States',
            'united states of american': 'United States',
            'united states of americas': 'United States',
            'united states is america': 'United States',
            'unites states': 'United States',
            'uk': 'United Kingdom',
            'u.k.': 'United Kingdom',
            'britain': 'United Kingdom',
            'great britain': 'United Kingdom',
            'england': 'United Kingdom',
            'scotland': 'United Kingdom',
            'wales': 'United Kingdom',
            'northern ireland': 'United Kingdom',
            'united kindom': 'United Kingdom',
            'united kingdomk': 'United Kingdom',
            'uae': 'United Arab Emirates',
            'u.a.e.': 'United Arab Emirates'
        }
        
        # Apply mapping using lowercase comparison, then title case for others
        df[country_col] = df[country_col].apply(
            lambda x: country_mapping_lower.get(str(x).lower().strip(), str(x).strip().title()) 
            if pd.notna(x) and str(x).strip() != '' else x
        )
    
    print(f"Final dataset: {len(df):,} rows")
    return df

if __name__ == "__main__":
    cleaned_df = clean_dataset('./data.csv')
    
    # Grouping by currency for regional analysis and saving to separate files
    currency_column = 'please indicate the currency'
    
    if currency_column in cleaned_df.columns:
        # Get unique currencies
        currencies = cleaned_df[currency_column].unique()
        currencies = sorted([c for c in currencies if pd.notna(c) and c != ''])
        print(f"\nFound {len(currencies)} unique currencies: {', '.join(currencies[:10])}")
        
        # Save each currency group to a separate file
        for currency in currencies:
            currency_df = cleaned_df[cleaned_df[currency_column] == currency]
            safe_currency_name = currency.replace('/', '_').replace('\\', '_')
            output_file = f'cleaned_data_{safe_currency_name}.csv'
            currency_df.to_csv(output_file, index=False)
            print(f"  {currency}: {len(currency_df):,} rows Moved to '{output_file}'")
        
        # Also save the complete cleaned dataset
        cleaned_df.to_csv('cleaned_data_all.csv', index=False)
        print(f"\nComplete dataset saved to 'cleaned_data_all.csv'")