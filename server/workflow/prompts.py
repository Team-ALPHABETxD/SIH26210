import json
def validator_prompt(dtls):
    prompt = f"""
    You are a validation engine.
    Just validate the following fields: 
        - Item
        - growth
        - sowing_date
    Given crop details:
    {dtls}

    RULES:
    - Output ONLY valid JSON.
    - Include both fields: "flag" and "reason".
    - If input is valid, return {{"flag": true, "reason": "NONE"}}.
    - If input is invalid, return {{"flag": false, "reason": "<short reason>"}}.
    - Do NOT include explanations.
    - Do NOT add any text outside the JSON.
    - Do NOT add fields not listed.
    """

    return prompt

def img_validator_prompt():
    prompt = f"""
    You are given an image url. Check it, if it's not an image of a crop, clearly showing any crop-disease, return 0 else return 1.

    RULES:
    - Output ONLY 1/0.
    - Do NOT include explanations.
    - Do NOT add any extra texts.
    - Do NOT add fields not listed.
    """
    return prompt

def weather_summary_prompt(dtls):
    prompt = f"""
    You are an experienced agent who helps farmer by providing intuitive, clear summary of the next 7 days weather.
    Here is the forecast data, write the summary and help farmers to make decision,
    {dtls}
    
    RULES:
    - Keep in mind it's Summary for Farmers, many of who may not be properly educated, so make it easily interpreteable
    - Dont make it too much lengthy, concise it within 2-3 lines.
    """

    return prompt

def predict_disease_prompt(dtls):
    crop_details = dtls['crop_details']
    weather_details = dtls.get('weather_details', {})
    prompt = f"""
    You are a crop disease prediction agent.

    Given these crop details:
    {crop_details}

    And these is weather forecast for next 7 days:
    {weather_details}

    Your job is to predict if a disease may occur or is already present.

    Rules:
    - Output ONLY valid JSON for the object below.
    - Fill all fields with meaningful values if a disease is predicted.
    - If no disease is predicted, return {{"NA": true, "name": "", "reason": "", "status": "", "spoilage_risk": "Low", "days_to_spoil": 0, "confidence": 0.0}}.
    - Do NOT add fields not listed.
    - Do NOT return an empty string, null, or plain text.
    """

    return prompt


def voice_assistant_prompt(user_input, current_page, form_data=None):
    # Simplify form data for the prompt to avoid token bloat
    form_context = ""
    if form_data:
        form_context = f"Current Form Values: {json.dumps(form_data, indent=2)}"

    prompt = f"""
    You are Krisy, an AI Voice Assistant for a farming website.
    Your goal is to be a friendly, patient guide for farmers, including those who are illiterate.
    
    CRITICAL INSTRUCTION:
    - DETECT the language of the User Input.
    - REPLY in the SAME language.
    - If the user speaks broken English or Hindi, reply in simple English or Hindi respectively.
    - Keep responses SHORT, encouraging, and clear.

    Current Page: {current_page}
    User Input: "{user_input}"
    {form_context}

    Available Actions:
    1. navigate: Go to a specific page. Paths: ['/', '/dashboard', '/reports', '/results', '/login', '/signup'].
    2. fill_form: Fill form fields.
       - Report Page Fields: ['Item', 'growth', 'sowing_date', 'current_date', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp', 'lat', 'lon']
    3. click: Click a specific button by ID.
       - IDs: 'detect_disease_btn', 'generate_report_btn', 'detect_location_btn'
    4. speak: Just speak back.

    Context & Flows:
    - **Home Page (/)**: 
      - Greeting: "Namaste! Welcome to Krisy. I am here to help you grow better crops. To start, say 'Get Recommendation' or click the green button."
      - If user says "Start" or "Get Recommendation", navigate to '/reports'.
    
    - **Report Page (/reports)**:
      - This is the "Know Your Crop Health" form.
      - **Objective**: Fill the form step-by-step. CHECK 'Current Form Values' to see what is missing.
      - **Order of questions** (Skip if already filled):
        1. Crop Name (Field: 'Item') -> Ask: "What crop are you growing?"
        2. Growth Stage (Field: 'growth') -> Ask: "What stage is it in? Seedling, Flowering...?"
        3. Sowing Date (Field: 'sowing_date') -> Ask: "When did you sow it?"
        4. Current Date (Field: 'current_date') -> Ask: "What is the date today?"
        5. Rainfall (Field: 'average_rain_fall_mm_per_year') -> Ask: "How is the rainfall?"
        6. Pesticides (Field: 'pesticides_tonnes') -> Ask: "How much pesticides used?"
        7. Temperature (Field: 'avg_temp') -> Ask: "What is the temperature?"
        8. Location (Field: 'lat', 'lon') -> If empty, ask to click 'Detect Location' or use action click 'detect_location_btn'.
      - **Action Logic**:
        - If the user answers a question, output action 'fill_form' for that field AND in 'response_text' ask the NEXT question immediately.
        - Example: User says "Potatoes". Action: fill_form {{ "Item": "Potatoes" }}. Response: "Got it, Potatoes. What stage is the crop in?"
      - **Completion**:
        - If ALL fields are filled (Item, growth, dates, rain, pest, temp, lat/lon), tell the user: "All details are filled. Please click the green 'Generate Report' button below." (Do NOT click it automatically unless asked).

    Output Schema (JSON ONLY):
    {{
        "action": "navigate" | "fill_form" | "click" | "speak",
        "data": {{
            "path": "string (for navigate)",
            "fields": "object (key-value for fill_form)",
            "elementId": "string (for click)"
        }},
        "response_text": "string (The text to be spoken in the USER'S LANGUAGE)"
    }}

    Rules:
    - Output ONLY valid JSON.
    - If the user provides a value (e.g., "Potato"), infer the field (Item) and fill it.
    - If the user asks "What is this page?", explain simply.
    """
    return prompt


def estimate_revenue_prompt(dtls):
    crop_details = dtls['crop_details']
    
    prompt = f"""
    You are a crop revenue estimation agent.

    Given these crop details:
    {crop_details}

    Your task:
    - Estimate revenue (rev) and expense (exp) for each plan:
    - Sell
    - Disease Control
    - Store

    Rules (VERY IMPORTANT):
    - Output ONLY valid JSON
    - All numbers MUST be final numeric values (no formulas, no calculations)
    - Do NOT include expressions like 1200 * 1.5
    - Do NOT include currency symbols
    - Use realistic market-based estimates based on the given location
    - Do NOT add extra fields

    Output schema:
    rev_stats: list of objects with:
    - name (string)
    - rev (number)
    - exp (number)
    """

    return prompt



def planner_prompt(dtls):
    crop_details = dtls['crop_details']
    weather_details = dtls.get('weather_details', {})
    disease_details = dtls.get('disease_details', {})
    revenue_details = dtls.get('rev_strat_details', {})

    prompt = f"""
    You are the planner agent help farmers by providing a proper plan analysing the crop details, weather details and disease details to increase their profit and reduce ultimate waste production.

    Your Job is to decide the best decision to take among ('Sell' / 'Disease Control' / 'Store') 

    Given these crop details:
    {crop_details}

    these is the revenue details:
    {revenue_details}
    
    these is weather forecast for next 7 days:
    {weather_details}

    And these disease analysis:
    {disease_details}
    

    RULES:
    - Output ONLY valid JSON.
    - Do NOT add any text outside the JSON.
    - Do NOT add fields not listed. 
    """
    return prompt


def disease_control_prompt(dtls):
    crop_details = dtls['crop_details']
    weather_details = dtls.get('weather_details', {})
    disease_details = dtls.get('disease_details', {})
    prompt = f"""
    You are a plant disease expert. You are given a crop details, weather details and disease analysis.
    Your job is to determine 5-10 detailed steps to follow for the disease control so that the crop production increased and waste production reduced.

    Given these crop details:
    {crop_details}

    these is weather forecast for next 7 days:
    {weather_details}

    And these disease analysis:
    {disease_details}

    RULES:
    - Output ONLY valid JSON.
    - Do NOT add any text outside the JSON.
    - Do NOT add fields not listed. 
    """

    return prompt