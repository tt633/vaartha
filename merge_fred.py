import pandas as pd
from fredapi import Fred

# 1. Initialize FRED API 
# Replace with your actual 32-character FRED API key
FRED_API_KEY = '2f9ed0cae4634d7526f0d702c0fdf612'
fred = Fred(api_key=FRED_API_KEY)

def merge_fred_data(sec_csv_path, output_csv_path):
    print("Loading SEC data...")
    # Load the existing SEC data checkpoint
    try:
        sec_df = pd.read_csv(sec_csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find {sec_csv_path}. Make sure it is in the same folder.")
        return
        
    sec_df['end'] = pd.to_datetime(sec_df['end'])

    print("Fetching FRED series BOGZ1FA895050005Q...")
    # Fetch Total US Capital Expenditures (Quarterly, All Sectors)
    fred_series = fred.get_series('BOGZ1FA895050005Q')
    
    # Convert the raw FRED series into a clean pandas DataFrame
    fred_df = pd.DataFrame({
        'end': fred_series.index, 
        'US_Total_CapEx_Millions': fred_series.values
    })
    
    # Data Wrangling crucial step: Align the dates
    # FRED reports quarterly data on the 1st of the month (e.g., 2020-01-01)
    # Our SEC data uses Quarter-End dates (e.g., 2020-03-31)
    # We must shift FRED's dates to Quarter-End so the merge lines up perfectly
    fred_df['end'] = pd.to_datetime(fred_df['end'])
    fred_df.set_index('end', inplace=True)
    fred_df = fred_df.resample('QE').last().reset_index()

    print("Merging datasets...")
    # Left merge: Keeps all SEC company rows, and attaches the matching FRED macro baseline for that specific quarter
    merged_df = pd.merge(sec_df, fred_df, on='end', how='left')

    # Save to a new, finalized CSV
    merged_df.to_csv(output_csv_path, index=False)
    print(f"\n[SUCCESS] Merged data saved to: {output_csv_path}")
    
    return merged_df

if __name__ == "__main__":
    # Ensure these filenames match what you named your SEC output
    INPUT_CSV = 'corporate_capex_rd_restructuring_V2.csv'
    OUTPUT_CSV = 'final_thesis_dataset_subtopic4.csv'
    
    final_df = merge_fred_data(INPUT_CSV, OUTPUT_CSV)
    
    if final_df is not None:
        print("\nSample of merged data (Notice the macro baseline attached!):")
        # Displaying just a few columns to verify the merge worked
        print(final_df[['end', 'Ticker', 'CapEx', 'US_Total_CapEx_Millions']].head(10))