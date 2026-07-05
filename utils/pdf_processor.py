import io
import os
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter

def split_pdf_pages(uploaded_file, debug_dir="debug_splits"):
    """
    Final optimized PDF processor. 
    Uses multi-page pypdf logic for Top Prices.
    Uses fitz logic for Weather and Exchange rates.
    """
    # 1. Setup Debug Folder
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    # 2. Reset and Read File
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    results = {"top_prices": None, "weather": None, "ex_rate": None}

    # --- 3. TOP PRICES SPLIT (Multi-page Logic from your script) ---
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        found_at_least_one_price_page = False

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_upper = text.upper()
                # EXACT LOGIC: Main header OR the specific footer signature
                if "TOP PRICE" in text_upper or "@ - SOLD BY FORBES & WALKER TEA BROKERS (PVT) LTD" in text_upper:
                    writer.add_page(page)
                    found_at_least_one_price_page = True
        
        if found_at_least_one_price_page:
            price_stream = io.BytesIO()
            writer.write(price_stream)
            price_stream.seek(0)
            results["top_prices"] = price_stream
            _save_to_disk(price_stream, f"{debug_dir}/debug_prices.pdf")
            print("✅ TOP PRICES: Multi-page extraction successful.")
    except Exception as e:
        print(f"❌ Error in Top Prices Split: {e}")

    # --- 4. WEATHER & EX-RATE SPLIT (fitz Logic) ---
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page_text = doc[page_num].get_text("text").upper()
            
            # Weather Search
            if "CROP AND WEATHER" in page_text and results["weather"] is None:
                results["weather"] = _extract_with_fitz(doc, page_num)
                _save_to_disk(results["weather"], f"{debug_dir}/debug_weather.pdf")
                print(f"✅ WEATHER: Found on Page {page_num+1}")

            # Exchange Rate Search
            if "RATES OF EXCHANGE" in page_text and results["ex_rate"] is None:
                results["ex_rate"] = _extract_with_fitz(doc, page_num)
                _save_to_disk(results["ex_rate"], f"{debug_dir}/debug_exrate.pdf")
                print(f"✅ EX-RATE: Found on Page {page_num+1}")
        doc.close()
    except Exception as e:
        print(f"❌ Error in Weather/Ex-Rate Split: {e}")

    return results

def _extract_with_fitz(doc, page_num):
    """Creates a single-page memory stream."""
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    stream = io.BytesIO()
    new_doc.save(stream)
    stream.seek(0)
    return stream

def _save_to_disk(stream, filename):
    """Saves the stream to disk for your verification."""
    stream.seek(0)
    with open(filename, "wb") as f:
        f.write(stream.read())
    stream.seek(0) # IMPORTANT: Reset pointer so Gemini can read from start