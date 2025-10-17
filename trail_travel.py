import streamlit as st
import requests
import pandas as pd
import PyPDF2
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import numpy as np
import overpy
from geopy.geocoders import Nominatim
import random
import datetime

# App configuration
st.set_page_config(page_title="TravelScope", layout="wide")
st.title("🌍 TravelScope: Your All-in-One Travel Companion")

# Initialize session state for expenses and itinerary
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=["Item", "Category", "Amount (₹)"])
if "itinerary" not in st.session_state:
    st.session_state["itinerary"] = None
if "city" not in st.session_state:
    st.session_state["city"] = None

# Sidebar navigation
page = st.sidebar.selectbox(
    "Choose a feature",
    ["Nearby Explorer", "Trip Itinerary", "Expense Tracker", "Weather Explorer", "Language Translator", "Cultural Insights"]
)

# Language dictionary for translator
LANGUAGES = {
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Spanish': 'es',
    'Italian': 'it',
    'Hindi': 'hi',
    'Russian': 'ru',
    'Chinese': 'zh',
    'Japanese': 'ja',
    'Telugu': 'te',
}

# Nearby Explorer Functions
@st.cache_data
def geocode_location(city_name):
    geocode_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "TravelScopeApp/1.0"
    }
    try:
        response = requests.get(geocode_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon']), data[0]['display_name']
            else:
                st.warning("No results found for the entered city name.")
        else:
            st.error(f"Error: Received status code {response.status_code} from the server.")
    except requests.exceptions.RequestException as e:
        st.error(f"Network error occurred: {e}")
    return None, None, None

@st.cache_data
def find_nearby_places(lat, lon, category="tourism"):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node(around:5000,{lat},{lon})["{category}"];
    out;
    """
    headers = {
        "User-Agent": "TravelScopeApp/1.0"
    }
    try:
        response = requests.get(overpass_url, data=query, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "elements" in data and len(data["elements"]) > 0:
                return data["elements"]
            else:
                st.warning("No nearby places found for the given category.")
        else:
            st.error(f"Error: Received status code {response.status_code} from the server.")
    except requests.exceptions.RequestException as e:
        st.error(f"Network error occurred: {e}")
    return []

# Weather Functions
@st.cache_data
def fetch_coordinates(city_name):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
    response = requests.get(geo_url)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]["latitude"], results[0]["longitude"], results[0]["name"]
    return None, None, None

@st.cache_data
def fetch_weather_and_details(lat, lon):
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m,pressure_msl,uv_index"
    )
    response = requests.get(weather_url)
    if response.status_code == 200:
        return response.json()
    return None

# Itinerary Functions
geolocator = Nominatim(user_agent="trip_planner_app")
api = overpy.Overpass()

def geocode_city(city: str):
    loc = geolocator.geocode(city)
    return (loc.latitude, loc.longitude) if loc else (None, None)

def fetch_attractions(lat: float, lon: float, radius_famous: int = 10000, radius_fallback: int = 8000) -> list[dict]:
    places, seen = [], set()
    famous_q = f"""
    (
      node["tourism"~"attraction|museum|viewpoint|artwork|zoo|theme_park"]
      (around:{radius_famous},{lat},{lon})["name"]["wikidata"];
      node["tourism"~"attraction|museum|viewpoint|artwork|zoo|theme_park"]
      (around:{radius_famous},{lat},{lon})["name"]["wikipedia"];
      node["tourism"~"attraction|museum|viewpoint|artwork|zoo|theme_park"]
      (around:{radius_famous},{lat},{lon})["name"]["heritage"];
    );
    out body;
    """
    places += _run_overpass_query(famous_q, seen)
    if len(places) < 10:
        near_q = f"""
        node["tourism"~"attraction|museum|viewpoint|artwork|zoo|theme_park"]
        (around:{radius_fallback},{lat},{lon})["name"];
        out body;
        """
        places += _run_overpass_query(near_q, seen)
    return places

def _run_overpass_query(query: str, seen: set) -> list[dict]:
    try:
        res = api.query(query)
    except overpy.exception.OverpassTooManyRequests:
        st.error("Too many requests to Overpass. Please wait and try again.")
        return []
    except overpy.exception.OverpassGatewayTimeout:
        st.error("Overpass timed out. Try a smaller radius or another city.")
        return []
    except Exception as e:
        st.error(f"Overpass error: {repr(e)}")
        return []
    out = []
    for n in res.nodes:
        name = n.tags.get("name")
        if name and name not in seen:
            seen.add(name)
            out.append({"name": name, "lat": float(n.lat), "lon": float(n.lon)})
    return out

def build_itinerary(places: list[dict], days: int) -> dict:
    if not places:
        return {}
    random.shuffle(places)
    min_pd, max_pd = 2, 5
    total = len(places)
    if total < days * min_pd:
        days = max(1, total // min_pd)
    plan, idx = {}, 0
    for d in range(days):
        key = f"Day {d+1}"
        plan[key] = []
        remain_days, remain = days - d, total - idx
        n_today = min(max_pd, max(min_pd, remain // remain_days))
        start = 9
        for i in range(n_today):
            if idx >= total:
                break
            time_str = datetime.time(start + i*2, 0).strftime("%H:%M")
            plan[key].append({"time": time_str, "place": places[idx]["name"]})
            idx += 1
    return plan

# Audio Processor for Translator
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.buffer = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        self.buffer.append(audio)
        return frame

# Page: Nearby Explorer
if page == "Nearby Explorer":
    st.header("📍 Nearby Explorer")
    st.write("Find places to visit near a city using OpenStreetMap APIs.")
    city_name = st.text_input("Enter the name of a city to explore nearby places:", key="nearby_city")
    if city_name:
        lat, lon, display_name = geocode_location(city_name)
        if lat and lon:
            st.success(f"City found: {display_name} ({lat}, {lon})")
            category = st.selectbox(
                "Choose a category to explore:",
                ["tourism", "amenity", "shop", "leisure", "natural"],
                key="nearby_category"
            )
            nearby_places = find_nearby_places(lat, lon, category)
            if nearby_places:
                st.write(f"### Nearby {category.capitalize()} Places:")
                for place in nearby_places:
                    name = place.get("tags", {}).get("name", "Unknown")
                    st.write(f"- {name}")
            else:
                st.info(f"No {category} places found near {city_name}.")
        else:
            st.error("Could not find the city. Please check the name and try again.")
    else:
        st.info("Please enter a city name to explore nearby places.")

# Page: Trip Itinerary
elif page == "Trip Itinerary":
    st.header("🌍 Dynamic Trip Itinerary Generator")
    city = st.text_input("📍 Enter city", "Paris", key="itinerary_city")
    num_days = st.number_input("🗓️ Number of days", 1, 10, 3, key="itinerary_days")
    if st.button("Generate Itinerary", key="generate_itinerary"):
        lat, lon = geocode_city(city)
        if lat is None:
            st.error("City not found. Please check the spelling.")
        else:
            attractions = fetch_attractions(lat, lon)
            if not attractions:
                st.warning("No attractions found within range.")
            else:
                st.session_state["itinerary"] = build_itinerary(attractions, num_days)
                st.session_state["city"] = city
    itinerary = st.session_state.get("itinerary")
    if itinerary:
        st.header(f"🧳 Trip Itinerary for {st.session_state['city']}")
        for day, items in itinerary.items():
            with st.expander(day, expanded=True):
                for item in items:
                    st.markdown(f"🕘 **{item['time']}** — {item['place']}")
    else:
        st.info("Enter a city and click Generate Itinerary.")

# Page: Expense Tracker
elif page == "Expense Tracker":
    st.header("🧾 Cultural Insights Expense Tracker")
    st.subheader("➕ Add a New Expense")
    item = st.text_input("Item / Description", key="expense_item")
    category = st.selectbox("Category", ["Food", "Travel", "Accommodation", "Miscellaneous"], key="expense_category")
    amount = st.number_input("Enter amount in ₹", min_value=0.0, step=10.0, format="%.2f", key="expense_amount")
    if st.button("Add Expense", key="add_expense"):
        if item and amount:
            new_expense = {"Item": item, "Category": category, "Amount (₹)": amount}
            new_df = pd.DataFrame([new_expense])
            st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_df], ignore_index=True)
            st.success(f"Added expense: {item} – ₹{amount:.2f}")
        else:
            st.warning("Please fill out both the item and amount.")
    st.subheader("📋 Expense Log")
    if not st.session_state["expenses"].empty:
        st.dataframe(st.session_state["expenses"], use_container_width=True)
        total = st.session_state["expenses"]["Amount (₹)"].sum()
        st.markdown(f"### 💰 Total Spent: ₹{total:.2f}")
    else:
        st.info("No expenses added yet.")
    if st.button("🔄 Clear All Expenses", key="clear_expenses"):
        st.session_state["expenses"] = pd.DataFrame(columns=["Item", "Category", "Amount (₹)"])
        st.success("All expenses cleared.")

# Page: Weather Explorer
elif page == "Weather Explorer":
    st.header("🌦️ Accurate Weather Explorer")
    st.write("Enter a city name to get real-time weather conditions, including humidity, air pressure, and UV index.")
    city_name = st.text_input("Enter a city name:", key="weather_city")
    if city_name:
        lat, lon, display_name = fetch_coordinates(city_name)
        if lat and lon:
            st.success(f"Fetching real-time weather for: {display_name}")
            weather_data = fetch_weather_and_details(lat, lon)
            if weather_data and "current_weather" in weather_data:
                current_weather = weather_data["current_weather"]
                hourly_data = weather_data.get("hourly", {})
                st.subheader(f"Real-Time Weather in {display_name}:")
                st.write(f"**Temperature:** {current_weather['temperature']}°C")
                st.write(f"**Wind Speed:** {current_weather['windspeed']} km/h")
                st.write(f"**Wind Direction:** {current_weather['winddirection']}°")
                if hourly_data:
                    try:
                        humidity = hourly_data["relative_humidity_2m"][0]
                        pressure = hourly_data["pressure_msl"][0]
                        uv_index = hourly_data["uv_index"][0]
                        st.subheader("Additional Weather Details:")
                        st.write(f"**Humidity:** {humidity}%")
                        st.write(f"**Air Pressure:** {pressure} hPa")
                        st.write(f"**UV Index:** {uv_index}")
                    except (IndexError, KeyError):
                        st.error("Unable to retrieve additional metrics from hourly data.")
            else:
                st.error("Unable to fetch weather data. Please try again later.")
        else:
            st.error("City not found. Please check the name and try again.")
    else:
        st.info("Please enter a city name to get the weather conditions.")

# Page: Language Translator
elif page == "Language Translator":
    st.header("🌐 Language Translator with Live Audio 🎙️")
    src_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0, key="src_lang")
    dest_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1, key="dest_lang")
    text = st.text_area("Enter text to translate:", key="translate_text")
    st.markdown("### 📄 Or upload a PDF to translate its text")
    pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_upload")
    input_text = text
    if pdf_file is not None:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            input_text = ""
            for page in reader.pages:
                input_text += page.extract_text() or ""
            st.success("PDF text extracted!")
            st.write(input_text[:1000] + "..." if len(input_text) > 1000 else input_text)
        except Exception as e:
            st.error(f"Could not extract text from PDF: {e}")
    st.markdown("### 🎙️ Or speak into your mic to transcribe and translate")
    ctx = webrtc_streamer(
        key="speech",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )
    if ctx.audio_processor and st.button("Transcribe Audio", key="transcribe_audio"):
        try:
            recognizer = sr.Recognizer()
            audio_data = np.concatenate(ctx.audio_processor.buffer, axis=1).flatten().astype(np.int16).tobytes()
            with open("live_audio.wav", "wb") as f:
                f.write(audio_data)
            with sr.AudioFile("live_audio.wav") as source:
                audio = recognizer.record(source)
                input_text = recognizer.recognize_google(audio)
            st.success("Live audio transcribed!")
            st.write(input_text)
        except Exception as e:
            st.error(f"Could not transcribe audio: {e}")
    if st.button("Translate", key="translate_button"):
        if not input_text.strip():
            st.warning("Please enter or speak some text.")
        else:
            src_code = LANGUAGES[src_lang]
            dest_code = LANGUAGES[dest_lang]
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": input_text,
                "langpair": f"{src_code}|{dest_code}"
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                translated_text = data['responseData']['translatedText']
                st.success("Translation:")
                st.write(translated_text)
            except requests.exceptions.RequestException as e:
                st.error(f"Translation failed: {e}")

# Page: Cultural Insights
elif page == "Cultural Insights":
    st.header("Cultural Insights App")
    destination = st.text_input("Enter a place:", placeholder="e.g., Paris, Tokyo, New Delhi", key="culture_destination")
    if destination:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{destination}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "No title available")
                extract = data.get("extract", "No insights available for this place.")
                thumbnail = data.get("thumbnail", {}).get("source", None)
                st.subheader(title)
                if thumbnail:
                    st.image(thumbnail, caption=f"Image of {destination}")
                st.write(extract)
            else:
                st.error("Unable to fetch cultural insights. Please try a different place.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Enter a place above to get started!")
    st.markdown("---")
    st.caption("Powered by Wikipedia API")

# Footer
st.markdown("---")
st.caption("TravelScope: Powered by OpenStreetMap, Open-Meteo, MyMemory, and Wikipedia APIs")