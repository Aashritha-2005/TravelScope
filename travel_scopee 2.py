# import streamlit as st
# import requests
# import PyPDF2
# import speech_recognition as sr
# from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
# import av
# import numpy as np

# # ---------------- Configuration ----------------
# LANGUAGES = {
#     'English': 'en',
#     'French': 'fr',
#     'German': 'de',
#     'Spanish': 'es',
#     'Italian': 'it',
#     'Hindi': 'hi',
#     'Russian': 'ru',
#     'Chinese': 'zh',
#     'Japanese': 'ja',
#     'Telugu': 'te',
# }

# WEATHER_API_KEY = "YOUR_API_KEY"  # Replace this with your actual OpenWeatherMap API key

# # ---------------- Sidebar Navigation ----------------
# st.sidebar.title("Navigation")
# section = st.sidebar.radio("Go to", ["🌐 Translator", "🍽️ Dining", "🌤️ Weather", "🗓️ Itinerary", "📍Attractions"])

# st.title("✈️ Travel Assistant App")

# # ---------------- Section: Translator ----------------
# if section == "🌐 Translator":
#     st.header("🌐 Language Translator with Live Audio 🎙️")

#     src_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
#     dest_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1)
#     text = st.text_area("Enter text to translate:")

#     st.markdown("### 📄 Or upload a PDF to translate its text")
#     pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"])

#     input_text = text

#     if pdf_file is not None:
#         try:
#             reader = PyPDF2.PdfReader(pdf_file)
#             input_text = ""
#             for page in reader.pages:
#                 input_text += page.extract_text() or ""
#             st.success("PDF text extracted!")
#             st.write(input_text[:1000] + "..." if len(input_text) > 1000 else input_text)
#         except Exception as e:
#             st.error(f"Could not extract text from PDF: {e}")

#     st.markdown("### 🎙️ Or speak into your mic to transcribe and translate")

#     class AudioProcessor(AudioProcessorBase):
#         def __init__(self) -> None:
#             self.buffer = []

#         def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
#             audio = frame.to_ndarray()
#             self.buffer.append(audio)
#             return frame

#     ctx = webrtc_streamer(
#         key="speech",
#         audio_processor_factory=AudioProcessor,
#         media_stream_constraints={"audio": True, "video": False},
#         async_processing=True,
#     )

#     if ctx.audio_processor and st.button("Transcribe Audio"):
#         try:
#             recognizer = sr.Recognizer()
#             audio_data = np.concatenate(ctx.audio_processor.buffer, axis=1).flatten().astype(np.int16).tobytes()
#             with open("live_audio.wav", "wb") as f:
#                 f.write(audio_data)
#             with sr.AudioFile("live_audio.wav") as source:
#                 audio = recognizer.record(source)
#                 input_text = recognizer.recognize_google(audio)
#             st.success("Live audio transcribed!")
#             st.write(input_text)
#         except Exception as e:
#             st.error(f"Could not transcribe audio: {e}")

#     if st.button("Translate"):
#         if not input_text.strip():
#             st.warning("Please enter or provide some text to translate.")
#         else:
#             src_code = LANGUAGES[src_lang]
#             dest_code = LANGUAGES[dest_lang]
#             url = "https://api.mymemory.translated.net/get"
#             params = {"q": input_text, "langpair": f"{src_code}|{dest_code}"}
#             try:
#                 response = requests.get(url, params=params, timeout=10)
#                 response.raise_for_status()
#                 data = response.json()
#                 translated_text = data['responseData']['translatedText']
#                 st.success("Translation:")
#                 st.write(translated_text)
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Translation failed: {e}")

# # ---------------- Section: Dining ----------------
# elif section == "🍽️ Dining":
#     st.header("🍽️ Local Dining Recommendations")
#     city = st.text_input("Enter a city")
#     if city:
#         st.write(f"🍕 Best places to eat in {city}:")
#         st.markdown("- 🍜 **Savor Street Food**")
#         st.markdown("- 🍷 **Luxury Dining**")
#         st.markdown("- 🥗 **Vegan Cafes**")
#         st.markdown("- 🍔 **Popular Fast Food Chains**")

# # ---------------- Section: Weather ----------------
# elif section == "🌤️ Weather":
#     st.header("🌤️ Real-time Weather Forecast")

#     st.subheader("📍 Get weather by city")
#     city = st.text_input("City Name")
#     if city:
#         try:
#             url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
#             res = requests.get(url).json()
#             if res.get("cod") != 200:
#                 st.error(f"City not found: {city}")
#             else:
#                 st.success(f"📍 Weather in {city}")
#                 st.markdown(f"**🌡️ Temperature:** {res['main']['temp']}°C")
#                 st.markdown(f"**💧 Humidity:** {res['main']['humidity']}%")
#                 st.markdown(f"**🌬️ Wind Speed:** {res['wind']['speed']} m/s")
#                 st.markdown(f"**🌥️ Condition:** {res['weather'][0]['description'].title()}")
#         except Exception as e:
#             st.error(f"Could not fetch weather: {e}")

#     st.markdown("---")
#     st.subheader("🌐 Get weather by coordinates")
#     lat = st.number_input("Enter Latitude", format="%.6f")
#     lon = st.number_input("Enter Longitude", format="%.6f")
#     if st.button("Get Weather by Coordinates"):
#         try:
#             url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
#             res = requests.get(url).json()
#             if res.get("cod") != 200:
#                 st.error(f"Location not found for coordinates.")
#             else:
#                 st.success(f"📍 Weather at ({lat}, {lon})")
#                 st.markdown(f"**🌡️ Temperature:** {res['main']['temp']}°C")
#                 st.markdown(f"**💧 Humidity:** {res['main']['humidity']}%")
#                 st.markdown(f"**🌬️ Wind Speed:** {res['wind']['speed']} m/s")
#                 st.markdown(f"**🌥️ Condition:** {res['weather'][0]['description'].title()}")
#         except Exception as e:
#             st.error(f"Could not fetch weather by coordinates: {e}")

# # ---------------- Section: Itinerary ----------------
# elif section == "🗓️ Itinerary":
#     st.header("🗓️ Plan Your Itinerary")
#     days = st.number_input("Number of Days", min_value=1, max_value=30, value=3)
#     itinerary = {}
#     for day in range(1, days + 1):
#         with st.expander(f"Day {day} Plan"):
#             morning = st.text_input(f"Day {day} - Morning", key=f"m{day}")
#             afternoon = st.text_input(f"Day {day} - Afternoon", key=f"a{day}")
#             evening = st.text_input(f"Day {day} - Evening", key=f"e{day}")
#             itinerary[day] = {"Morning": morning, "Afternoon": afternoon, "Evening": evening}
#     if st.button("Generate Itinerary Summary"):
#         st.subheader("📝 Your Travel Plan")
#         for day, plan in itinerary.items():
#             st.markdown(f"**Day {day}**")
#             for part, activity in plan.items():
#                 st.markdown(f"- {part}: {activity if activity else 'Not planned'}")

# # ---------------- Section: Attractions ----------------
# elif section == "📍Attractions":
#     st.header("📍 Top Tourist Attractions")
#     city = st.text_input("Enter a city to find attractions")
#     if city:
#         st.write(f"🌆 Top attractions in {city}:")
#         st.markdown("- 🗼 **Iconic Landmarks**")
#         st.markdown("- 🖼️ **Museums & Galleries**")
#         st.markdown("- 🌳 **Parks & Gardens**")
#         st.markdown("- 🎡 **Amusement Spots**")
#         st.markdown("🧭 Tip: Connect Google Places or TripAdvisor API for live data")
# import streamlit as st
# import requests
# import PyPDF2
# import speech_recognition as sr
# from streamlit_webrtc import webrtc_streamer # AudioProcessorBase
# import av
# import numpy as np

# # ---------------- Language Setup ----------------
# LANGUAGES = {
#     'English': 'en',
#     'French': 'fr',
#     'German': 'de',
#     'Spanish': 'es',
#     'Italian': 'it',
#     'Hindi': 'hi',
#     'Russian': 'ru',
#     'Chinese': 'zh',
#     'Japanese': 'ja',
#     'Telugu': 'te',
# }

# WEATHER_API_KEY = "YOUR_API_KEY"  # 🔁 Replace with your OpenWeatherMap API key

# # ---------------- Sidebar Navigation ----------------
# st.sidebar.title("Navigation")
# section = st.sidebar.radio("Go to", ["🌐 Translator", "🍽️ Dining", "🌤️ Weather", "🗓️ Itinerary", "📍Attractions"])

# st.title("✈️ Travel Assistant App")

# # ---------------- Section: Translator ----------------
# if section == "🌐 Translator":
#     # st.header("🌐 Language Translator with Live Audio 🎙️")

#     src_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
#     dest_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1)

#     text = st.text_area("Enter text to translate:")

#     # st.markdown("### 📄 Or upload a PDF to translate its text")
#     # pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"])

#     input_text = text

#     # if pdf_file is not None:
#     #     try:
#     #         reader = PyPDF2.PdfReader(pdf_file)
#     #         input_text = ""
#     #         for page in reader.pages:
#     #             input_text += page.extract_text() or ""
#     #         st.success("PDF text extracted!")
#     #         st.write(input_text[:1000] + "..." if len(input_text) > 1000 else input_text)
#     #     except Exception as e:
#     #         st.error(f"Could not extract text from PDF: {e}")

#     # st.markdown("### 🎙️ Or speak into your mic to transcribe and translate")

#     # class AudioProcessor(AudioProcessorBase):
#     #     def __init__(self) -> None:
#     #         self.buffer = []

#     #     def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
#     #         audio = frame.to_ndarray()
#     #         self.buffer.append(audio)
#     #         return frame

#     # ctx = webrtc_streamer(
#     #     key="speech",
#     #     audio_processor_factory=AudioProcessor,
#     #     media_stream_constraints={"audio": True, "video": False},
#     #     async_processing=True,
#     # )

#     # if ctx.audio_processor and st.button("Transcribe Audio"):
#     #     try:
#     #         recognizer = sr.Recognizer()
#     #         audio_data = np.concatenate(ctx.audio_processor.buffer, axis=1).flatten().astype(np.int16).tobytes()
#     #         with open("live_audio.wav", "wb") as f:
#     #             f.write(audio_data)

#     #         with sr.AudioFile("live_audio.wav") as source:
#     #             audio = recognizer.record(source)
#     #             input_text = recognizer.recognize_google(audio)
#     #         st.success("Live audio transcribed!")
#     #         st.write(input_text)
#     #     except Exception as e:
#     #         st.error(f"Could not transcribe audio: {e}")

#     if st.button("Translate"):
#         if not input_text.strip():
#             st.warning("Please enter or provide some text to translate.")
#         else:
#             src_code = LANGUAGES[src_lang]
#             dest_code = LANGUAGES[dest_lang]
#             url = "https://api.mymemory.translated.net/get"
#             params = {"q": input_text, "langpair": f"{src_code}|{dest_code}"}
#             try:
#                 response = requests.get(url, params=params, timeout=10)
#                 response.raise_for_status()
#                 data = response.json()
#                 translated_text = data['responseData']['translatedText']
#                 st.success("Translation:")
#                 st.write(translated_text)
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Translation failed: {e}")

# # ---------------- Section: Dining ----------------
# elif section == "🍽️ Dining":
#     st.header("🍽️ Local Dining Recommendations")
#     city = st.text_input("Enter a city")
#     if city:
#         st.write(f"🍕 Best places to eat in {city}:")
#         st.markdown("- 🍜 **Savor Street Food**")
#         st.markdown("- 🍷 **Luxury Dining**")
#         st.markdown("- 🥗 **Vegan Cafes**")
#         st.markdown("- 🍔 **Popular Fast Food Chains**")

# # ---------------- Section: Weather ----------------
# elif section == "🌤️ Weather":
#     st.header("🌤️ Real-time Weather Forecast")
#     city = st.text_input("Enter city name")
#     if city:
#         try:
#             url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
#             res = requests.get(url).json()
#             if res.get("cod") != 200:
#                 st.error(f"City not found: {city}")
#             else:
#                 st.success(f"📍 Weather in {city}")
#                 st.markdown(f"**🌡️ Temperature:** {res['main']['temp']}°C")
#                 st.markdown(f"**💧 Humidity:** {res['main']['humidity']}%")
#                 st.markdown(f"**🌬️ Wind Speed:** {res['wind']['speed']} m/s")
#                 st.markdown(f"**🌥️ Condition:** {res['weather'][0]['description'].title()}")
#         except Exception as e:
#             st.error(f"Could not fetch weather: {e}")

# # ---------------- Section: Itinerary ----------------
# elif section == "🗓️ Itinerary":
#     st.header("🗓️ Plan Your Itinerary")
#     days = st.number_input("Number of Days", min_value=1, max_value=30, value=3)
#     itinerary = {}
#     for day in range(1, days + 1):
#         with st.expander(f"Day {day} Plan"):
#             morning = st.text_input(f"Day {day} - Morning", key=f"m{day}")
#             afternoon = st.text_input(f"Day {day} - Afternoon", key=f"a{day}")
#             evening = st.text_input(f"Day {day} - Evening", key=f"e{day}")
#             itinerary[day] = {"Morning": morning, "Afternoon": afternoon, "Evening": evening}
#     if st.button("Generate Itinerary Summary"):
#         st.subheader("📝 Your Travel Plan")
#         for day, plan in itinerary.items():
#             st.markdown(f"**Day {day}**")
#             for part, activity in plan.items():
#                 st.markdown(f"- {part}: {activity if activity else 'Not planned'}")

# # ---------------- Section: Attractions ----------------
# elif section == "📍Attractions":
#     st.header("📍 Top Tourist Attractions")
#     city = st.text_input("Enter a city to find attractions")
#     if city:
#         st.write(f"🌆 Top attractions in {city}:")
#         st.markdown("- 🗼 **Iconic Landmarks**")
#         st.markdown("- 🖼️ **Museums & Galleries**")
#         st.markdown("- 🌳 **Parks & Gardens**")
#         st.markdown("- 🎡 **Amusement Spots**")
#         st.markdown("🧭 Tip: Connect Google Places or TripAdvisor API for live data")

# if __name__ == "__main__":
#     main()

import streamlit as st
import requests
import random
from datetime import datetime, timedelta
from faker import Faker
import PyPDF2
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import numpy as np

# Initialize faker
fake = Faker()

# ======================
# Language Configuration
# ======================
LANGUAGES = {
    'English': 'en', 'French': 'fr', 'German': 'de', 'Spanish': 'es', 'Italian': 'it',
    'Hindi': 'hi', 'Russian': 'ru', 'Chinese': 'zh', 'Japanese': 'ja', 'Telugu': 'te'
}

# ======================
# Real Weather API Fetch (OpenWeatherMap)
# ======================
def fetch_weather(location, days=3):
    api_key = "your_api_key_here"  # Replace with your OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/forecast"

    try:
        response = requests.get(base_url, params={
            "q": location,
            "units": "metric",
            "cnt": days * 8,
            "appid": api_key
        }, timeout=10)
        data = response.json()

        weather = []
        for i in range(days):
            day_data = data['list'][i * 8]
            date = datetime.fromtimestamp(day_data['dt'])
            weather.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": date.strftime("%A"),
                "temp": f"{day_data['main']['temp']:.1f}°C",
                "icon": "🌤️",
                "condition": day_data['weather'][0]['description'].title(),
                "rain": f"{day_data.get('pop', 0) * 100:.0f}%",
                "humidity": f"{day_data['main']['humidity']}%"
            })
        return weather
    except Exception as e:
        st.warning(f"Using fallback data due to: {e}")
        return auto_generate_weather(location, days)

# Fallback generator
def auto_generate_weather(location, days):
    weather = []
    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        temp = random.gauss(25, 5)
        condition = random.choice([("☀️", "Sunny"), ("⛅", "Cloudy"), ("🌧️", "Rainy")])
        weather.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "temp": f"{max(-5, min(40, temp)):.1f}°C",
            "icon": condition[0],
            "condition": condition[1],
            "rain": f"{random.randint(10, 90)}%",
            "humidity": f"{random.randint(30, 90)}%"
        })
    return weather

# ======================
# Mock Place Generator
# ======================
def auto_generate_places(location, place_type):
    types = {
        "restaurant": {
            "names": list(set([f"{fake.company()} {x}" for x in ["Bistro", "Grill", "Kitchen", "Eatery"]])),
            "cuisines": ["Italian", "Japanese", "Indian", "Mexican", "Local", "Fusion"],
            "descriptors": ["Cozy", "Modern", "Traditional", "Upscale", "Casual"]
        },
        "attraction": {
            "names": list(set([f"{x} {y}" for x in ["National", "City", "Old", "Grand"] 
                              for y in ["Museum", "Park", "Gallery", "Tower"]])),
            "types": ["Museum", "Park", "Landmark", "Historical Site"],
            "descriptors": ["Famous", "Iconic", "Must-see", "Hidden gem"]
        }
    }
    random.shuffle(types[place_type]['names'])
    places = []
    for _ in range(5):
        place_data = types[place_type]
        name = f"{random.choice(place_data['descriptors'])} {random.choice(place_data['names'])}"
        places.append({
            "name": name,
            "type": random.choice(place_data['types'] if place_type == "attraction" else place_data['cuisines']),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "price": "$" * random.randint(1, 4),
            "distance": f"{random.uniform(0.1, 5.0):.1f} km",
            "address": fake.address().replace("\n", ", "),
            "description": fake.sentence()
        })
    return sorted(places, key=lambda x: x["rating"], reverse=True)

# ======================
# Itinerary Planner
# ======================
def generate_itinerary(attractions, restaurants, start_date):
    itinerary = []
    total_days = min(len(attractions), len(restaurants))
    for i in range(total_days):
        day_date = (start_date + timedelta(days=i)).strftime('%A')
        itinerary.append({
            "day": f"Day {i+1} - {day_date}",
            "morning": f"Visit {attractions[i]['name']} ({attractions[i]['type']})",
            "afternoon": f"Lunch at {restaurants[i]['name']} ({restaurants[i]['type']})",
            "evening": f"Dinner at {random.choice(restaurants)['name']} and evening walk"
        })
    return itinerary

# ======================
# Translator (unchanged)
# ======================
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.buffer = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.buffer.append(frame.to_ndarray())
        return frame

def translate_text(text, src_lang, dest_lang):
    base_url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": f"{LANGUAGES[src_lang]}|{LANGUAGES[dest_lang]}"}
    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()['responseData']['translatedText']
    except:
        return f"[MOCK TRANSLATION] {text} in {dest_lang}"

# ======================
# Main App
# ======================
def main():
    st.set_page_config(page_title="Travel Scope", layout="wide")
    st.title("🌍 Smart Travel Scope with Translation")

    with st.sidebar:
        location = st.text_input("Destination", "Paris, France")
        start_date = st.date_input("Start Date", datetime.now())
        end_date = st.date_input("End Date", datetime.now() + timedelta(days=3))
        interests = st.multiselect("Interests", ["Adventure", "Culture", "Food", "Nature", "Shopping", "Relaxation"])

    days = (end_date - start_date).days + 1

    tabs = st.tabs(["🌤️ Overview", "🗓️ Itinerary", "🍽️ Dining", "🏛️ Attractions", "🌐 Translator"])

    with tabs[0]:
        st.subheader(f"{location} Weather Forecast")
        weather = fetch_weather(location, days)
        cols = st.columns(min(7, days))
        for i, col in enumerate(cols[:days]):
            with col:
                st.markdown(f"**{weather[i]['day']}**")
                st.write(weather[i]["date"])
                st.write(f"{weather[i]['icon']} {weather[i]['temp']}")
                st.caption(weather[i]["condition"])
                st.progress(float(weather[i]["rain"][:-1])/100, text=weather[i]["rain"])

    with tabs[2]:
        st.subheader("Top Restaurants")
        restaurants = auto_generate_places(location, "restaurant")
        for r in restaurants:
            with st.expander(f"{r['name']} ({r['rating']}⭐)"):
                st.write(f"**Cuisine:** {r['type']}")
                st.write(f"**Price:** {r['price']}")
                st.write(f"**Distance:** {r['distance']}")

    with tabs[3]:
        st.subheader("Must-See Attractions")
        attractions = auto_generate_places(location, "attraction")
        for a in attractions:
            with st.expander(f"{a['name']} ({a['rating']}⭐)"):
                st.write(f"**Type:** {a['type']}")
                st.write(f"**Time Needed:** {random.randint(1, 3)} hours")

    with tabs[1]:
        st.subheader(f"{days}-Day Personalized Itinerary")
        itinerary = generate_itinerary(attractions, restaurants, start_date)
        for day in itinerary:
            with st.expander(day["day"]):
                st.write("**Morning:**", day["morning"])
                st.write("**Afternoon:**", day["afternoon"])
                st.write("**Evening:**", day["evening"])

    with tabs[4]:
        st.subheader("🌐 Language Translator with Live Audio")
        col1, col2 = st.columns(2)

        with col1:
            src_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
            text = st.text_area("Enter text to translate:")
            st.markdown("### 📄 PDF Translation")
            pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
            input_text = text
            if pdf_file is not None:
                try:
                    reader = PyPDF2.PdfReader(pdf_file)
                    input_text = "".join([page.extract_text() or "" for page in reader.pages])
                    st.success("PDF text extracted!")
                except Exception as e:
                    st.error(f"Could not extract text: {e}")

        with col2:
            dest_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1)
            st.markdown("### 🎙️ Speak to Translate")
            ctx = webrtc_streamer(
                key="speech", audio_processor_factory=AudioProcessor,
                media_stream_constraints={"audio": True, "video": False}, async_processing=True)

            if ctx.audio_processor and st.button("Transcribe Audio"):
                try:
                    recognizer = sr.Recognizer()
                    audio_data = np.concatenate(ctx.audio_processor.buffer, axis=1).flatten().astype(np.int16).tobytes()
                    audio = sr.AudioData(audio_data, 44100, 2)
                    input_text = recognizer.recognize_google(audio)
                    st.success("Transcribed Text:")
                    st.write(input_text)
                except Exception as e:
                    st.error(f"Could not transcribe audio: {e}")

            if st.button("Translate"):
                if not input_text.strip():
                    st.warning("Please enter or speak some text.")
                else:
                    translated = translate_text(input_text, src_lang, dest_lang)
                    st.success("Translation:")
                    st.write(translated)

if __name__ == "__main__":
    main()
