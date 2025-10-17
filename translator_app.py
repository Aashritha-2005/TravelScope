import streamlit as st
import requests
import PyPDF2
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import numpy as np

# ---------------- Configuration ----------------
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

WEATHER_API_KEY = "YOUR_API_KEY"  # Replace this with your actual OpenWeatherMap API key

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["🌐 Translator", "🍽️ Dining", "🌤️ Weather", "🗓️ Itinerary", "📍Attractions"])

st.title("✈️ Travel Assistant App")

# ---------------- Section: Translator ----------------
if section == "🌐 Translator":
    st.header("🌐 Language Translator with Live Audio 🎙️")

    src_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
    dest_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1)
    text = st.text_area("Enter text to translate:")

    st.markdown("### 📄 Or upload a PDF to translate its text")
    pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"])

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

    class AudioProcessor(AudioProcessorBase):
        def __init__(self) -> None:
            self.buffer = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray()
            self.buffer.append(audio)
            return frame

    ctx = webrtc_streamer(
        key="speech",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

    if ctx.audio_processor and st.button("Transcribe Audio"):
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

    if st.button("Translate"):
        if not input_text.strip():
            st.warning("Please enter or provide some text to translate.")
        else:
            src_code = LANGUAGES[src_lang]
            dest_code = LANGUAGES[dest_lang]
            url = "https://api.mymemory.translated.net/get"
            params = {"q": input_text, "langpair": f"{src_code}|{dest_code}"}
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                translated_text = data['responseData']['translatedText']
                st.success("Translation:")
                st.write(translated_text)
            except requests.exceptions.RequestException as e:
                st.error(f"Translation failed: {e}")

# ---------------- Section: Dining ----------------
elif section == "🍽️ Dining":
    st.header("🍽️ Local Dining Recommendations")
    city = st.text_input("Enter a city")
    if city:
        st.write(f"🍕 Best places to eat in {city}:")
        st.markdown("- 🍜 **Savor Street Food**")
        st.markdown("- 🍷 **Luxury Dining**")
        st.markdown("- 🥗 **Vegan Cafes**")
        st.markdown("- 🍔 **Popular Fast Food Chains**")

# ---------------- Section: Weather ----------------
elif section == "🌤️ Weather":
    st.header("🌤️ Real-time Weather Forecast")

    st.subheader("📍 Get weather by city")
    city = st.text_input("City Name")
    if city:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            res = requests.get(url).json()
            if res.get("cod") != 200:
                st.error(f"City not found: {city}")
            else:
                st.success(f"📍 Weather in {city}")
                st.markdown(f"**🌡️ Temperature:** {res['main']['temp']}°C")
                st.markdown(f"**💧 Humidity:** {res['main']['humidity']}%")
                st.markdown(f"**🌬️ Wind Speed:** {res['wind']['speed']} m/s")
                st.markdown(f"**🌥️ Condition:** {res['weather'][0]['description'].title()}")
        except Exception as e:
            st.error(f"Could not fetch weather: {e}")

    st.markdown("---")
    st.subheader("🌐 Get weather by coordinates")
    lat = st.number_input("Enter Latitude", format="%.6f")
    lon = st.number_input("Enter Longitude", format="%.6f")
    if st.button("Get Weather by Coordinates"):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            res = requests.get(url).json()
            if res.get("cod") != 200:
                st.error(f"Location not found for coordinates.")
            else:
                st.success(f"📍 Weather at ({lat}, {lon})")
                st.markdown(f"**🌡️ Temperature:** {res['main']['temp']}°C")
                st.markdown(f"**💧 Humidity:** {res['main']['humidity']}%")
                st.markdown(f"**🌬️ Wind Speed:** {res['wind']['speed']} m/s")
                st.markdown(f"**🌥️ Condition:** {res['weather'][0]['description'].title()}")
        except Exception as e:
            st.error(f"Could not fetch weather by coordinates: {e}")

# ---------------- Section: Itinerary ----------------
elif section == "🗓️ Itinerary":
    st.header("🗓️ Plan Your Itinerary")
    days = st.number_input("Number of Days", min_value=1, max_value=30, value=3)
    itinerary = {}
    for day in range(1, days + 1):
        with st.expander(f"Day {day} Plan"):
            morning = st.text_input(f"Day {day} - Morning", key=f"m{day}")
            afternoon = st.text_input(f"Day {day} - Afternoon", key=f"a{day}")
            evening = st.text_input(f"Day {day} - Evening", key=f"e{day}")
            itinerary[day] = {"Morning": morning, "Afternoon": afternoon, "Evening": evening}
    if st.button("Generate Itinerary Summary"):
        st.subheader("📝 Your Travel Plan")
        for day, plan in itinerary.items():
            st.markdown(f"**Day {day}**")
            for part, activity in plan.items():
                st.markdown(f"- {part}: {activity if activity else 'Not planned'}")

# ---------------- Section: Attractions ----------------
elif section == "📍Attractions":
    st.header("📍 Top Tourist Attractions")
    city = st.text_input("Enter a city to find attractions")
    if city:
        st.write(f"🌆 Top attractions in {city}:")
        st.markdown("- 🗼 **Iconic Landmarks**")
        st.markdown("- 🖼️ **Museums & Galleries**")
        st.markdown("- 🌳 **Parks & Gardens**")
        st.markdown("- 🎡 **Amusement Spots**")
        st.markdown("🧭 Tip: Connect Google Places or TripAdvisor API for live data")
import streamlit as st
import requests
import PyPDF2
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer # AudioProcessorBase
import av
import numpy as np

# ---------------- Language Setup ----------------
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

WEATHER_API_KEY = "YOUR_API_KEY"  # 🔁 Replace with your OpenWeatherMap API key

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["🌐 Translator", "🍽️ Dining", "🌤️ Weather", "🗓️ Itinerary", "📍Attractions"])

st.title("✈️ Travel Assistant App")

# ---------------- Section: Translator ----------------
if section == "🌐 Translator":
    # st.header("🌐 Language Translator with Live Audio 🎙️")

    src_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
    dest_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1)

    text = st.text_area("Enter text to translate:")

    # st.markdown("### 📄 Or upload a PDF to translate its text")
    # pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    input_text = text

    # if pdf_file is not None:
    #     try:
    #         reader = PyPDF2.PdfReader(pdf_file)
    #         input_text = ""
    #         for page in reader.pages:
    #             input_text += page.extract_text() or ""
    #         st.success("PDF text extracted!")
    #         st.write(input_text[:1000] + "..." if len(input_text) > 1000 else input_text)
    #     except Exception as e:
    #         st.error(f"Could not extract text from PDF: {e}")

    # st.markdown("### 🎙️ Or speak into your mic to transcribe and translate")

    # class AudioProcessor(AudioProcessorBase):
    #     def __init__(self) -> None:
    #         self.buffer = []

    #     def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
    #         audio = frame.to_ndarray()
    #         self.buffer.append(audio)
    #         return frame

    # ctx = webrtc_streamer(
    #     key="speech",
    #     audio_processor_factory=AudioProcessor,
    #     media_stream_constraints={"audio": True, "video": False},
    #     async_processing=True,
    # )

    # if ctx.audio_processor and st.button("Transcribe Audio"):
    #     try:
    #         recognizer = sr.Recognizer()
    #         audio_data = np.concatenate(ctx.audio_processor.buffer, axis=1).flatten().astype(np.int16).tobytes()
    #         with open("live_audio.wav", "wb") as f:
    #             f.write(audio_data)

    #         with sr.AudioFile("live_audio.wav") as source:
    #             audio = recognizer.record(source)
    #             input_text = recognizer.recognize_google(audio)
    #         st.success("Live audio transcribed!")
    #         st.write(input_text)
    #     except Exception as e:
    #         st.error(f"Could not transcribe audio: {e}")

    if st.button("Translate"):
        if not input_text.strip():
            st.warning("Please enter or provide some text to translate.")
        else:
            src_code = LANGUAGES[src_lang]
            dest_code = LANGUAGES[dest_lang]
            url = "https://api.mymemory.translated.net/get"
            params = {"q": input_text, "langpair": f"{src_code}|{dest_code}"}
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                translated_text = data['responseData']['translatedText']
                st.success("Translation:")
                st.write(translated_text)
            except requests.exceptions.RequestException as e:
                st.error(f"Translation failed: {e}")

# ---------------- Section: Dining ----------------
elif section == "🍽️ Dining":
    st.header("🍽️ Local Dining Recommendations")
    city = st.text_input("Enter a city")
    if city:
        st.write(f"🍕 Best places to eat in {city}:")
        st.markdown("- 🍜 **Savor Street Food**")
        st.markdown("- 🍷 **Luxury Dining**")
        st.markdown("- 🥗 **Vegan Cafes**")
        st.markdown("- 🍔 **Popular Fast Food Chains**")

# ---------------- Section: Weather ----------------
elif section == "🌤️ Weather":
    st.header("🌤️ Real-time Weather Forecast")
    city = st.text_input("Enter city name")
    if city:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            res = requests.get(url).json()
            if res.get("cod") != 200:
                st.error(f"City not found: {city}")
            else:
                st.success(f"📍 Weather in {city}")
                st.markdown(f"**🌡️ Temperature:** {res['main']['temp']}°C")
                st.markdown(f"**💧 Humidity:** {res['main']['humidity']}%")
                st.markdown(f"**🌬️ Wind Speed:** {res['wind']['speed']} m/s")
                st.markdown(f"**🌥️ Condition:** {res['weather'][0]['description'].title()}")
        except Exception as e:
            st.error(f"Could not fetch weather: {e}")

# ---------------- Section: Itinerary ----------------
elif section == "🗓️ Itinerary":
    st.header("🗓️ Plan Your Itinerary")
    days = st.number_input("Number of Days", min_value=1, max_value=30, value=3)
    itinerary = {}
    for day in range(1, days + 1):
        with st.expander(f"Day {day} Plan"):
            morning = st.text_input(f"Day {day} - Morning", key=f"m{day}")
            afternoon = st.text_input(f"Day {day} - Afternoon", key=f"a{day}")
            evening = st.text_input(f"Day {day} - Evening", key=f"e{day}")
            itinerary[day] = {"Morning": morning, "Afternoon": afternoon, "Evening": evening}
    if st.button("Generate Itinerary Summary"):
        st.subheader("📝 Your Travel Plan")
        for day, plan in itinerary.items():
            st.markdown(f"**Day {day}**")
            for part, activity in plan.items():
                st.markdown(f"- {part}: {activity if activity else 'Not planned'}")

# ---------------- Section: Attractions ----------------
elif section == "📍Attractions":
    st.header("📍 Top Tourist Attractions")
    city = st.text_input("Enter a city to find attractions")
    if city:
        st.write(f"🌆 Top attractions in {city}:")
        st.markdown("- 🗼 **Iconic Landmarks**")
        st.markdown("- 🖼️ **Museums & Galleries**")
        st.markdown("- 🌳 **Parks & Gardens**")
        st.markdown("- 🎡 **Amusement Spots**")
        st.markdown("🧭 Tip: Connect Google Places or TripAdvisor API for live data")

if __name__ == "__main__":
    main()