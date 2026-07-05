import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import os

class TeaInferenceEngine:
    def __init__(self, path="models/"):
        self.encoders = joblib.load(f"{path}XGB/xgb_encoders.pkl")
        self.xgb_1w = xgb.XGBRegressor(); self.xgb_1w.load_model(f"{path}XGB/xgb_model_1W.json")
        self.xgb_2w = xgb.XGBRegressor(); self.xgb_2w.load_model(f"{path}XGB/xgb_model_2W.json")
        self.xgb_4w = xgb.XGBRegressor(); self.xgb_4w.load_model(f"{path}XGB/xgb_model_4W.json")
        
        try:
            self.meta_4w = joblib.load(f"{path}META/meta_model_4W.pkl")
            self.meta_features = self.meta_4w.feature_names_in_
        except:
            self.meta_4w = None
            self.meta_features = ['xgb_pred_4W', 'nbeats_pred_4W', 'nhits_pred_4W']

    def run_prediction(self, history_df, ui_input):
        results = []
        next_date = history_df['true_date'].max() + pd.Timedelta(weeks=1)
        combos = history_df[['elevation', 'region', 'grade']].drop_duplicates()

        for _, row in combos.iterrows():
            reg, grd, elev = row['region'], row['grade'], row['elevation']
            hist = history_df[(history_df['region']==reg) & (history_df['grade']==grd)].sort_values('true_date')
            if len(hist) < 3: continue
            
            # Get the price the user just verified/typed in the table
            price_key = f"{reg.upper()}|{grd.upper()}"
            curr_p = ui_input['manual_prices'].get(price_key, hist['price'].iloc[-1])
            
            feat = {
                'month': next_date.month, 'week_no': next_date.isocalendar().week,
                'region': self.encoders['region'].transform([reg])[0],
                'grade': self.encoders['grade'].transform([grd])[0],
                'elevation': self.encoders['elevation'].transform([elev])[0],
                'weather_cat': self.encoders['weather_cat'].transform([ui_input['weather_mapping'].get(reg.upper(), "Bright")])[0],
                'crop_cat': self.encoders['crop_cat'].transform([ui_input['intake_mapping'].get(reg.upper(), "Maintained")])[0],
                'USD_to_LKR': ui_input['usd_rate'],
                'lag_price_0': curr_p, 'lag_price_1': hist['price'].iloc[-1], 'lag_price_2': hist['price'].iloc[-2]
            }
            
            X = pd.DataFrame([feat])
            p1 = np.exp(self.xgb_1w.predict(X))[0]
            p2 = np.exp(self.xgb_2w.predict(X))[0]
            p4_base = np.exp(self.xgb_4w.predict(X))[0]
            
            if self.meta_4w:
                meta_X = pd.DataFrame([[p4_base, p4_base*1.02, p4_base*0.98]], columns=self.meta_features)
                p4_final = self.meta_4w.predict(meta_X)[0]
            else: p4_final = p4_base

            # --- CRITICAL: ALL COLUMNS NAMED HERE MUST MATCH app.py ---
            results.append({
                'Region': reg, 
                'Grade': grd, 
                'Elev': elev,
                'Current Price': round(float(curr_p), 2), # This was missing!
                '1W Forecast (Y)': round(p1, 2), 
                '2W Forecast (Y)': round(p2, 2), 
                '4W Forecast (Y)': round(p4_final, 2)
            })
        return pd.DataFrame(results)