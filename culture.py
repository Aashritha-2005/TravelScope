import streamlit as st
import requests

# App Title
st.title("Cultural Insights App")

# Input: Destination
st.header("Explore the Culture of Your Destination")
destination = st.text_input("Enter a place:", placeholder="e.g., Paris, Tokyo, New Delhi")

if destination:
    # Fetch data from Wikipedia API
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{destination}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Display cultural insights
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

# Footer
st.markdown("---")
st.caption("Powered by Wikipedia API")
