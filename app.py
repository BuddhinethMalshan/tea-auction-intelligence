import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import base64
import datetime
import re

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Ceylon Tea Price Intelligence",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PERFORMANCE CACHING ---
@st.cache_data
def load_base_data():
    if os.path.exists("df_global_final.csv"):
        df = pd.read_csv("df_global_final.csv")
        df['true_date'] = pd.to_datetime(df['true_date'])
        return df
    return pd.DataFrame()

history = load_base_data()

# --- 3. THE CINEMA UI DESIGN (Strict Dark Overlay) ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_design():
    bg_css = ""
    if os.path.exists("assets/bg_tea.jpg"):
        bin_str = get_base64("assets/bg_tea.jpg")
        bg_css = f'''
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url("data:image/png;base64,{bin_str}");
        '''

def set_design():
    bg_css = ""
    if os.path.exists("assets/bg_tea.jpg"):
        bin_str = get_base64("assets/bg_tea.jpg")
        bg_css = f'''
        background: linear-gradient(rgba(0, 0, 0, 0.88), rgba(0, 0, 0, 0.88)), 
                    url("data:image/png;base64,{bin_str}");
        '''

    st.markdown(f'''
        <style>
        /* 1. Global Background Overlay */
        .stApp {{
            {bg_css}
            background-size: cover;
            background-attachment: fixed;
        }}
        
        /* 2. Main Container */
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.75); 
            margin-top: 20px;
            border-radius: 15px;
            padding: 30px !important;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        /* 3. Global Typography & Labels */
        h1, h2, h3, h4, p, span, label, [data-testid="stWidgetLabel"] p {{
            color: #ffffff !important;
            font-weight: 500 !important;
        }}

        /* 4. Metric Formatting */
        [data-testid="stMetricValue"] {{ color: #ffffff !important; font-size: 1.6rem !important; }}
        [data-testid="stMetricLabel"] {{ color: #bbbbbb !important; font-size: 0.85rem !important; }}
        [data-testid="stMetricDelta"] > div {{ color: inherit !important; }}
        div[data-testid="stMetricDelta"] > div[data-direction="up"] {{ color: #00ff00 !important; }}
        div[data-testid="stMetricDelta"] > div[data-direction="down"] {{ color: #ff4b4b !important; }}

        /* 5. Selectbox / Dropdown Fix */
        div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
        }}
        div[role="listbox"] ul {{ background-color: #1a1c23 !important; color: white !important; }}

        /* 6. Carousel Arrows Fix */
        div[data-testid="stHorizontalBlock"] button {{
            background-color: transparent !important;
            border: none !important;
            color: #d4af37 !important;
            font-size: 45px !important;
        }}

        /* 7. Plotly Container Transparency */
        .stPlotlyChart {{ background-color: transparent !important; }}

        /* 8. Tab Design */
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: #aaaaaa !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #1e3d2b !important;
            color: #d4af37 !important;
        }}

        /* 9. Market Coverage Badges */
        .combo-badge {{
            background-color: rgba(0, 0, 0, 0.5);
            color: #d4af37 !important;
            border: 1px solid #d4af37;
        }}

        /* 10. Grade Cards */
        .grade-card {{
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            height: auto;
        }}

        /* 11. FILE UPLOADER DARK FIX (Aggressive override for white bar) */
        [data-testid="stFileUploader"] {{
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px dashed #d4af37 !important;
            border-radius: 10px;
        }}
        [data-testid="stFileUploaderDropzone"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
        }}
        /* Force the button inside the uploader to be Gold */
        [data-testid="stFileUploader"] button {{
            background-color: #d4af37 !important;
            color: #000000 !important;
            border-radius: 5px !important;
        }}

        /* 12. DATA EDITOR (GRID) FINAL THEME LOCK */
        /* This kills the white grid background in Light Mode */
        div[data-testid="stDataEditor"] > div {{
            background-color: #1a1c23 !important;
        }}
        .ag-theme-streamlit {{
            --ag-background-color: #1a1c23 !important;
            --ag-header-background-color: #0e1117 !important;
            --ag-odd-row-background-color: #1a1c23 !important;
            --ag-header-foreground-color: #d4af37 !important;
            --ag-foreground-color: #ffffff !important;
        }}

        /* 13. SOLID ACTION BUTTONS (Confirm, Re-process, etc.) */
        div.stButton > button:not([key="p_btn"]):not([key="n_btn"]) {{
            background-color: #1e3d2b !important;
            color: #d4af37 !important;
            border: 1px solid #d4af37 !important;
        }}

        /* 14. System Cleanup */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        [data-testid="stImage"] {{ margin-bottom: -15px !important; }}
        </style>
        ''', unsafe_allow_html=True)

set_design()

# --- 4. IMPORTS ---
from utils.sheets_handler import get_merged_data, save_to_gsheet
from utils.pdf_processor import split_pdf_pages
from utils.gemini_engine import TeaGeminiEngine
from utils.inference_logic import TeaInferenceEngine

# --- 5. HEADER ---
st.title("🍃 Ceylon Tea Price Intelligence System")
st.caption("Industry-Based Decision Support System | Master's Research Prototype © 2026")

# --- 6. NAVIGATION TABS ---
tab_home, tab_dash, tab_pred = st.tabs(["🏠 Home / Info", "📊 Market Dashboard", "🔮 Price Predictor"])

# ==========================================
# TAB 1: HOME / INFO (REBALANCED ROW 1)
# ==========================================
# ==========================================
# TAB 1: HOME / INFO (FINAL UI/UX POLISH)
# ==========================================
with tab_home:
    # --- 1. GLOBAL UI STYLING (Cinema Overlay & Components) ---
    # We apply this here to ensure it covers all elements in this tab
    bg_css = ""
    if os.path.exists("assets/bg_tea.jpg"):
        bin_str = get_base64("assets/bg_tea.jpg")
        bg_css = f'background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), url("data:image/png;base64,{bin_str}");'

    st.markdown(f'''
            <style>
            /* 1. Background & Overlay */
            .stApp {{
                {bg_css}
                background-size: cover;
                background-attachment: fixed;
            }}
            
            .main {{
                background-color: rgba(0, 0, 0, 0.85); 
                margin: 15px;
                border-radius: 15px;
                padding: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            /* 2. Simplified Safe Typography */
            h1, h2, h3, .stMarkdown p {{
                color: #ffffff !important;
            }}

            /* 3. RESPONSIVE METRIC FIX: Prevents Truncation (Rs. 1...) on Laptops */
            [data-testid="stMetricValue"] {{
                color: #ffffff !important;
                font-size: 1.5rem !important; /* Smaller font to fit laptop screens */
            }}
            [data-testid="stMetricLabel"] {{
                font-size: 0.85rem !important;
                color: #bbbbbb !important;
                white-space: nowrap !important;
            }}
            [data-testid="stMetricDelta"] > div {{
                color: inherit !important;
                font-size: 0.9rem !important;
            }}
            
            /* Force Green/Red for Market Trends */
            div[data-testid="stMetricDelta"] > div[data-direction="up"] {{
                color: #09ab3b !important; /* Green */
            }}
            div[data-testid="stMetricDelta"] > div[data-direction="down"] {{
                color: #ff4b4b !important; /* Red */
            }}

            /* 4. Tab Design */
            .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 4px 4px 0 0;
                padding: 8px 20px;
            }}
            .stTabs [aria-selected="true"] {{
                background-color: #1e3d2b !important;
                color: #d4af37 !important;
                border-bottom: 2px solid #d4af37 !important;
            }}

            /* 5. Market Coverage Badges */
            .combo-container {{
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(212, 175, 55, 0.3);
                border-radius: 12px;
                padding: 20px;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .combo-badge {{
                background-color: rgba(0, 0, 0, 0.5);
                color: #d4af37 !important;
                border: 1px solid #d4af37;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.72rem;
            }}

            /* 6. Grade Cards */
            .grade-card {{
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 12px 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-top: 0px;   
                height: auto;
                min-height: 220px;
            }}
            .grade-header {{ color: #ffffff; font-size: 1.05rem; font-weight: bold; margin: 0px !important; }}
            .grade-full-name {{ font-size: 0.85rem; color: #d4af37; }}
            .grade-desc {{ font-size: 0.82rem; color: #cccccc; }}
            
            .region-tag {{
                background-color: #1e3d2b;
                color: #d4af37 !important;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.65rem;
                border: 1px solid #d4af37;
                margin-right: 4px;
                margin-bottom: 4px;
                display: inline-block;
            }}

            /* 7. Image Gap Fix */
            [data-testid="stImage"] {{
                margin-bottom: -15px !important;
            }}

            /* 8. Minimalist Arrows */
            div[data-testid="column"] button {{
                background-color: transparent !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                color: #ffffff !important;
                border-radius: 50% !important;
                width: 45px !important;
                height: 45px !important;
            }}
            div[data-testid="column"] button:hover {{
                border-color: #d4af37 !important;
                color: #d4af37 !important;
                background-color: rgba(212, 175, 55, 0.1) !important;
            }}
            </style>
            ''', unsafe_allow_html=True)

    # --- 2. ROW 1: MARKET COVERAGE & MAP (Balanced 1.5:1 Ratio) ---
    col_scope, col_map = st.columns([1.5, 1], vertical_alignment="center")

    with col_scope:
        st.markdown("<h3 style='color:#d4af37; margin:0;'>📊 Market Coverage</h3>", unsafe_allow_html=True)
        st.write("Ensuring deep visibility into 43 regional auction segments:")
        
        all_combos = [
            "UDAPUSSELLAWAS | FBOP/FBOP1", "UVA MEDIUM | BOP1", "UVA MEDIUM | BOPF/BOPFSP", 
            "UVA MEDIUM | FBOP/FBOP1", "UVA MEDIUM | OP/OPA", "UVA MEDIUM | OP1", 
            "UVA MEDIUM | PEK/PEK1", "WESTERN HIGH | BOP", "WESTERN HIGH | BOPF/BOPFSP", 
            "WESTERN HIGH | FBOP/FBOP1", "WESTERN HIGH | OP/OPA", "WESTERN HIGH | OP1", 
            "WESTERN HIGH | PEK/PEK1", "WESTERN MEDIUM | BOP", "WESTERN MEDIUM | BOP1", 
            "WESTERN MEDIUM | BOPF/BOPFSP", "WESTERN MEDIUM | FBOP/FBOP1", "WESTERN MEDIUM | OP/OPA", 
            "UVA MEDIUM | BOP", "UVA HIGH | PEK/PEK1", "UVA HIGH | OP1", "UVA HIGH | OP/OPA", 
            "LOW GROWNS | BOP", "LOW GROWNS | BOP1", "LOW GROWNS | BOPF", "LOW GROWNS | FBOP", 
            "LOW GROWNS | FBOP1", "LOW GROWNS | OP1", "LOW GROWNS | PEK1", "NUWARA ELIYAS | BOP", 
            "WESTERN MEDIUM | OP1", "NUWARA ELIYAS | BOPF/BOPFSP", "UDAPUSSELLAWAS | BOP", 
            "UDAPUSSELLAWAS | BOPF/BOPFSP", "UDAPUSSELLAWAS | OP/OPA", "UDAPUSSELLAWAS | PEK/PEK1", 
            "UVA HIGH | BOP", "UVA HIGH | BOP1", "UVA HIGH | BOPF/BOPFSP", "UVA HIGH | FBOP/FBOP1", 
            "NUWARA ELIYAS | PEK/PEK1", "WESTERN MEDIUM | PEK/PEK1", "WESTERN HIGH | BOP1"
        ]
        
        badges_html = "".join([f"<div class='combo-badge'>{c}</div>" for c in sorted(all_combos)])
        st.markdown(f"<div class='combo-container'>{badges_html}</div>", unsafe_allow_html=True)

    with col_map:
        st.markdown("<h4 style='color:#d4af37; margin:0;'>🗺️ Ceylon Tea: Agro-Climatic Growing Regions</h4>", unsafe_allow_html=True)
        if os.path.exists("assets/map_sl.png"):
            # use_container_width=True in a narrower column keeps it small but high-resolution
            st.image("assets/map_sl.png", use_container_width=True)
        else:
            st.info("Map image missing in assets folder.")

    st.divider()

    # --- 3. ROW 2: GRADE CAROUSEL ---
    st.markdown("<h3 style='color:#d4af37; text-align:center; margin-bottom:20px;'>🍃 Unique Tea Grades & Regional Profiles</h3>", unsafe_allow_html=True)

    tea_grades = [
        {"name": "BOP", "full": "Broken Orange Pekoe", "img": "assets/grade_bop.jpg", "desc": "Neat, medium broken leaf. Balances strength with bright liquor.", "regions": ["WESTERN HIGH", "WESTERN MEDIUM", "UVA MEDIUM", "LOW GROWNS", "NUWARA ELIYAS", "UDAPUSSELLAWAS", "UVA HIGH"]},
        {"name": "BOPF / BOPFSP", "full": "BOP Fannings / Special", "img": "assets/grade_bopfsp.jpg", "desc": "Fine grain fannings. Quick brewing with intense brightness.", "regions": ["UVA MEDIUM", "WESTERN HIGH", "WESTERN MEDIUM", "NUWARA ELIYAS", "UDAPUSSELLAWAS", "UVA HIGH", "LOW GROWNS"]},
        {"name": "FBOP / FBOP1", "full": "Flowery Broken Orange Pekoe", "img": "assets/grade_fbop.jpg", "desc": "Leafy grade with tips. Provides rich aroma and sweetness.", "regions": ["UDAPUSSELLAWAS", "UVA MEDIUM", "WESTERN HIGH", "WESTERN MEDIUM", "UVA HIGH", "LOW GROWNS"]},
        # {"name": "OP1", "full": "Orange Pekoe 1", "img": "assets/grade_op1.jpg", "desc": "Long, wiry specialty leaf. Delivers a smooth, honey-like liquor.", "regions": ["UVA MEDIUM", "WESTERN HIGH", "UVA HIGH", "LOW GROWNS", "WESTERN MEDIUM"]},
        {"name": "PEK / PEK1", "full": "Pekoe / Pekoe 1", "img": "assets/grade_pek.jpg", "desc": "Curly, shotty style. High thickness and infusion depth.", "regions": ["UVA MEDIUM", "WESTERN HIGH", "UVA HIGH", "NUWARA ELIYAS", "UDAPUSSELLAWAS", "WESTERN MEDIUM", "LOW GROWNS"]},
        {"name": "OP / OPA", "full": "Orange Pekoe / Orange Pekoe A", "img": "assets/grade_op.jpg", "desc": "Bold, large leaf. Mild liquor popular in European tea markets.", "regions": ["UVA MEDIUM", "WESTERN HIGH", "WESTERN MEDIUM", "UVA HIGH", "UDAPUSSELLAWAS"]},
        {"name": "BOP1", "full": "Broken Orange Pekoe 1", "img": "assets/grade_bop1.jpg", "desc": "Wiry, shorter than OP1. Known for refined appearance.", "regions": ["UVA MEDIUM", "WESTERN MEDIUM", "LOW GROWNS", "UVA HIGH", "WESTERN HIGH"]}
    ]

    if 'grade_index' not in st.session_state:
        st.session_state.grade_index = 0

    # Layout: Minimalist Arrows (Thin chevrons for professionalism)
    arr_l, c1, c2, c3, arr_r = st.columns([0.15, 1, 1, 1, 0.15], vertical_alignment="top")

    with arr_l:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("‹", key="p_btn"):
            if st.session_state.grade_index > 0:
                st.session_state.grade_index -= 1
                st.rerun()

    display_list = tea_grades[st.session_state.grade_index : st.session_state.grade_index + 3]

    for i, grade in enumerate(display_list):
        with [c1, c2, c3][i]:
            if os.path.exists(grade['img']):
                st.image(grade['img'], use_container_width=True)
            
            tags_html = "".join([f"<span class='region-tag'>{r}</span>" for r in grade['regions']])
            st.markdown(f"""
                <div class='grade-card'>
                    <div class='grade-header'>{grade['name']}</div>
                    <div class='grade-full-name'>{grade['full']}</div>
                    <div class='grade-desc'>{grade['desc']}</div>
                    <p style='font-weight:bold; font-size:0.75rem; margin:0 0 5px 0; color:#ffffff;'>Market Scope:</p>
                    <div>{tags_html}</div>
                </div>
            """, unsafe_allow_html=True)

    with arr_r:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("›", key="n_btn"):
            if st.session_state.grade_index < len(tea_grades) - 3:
                st.session_state.grade_index += 1
                st.rerun()

# ==========================================
# TAB 2 & 3: [Keep your current working blocks here]
# ==========================================

# ==========================================
# TAB 2: MARKET DASHBOARD
# ==========================================
with tab_dash:
    # PASTE YOUR EXISTING TAB 2 CODE HERE
    st.info("Market Dashboard is active. Historical trends and forecast trajectories are synced.")
    st.header("📈 Weekly Market Dashboard")
    
    # Load Data (2022 already filtered by handler)
    df = get_merged_data()

    col_h, col_m, col_l = st.columns(3)

    def create_kpi_chart_block(column, elev, color):
        with column:
            st.subheader(f"{elev} Grown")
            elev_df = df[df['elevation'].str.upper() == elev.upper()]
            
            # 1. Filters
            reg = st.selectbox(f"Region", sorted(elev_df['region'].unique()), key=f"r_{elev}")
            grd = st.selectbox(f"Grade", sorted(elev_df[elev_df['region'] == reg]['grade'].unique()), key=f"g_{elev}")
            
            # 2. Extract specific series (Merged History CSV + Cloud GSheet)
            series_df = elev_df[(elev_df['region'] == reg) & (elev_df['grade'] == grd)].sort_values('true_date')
            
            if series_df.empty:
                st.write("No data found.")
                return

            # --- STEP 1: FIND LATEST ACTUAL PRICE ---
            # Dropping NaNs ensures we find the last date an actual price was recorded
            actuals = series_df.dropna(subset=['price'])
            if not actuals.empty:
                latest_price = actuals['price'].iloc[-1]
                last_actual_date = actuals['true_date'].iloc[-1]
            else:
                latest_price, last_actual_date = 0, series_df['true_date'].iloc[0]

            # --- STEP 2: FIND FORECASTS (PRIORITY: LIVE SESSION > DATABASE) ---
            f1, f2, f4 = None, None, None
            
            # A. Priority 1: Check Live Session (Tab 3 results)
            if 'final_results' in st.session_state:
                res = st.session_state.final_results
                r_col = [c for c in res.columns if c.lower() == 'region'][0]
                g_col = [c for c in res.columns if c.lower() == 'grade'][0]
                
                # Flexible column matching to find 1W, 2W, 4W forecasts
                f1_cols = [c for c in res.columns if '1w' in c.lower() or 'forecast' in c.lower()]
                f2_cols = [c for c in res.columns if '2w' in c.lower()]
                f4_cols = [c for c in res.columns if '4w' in c.lower()]
                
                match = res[(res[r_col].str.upper() == reg.upper()) & (res[g_col].str.upper() == grd.upper())]
                if not match.empty:
                    f1 = match[f1_cols[0]].iloc[0] if f1_cols else None
                    f2 = match[f2_cols[0]].iloc[0] if f2_cols else None
                    f4 = match[f4_cols[0]].iloc[0] if f4_cols else None

            # B. Priority 2: Check Database (History from Google Sheet)
            if f1 is None:
                # Search for any columns containing these keywords in the merged dataframe
                db_f_cols = [c for c in series_df.columns if 'forecast' in c.lower() or 'pred' in c.lower()]
                if db_f_cols:
                    history_forecasts = series_df.dropna(subset=[db_f_cols[0]])
                    if not history_forecasts.empty:
                        latest_f_row = history_forecasts.iloc[-1]
                        f1 = latest_f_row[db_f_cols[0]]
                        f2_m = [c for c in db_f_cols if '2w' in c.lower()]
                        f4_m = [c for c in db_f_cols if '4w' in c.lower()]
                        f2 = latest_f_row[f2_m[0]] if f2_m else None
                        f4 = latest_f_row[f4_m[0]] if f4_m else None

            # --- STEP 3: RENDER KPI METRICS (Thousand Sep, Unit Labels & Theme Colors) ---
            k_cols = st.columns(3)
            # Value formatted with thousand separator, Unit moved to Label
            k_cols[0].metric("Current (Rs/kg)", f"{latest_price:,.0f}")
            
            if f1:
                pct_1w = ((f1 - latest_price) / latest_price) * 100 if latest_price > 0 else 0
                pct_4w = ((f4 - latest_price) / latest_price) * 100 if latest_price > 0 and f4 else 0

                # Card 1: 1-Week Forecast
                k_cols[1].metric(
                    label="Next Week (Rs/kg)", 
                    value=f"{f1:,.0f}", 
                    delta=f"{pct_1w:+.2f}%",
                    delta_color="normal" 
                )
                
                # Card 2: 4-Week Forecast
                k_cols[2].metric(
                    label="Forecast (4W) (Rs/kg)", 
                    value=f"{f4:,.0f}" if f4 else "N/A", 
                    delta=f"{pct_4w:+.2f}%" if f4 else None,
                    delta_color="normal"
                )
            else:
                k_cols[1].metric("Next Week (Rs/kg)", "N/A")
                k_cols[2].metric("Forecast (4W) (Rs/kg)", "N/A")

            # --- STEP 4: RENDER CHART (Complete UX Feature Set) ---
            fig = px.line(series_df, x='true_date', y='price', title=f"{reg} - {grd}", template="plotly_dark")
            
            # Hover Fix for Actual Price: Pure white text on dark background, removes "Actual Price" label
            fig.update_traces(
                line=dict(color=color, width=2.5), 
                name="Actual Price", 
                showlegend=True,
                hovertemplate="<b>%{x|%b %d, %Y}</b><br>Price: Rs. %{y:,.0f}<extra></extra>"
            )
            
            # Mute Grid Lines (0.05 opacity) to keep focus on price trends
            grid_style = dict(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False)

            # 1. 2022 Gap Removal, Grid Styling & Tick Formatting
            fig.update_xaxes(
                **grid_style,
                rangebreaks=[dict(values=pd.date_range("2022-01-01", "2022-12-31"))],
                rangeslider_visible=True,
                tickfont=dict(color="#cccccc")
            )
            fig.update_yaxes(**grid_style, tickfont=dict(color="#cccccc"))

            # 2. Default Zoom (Last 6 Months + room for forecast window)
            last_dt_in_data = series_df['true_date'].max()
            fig.update_xaxes(range=[last_dt_in_data - pd.DateOffset(months=6), last_dt_in_data + pd.Timedelta(weeks=6)])

            # 3. HISTORICAL FORECAST DOTS (Previous Model Performance)
            db_f_cols = [c for c in series_df.columns if 'forecast' in c.lower() or 'pred' in c.lower()]
            if db_f_cols:
                fig.add_scatter(x=series_df['true_date'], y=series_df[db_f_cols[0]], 
                                mode='markers', name='Saved Forecasts', 
                                marker=dict(color='orange', size=3.5, opacity=0.4),
                                hovertemplate="<b>%{x|%b %d, %Y}</b><br>Prev. Forecast: Rs. %{y:,.0f}<extra></extra>")

            # 4. FUTURE FORECAST PATH (Connecting Actuals to 1W, 2W, 4W)
            if f1:
                path_dates = [last_actual_date, last_actual_date + pd.Timedelta(weeks=1)]
                path_prices = [latest_price, f1]
                if f2:
                    path_dates.append(last_actual_date + pd.Timedelta(weeks=2)); path_prices.append(f2)
                if f4:
                    path_dates.append(last_actual_date + pd.Timedelta(weeks=4)); path_prices.append(f4)
                
                fig.add_scatter(x=path_dates, y=path_prices, mode='lines+markers', 
                                name='Forecast Path', 
                                line=dict(dash='dash', color='#FFD700', width=3),
                                marker=dict(size=9, color='#FFD700', symbol='diamond'),
                                hovertemplate="<b>%{x|%b %d, %Y}</b><br>Ensemble Forecast: Rs. %{y:,.0f}<extra></extra>")

            # 5. UI LAYOUT, TRANSPARENCY & HOVER VISIBILITY
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#ffffff"), 
                title_font=dict(size=14, color="#d4af37"),
                margin=dict(l=0, r=0, t=40, b=0),
                height=450,
                # Legend Visibility Fix: Forces white text
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="right", 
                    x=1,
                    font=dict(color="white", size=10),
                    bgcolor="rgba(0,0,0,0)"
                ),
                # Hover Box Fix: Forces dark background and white text for high contrast on all devices
                hoverlabel=dict(
                    bgcolor="#1a1c23", 
                    font_size=12,
                    font_color="white",
                    bordercolor="#d4af37"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

# --- EXECUTION ---
# Ensure these match your previous design settings
create_kpi_chart_block(col_h, "High", "#18ccec")
create_kpi_chart_block(col_m, "Medium", "#9467bd") # Changed from yellow to Purple for contrast
create_kpi_chart_block(col_l, "Low", "#2ca02c")




# # ==========================================
# # TAB 3: PRICE PREDICTOR (TOTAL STABLE INTEGRATION)
# # ==========================================
# with tab_pred:
#     st.header("🔮 Price Prediction Engine")

#     # 1. Initialize Engines in Session State
#     if "gemini" not in st.session_state:
#         st.session_state.gemini = TeaGeminiEngine(api_key=st.secrets["GEMINI_API_KEY"])
#     if "engine" not in st.session_state:
#         st.session_state.engine = TeaInferenceEngine()

#     # Load master history for combinations (using cached function)
#     history = load_base_data() 
#     combos = history[['elevation', 'region', 'grade']].drop_duplicates().sort_values(['elevation', 'region'])

#     # 2. Upload Section
#     st.write("### 📂 1. Upload Weekly Auction Report")
#     uploaded_file = st.file_uploader("Upload Forbes & Walker PDF to pre-fill data", type="pdf")
    
#     if uploaded_file:
#         # Automated AI Extraction & Debug Splitting
#         if 'extracted' not in st.session_state or st.button("🔄 Re-process PDF Report"):
#             with st.status("⚙️ Processing Intelligence Pipeline...", expanded=True) as status:
#                 from utils.pdf_processor import split_pdf_pages
#                 pages = split_pdf_pages(uploaded_file)
                
#                 st.write("🤖 Gemini AI reading and averaging market data...")
#                 st.session_state.extracted = st.session_state.gemini.process_all(pages)
#                 # Clear previous results when a new file is uploaded
#                 if 'final_results' in st.session_state:
#                     del st.session_state.final_results
#                 if 'show_results' in st.session_state:
#                     st.session_state.show_results = False
#                 status.update(label="✅ AI Extraction & Averaging Complete!", state="complete")
        
#         ext = st.session_state.extracted

#         st.divider()
#         st.subheader("🛠 Step 1: Verify Market Context")
        
#         # --- ROBUST DATE HANDLING (CLOUD COMPATIBLE) ---
#         raw_ai_date = ext.get('sale_date')
#         date_extracted_successfully = False
#         def_date = datetime.date.today()
        
#         if raw_ai_date:
#             try:
#                 temp_date = pd.to_datetime(raw_ai_date)
#                 if not pd.isna(temp_date):
#                     def_date = temp_date.date()
#                     date_extracted_successfully = True
#             except: pass
        
#         col_m1, col_m2 = st.columns(2)
#         verified_date = col_m1.date_input("Auction Date (Anchor)", value=def_date)
#         u_usd = col_m2.number_input("Latest USD/LKR Rate", value=float(ext.get('usd_rate', 300.0)), format="%.2f")
        
#         # --- DATA INTEGRITY GUARD ---
#         if not date_extracted_successfully:
#             st.warning("⚠️ **Please select the Auction Date of the report before continuing** ")
#             date_confirmed = st.checkbox("I have manually verified that the Auction Date above is correct.")
#         else:
#             st.success(f"✅ AI detected Auction Date: {verified_date}")
#             date_confirmed = True

#         if not date_confirmed:
#             st.error("🚨 Please verify/correct the Auction Date and check the confirmation box to proceed.")
#             st.stop()

#         # --- NORMALIZATION HELPERS ---
#         def clean_text(text):
#             if not text: return ""
#             return str(text).replace("[", "").replace("]", "").replace("||", "|").strip().upper()

#         def clean_grade(text):
#             if not text: return ""
#             return str(text).replace("[", "").replace("]", "").replace("/", "").replace(" ", "").upper().strip()
        


# # --- UPDATED ADVANCED MAPPING & AVERAGING LOGIC ---
        
#         # 1. Clean the AI-extracted dataframe for matching
#         df_pdf = ext['extracted_prices_df'].copy()
#         if not df_pdf.empty:
#             df_pdf['clean_reg'] = df_pdf['region'].apply(clean_text)
#             # For AI data, we keep slashes but remove spaces/brackets for comparison
#             df_pdf['clean_grd'] = df_pdf['grade'].astype(str).replace(r'[\[\]\s]', '', regex=True).str.upper()

#         # 2. Normalize AI Weather and Intake Mappings
#         ai_w_map = {clean_text(k): v for k, v in ext.get('weather_mapping', {}).items()}
#         ai_i_map = {clean_text(k): v for k, v in ext.get('intake_mapping', {}).items()}

#         # 3. Build the 43-Row Table with Priority Logic
#     # --- 3. BUILD THE 43-ROW TABLE (CLEAN UI + TECH REPORT) ---
#         verify_rows = []
#         mapping_report = [] # To store the "Why" for the investigation section

#         for _, row in combos.iterrows():
#             reg_h = row['region']
#             grd_h = row['grade']
#             hist_reg = clean_text(reg_h)
#             hist_grd = clean_grade(grd_h)
#             lookup_key = f"{hist_reg}|{hist_grd}"
            
#             hist_p = history[(history['region'] == reg_h) & (history['grade'] == grd_h)]['price'].iloc[-1]
            
#             current_p = None
#             display_src = "⏳ History"
#             tech_note = "Not found in PDF."

#             if not df_pdf.empty:
#                 # PRIORITY 1: EXACT MATCH
#                 exact_match = df_pdf[(df_pdf['clean_reg'] == hist_reg) & (df_pdf['clean_grd'] == hist_grd)]
#                 if not exact_match.empty:
#                     current_p = exact_match['price'].mean()
#                     display_src = "✅ PDF"
#                     tech_note = "Exact match found and averaged."
                
#                 # PRIORITY 2: SLASH GRADE DECOMPOSITION
#                 elif "/" in grd_h:
#                     parts = [p.strip().upper().replace(" ", "") for p in grd_h.split("/")]
#                     matches = df_pdf[(df_pdf['clean_reg'] == hist_reg) & (df_pdf['clean_grd'].isin(parts))]
                    
#                     if not matches.empty:
#                         part_averages = matches.groupby('clean_grd')['price'].mean()
#                         if len(part_averages) > 1:
#                             price_diff = abs(part_averages.iloc[0] - part_averages.iloc[1])
#                             if price_diff <= 250:
#                                 current_p = part_averages.mean()
#                                 display_src = "✅ PDF"
#                                 tech_note = f"Averaged {list(part_averages.index)} (Diff: {price_diff:.0f})"
#                             else:
#                                 current_p = hist_p
#                                 display_src = "⏳ History"
#                                 tech_note = f"High Diff ({price_diff:.0f} > 250) between {list(part_averages.index)}. Using History."
#                         else:
#                             current_p = part_averages.iloc[0]
#                             display_src = "✅ PDF"
#                             tech_note = f"Partial match: used {part_averages.index[0]} only."

#             if current_p is None:
#                 current_p = hist_p
            
#             # Add to the Clean Grid
#             verify_rows.append({
#                 "Region": reg_h, "Grade": grd_h, "Price (LKR)": float(current_p),
#                 "Source": display_src, "Weather": ai_w_map.get(hist_reg, "Bright"), "Intake": ai_i_map.get(hist_reg, "Maintained")
#             })
            
#             # Add to the Technical Report (for the expander)
#             mapping_report.append(f"{reg_h} | {grd_h}: {tech_note}")

#         # Render the Clean Data Editor
#         edited_df = st.data_editor(pd.DataFrame(verify_rows), use_container_width=True, hide_index=True, height=400,
#             column_config={"Source": st.column_config.TextColumn(disabled=True)})




#         # # 1. Process Extracted AI Prices into Lookup Map
#         # pdf_avg_price_lookup = {}
#         # if not ext['extracted_prices_df'].empty:
#         #     df_pdf = ext['extracted_prices_df'].copy()
#         #     df_pdf['clean_reg'] = df_pdf['region'].apply(clean_text)
#         #     df_pdf['clean_grd'] = df_pdf['grade'].apply(clean_grade)
#         #     pdf_avg_price_lookup = dict(zip(df_pdf['clean_reg'] + "|" + df_pdf['clean_grd'], df_pdf['price']))
        
#         # # 2. Normalize AI Weather/Intake
#         # ai_w_map = {clean_text(k): v for k, v in ext.get('weather_mapping', {}).items()}
#         # ai_i_map = {clean_text(k): v for k, v in ext.get('intake_mapping', {}).items()}

#         # # 3. Build the 43-Row Table
#         # verify_rows = []
#         # for _, row in combos.iterrows():
#         #     h_reg = clean_text(row['region'])
#         #     h_grd = clean_grade(row['grade'])
#         #     lookup_key = f"{h_reg}|{h_grd}"
#         #     hist_p = history[(history['region'] == row['region']) & (history['grade'] == row['grade'])]['price'].iloc[-1]
            
#         #     # Match check
#         #     if lookup_key in pdf_avg_price_lookup:
#         #         curr_p, src_label = round(pdf_avg_price_lookup[lookup_key], 2), "✅ PDF"
#         #     else:
#         #         curr_p, src_label = hist_p, "⏳ History"
            
#         #     verify_rows.append({
#         #         "Region": row['region'], "Grade": row['grade'],
#         #         "Price (LKR)": float(curr_p), "Source": src_label,
#         #         "Weather": ai_w_map.get(h_reg, "Bright"),
#         #         "Intake": ai_i_map.get(h_reg, "Maintained")
#         #     })

#         # --- THE VERIFICATION GRID ---
#         # edited_df = st.data_editor(pd.DataFrame(verify_rows), use_container_width=True, hide_index=True, height=400,
#         #     column_config={
#         #         "Source": st.column_config.TextColumn(disabled=True),
#         #         "Region": st.column_config.TextColumn(disabled=True),
#         #         "Grade": st.column_config.TextColumn(disabled=True),
#         #         "Weather": st.column_config.SelectboxColumn(options=["Bright", "Rainy", "Overcast", "Mixed"]),
#         #         "Intake": st.column_config.SelectboxColumn(options=["Maintained", "Increase", "Decline", "Slight Decline"])
#         #     })

  
#         # # --- THE INVESTIGATION BUTTON (DEBUG EXPANDER) ---
#         # with st.expander("🔍 View Raw Intelligence Extraction Details"):
#         #     st.info("Raw pipe-delimited data exactly as returned by Gemini AI.")
#         #     st.write(f"**Extracted USD Rate:** Rs. {ext.get('usd_rate')}")
#         #     col_a, col_b = st.columns(2)
#         #     col_a.text_area("Weather Extraction (Raw)", ext.get('weather_raw', 'No data'), height=150)
#         #     col_b.text_area("Top Price Extraction (Raw)", ext.get('prices_raw', 'No data'), height=150)





# # --- UPDATED INVESTIGATION SECTION ---
#         with st.expander("🔍 View Raw Intelligence Extraction Details"):
#             st.info("Technical Mapping Report: Why prices were selected or averaged.")
            
#             # Display the technical notes we gathered in the loop
#             st.text_area("Extraction Logic Notes", value="\n".join(mapping_report), height=200)
            
#             st.divider()
#             st.write(f"**Extracted USD Rate:** Rs. {ext.get('usd_rate')}")
#             col_a, col_b = st.columns(2)
#             col_a.text_area("Weather Extraction (Raw)", ext.get('weather_raw', 'No data'), height=150)
#             col_b.text_area("Top Price Extraction (Raw)", ext.get('prices_raw', 'No data'), height=150)





#         # --- 3. PREDICTION EXECUTION ---
#         if st.button("🚀 Confirm & Run Forecast"):
#             st.session_state.current_user_payload = {
#                 "usd_rate": u_usd,
#                 "weather_mapping": dict(zip(edited_df['Region'], edited_df['Weather'])),
#                 "intake_mapping": dict(zip(edited_df['Region'], edited_df['Intake'])),
#                 "manual_prices": dict(zip(edited_df['Region'] + "|" + edited_df['Grade'], edited_df['Price (LKR)']))
#             }
            
#             with st.spinner("🧠 Generating Multi-Horizon Forecasts..."):
#                 st.session_state.final_results = st.session_state.engine.run_prediction(history, st.session_state.current_user_payload)
#                 st.session_state.show_results = True
#                 st.rerun()

#         # --- 4. DISPLAY AND SAVE RESULTS ---
#         if st.session_state.get('show_results') and 'final_results' in st.session_state:
#             st.divider()
#             st.subheader("📈 Integrated Forecast Results")
#             st.dataframe(st.session_state.final_results, use_container_width=True)
            
#             if st.button("💾 Finalize & Push to Cloud (Google Sheets)"):
#                 with st.spinner("Syncing to Cloud..."):
#                     to_save = st.session_state.final_results.copy()
#                     to_save['true_date'] = verified_date 
#                     to_save['USD_to_LKR'] = u_usd
                    
#                     payload = st.session_state.current_user_payload
#                     to_save['weather_cat'] = to_save['Region'].map(payload['weather_mapping'])
#                     to_save['crop_cat'] = to_save['Region'].map(payload['intake_mapping'])
                    
#                     # Restore Elevation mapping for Dashboard
#                     elev_map = dict(zip(combos['region'], combos['elevation']))
#                     to_save['elevation'] = to_save['Region'].map(elev_map)
                    
#                     # Final Schema Formatting
#                     to_save = to_save.rename(columns={
#                         'Region': 'region', 'Grade': 'grade',
#                         'Current Price': 'price', '1W Forecast (Y)': 'forecast_1w',
#                         '2W Forecast (Y)': 'forecast_2w', '4W Forecast (Y)': 'forecast_4w'
#                     })

#                     # Strict 11-column selection
#                     gsheet_cols = ['true_date', 'region', 'grade', 'elevation', 'price', 'forecast_1w', 'forecast_2w', 'forecast_4w', 'weather_cat', 'crop_cat', 'USD_to_LKR']
#                     final_to_push = to_save[gsheet_cols]

#                     if save_to_gsheet(final_to_push):
#                         st.balloons()
#                         st.success("✅ Dashboard Updated Permanently!")
#                         st.rerun()






# ==========================================
# TAB 3: PRICE PREDICTOR (TOTAL STABLE INTEGRATION)
# ==========================================
with tab_pred:
    st.header("🔮 Price Prediction Engine")

    # 1. Initialize Engines in Session State
    if "gemini" not in st.session_state:
        st.session_state.gemini = TeaGeminiEngine(api_key=st.secrets["GEMINI_API_KEY"])
    if "engine" not in st.session_state:
        st.session_state.engine = TeaInferenceEngine()

    # Load master history for combinations (using cached function)
    history = load_base_data() 
    combos = history[['elevation', 'region', 'grade']].drop_duplicates().sort_values(['elevation', 'region'])

    # 2. Upload Section
    st.write("### 📂 1. Upload Weekly Auction Report")
    uploaded_file = st.file_uploader("Upload Forbes & Walker PDF to pre-fill data", type="pdf")
    
    if uploaded_file:
        # Automated AI Extraction & Debug Splitting
        if 'extracted' not in st.session_state or st.button("🔄 Re-process PDF Report"):
            with st.status("⚙️ Processing Intelligence Pipeline...", expanded=True) as status:
                from utils.pdf_processor import split_pdf_pages
                pages = split_pdf_pages(uploaded_file)
                
                st.write("🤖 Gemini AI reading and averaging market data...")
                st.session_state.extracted = st.session_state.gemini.process_all(pages)
                # Clear previous results when a new file is uploaded
                if 'final_results' in st.session_state:
                    del st.session_state.final_results
                if 'show_results' in st.session_state:
                    st.session_state.show_results = False
                status.update(label="✅ AI Extraction & Averaging Complete!", state="complete")
        
        ext = st.session_state.extracted

        st.divider()
        st.subheader("🛠 Step 1: Verify Market Context")
        
        # --- ROBUST DATE HANDLING (CLOUD COMPATIBLE) ---
        raw_ai_date = ext.get('sale_date')
        date_extracted_successfully = False
        def_date = datetime.date.today()
        
        if raw_ai_date:
            try:
                temp_date = pd.to_datetime(raw_ai_date)
                if not pd.isna(temp_date):
                    def_date = temp_date.date()
                    date_extracted_successfully = True
            except: pass
        
        col_m1, col_m2 = st.columns(2)
        verified_date = col_m1.date_input("Auction Date (Anchor)", value=def_date)
        u_usd = col_m2.number_input("Latest USD/LKR Rate", value=float(ext.get('usd_rate', 300.0)), format="%.2f")
        
        # --- DATA INTEGRITY GUARD ---
        if not date_extracted_successfully:
            st.warning("⚠️ **Please select the Auction Date of the report before continuing** ")
            date_confirmed = st.checkbox("I have manually verified that the Auction Date above is correct.")
        else:
            st.success(f"✅ AI detected Auction Date: {verified_date}")
            date_confirmed = True

        if not date_confirmed:
            st.error("🚨 Please verify/correct the Auction Date and check the confirmation box to proceed.")
            st.stop()

        # Keep the report date for source matching, but use T+1 for forecasting.
        forecast_date = pd.to_datetime(verified_date) + pd.Timedelta(days=7)

        # --- NORMALIZATION HELPERS ---
        def clean_key(text):
            if not text:
                return ""
            return re.sub(r'[^A-Z0-9]+', '', str(text).upper())

        def clean_text(text):
            if not text: return ""
            return clean_key(text)

        def clean_grade(text):
            if not text: return ""
            return clean_key(text)

        def grade_variants(text):
            raw_text = str(text).upper() if text is not None else ""
            parts = [clean_key(part) for part in raw_text.replace("-", "/").split("/")]
            alias_map = {
                "OPA": "OP",
                "OP1": "OP",
                "PEK1": "PEK",
                "FBOP1": "FBOP",
                "BOPFSP": "BOPF",
                "BOP1": "BOP",
            }

            variants = set()
            for part in parts:
                if not part:
                    continue
                variants.add(part)
                variants.add(alias_map.get(part, part))
            return variants

        def grade_family(text):
            variants = grade_variants(text)
            family_map = {
                "BOP": "BOP",
                "BOPF": "BOPF",
                "FBOP": "FBOP",
                "PEK": "PEK",
                "OP": "OP",
            }

            for variant in variants:
                for prefix, family in family_map.items():
                    if variant.startswith(prefix):
                        return family
            return "" if not variants else sorted(variants)[0]
        


# --- UPDATED ADVANCED MAPPING & AVERAGING LOGIC ---
        
        # 1. Clean the AI-extracted dataframe for matching
        df_pdf = ext['extracted_prices_df'].copy()
        if not df_pdf.empty:
            df_pdf['clean_reg'] = df_pdf['region'].apply(clean_key)
            df_pdf['clean_grd'] = df_pdf['grade'].apply(clean_key)
            df_pdf['grade_family'] = df_pdf['grade'].apply(grade_variants)
            df_pdf['grade_group'] = df_pdf['grade'].apply(grade_family)

        # 2. Normalize AI Weather and Intake Mappings
        ai_w_map = {clean_text(k): v for k, v in ext.get('weather_mapping', {}).items()}
        ai_i_map = {clean_text(k): v for k, v in ext.get('intake_mapping', {}).items()}

        # 3. Build the 43-Row Table with Priority Logic
        verify_rows = []
        mapping_report = [] # To store the "Why" for the investigation section

        for _, row in combos.iterrows():
            reg_h = row['region']
            grd_h = row['grade']
            hist_reg = clean_key(reg_h)
            hist_grd = clean_key(grd_h)
            hist_grade_family = grade_variants(grd_h)
            hist_grade_group = grade_family(grd_h)
            
            hist_p = history[(history['region'] == reg_h) & (history['grade'] == grd_h)]['price'].iloc[-1]
            
            current_p = None
            display_src = "⏳ History"
            tech_note = "Not found in PDF."

            if not df_pdf.empty:
                exact_match = df_pdf[(df_pdf['clean_reg'] == hist_reg) & (df_pdf['clean_grd'] == hist_grd)]

                if exact_match.empty:
                    family_match = df_pdf[
                        (df_pdf['clean_reg'] == hist_reg) &
                        (
                            (df_pdf['grade_group'] == hist_grade_group) |
                            (df_pdf['grade_family'].apply(lambda family: bool(family & hist_grade_family)))
                        )
                    ]
                    if not family_match.empty:
                        exact_match = family_match

                if not exact_match.empty:
                    current_p = exact_match['price'].mean()
                    display_src = "✅ PDF"
                    tech_note = "Matched PDF row(s) and averaged."

            if current_p is None:
                current_p = hist_p
            
            # Add to the Clean Grid
            verify_rows.append({
                "Region": reg_h, "Grade": grd_h, "Price (LKR)": float(current_p),
                "Source": display_src, "Weather": ai_w_map.get(hist_reg, "Bright"), "Intake": ai_i_map.get(hist_reg, "Maintained")
            })
            
            # Add to the Technical Report (for the expander)
            mapping_report.append(f"{reg_h} | {grd_h}: {tech_note}")

        # Render the Clean Data Editor
        edited_df = st.data_editor(pd.DataFrame(verify_rows), use_container_width=True, hide_index=True, height=400,
            column_config={"Source": st.column_config.TextColumn(disabled=True)})

        # pdf_rows = int((pd.DataFrame(verify_rows)["Source"] == "✅ PDF").sum()) if verify_rows else 0
        # history_rows = int((pd.DataFrame(verify_rows)["Source"] == "⏳ History").sum()) if verify_rows else 0
        # st.caption(
        #     f"Verification source summary: PDF rows = {pdf_rows}, History rows = {history_rows}, "
        #     f"Gemini extracted rows = {len(df_pdf)}"
        # )


# --- UPDATED INVESTIGATION SECTION ---
        with st.expander("🔍 View Raw Intelligence Extraction Details"):
            st.info("Technical Mapping Report: Why prices were selected or averaged.")
            
            # Display the technical notes we gathered in the loop
            st.text_area("Extraction Logic Notes", value="\n".join(mapping_report), height=200)
            
            st.divider()
            st.write(f"**Extracted USD Rate:** Rs. {ext.get('usd_rate')}")
            col_a, col_b = st.columns(2)
            col_a.text_area("Weather Extraction (Raw)", ext.get('weather_raw', 'No data'), height=150)
            col_b.text_area("Top Price Extraction (Raw)", ext.get('prices_raw', 'No data'), height=150)



        # --- 3. PREDICTION EXECUTION ---
        if st.button("🚀 Confirm & Run Forecast"):
            st.session_state.current_user_payload = {
                "usd_rate": u_usd,
                "auction_date": verified_date,
                "forecast_date": forecast_date,
                "weather_mapping": dict(zip(edited_df['Region'], edited_df['Weather'])),
                "intake_mapping": dict(zip(edited_df['Region'], edited_df['Intake'])),
                "manual_prices": dict(zip(edited_df['Region'] + "|" + edited_df['Grade'], edited_df['Price (LKR)']))
            }
            
            with st.spinner("🧠 Generating Multi-Horizon Forecasts..."):
                st.session_state.final_results = st.session_state.engine.run_prediction(history, st.session_state.current_user_payload)
                st.session_state.show_results = True
                st.rerun()

        # --- 4. DISPLAY AND SAVE RESULTS ---
        if st.session_state.get('show_results') and 'final_results' in st.session_state:
            st.divider()
            st.subheader("📈 Integrated Forecast Results")
            st.dataframe(st.session_state.final_results, use_container_width=True)
            
            if st.button("💾 Finalize & Push to Cloud (Google Sheets)"):
                with st.spinner("Syncing to Cloud..."):
                    to_save = st.session_state.final_results.copy()
                    to_save['true_date'] = verified_date 
                    to_save['USD_to_LKR'] = u_usd
                    
                    payload = st.session_state.current_user_payload
                    to_save['weather_cat'] = to_save['Region'].map(payload['weather_mapping'])
                    to_save['crop_cat'] = to_save['Region'].map(payload['intake_mapping'])
                    
                    # Restore Elevation mapping for Dashboard
                    elev_map = dict(zip(combos['region'], combos['elevation']))
                    to_save['elevation'] = to_save['Region'].map(elev_map)
                    
                    # Final Schema Formatting
                    to_save = to_save.rename(columns={
                        'Region': 'region', 'Grade': 'grade',
                        'Current Price': 'price', '1W Forecast (Y)': 'forecast_1w',
                        '2W Forecast (Y)': 'forecast_2w', '4W Forecast (Y)': 'forecast_4w'
                    })

                    # Strict 11-column selection
                    gsheet_cols = ['true_date', 'region', 'grade', 'elevation', 'price', 'forecast_1w', 'forecast_2w', 'forecast_4w', 'weather_cat', 'crop_cat', 'USD_to_LKR']
                    final_to_push = to_save[gsheet_cols]

                    if save_to_gsheet(final_to_push):
                        st.balloons()
                        st.success("✅ Dashboard Updated Permanently!")
                        st.rerun()