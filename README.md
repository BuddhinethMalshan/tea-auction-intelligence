================================================================================

1. PROJECT OVERVIEW
-------------------
The Ceylon Tea Price Intelligence System is an automated Decision Support System (DSS) 
designed to navigate price volatility in the Colombo Tea Auction. The platform facilitates 
the digital transformation of unstructured auction reports into actionable market 
intelligence through a dual-stage pipeline:

- Data Intelligence: Utilizes the Gemini 2.5 Flash-Lite API to perform semantic extraction 
  of prices, weather conditions, and exchange rates from unstructured PDF broker reports. It
  features a Human-in-the-Loop (HITL) verification grid to ensure 100% data integrity before 
  forecasting.

- Predictive Modeling: Implements a multi-horizon forecasting framework covering 43 unique
  region-grade combinations. The system utilizes XGBoost for high-precision short-term 
  forecasts (Week 1 and Week 2) and a Level-2 Stacking Ensemble (integrating XGBoost, 
  N-BEATS, and N-HiTS via a Lasso Meta-learner) for stable mid-term forecasts (Week 4).

- Persistence & Visualization: Synchronizes validated data with a Google Sheets Cloud 
  Database and renders interactive price trajectories and strategic KPIs via a 
  professional Streamlit web interface.

2. PREREQUISITES
----------------
- Python 3.10 or higher
- A Google Gemini API Key (available via Google AI Studio)
- A Google Cloud Service Account (for Google Sheets integration)

3. LOCAL SETUP INSTRUCTIONS
---------------------------
Step 1: Unzip the folder 'RGU_Number.source.zip'.
Step 2: Open a terminal/command prompt in the extracted folder.
Step 3: (Recommended) Create a virtual environment:
        python -m venv venv
        .\venv\Scripts\activate  (Windows) or source venv/bin/activate (Mac/Linux)
Step 4: Install the required libraries:
        pip install -r requirements.txt

4. CONFIGURING SECRETS (MANDATORY)
----------------------------------
The application requires API keys to function. Create a folder named '.streamlit' 
in the root directory and create a file inside it named 'secrets.toml'. 
Add the following template and replace with valid credentials:

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

[connections.gsheets]
spreadsheet = "YOUR_GOOGLE_SHEET_URL"
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

5. RUNNING THE PROTOTYPE
------------------------
To launch the application, run the following command in the terminal:
streamlit run app.py --server.fileWatcherType none

6. THIRD-PARTY LIBRARIES & SOFTWARE
-----------------------------------
The following libraries are utilized in this prototype:
- Streamlit (Web Framework): https://streamlit.io/
- XGBoost (Gradient Boosting): https://xgboost.readthedocs.io/
- PyTorch (Deep Learning): https://pytorch.org/
- Darts (Time-Series Forecasting): https://unit8co.github.io/darts/
- Google GenAI (Gemini API): https://ai.google.dev/
- PyMuPDF/Fitz (PDF Processing): https://pymupdf.readthedocs.io/
- Pandas (Data Manipulation): https://pandas.pydata.org/
- Scikit-Learn (Metrics & Scaling): https://scikit-learn.org/

7. CUSTOM DATASET
-----------------
- File: df_global_final.csv
- Description: Reconstructed longitudinal dataset of the Colombo Tea Auction (2021-2025).
- Size: ~612 KB (Included in the source zip).

8. LIVE DEPLOYMENT URL
----------------------
The prototype is also accessible online at:
https://github.com/BuddhinethMalshan/tea-auction-intelligence

================================================================================
