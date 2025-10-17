import streamlit as st
import overpy
from geopy.geocoders import Nominatim
import random
import datetime

# ──────────────────────────────────────────────────────────────
# App configuration
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dynamic Trip Planner", layout="wide")
st.title("🌍 Dynamic Trip Itinerary Generator")

geolocator = Nominatim(user_agent="trip_planner_app")
api = overpy.Overpass()

# ──────────────────────────────────────────────────────────────
# 1.  Geocode city → (lat, lon)
# ──────────────────────────────────────────────────────────────
def geocode_city(city: str):
    loc = geolocator.geocode(city)
    return (loc.latitude, loc.longitude) if loc else (None, None)

# ──────────────────────────────────────────────────────────────
# 2.  Fetch attractions: famous first, then nearby fallback
# ──────────────────────────────────────────────────────────────
def fetch_attractions(lat: float, lon: float,
                      radius_famous: int = 10000,
                      radius_fallback: int = 8000) -> list[dict]:
    """Return a de-duplicated list of attraction dicts with keys:
       {name, lat, lon}. Famous first; if not enough, add nearby ones."""
    places, seen = [], set()

    # ---------- (a) famous ----------
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

    # ---------- (b) nearby fallback if < 10 famous ----------
    # (You can tweak the threshold.)
    if len(places) < 10:
        near_q = f"""
        node["tourism"~"attraction|museum|viewpoint|artwork|zoo|theme_park"]
        (around:{radius_fallback},{lat},{lon})["name"];
        out body;
        """
        places += _run_overpass_query(near_q, seen)

    return places

def _run_overpass_query(query: str, seen: set) -> list[dict]:
    """Helper that executes query, filters dups, returns list."""
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

# ──────────────────────────────────────────────────────────────
# 3.  Build itinerary (2–5 per day, all days filled)
# ──────────────────────────────────────────────────────────────
def build_itinerary(places: list[dict], days: int) -> dict:
    if not places:
        return {}

    random.shuffle(places)
    min_pd, max_pd = 2, 5
    total = len(places)

    # shrink day count if places are very few
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

# ──────────────────────────────────────────────────────────────
# 4.  Sidebar inputs
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    city = st.text_input("📍 Enter city", "Paris")
    num_days = st.number_input("🗓️ Number of days", 1, 10, 3)
    if st.button("Generate Itinerary"):
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

# ──────────────────────────────────────────────────────────────
# 5.  Show itinerary
# ──────────────────────────────────────────────────────────────
itinerary = st.session_state.get("itinerary")
if itinerary:
    st.header(f"🧳 Trip Itinerary for {st.session_state['city']}")
    for day, items in itinerary.items():
        with st.expander(day, expanded=True):
            for item in items:
                st.markdown(f"🕘 **{item['time']}** — {item['place']}")
else:
    st.info("Enter a city and click **Generate Itinerary**.")