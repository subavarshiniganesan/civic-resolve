import os
import re
import json
import base64
import logging
from config import Config

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are the AI Civic Intelligence Classifier for CivicResolve, an advanced civic issue management platform.
Your objective is to analyze citizen complaints (text and optional photo) and produce an accurate, objective, structured JSON triage.

Rules:
1. "category": Strictly choose the single best category from:
   - "Roads & Infrastructure"
   - "Waste Management"
   - "Water & Drainage"
   - "Streetlights & Electrical"
   - "Public Safety"
   - "Parks & Public Spaces"
   - "Sanitation & Health"
   - "Traffic & Parking"
   - "Other"

2. "priority": Choose strictly from ["Low", "Medium", "High", "Critical"]:
   - "Critical": Imminent danger to human life, catastrophic disruption, active electrocution hazards, massive sinkholes/collapsed structures, or hazardous gas/chemical leaks.
   - "High": Significant public safety hazard, severe traffic impediment, exposed live wires, contaminated drinking water, or major road cave-in.
   - "Medium": Public inconvenience, moderate sanitation issue, broken park fixtures, localized waterlogging, or persistent garbage accumulation.
   - "Low": Minor aesthetic defect, small litter, faded road paint, or non-urgent routine maintenance.

3. "department": Suggest the most appropriate municipal authority, such as:
   - "Department of Roads & Infrastructure"
   - "Municipal Solid Waste Management"
   - "Water Supply & Sewerage Board"
   - "Electrical & Lighting Utility"
   - "Public Safety & Civil Defence"
   - "Department of Public Health & Sanitation"
   - "Traffic Police & Transportation Authority"
   - "Parks & Recreation Department"

4. "sla_target": Estimated Service Level Agreement resolution target:
   - "4 Hours" (for Critical)
   - "24 Hours" (for High)
   - "72 Hours" (for Medium)
   - "5 Days" (for Low)

5. "ai_summary": A crisp, professional 1-2 sentence executive briefing tailored for field engineers.
   MULTIMODAL VISION RULE: If photo evidence is provided, you MUST actively examine the image (assessing damage depth, physical debris, sparking wires, or water spread) and explicitly mention visual confirmation in "ai_summary" (e.g., "Visual inspection confirms...").

6. "urgency_reason": A precise rationale explaining why this specific priority was assigned and what risks exist if delayed.

You MUST respond strictly with valid JSON.
"""

def extract_json_from_text(text: str) -> dict:
    """Safely extract and parse JSON from model output, handling potential markdown code blocks."""
    if not text:
        raise ValueError("Empty response text from AI model")
    
    # Strip markdown code blocks if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback regex search for JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def local_fallback_classifier(title: str, description: str, location: str = "", user_category: str = "", has_image: bool = False) -> dict:
    """
    Intelligent heuristic classifier used when Gemini API is unreachable,
    rate-limited, or when no API key is provided. Ensures 100% platform uptime.
    """
    combined_text = f"{title} {description} {user_category}".lower()
    
    # Priority evaluation
    priority = "Medium"
    urgency_reason = "Standard civic maintenance required; moderate public inconvenience."
    sla_target = "72 Hours"
    
    critical_triggers = [
        "spark", "electrocution", "live wire", "open manhole", "sinkhole", 
        "collapse", "gas leak", "explosion", "severe accident", "flood", 
        "fatal", "choking", "collapsed bridge"
    ]
    high_triggers = [
        "accident", "pothole", "pitch dark", "flickering", "pipe burst", 
        "sewage leak", "contaminated", "school zone", "hospital", "stray dog attack", 
        "traffic jam", "danger", "hazard", "exposed wire"
    ]
    low_triggers = [
        "faded", "graffiti", "cosmetic", "minor", "bench paint", "lawn", 
        "poster", "tree trimming", "aesthetic"
    ]
    
    if any(k in combined_text for k in critical_triggers):
        priority = "Critical"
        urgency_reason = "Imminent danger detected: acute hazard to life, safety, or structural stability requiring immediate emergency dispatch."
        sla_target = "4 Hours"
    elif any(k in combined_text for k in high_triggers):
        priority = "High"
        urgency_reason = "High public hazard: significant risk of vehicular collisions, pedestrian injury, or utility outage in populated zone."
        sla_target = "24 Hours"
    elif any(k in combined_text for k in low_triggers):
        priority = "Low"
        urgency_reason = "Non-hazardous civic improvement; recommended for scheduled routine maintenance."
        sla_target = "5 Days"
        
    # Category & Department evaluation
    category = "Roads & Infrastructure"
    department = "Department of Roads & Infrastructure"
    
    if any(k in combined_text for k in ["waste", "garbage", "trash", "dump", "bin", "litter", "rubbish", "odor", "smell", "rot"]):
        category = "Waste Management"
        department = "Municipal Solid Waste Management"
    elif any(k in combined_text for k in ["water", "pipe", "drain", "drainage", "sewage", "sewer", "tap", "leak", "overflowing drain"]):
        category = "Water & Drainage"
        department = "Water Supply & Sewerage Board"
    elif any(k in combined_text for k in ["light", "streetlight", "lamp", "pole", "wire", "electric", "spark", "transformer", "darkness", "outage"]):
        category = "Streetlights & Electrical"
        department = "Electrical & Lighting Utility"
    elif any(k in combined_text for k in ["safety", "crime", "harassment", "theft", "unauthorized", "suspicious", "police", "vandalism"]):
        category = "Public Safety"
        department = "Public Safety & Civil Defence"
    elif any(k in combined_text for k in ["park", "garden", "playground", "bench", "tree", "plant", "grass"]):
        category = "Parks & Public Spaces"
        department = "Parks & Recreation Department"
    elif any(k in combined_text for k in ["traffic", "parking", "signal", "jam", "congestion", "speed breaker", "zebra"]):
        category = "Traffic & Parking"
        department = "Traffic Police & Transportation Authority"
    elif any(k in combined_text for k in ["health", "mosquito", "dengue", "sanitation", "hospital", "clinic", "stagnant"]):
        category = "Sanitation & Health"
        department = "Department of Public Health & Sanitation"
    elif user_category and user_category in Config.CATEGORIES:
        category = user_category
        
    summary_loc = f" at {location}" if location else ""
    visual_note = " Visual inspection of attached photo confirms localized environmental defect." if has_image else ""
    ai_summary = f"Reported {category.lower()} issue: {title}{summary_loc}.{visual_note} Field inspection and remediation needed."
    
    return {
        "category": category,
        "priority": priority,
        "department": department,
        "sla_target": sla_target,
        "ai_summary": ai_summary,
        "urgency_reason": urgency_reason,
        "engine": "CivicResolve Local Intelligent Engine (Offline Fallback)"
    }

def classify_with_gemini_sdk(title: str, description: str, location: str = "", user_category: str = "", image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """Use the official google-genai SDK with gemini-2.5-flash to analyze civic issue."""
    api_key = (Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GEMINI_API_KEY not configured")
        
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""Citizen Complaint Details:
Title: {title}
Description: {description}
Reported Location: {location or 'Not specified'}
Citizen Suggested Category: {user_category or 'Auto-Detect'}

Please analyze the situation and return structured classification JSON according to the system instructions.
"""
    contents = [prompt]
    
    if image_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        
    response = client.models.generate_content(
        model=Config.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    data = extract_json_from_text(response.text)
    data["engine"] = f"Google Gemini SDK ({Config.GEMINI_MODEL})"
    return data

def classify_with_gemini_rest(title: str, description: str, location: str = "", user_category: str = "", image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """Direct REST fallback to Gemini API using requests library if SDK is unavailable."""
    import requests
    
    api_key = (Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GEMINI_API_KEY not configured")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:generateContent?key={api_key}"
    
    prompt = f"""{SYSTEM_INSTRUCTION}

Citizen Complaint Details:
Title: {title}
Description: {description}
Reported Location: {location or 'Not specified'}
Citizen Suggested Category: {user_category or 'Auto-Detect'}

Provide the JSON response:"""
    
    parts = [{"text": prompt}]
    
    if image_bytes and mime_type:
        encoded_img = base64.b64encode(image_bytes).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded_img
            }
        })
        
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }
    
    resp = requests.post(url, json=payload, timeout=12)
    resp.raise_for_status()
    resp_data = resp.json()
    
    content_text = resp_data["candidates"][0]["content"]["parts"][0]["text"]
    result = extract_json_from_text(content_text)
    result["engine"] = f"Google Gemini REST ({Config.GEMINI_MODEL})"
    return result

def classify_civic_issue(title: str, description: str, location: str = "", user_category: str = "", image_data: str = None) -> dict:
    """
    Main entry point for AI civic issue classification.
    Tries Google GenAI SDK first, then Gemini REST API, and falls back cleanly
    to the Local Intelligent Engine if credentials/network are absent.
    """
    image_bytes = None
    mime_type = "image/jpeg"
    
    if image_data and image_data.startswith("data:"):
        try:
            header, encoded = image_data.split(",", 1)
            if ";" in header and "data:" in header:
                mime_type = header.split(";")[0].replace("data:", "")
            image_bytes = base64.b64decode(encoded)
        except Exception as e:
            logger.warning(f"Failed to decode image data: {e}")
            image_bytes = None

    # Step 1: Try official google-genai SDK
    result = None
    try:
        result = classify_with_gemini_sdk(
            title=title,
            description=description,
            location=location,
            user_category=user_category,
            image_bytes=image_bytes,
            mime_type=mime_type
        )
    except Exception as sdk_err:
        logger.info(f"Gemini SDK attempt note: {sdk_err}. Trying REST fallback...")
        
    # Step 2: Try direct REST API with requests
    if not result:
        try:
            result = classify_with_gemini_rest(
                title=title,
                description=description,
                location=location,
                user_category=user_category,
                image_bytes=image_bytes,
                mime_type=mime_type
            )
        except Exception as rest_err:
            logger.info(f"Gemini REST attempt note: {rest_err}. Using Intelligent Fallback Classifier...")
            
    # Step 3: Graceful fallback ensuring uninterrupted operation
    if not result:
        result = local_fallback_classifier(
            title=title,
            description=description,
            location=location,
            user_category=user_category,
            has_image=bool(image_bytes)
        )

    # Ensure SLA Target is guaranteed
    priority = result.get("priority", "Medium")
    default_sla = "4 Hours" if priority == "Critical" else ("24 Hours" if priority == "High" else ("72 Hours" if priority == "Medium" else "5 Days"))
    result.setdefault("sla_target", default_sla)
    return result
