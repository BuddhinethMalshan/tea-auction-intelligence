import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def get_merged_data(csv_path="df_global_final.csv"):
    """Loads CSV and GSheet data, standardizing mixed date formats."""
    # 1. Load History (Static CSV)
    try:
        df_csv = pd.read_csv(csv_path)
        # Use format='mixed' to handle various string types
        df_csv['true_date'] = pd.to_datetime(df_csv['true_date'], format='mixed')
        # Filter 2022
        df_csv = df_csv[df_csv['true_date'].dt.year != 2022]
    except Exception as e:
        st.error(f"Critical Error: CSV load failed: {e}")
        return pd.DataFrame()

    # 2. Load Cloud Data (Dynamic GSheet)
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_sheets = conn.read(worksheet="Sheet1", ttl=0)
        
        if df_sheets is not None and not df_sheets.empty:
            # Handle the date format from the GSheet
            df_sheets['true_date'] = pd.to_datetime(df_sheets['true_date'], format='mixed')
            
            # Standardize column name if necessary
            if 'predicted_price' in df_sheets.columns:
                df_sheets = df_sheets.rename(columns={'predicted_price': 'forecast_1w'})
            
            # Combine CSV + Sheets
            df_merged = pd.concat([df_csv, df_sheets], ignore_index=True)
            
            # NORMALIZE: Convert all to date-only (removes 00:00:00 timestamps)
            df_merged['true_date'] = df_merged['true_date'].dt.normalize()
            
            # Sort by date and remove duplicates
            df_merged = df_merged.sort_values('true_date')
            return df_merged.drop_duplicates(subset=['true_date', 'region', 'grade'], keep='last')
    except Exception as e:
        # Fallback to normalized CSV if sheet fails
        df_csv['true_date'] = df_csv['true_date'].dt.normalize()
        return df_csv
        
    df_csv['true_date'] = df_csv['true_date'].dt.normalize()
    return df_csv

def save_to_gsheet(new_results_df):
    """Saves data to GSheet, ensuring date format is consistent."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        
        required_cols = [
            'true_date', 'region', 'grade', 'elevation', 'price', 
            'forecast_1w', 'forecast_2w', 'forecast_4w', 
            'weather_cat', 'crop_cat', 'USD_to_LKR'
        ]
        
        data_to_push = new_results_df[required_cols]

        # Convert date to string before pushing to GSheet to ensure Google treats it as a Date
        data_to_push['true_date'] = pd.to_datetime(data_to_push['true_date']).dt.strftime('%Y-%m-%d')

        if existing_data is not None and not existing_data.empty:
            # Duplicate check
            existing_data['true_date'] = pd.to_datetime(existing_data['true_date'], format='mixed').dt.date
            new_date = pd.to_datetime(data_to_push['true_date'].iloc[0]).date()
            
            if new_date in existing_data['true_date'].values:
                st.error(f"🛑 Entry already exists for {new_date}. Move to Dashboard to view.")
                return False
            
            updated_df = pd.concat([existing_data, data_to_push], ignore_index=True)
        else:
            updated_df = data_to_push

        conn.update(worksheet="Sheet1", data=updated_df)
        return True
    except Exception as e:
        st.error(f"Cloud Sync Error: {e}")
        return False