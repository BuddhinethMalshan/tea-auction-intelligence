import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import base64
import datetime

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

        /* 2. Simplified Safe Typography (No longer blocks Green/Red) */
        h1, h2, h3, .stMarkdown p {{
            color: #ffffff !important;
        }}

        /* 3. METRIC COLOR FIX: Force Green/Red for Market Trends */
        [data-testid="stMetricValue"] {{
            color: #ffffff !important;
        }}
        [data-testid="stMetricDelta"] > div {{
            color: inherit !important;
        }}
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
            padding: 12px 15px; /* Reduced padding */
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: -10px;   /* Pulls card closer to the image */
            min-height: 220px;   /* Reduced min-height */
            height: auto;
        }}
        .grade-header {{ color: #ffffff; font-size: 1.05rem; font-weight: bold; margin: 0px !important; /* Remove default margins */}}
        .grade-full-name {{ font-size: 0.85rem; color: #d4af37; }}
        .grade-desc {{ font-size: 0.82rem; color: #cccccc; }}
        
        .region-tag {{
            background-color: #1e3d2b;
            color: #d4af37 !important;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.65rem;
            border: 1px solid #d4af37;
        }}

        /* 7. Minimalist Arrows */
        div[data-testid="column"] button {{
            background-color: transparent !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            border-radius: 50% !important;
        }}
        div[data-testid="column"] button:hover {{
            border-color: #d4af37 !important;
            color: #d4af37 !important;
        }}
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
        /* Background & Overlay */
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

        /* Typography */
        h1, h2, h3, h4, .stMarkdown p {{
            color: #ffffff !important;
        }}

        /* Metric Colors Fix */
        [data-testid="stMetricValue"] {{ color: #ffffff !important; }}
        [data-testid="stMetricDelta"] > div {{ color: inherit !important; }}
        div[data-testid="stMetricDelta"] > div[data-direction="up"] {{ color: #09ab3b !important; }}
        div[data-testid="stMetricDelta"] > div[data-direction="down"] {{ color: #ff4b4b !important; }}

        /* Market Coverage Badges */
        .combo-container {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: flex-start;
        }}
        .combo-badge {{
            background-color: rgba(0, 0, 0, 0.5);
            color: #d4af37 !important;
            border: 1px solid #d4af37;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 500;
            white-space: nowrap;
        }}

        /* Grade Cards (Compact & Hugging Image) */
        .grade-card {{
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 12px 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 0px; 
            height: auto;
            min-height: 220px;
        }}
        .grade-header {{ color: #ffffff; font-size: 1.1rem; font-weight: bold; margin-bottom: 2px; }}
        .grade-full-name {{ font-size: 0.82rem; color: #d4af37; margin-bottom: 8px; font-weight: 500; }}
        .grade-desc {{ font-size: 0.8rem; color: #bbbbbb; line-height: 1.3; margin-bottom: 12px; }}
        
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

        /* Image Gap Fix */
        [data-testid="stImage"] {{
            margin-bottom: -15px !important;
        }}

        /* Professional Minimalist Arrows */
        div[data-testid="column"] button {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            border-radius: 50% !important;
            transition: 0.3s;
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
        {"name": "OP1", "full": "Orange Pekoe 1", "img": "assets/grade_op1.jpg", "desc": "Long, wiry specialty leaf. Delivers a smooth, honey-like liquor.", "regions": ["UVA MEDIUM", "WESTERN HIGH", "UVA HIGH", "LOW GROWNS", "WESTERN MEDIUM"]},
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
            
            # 2. Extract specific series
            series_df = elev_df[(elev_df['region'] == reg) & (elev_df['grade'] == grd)].sort_values('true_date')
            
            if series_df.empty:
                st.write("No data found.")
                return

            # --- STEP 1: FIND LATEST ACTUAL PRICE ---
            actuals = series_df.dropna(subset=['price'])
            if not actuals.empty:
                latest_price = actuals['price'].iloc[-1]
                last_actual_date = actuals['true_date'].iloc[-1]
            else:
                latest_price, last_actual_date = 0, series_df['true_date'].iloc[0]

            # --- STEP 2: FIND FORECASTS (LIVE SESSION OR DATABASE) ---
            f1, f2, f4 = None, None, None
            
            # A. Priority 1: Check Live Session (Tab 3 was just run)
            if 'final_results' in st.session_state:
                res = st.session_state.final_results
                r_col = [c for c in res.columns if c.lower() == 'region'][0]
                g_col = [c for c in res.columns if c.lower() == 'grade'][0]
                
                # Find the specific columns for 1W, 2W, 4W based on keywords
                f1_cols = [c for c in res.columns if '1w' in c.lower() or 'forecast' in c.lower()]
                f2_cols = [c for c in res.columns if '2w' in c.lower()]
                f4_cols = [c for c in res.columns if '4w' in c.lower()]
                
                match = res[(res[r_col].str.upper() == reg.upper()) & (res[g_col].str.upper() == grd.upper())]
                if not match.empty:
                    f1 = match[f1_cols[0]].iloc[0] if f1_cols else None
                    f2 = match[f2_cols[0]].iloc[0] if f2_cols else None
                    f4 = match[f4_cols[0]].iloc[0] if f4_cols else None

            # B. Priority 2: Check Database (Loaded from GSheet history)
            if f1 is None:
                db_f_cols = [c for c in series_df.columns if 'forecast' in c.lower() or 'pred' in c.lower()]
                if db_f_cols:
                    # Look for the last row that HAS a forecast saved
                    history_forecasts = series_df.dropna(subset=[db_f_cols[0]])
                    if not history_forecasts.empty:
                        latest_f_row = history_forecasts.iloc[-1]
                        f1 = latest_f_row[db_f_cols[0]]
                        # Match 2w/4w by name
                        f2_m = [c for c in db_f_cols if '2w' in c.lower()]
                        f4_m = [c for c in db_f_cols if '4w' in c.lower()]
                        f2 = latest_f_row[f2_m[0]] if f2_m else None
                        f4 = latest_f_row[f4_m[0]] if f4_m else None

            # --- STEP 3: RENDER KPI METRICS ---
            # --- STEP 3: RENDER KPI METRICS (Color Optimized) ---
            k_cols = st.columns(3)
            k_cols[0].metric("Current", f"Rs. {latest_price:.0f}")
            
            if f1:
                # Calculate Percentage Changes
                pct_1w = ((f1 - latest_price) / latest_price) * 100 if latest_price > 0 else 0
                pct_4w = ((f4 - latest_price) / latest_price) * 100 if latest_price > 0 and f4 else 0

                # Card 1: 1-Week Forecast
                # normal color = green for positive, red for negative
                k_cols[1].metric(
                    label="Next Week", 
                    value=f"Rs. {f1:.0f}", 
                    delta=f"{pct_1w:+.2f}%",
                    delta_color="normal" 
                )
                
                # Card 2: 4-Week Forecast
                k_cols[2].metric(
                    label="Forecast (4W)", 
                    value=f"Rs. {f4:.0f}" if f4 else "N/A", 
                    delta=f"{pct_4w:+.2f}%" if f4 else None,
                    delta_color="normal"
                )
            else:
                k_cols[1].metric("Next Week", "N/A")
                k_cols[2].metric("Forecast", "N/A")

            # --- STEP 4: RENDER CHART ---
            fig = px.line(series_df, x='true_date', y='price', title=f"{reg} - {grd}")
            fig.update_traces(line=dict(color=color, width=2), name="Market Price", showlegend=True)
            
            # 1. 2022 Gap Removal
            fig.update_xaxes(rangebreaks=[dict(values=pd.date_range("2022-01-01", "2022-12-31"))])
            
            # 2. Horizontal Scroll Bar (Range Slider)
            fig.update_xaxes(rangeslider_visible=True)

            # 3. Default Zoom (Last 6 Months + Forecast window)
            last_dt_in_data = series_df['true_date'].max()
            fig.update_xaxes(range=[last_dt_in_data - pd.DateOffset(months=6), last_dt_in_data + pd.Timedelta(weeks=6)])

            # 4. HISTORICAL FORECAST DOTS (Restored Feature)
            # Shows orange dots where the model made predictions in the past
            db_f_cols = [c for c in series_df.columns if 'forecast' in c.lower() or 'pred' in c.lower()]
            if db_f_cols:
                fig.add_scatter(x=series_df['true_date'], y=series_df[db_f_cols[0]], 
                                mode='markers', name='Past Forecasts', 
                                marker=dict(color='orange', size=3, opacity=0.4))

            # 5. FUTURE FORECAST PATH (Connecting Live/Saved Forecasts)
            if f1:
                path_dates = [last_actual_date, last_actual_date + pd.Timedelta(weeks=1)]
                path_prices = [latest_price, f1]
                if f2:
                    path_dates.append(last_actual_date + pd.Timedelta(weeks=2))
                    path_prices.append(f2)
                if f4:
                    path_dates.append(last_actual_date + pd.Timedelta(weeks=4))
                    path_prices.append(f4)
                
                fig.add_scatter(x=path_dates, y=path_prices, mode='lines+markers', 
                                name='Forecast Path', 
                                line=dict(dash='dash', color="#FF7B00", width=3),
                                marker=dict(size=10, color="#FF4D00", symbol='diamond'))

            # 6. UI Layout Cleanup
            fig.update_layout(
                height=450,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)

    create_kpi_chart_block(col_h, "High", "#18ccec")
    create_kpi_chart_block(col_m, "Medium", "#d4de14")
    create_kpi_chart_block(col_l, "Low", "#2ca02c")



# ==========================================
# TAB 3: PRICE PREDICTOR
# ==========================================
with tab_pred:
    st.header("🔮 Price Prediction Engine")

    # 1. Initialize Engines
    if "gemini" not in st.session_state:
        st.session_state.gemini = TeaGeminiEngine(api_key=st.secrets["GEMINI_API_KEY"])
    if "engine" not in st.session_state:
        st.session_state.engine = TeaInferenceEngine()

    # Load master history for combinations
    # Using the cached function we created earlier for speed
    history = load_base_data() 
    combos = history[['elevation', 'region', 'grade']].drop_duplicates().sort_values(['elevation', 'region'])

    # 2. Upload Section
    uploaded_file = st.file_uploader("Upload Weekly Auction Report (PDF)", type="pdf")
    
    if uploaded_file:
        if 'extracted' not in st.session_state or st.button("🔄 Re-process PDF Report"):
            with st.status("🛠 AI Data Intelligence...", expanded=True) as status:
                from utils.pdf_processor import split_pdf_pages
                pages = split_pdf_pages(uploaded_file)
                st.session_state.extracted = st.session_state.gemini.process_all(pages)
                status.update(label="✅ AI Extraction Complete", state="complete")
        
        ext = st.session_state.extracted

        st.divider()
        st.subheader("🛠 Step 1: Verify Market Context")
        
        # --- ROBUST DATE HANDLING (CLOUD COMPATIBLE) ---
        raw_ai_date = ext.get('sale_date')
        date_extracted_successfully = False
        
        # We use today's date ONLY as a placeholder to prevent the Cloud crash
        # But we track if it was actually found by the AI
        def_date = datetime.date.today()
        
        if raw_ai_date:
            try:
                temp_date = pd.to_datetime(raw_ai_date)
                if not pd.isna(temp_date):
                    def_date = temp_date.date()
                    date_extracted_successfully = True
            except:
                pass
        
        col_m1, col_m2 = st.columns(2)
        
        # This renders safely on Cloud because def_date is never None
        verified_date = col_m1.date_input(
            "Auction Date (Anchor)", 
            value=def_date, 
            help="Mandatory: Select the Wednesday of the auction."
        )
        
        u_usd = col_m2.number_input(
            "Latest USD/LKR Rate", 
            value=float(ext.get('usd_rate', 300.0)), 
            format="%.2f"
        )
        
        # --- DATA INTEGRITY GUARD ---
        # If AI failed, force the user to interact with a checkbox to prevent accidental "Today" sync
        if not date_extracted_successfully:
            st.warning("⚠️ **AI Date Extraction Failed.** The date below is set to 'Today' as a placeholder.")
            date_confirmed = st.checkbox("I have manually verified that the Auction Date above is correct.")
        else:
            st.success(f"✅ AI detected Auction Date: {verified_date}")
            date_confirmed = True # AI found it, so it's pre-confirmed

        # Logic to block the rest of the UI if date isn't confirmed
        if not date_confirmed:
            st.error("🚨 Please verify/correct the Auction Date and check the confirmation box to proceed.")
            st.stop() # Stops execution here until the user checks the box

        # --- TABLE BUILDING HELPERS ---
        weather_opts = ["Bright", "Rainy", "Overcast", "Mixed"]
        intake_opts = ["Maintained", "Decline", "Increase", "Slight Decline"]

        def norm_reg(name):
            n = str(name).upper().strip()
            if "NUWARA ELIYA" in n: return "NUWARA ELIYAS"
            if "UDAPUSSELLAWA" in n: return "UDAPUSSELLAWAS"
            if "LOW GROWN" in n: return "LOW GROWNS"
            return n

        avg_p_map = {}
        if not ext['extracted_prices_df'].empty:
            df_avg_p = ext['extracted_prices_df']
            avg_p_map = dict(zip(df_avg_p['region'] + "|" + df_avg_p['grade'], df_avg_p['price']))
        
        ai_w_map = {norm_reg(k): v for k, v in ext.get('weather_mapping', {}).items()}
        ai_i_map = {norm_reg(k): v for k, v in ext.get('intake_mapping', {}).items()}

        verify_rows = []
        for _, row in combos.iterrows():
            reg_u, grd_u = row['region'].upper(), row['grade'].upper()
            lookup_key = f"{reg_u}|{grd_u}"
            hist_p = history[(history['region'] == row['region']) & (history['grade'] == row['grade'])]['price'].iloc[-1]
            
            is_pdf = lookup_key in avg_p_map
            verify_rows.append({
                "Region": row['region'], "Grade": row['grade'],
                "Price (LKR)": float(avg_p_map.get(lookup_key, hist_p)),
                "Source": "✅ PDF" if is_pdf else "⏳ History",
                "Weather": ai_w_map.get(reg_u, "Bright"),
                "Intake": ai_i_map.get(reg_u, "Maintained")
            })

        edited_df = st.data_editor(pd.DataFrame(verify_rows), use_container_width=True, hide_index=True, height=400,
            column_config={
                "Source": st.column_config.TextColumn(disabled=True),
                "Weather": st.column_config.SelectboxColumn(options=weather_opts),
                "Intake": st.column_config.SelectboxColumn(options=intake_opts)
            })
        
        # Debug Expander (Human-in-the-loop evidence) #####################################
        with st.expander("🔍 View Raw Intelligence Extraction Details"):
            st.info("Raw data returned by Gemini AI before normalization.")
            st.write(f"**Extracted USD Rate:** Rs. {ext.get('usd_rate')}")
            col_a, col_b = st.columns(2)
            col_a.text_area("Weather Extraction (Raw)", ext.get('weather_raw', 'No data'), height=150)
            col_b.text_area("Top Price Extraction (Raw)", ext.get('prices_raw', 'No data'), height=150)

        # --- 3. PREDICTION EXECUTION ---
        # Button disabled if date is missing
        if st.button("🚀 Confirm & Run Forecast", disabled=(verified_date is None)):
            st.session_state.current_user_payload = {
                "usd_rate": u_usd,
                "weather_mapping": dict(zip(edited_df['Region'], edited_df['Weather'])),
                "intake_mapping": dict(zip(edited_df['Region'], edited_df['Intake'])),
                "manual_prices": dict(zip(edited_df['Region'].apply(norm_reg) + "|" + edited_df['Grade'].str.upper(), edited_df['Price (LKR)']))
            }
            
            with st.spinner("🧠 Generating Multi-Horizon Forecasts..."):
                st.session_state.final_results = st.session_state.engine.run_prediction(history, st.session_state.current_user_payload)
                st.session_state.show_results = True
                st.rerun()

        # --- 4. DISPLAY AND SAVE RESULTS ---
        if st.session_state.get('show_results'):
            st.divider()

            st.subheader("📈 Integrated Forecast Results")
            st.dataframe(st.session_state.final_results, use_container_width=True)
            
            if st.button("💾 Finalize & Push to Cloud (Google Sheets)", disabled=(verified_date is None)):
                with st.spinner("Syncing to Cloud..."):
                    to_save = st.session_state.final_results.copy()
                    
                    # 1. Map Inputs and Context
                    to_save['true_date'] = verified_date 
                    to_save['USD_to_LKR'] = u_usd
                    
                    payload = st.session_state.current_user_payload
                    to_save['weather_cat'] = to_save['Region'].map(payload['weather_mapping'])
                    to_save['crop_cat'] = to_save['Region'].map(payload['intake_mapping'])
                    
                    # 2. Re-map Elevation (CRITICAL for Dashboard charts)
                    elev_map = dict(zip(combos['region'], combos['elevation']))
                    to_save['elevation'] = to_save['Region'].map(elev_map)
                    
                    # 3. Rename to match Google Sheet strict Schema
                    to_save = to_save.rename(columns={
                        'Region': 'region', 'Grade': 'grade',
                        'Current Price': 'price',
                        '1W Forecast (Y)': 'forecast_1w',
                        '2W Forecast (Y)': 'forecast_2w',
                        '4W Forecast (Y)': 'forecast_4w'
                    })

                    from utils.sheets_handler import save_to_gsheet
                    if save_to_gsheet(to_save):
                        st.balloons()
                        st.success("✅ Dashboard Updated Permanently!")