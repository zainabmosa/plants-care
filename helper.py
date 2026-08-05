import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

env_path = BASE_DIR / ".env"

if not env_path.exists():
    env_path = BASE_DIR / "env"

load_dotenv(dotenv_path=env_path,override=True)

PLANTS_FILE = BASE_DIR / "plants.csv"
CARE_FILE = BASE_DIR / "care_history.csv"
GROWTH_FILE = BASE_DIR / "growth.csv"


def get_secret(name):
    value = os.getenv(name)

    if value:
        return value.strip()
    try:
        value = st.secrets[name]

        if value:
            return str(value).strip()

    except Exception:
        pass

    return None


def ensure_csv_files():
    
    if not os.path.exists(PLANTS_FILE):
        pd.DataFrame(columns=['Name','location','Acquired Date','Water','Fertilizing','Repotting','Pruning','Sunlight','Photo']).to_csv(PLANTS_FILE, index=False)

    if not os.path.exists(CARE_FILE):
        pd.DataFrame(columns=["Name", "Activity", "Date"]).to_csv(CARE_FILE, index=False)

    if not os.path.exists(GROWTH_FILE):
        pd.DataFrame(columns=["Name", "Height", "Date"]).to_csv(GROWTH_FILE, index=False)


ensure_csv_files()


def read():
    return pd.read_csv(PLANTS_FILE)


# 1: Add plant
def add_plant_data(name, location, date, water, sunlight, photo,Fertilizing ,Repotting,Pruning):
    
    df=read()
    
    new = pd.DataFrame([{
        "Name": name,
        "Location": location,
        "Acquired Date": date,
        "Water": water,
        "Sunlight": sunlight,
        "Photo": photo,
    "Fertilizing":Fertilizing,
    "Repotting":Repotting,
    "Pruning":Pruning}])
    

    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(PLANTS_FILE, index=False)


# 2: Record care
def record_care(name, activity, care_date):
    new = pd.DataFrame([
        {
            "Name": name,
            "Activity": activity,
            "Date": care_date,}])

    df = pd.read_csv(CARE_FILE)
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(CARE_FILE, index=False)


# 3: View due plants
def get_due_plants():
    plants = read()

    if plants.empty:
        return pd.DataFrame()

    try:
        history = pd.read_csv(CARE_FILE)
    except FileNotFoundError:
        history = pd.DataFrame(columns=["Name", "Activity", "Date"])

    today = pd.Timestamp.today().normalize()

    activities = {
    "Watering": "Water",
    "Fertilizing": "Fertilizing",
    "Repotting": "Repotting",
    "Pruning": "Pruning"}

    due_list = []

    for _, plant in plants.iterrows():

        for activity, column in activities.items():

            frequency = plant[column]

            activity_history = history[(history["Name"] == plant["Name"]) &(history["Activity"] == activity)]

            if activity_history.empty:
                last_date = pd.to_datetime(plant["Acquired Date"])
            else:
                last_date = pd.to_datetime(activity_history["Date"]).max()

            days = (today - last_date.normalize()).days

            if days >= frequency:

                due_list.append({
                    "Plant": plant["Name"],
                    "Activity": activity,
                    "Due Every (Days)": frequency,
                    "Days Since Last Care": days})

    return pd.DataFrame(due_list)


# 4: Search plants
def search_plants(term):
    df = read()

    if df.empty:
        return df

    term = term.strip()
    result = df[df["Name"].fillna("").str.contains(term, case=False, regex=False)| df["Location"].fillna("").str.contains(term, case=False, regex=False)]
    return result


# 6: Add growth
def add_growth(name, height, growth_date):
    new = pd.DataFrame([
        {
            "Name": name,
            "Height": height,
            "Date": growth_date,}])

    df = pd.read_csv(GROWTH_FILE)
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(GROWTH_FILE, index=False)


# 7: Seasonal reminder
def seasonal_reminder():
    month = datetime.now().month

    if month in [12, 1, 2]:
        return "Winter ❄️: Reduce watering"
    elif month in [6, 7, 8]:
        return "Summer ☀️: Increase watering"
    else:
        return "Normal season 🌿"


# 8: Original simple diagnosis
def diagnose(symptom):
    if symptom == "Yellow Leaves":
        return "Possible overwatering 💧"
    elif symptom == "Dry Leaves":
        return "The plant may need more water 💧"
    elif symptom == "Brown Tips":
        return "Check sunlight, humidity, and watering ☀️"
    return "Please provide more details about the symptom."


# 9: Adjust schedule
def adjust_schedule(water):
    month = datetime.now().month

    if month in [12, 1, 2]:
        season = "Winter"
        new_water = water + 1
    elif month in [3, 4, 5]:
        season = "Spring"
        new_water = water
    elif month in [6, 7, 8]:
        season = "Summer"
        new_water = max(1, water - 1)
    else:
        season = "Autumn"
        new_water = water

    return season, new_water


# 10: External Data API - Perenual Plant API
def search_plant_api(plant_name):

    api_key =get_secret("PERENUAL_API_KEY")

    if not api_key:
        raise ValueError("PERENUAL_API_KEY is missing.")

    plant_name = plant_name.strip()

    if not plant_name:
        raise ValueError("Please enter a plant name.")

    url = "https://www.perenual.com/api/v2/species-list"

    params = {"key": api_key,"q": plant_name,"page": 1,}

    try:
        response = requests.get(url,params=params,timeout=20,)

        if response.status_code == 429:
            raise RuntimeError("Perenual request limit reached. Try again later.")

        if response.status_code in [401, 403]:
            raise RuntimeError("Perenual rejected the API key.")

        if response.status_code == 404:
            raise RuntimeError("Perenual could not find the endpoint or validate the key.")

        response.raise_for_status()
        payload = response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            f"Plant API request failed: {error}"
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "Plant API returned an invalid response."
        ) from error

    results = []

    for plant in payload.get("data", []):
        scientific_names = plant.get("scientific_name") or []
        sunlight_values = plant.get("sunlight") or []
        image_data = plant.get("default_image") or {}

        results.append(
            {
                "id": plant.get("id"),
                "common_name": plant.get("common_name") or "Unknown",
                "scientific_name": (
                    ", ".join(scientific_names)
                    if isinstance(scientific_names, list)
                    else str(scientific_names)
                ),
                "watering": plant.get("watering") or "Unknown",
                "sunlight": (
                    ", ".join(sunlight_values)
                    if isinstance(sunlight_values, list)
                    else str(sunlight_values)
                ),
                "cycle": plant.get("cycle") or "Unknown",
                "image": (
                    image_data.get("regular_url")
                    or image_data.get("medium_url")
                    or ""),})

    return results


def get_plant_details(plant_id):

    api_key = get_secret("PERENUAL_API_KEY")

    if not api_key:
        raise ValueError(
            "PERENUAL_API_KEY is missing. Add it to the env file."
        )

    url = (f"https://www.perenual.com/api/v2/"f"species/details/{plant_id}")

    params = {"key": api_key}

    try:
        response = requests.get(url,params=params,timeout=20)

        response.raise_for_status()
        plant = response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            f"Plant details request failed: {error}"
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "Plant details API returned an invalid response."
        ) from error

    scientific_names = plant.get("scientific_name") or []
    sunlight_values = plant.get("sunlight") or []
    image_data = plant.get("default_image") or {}

    if isinstance(scientific_names, list):
        scientific_name = ", ".join(scientific_names)
    else:
        scientific_name = str(scientific_names)

    if isinstance(sunlight_values, list):
        sunlight = ", ".join(sunlight_values)
    else:
        sunlight = str(sunlight_values)

    image = (
        image_data.get("regular_url")
        or image_data.get("medium_url")
        or image_data.get("original_url")
        or ""
    )

    return {
        "id": plant.get("id"),
        "common_name": plant.get("common_name") or "Unknown",
        "scientific_name": scientific_name or "Unknown",
        "watering": plant.get("watering") or "Unknown",
        "sunlight": sunlight or "Unknown",
        "cycle": plant.get("cycle") or "Unknown",
        "image": image
    }

def watering_to_days(watering):
    """Convert the API watering description into a simple number of days."""
    mapping = {
        "frequent": 2,
        "average": 5,
        "minimum": 10,
        "none": 14,}
    return mapping.get(str(watering).lower(), 7)

    
def care_schedule(watering):
    
    watering_days = watering_to_days(watering)

    if watering_days <= 2:
        fertilizing = 14
        repotting = 365
        pruning = 30

    elif watering_days <= 5:
        fertilizing = 30
        repotting = 365
        pruning = 60

    else:
        fertilizing = 45
        repotting = 365
        pruning = 90        

    return watering_days, fertilizing, pruning, repotting


def sunlight_to_level(sunlight):

    sunlight = str(sunlight).lower().strip()

    if (
        "full_sun" in sunlight
        or "full sun" in sunlight
        or sunlight == "sun"
        or sunlight == "high"
    ):
        return "High"

    elif (
        "part_shade" in sunlight
        or "part shade" in sunlight
        or "partial shade" in sunlight
        or "sun-part_shade" in sunlight
        or "part sun" in sunlight
        or sunlight == "medium"
    ):
        return "Medium"

    elif (
        "full_shade" in sunlight
        or "full shade" in sunlight
        or sunlight == "shade"
        or sunlight == "low"
    ):
        return "Low"


# 11: LLM API - OpenRouter AI Plant Doctor
def ai_plant_doctor(plant_name, symptoms, plant_details, care_history):
    api_key = get_secret("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing. Add it to your .env file or Streamlit secrets.")

    if not symptoms.strip():
        raise ValueError("Please describe the plant symptoms.")

    prompt = f"""
You are an AI Plant Doctor inside a student plant-care application.
Give a careful, simple, and practical answer in English.
Do not claim certainty. Explain that the result is general guidance and not a professional botanical diagnosis.

Plant name: {plant_name}
Saved plant details: {plant_details}
Recent care history: {care_history}
Symptoms entered by the user: {symptoms}

Return the answer using these headings:
1. Possible causes
2. What to do now
3. What to monitor
4. When to seek expert help
"""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-OpenRouter-Title": "Plant Care Tracker",
    }
    body = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": "You provide cautious plant-care guidance in clear language.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.3,
        "max_tokens": 700,
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]
    except requests.RequestException as error:
        message = ""
        if getattr(error, "response", None) is not None:
            message = error.response.text[:500]
        raise RuntimeError(f"LLM API request failed. {message}") from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise RuntimeError("The LLM API returned an unexpected response.") from error
