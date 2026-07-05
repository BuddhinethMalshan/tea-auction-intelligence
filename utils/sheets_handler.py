import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def get_merged_data(csv_path="df_global_final.csv"):
    """Loads CSV and GSheet data, standardizing columns for the Dashboard."""
    # 1. Load History
    df_csv = pd.read_csv(csv_path)
    df_csv['true_date'] = pd.to_datetime(df_csv['true_date'])
    df_csv = df_csv[df_csv['true_date'].dt.year != 2022]

    # Standardize column names in history to match our new schema
    # (Rename 'predicted_price' to 'forecast_1w' if it exists in your CSV)
    if 'predicted_price' in df_csv.columns:
        df_csv = df_csv.rename(columns={'predicted_price': 'forecast_1w'})

    # 2. Load Cloud Data
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_sheets = conn.read(worksheet="Sheet1", ttl=0)
        
        if df_sheets is not None and not df_sheets.empty:
            df_sheets['true_date'] = pd.to_datetime(df_sheets['true_date'])
            df_merged = pd.concat([df_csv, df_sheets], ignore_index=True)
            # Use 'price' as the primary Y-axis value for charts
            return df_merged.drop_duplicates(subset=['true_date', 'region', 'grade'], keep='last')
    except Exception:
        return df_csv
        
    return df_csv

def save_to_gsheet(new_results_df):
    """Saves data strictly following the agreed schema, fixing FutureWarning."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        
        required_cols = [
            'true_date', 'region', 'grade', 'elevation', 'price', 
            'forecast_1w', 'forecast_2w', 'forecast_4w', 
            'weather_cat', 'crop_cat', 'USD_to_LKR'
        ]
        
        data_to_push = new_results_df[required_cols]

        if existing_data is not None and not existing_data.empty:
            existing_data['true_date'] = pd.to_datetime(existing_data['true_date'])
            new_date = pd.to_datetime(data_to_push['true_date'].iloc[0]).date()
            if new_date in existing_data['true_date'].dt.date.unique():
                st.error(f"🛑 Data for {new_date} already exists in Google Sheets.")
                return False
            # Clean up empty columns to avoid FutureWarning
            existing_data = existing_data.dropna(axis=1, how='all')
            updated_df = pd.concat([existing_data, data_to_push], ignore_index=True)
        else:
            updated_df = data_to_push

        conn.update(worksheet="Sheet1", data=updated_df)
        return True
    except Exception as e:
        st.error(f"Cloud Sync Error: {e}")
        return False