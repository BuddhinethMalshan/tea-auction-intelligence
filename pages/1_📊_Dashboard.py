import streamlit as st
import pandas as pd
import plotly.express as px
from utils.sheets_handler import get_merged_data

st.set_page_config(page_title="Market Dashboard", layout="wide")

st.title("📈 Weekly Market Trends & Forecasts")
st.write("Visualizing historical prices and predicted outcomes across tea elevations.")

# 1. Load and Filter Data
df = get_merged_data()

# Ensure 2022 is removed globally to prevent chronological gaps
df = df[df['true_date'].dt.year != 2022]

# Create 3 Columns for 3 Elevations
col_high, col_med, col_low = st.columns(3)

def create_elevation_block(column, elev_name, color):
    with column:
        st.header(f"{elev_name} Grown")
        
        # Filter regions for this elevation
        elev_df = df[df['elevation'].str.upper() == elev_name.upper()]
        available_regions = sorted(elev_df['region'].unique())
        
        selected_reg = st.selectbox(
            f"Select Region ({elev_name})", 
            available_regions, 
            key=f"reg_{elev_name}"
        )
        
        # Filter grades for selected region
        available_grades = sorted(elev_df[elev_df['region'] == selected_reg]['grade'].unique())
        selected_grd = st.selectbox(
            f"Select Grade ({elev_name})", 
            available_grades, 
            key=f"grd_{elev_name}"
        )
        
        # Final Data for Chart
        plot_df = elev_df[(elev_df['region'] == selected_reg) & (elev_df['grade'] == selected_grd)]
        plot_df = plot_df.sort_values('true_date')

        # Create Plotly Chart
        fig = px.line(plot_df, x='true_date', y='price', 
                      title=f"{selected_reg} - {selected_grd}",
                      labels={"price": "LKR / KG", "true_date": "Auction Date"},
                      color_discrete_sequence=[color])
        
        # --- THESIS UPGRADE: REMOVE 2022 GAP ---
        # This removes the horizontal line by telling Plotly 2022 doesn't exist
        fig.update_xaxes(
            rangebreaks=[
                dict(values=pd.date_range("2022-01-01", "2022-12-31"))
            ]
        )
        
        # Custom styling for professional look
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Auction Date",
            yaxis_title="Price (LKR/KG)",
            legend_title="Legend"
        )

        # Logic to show Forecast if it exists
        if 'predicted_price' in plot_df.columns and not plot_df['predicted_price'].isna().all():
            fig.add_scatter(x=plot_df['true_date'], y=plot_df['predicted_price'], 
                            mode='lines+markers', name='Ensemble Forecast', 
                            line=dict(dash='dash', width=2),
                            marker=dict(size=6))

        st.plotly_chart(fig, use_container_width=True)

# Generate the UI for all 3 tiers
create_elevation_block(col_high, "High", "#1f77b4")   # Blue for High Grown
create_elevation_block(col_med, "Medium", "#ff7f0e") # Orange for Medium Grown
create_elevation_block(col_low, "Low", "#2ca02c")    # Green for Low Grown

st.divider()
st.info("""
    💡 **System Note:** The year 2022 has been intentionally omitted from this visualization due to market 
    anomalies and data sparsity during that period. Dashed lines represent the output of the 
    Level-2 Stacking Ensemble (XGBoost + N-BEATS + N-HiTS).
""")