import streamlit as st
import requests

# Set up the page title and layout
st.set_page_config(page_title="📍 Nearby Explorer", layout="wide")
st.title("📍 Nearby Explorer")
st.write("This app lets you find places to visit near a city of your choice using OpenStreetMap APIs.")

@st.cache_data
def geocode_location(city_name):
    """
    Geocode a city name to get its latitude, longitude, and display name using OpenStreetMap's Nominatim API.
    """
    geocode_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name, 
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "NearbyExplorerApp/1.0"
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
    """
    Find nearby places based on latitude, longitude, and category using OpenStreetMap's Overpass API.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node(around:5000,{lat},{lon})["{category}"];
    out;
    """
    headers = {
        "User-Agent": "NearbyExplorerApp/1.0"
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

# User input for city name
city_name = st.text_input("Enter the name of a city to explore nearby places:")

if city_name:
    lat, lon, display_name = geocode_location(city_name)
    if lat and lon:
        st.success(f"City found: {display_name} ({lat}, {lon})")

        # Dropdown for selecting a category of places
        category = st.selectbox(
            "Choose a category to explore:",
            ["tourism", "amenity", "shop", "leisure", "natural"]
        )

        # Fetch nearby places
        nearby_places = find_nearby_places(lat, lon, category)

        # Display nearby places
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
