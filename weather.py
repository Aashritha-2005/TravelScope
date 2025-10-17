import streamlit as st
import requests

st.set_page_config(page_title="🌦️ Accurate Weather Explorer", layout="centered")
st.title("🌦️ Accurate Weather Explorer")
st.write("Enter a city name to get the current real-time weather conditions, including humidity, air pressure, and UV index.")

@st.cache_data
def fetch_coordinates(city_name):
    """Get latitude and longitude for the given city name."""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
    response = requests.get(geo_url)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]["latitude"], results[0]["longitude"], results[0]["name"]
    return None, None, None

@st.cache_data
def fetch_weather_and_details(lat, lon):
    """Fetch both current weather and hourly details."""
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m,pressure_msl,uv_index"
    )
    response = requests.get(weather_url)
    if response.status_code == 200:
        return response.json()
    return None

# User inputs city name
city_name = st.text_input("Enter a city name:")

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

            # Extracting the latest hourly metrics
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
