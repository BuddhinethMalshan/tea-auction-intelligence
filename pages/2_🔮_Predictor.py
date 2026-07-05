import streamlit as st
import pandas as pd
from utils.pdf_processor import split_pdf_pages
from utils.gemini_engine import TeaGeminiEngine
from utils.inference_logic import TeaInferenceEngine
from utils.sheets_handler import save_to_gsheet

st.set_page_config(page_title="Price Predictor", layout="wide")
st.title("🔮 Tea Price Prediction Engine")

# Initialize Engines
gemini = TeaGeminiEngine(api_key=st.secrets["GEMINI_API_KEY"])
model_engine = TeaInferenceEngine()

tab1, tab2 = st.tabs(["📄 PDF Report Upload", "📝 Manual Prediction Form"])

with tab1:
    st.header("Step 1: Upload Weekly Auction Report")
    uploaded_file = st.file_uploader("Upload Forbes & Walker PDF", type="pdf")
    
    if uploaded_file:
        with st.status("Processing Pipeline...", expanded=True) as status:
            # 1. Split PDF
            st.write("Splitting PDF pages...")
            pages = split_pdf_pages(uploaded_file)
            
            # 2. Extract with Gemini
            st.write("Extracting data via Gemini AI...")
            extracted_data = gemini.process_all(pages)
            
            # 3. Inference Logic
            st.write("Running Stacking Ensemble (XGB + Meta)...")
            # We load history for lags
            history = pd.read_csv("df_global_final.csv")
            predictions_df = model_engine.predict_all_horizons(history, extracted_data)
            
            status.update(label="Analysis Complete!", state="complete")

        # Display Results
        st.subheader("Extracted Market Data")
        st.json(extracted_data) # Show user what Gemini found
        
        st.subheader("Final Predictions (Next Auction)")
        st.table(predictions_df)
        
        if st.button("🚀 Commit Predictions to Dashboard"):
            for _, row in predictions_df.iterrows():
                save_to_gsheet(row.to_dict())

with tab2:
    st.header("Manual Input Form")
    with st.form("manual_entry"):
        col1, col2 = st.columns(2)
        elev = col1.selectbox("Elevation", ["High", "Medium", "Low"])
        reg = col1.selectbox("Region", ["WESTERN HIGH", "NUWARA ELIYAS", "LOW GROWNS"])
        grd = col2.selectbox("Grade", ["BOP", "BOPF", "PEKOE"])
        usd = col2.number_input("USD/LKR Rate", value=305.0)
        
        btn = st.form_submit_button("Predict Now")
        if btn:
            # Simulate Gemini-style dictionary from manual inputs
            manual_data = {
                'usd_rate': usd,
                'weather': {reg: "Bright"}, 
                'intake': {reg: "Maintained"}
            }
            # Run Model
            history = pd.read_csv("df_global_final.csv")
            res = model_engine.predict_all_horizons(history, manual_data)
            st.metric(f"Predicted Price ({reg} - {grd})", f"LKR {res['1W'][0]:.2f}")