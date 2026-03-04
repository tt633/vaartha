import requests
import pandas as pd
import time

# SEC requires a descriptive User-Agent in the headers; replace with your info
HEADERS = {'User-Agent': 'UniversityProject your.email@example.com'}

# Define companies and tag by sector
COMPANIES = {
    'NVDA': 'semiconductor', 'AMD': 'semiconductor', 'INTC': 'semiconductor',
    'GOOGL': 'hyperscaler', 'MSFT': 'hyperscaler', 'AMZN': 'hyperscaler',
    'TSLA': 'energy', 'XOM': 'energy', 'NEE': 'energy', 'ALB': 'mining'
}

# The "Waterfall" Strategy: Prioritized lists of XBRL tags to search
CONCEPT_WATERFALLS = {
    'Revenues': [
        'Revenues', 
        'RevenueFromContractWithCustomerExcludingAssessedTax', # Used by MSFT, GOOGL, AMZN
        'SalesRevenueNet',                                     # Used by AMD, TSLA
        'SalesRevenueGoodsNet'
    ],
    'CapEx': [
        'PaymentsToAcquirePropertyPlantAndEquipment',
        'PaymentsForPropertyPlantAndEquipment',
        'PaymentsForConstructionAndAcquisitionsOfPropertyPlantAndEquipment', # Used by Utilities like NEE
        'CapitalExpenditures'
    ],
    'R&D': [
        'ResearchAndDevelopmentExpense',
        'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost',
        'TechnologyAndContentExpense' # Amazon's equivalent to R&D
    ]
}

def get_cik_mapping():
    """Fetches official SEC ticker-to-CIK mapping."""
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    # SEC CIKs must be 10 digits padded with zeros
    mapping = {v['ticker']: str(v['cik_str']).zfill(10) for k, v in data.items()}
    return mapping

def fetch_concept_data(cik, concept):
    """Pulls quarterly concept data from SEC EDGAR XBRL API."""
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json"
    response = requests.get(url, headers=HEADERS)
    
    # Respect SEC rate limits (max 10 requests per second)
    time.sleep(0.15) 
    
    if response.status_code == 200:
        data = response.json()
        if 'units' in data and 'USD' in data['units']:
            df = pd.DataFrame(data['units']['USD'])
            
            # Filter for quarterly data (10-Q)
            df = df[df['form'] == '10-Q'].copy()
            df['end'] = pd.to_datetime(df['end'])
            
            # Keep the most recently filed data point for overlapping periods
            df = df.sort_values('filed').drop_duplicates(subset=['end'], keep='last')
            
            df = df[['end', 'val']].rename(columns={'val': concept})
            df.set_index('end', inplace=True)
            return df
    return pd.DataFrame()

def build_dataset():
    ticker_to_cik = get_cik_mapping()
    all_company_data = []

    for ticker, sector in COMPANIES.items():
        print(f"\nProcessing {ticker}...")
        cik = ticker_to_cik.get(ticker)
        if not cik:
            print(f"  CIK not found for {ticker}")
            continue

        company_dfs = []
        # Loop through our standardized categories (Revenues, CapEx, R&D)
        for standard_name, tags in CONCEPT_WATERFALLS.items():
            metric_df = pd.DataFrame()
            
            # Try each tag in the waterfall until we hit data
            for tag in tags:
                df = fetch_concept_data(cik, tag)
                if not df.empty:
                    # Rename the messy SEC tag to our clean standard name
                    df.rename(columns={tag: standard_name}, inplace=True)
                    metric_df = df
                    print(f"  [SUCCESS] Found {standard_name} using tag: {tag}")
                    break 
            
            if not metric_df.empty:
                company_dfs.append(metric_df)
            else:
                print(f"  [WARNING] Could not find any data for {standard_name}")

        if company_dfs:
            # Merge concepts on the date index
            merged_df = pd.concat(company_dfs, axis=1)
            
            # Align to quarterly frequency ('QE') and forward-fill missing quarters
            merged_df = merged_df.resample('QE').last().ffill()
            
            # Add metadata tags
            merged_df['Ticker'] = ticker
            merged_df['Sector'] = sector
            
            all_company_data.append(merged_df.reset_index())

    # Combine all companies into one master dataframe
    master_df = pd.concat(all_company_data, ignore_index=True)
    
    # Calculate Intensities (Now using our clean column names!)
    if 'CapEx' in master_df.columns and 'Revenues' in master_df.columns:
        master_df['CapEx_intensity'] = master_df['CapEx'] / master_df['Revenues']
        
    if 'R&D' in master_df.columns and 'Revenues' in master_df.columns:
        master_df['R&D_intensity'] = master_df['R&D'] / master_df['Revenues']

    return master_df

if __name__ == "__main__":
    final_data = build_dataset()
    print("\nExtraction Complete. Sample Data:")
    print(final_data.head())
    
    # Save to CSV for dashboarding
    final_data.to_csv("corporate_capex_rd_restructuring_V2.csv", index=False)