from dotenv import load_dotenv
import os
import requests
import base64
import joblib
import pandas as pd
import datetime
import json

load_dotenv()


def get_weather_details(lat, lon):
    response = requests.get(
        f"{os.getenv('WEATHER_ENDPOINT')}?lat={lat}&lon={lon}&units=metric&appid={os.getenv('WEATHER_API')}"
    )
    print(response.json())
    return response.json()


def predict_yeild(dtls):
    pipeline = joblib.load('../yield_prediction/crop_yield_pipeline.joblib')
    dtls_df = pd.DataFrame([dtls])
    pred = pipeline.predict(dtls_df.iloc[:, 0:4])
    return float(pred[0])


# ================= EXISTING CROP IMAGE ANALYSIS (UNCHANGED) =================
def analyse_crop_img(image, prompt):
    try:
        img_url = image
        img_bytes = requests.get(img_url).content

        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_base64
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"

        res = requests.post(endpoint, json=payload)
        print(res.json())
        print(res.json()['candidates'][0]['content']['parts'][0]['text'])
        return res

    except Exception as e:
        print("Exception: ", e)
        return 0


# ================= UPDATED SOIL IMAGE ANALYSIS (NUMERIC NPK) =================
def analyse_soil_img(image):
    """
    Analyzes an image and estimates soil nutrients (N, P, K, pH).
    Always returns a JSON object with estimations.
    """

    try:
        img_url = image
        img_bytes = requests.get(img_url).content
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        # Determine mime type based on URL extension
        mime_type = "image/png"
        if img_url.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        elif img_url.lower().endswith(".webp"):
            mime_type = "image/webp"

        soil_prompt = """
You are an agricultural soil analysis expert.
Analyze the provided image and estimate soil nutrients (N, P, K, pH) based on visual indicators like color and texture.
Always provide an estimation, even if plants or seedlings are present.

Return the result STRICTLY in this JSON format:
{
  "is_soil": true,
  "N": <number between 0 and 500>,
  "P": <number between 0 and 300>,
  "K": <number between 0 and 800>,
  "pH": <number between 3.5 and 9.5>,
  "unit": "mg/kg",
  "confidence": <number between 0 and 1>,
  "notes": "Short visual-based explanation"
}

STRICT RULES:
- Output ONLY the JSON object.
- N, P, K, pH MUST be numeric.
- No extra text outside JSON.
"""

        payload = {
            "contents": [
                {
                    "parts": [
                        { "inline_data": { "mime_type": mime_type, "data": img_base64 } },
                        { "text": soil_prompt }
                    ]
                }
            ]
        }

        # Fixed model name to a valid version
        model_name = "gemini-2.5-flash"
        endpoint = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={os.getenv('GEMINI_API_KEY')}"

        res = requests.post(endpoint, json=payload, timeout=25)
        res_json = res.json()
        
        if "candidates" not in res_json:
            print("Gemini API Error:", res_json)
            return {
                "is_soil": True,
                "N": 150.0, "P": 50.0, "K": 200.0, "pH": 6.5,
                "unit": "mg/kg", "confidence": 0.5,
                "notes": "API communication error; using default values."
            }

        text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Clean markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        soil_data = json.loads(text)
        soil_data["is_soil"] = True
        return soil_data
    
    except Exception as e:
        print("Exception in analyse_soil_img: ", e)
        return {
            "is_soil": True,
            "N": 0.0, "P": 0.0, "K": 0.0, "pH": 7.0,
            "unit": "mg/kg", "confidence": 0.0,
            "notes": f"Error: {str(e)}"
        }


def get_weather_forecast(lat, lon):
    d = datetime.datetime.now()
    ds = str(d).split(' ')[0]
    fd = d + datetime.timedelta(days=6)
    fds = str(fd).split(' ')[0]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "wind_speed_10m_max",
            "relative_humidity_2m_max",
            "surface_pressure_mean",
            "pressure_msl_mean",
            "apparent_temperature_max",
            "uv_index_max",
            "daylight_duration"
        ],
        "timezone": "auto",
        "start_date": ds,
        "end_date": fds,
    }

    res = requests.get(url, params=params)
    print(res.json())
    return res.json()