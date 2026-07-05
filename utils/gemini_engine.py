import pandas as pd
import time
import io
import json
import re
from google import genai
from google.genai import types

class TeaGeminiEngine:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.MODEL_ID = "gemini-3.1-flash-lite-preview"

    def _call_ai(self, stream, system_instruction, label):
        """Sequential task helper."""
        try:
            stream.seek(0)
            pdf_bytes = stream.read()
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=[
                    types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                    f"Task: Extract {label} details."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini Error ({label}): {e}")
            return None

    def process_all(self, split_results):
        final_output = {
            "usd_rate": 300.0,
            "weather_mapping": {},
            "intake_mapping": {},
            "extracted_prices_df": pd.DataFrame(),
            "weather_raw": "None",
            "prices_raw": "None"
        }

        # TASK 1: PRICES (Separate Prompt)
        if split_results.get("top_prices"):
            prompt_p = """Act as a Data Specialist. Extract 'TOP PRICE' rows. 
            Associate every estate with the Region Header above it.
            FORMAT: [Region]|[Estate]|[Grade]|[Price]|[IsForbes]"""
            raw = self._call_ai(split_results["top_prices"], prompt_p, "Prices")
            final_output["prices_raw"] = raw
            if raw:
                rows = []
                for line in raw.split('\n'):
                    p = line.split('|')
                    if len(p) == 5:
                        try:
                            rows.append({"region": p[0].strip().upper(), "grade": p[2].strip().upper(), "price": float(re.sub(r'[^\d.]', '', p[3]))})
                        except: continue
                if rows:
                    raw_df = pd.DataFrame(rows)
                    final_output["extracted_prices_df"] = raw_df.groupby(['region', 'grade'])['price'].mean().reset_index()
        
        time.sleep(1) # Free tier breathing room

        # TASK 2: WEATHER (Separate Prompt with Categories)
        if split_results.get("weather"):
            prompt_w = """Act as an Analyst. Extract 'CROP AND WEATHER'. 
            Map strictly to: NUWARA ELIYAS, UDAPUSSELLAWAS, UVA HIGH, UVA MEDIUM, WESTERN HIGH, WESTERN MEDIUM, LOW GROWNS.
            
            For Weather, choose EXACTLY one: [Bright, Rainy, Overcast, Mixed]
            For Intake, choose EXACTLY one: [Maintained, Decline, Increase, Slight Decline]
            
            FORMAT: [Region]|[Weather]|[Intake]
            NO brackets. NO sentences."""
            raw = self._call_ai(split_results["weather"], prompt_w, "Weather")
            final_output["weather_raw"] = raw
            if raw:
                for line in raw.split('\n'):
                    p = line.split('|')
                    if len(p) >= 3:
                        final_output["weather_mapping"][p[0].strip().upper()] = p[1].strip()
                        final_output["intake_mapping"][p[0].strip().upper()] = p[2].strip()

        time.sleep(1)

        # TASK 3: EXCHANGE RATE
        if split_results.get("ex_rate"):
            prompt_e = "Extract USD rate for 2026. Number only."
            raw = self._call_ai(split_results["ex_rate"], prompt_e, "Ex-Rate")
            if raw:
                match = re.search(r"(\d+\.\d+|\d+)", str(raw))
                if match: final_output["usd_rate"] = float(match.group(1))

        return final_output