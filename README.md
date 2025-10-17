# 🌍 Smart Travel Scope with Translation

**Smart Travel Scope** is an intelligent AI-powered travel planning and translation companion that helps users create personalized itineraries, calculate expenses, explore local culture, and translate text or speech on the go — all in one elegant interface.

---

## 🧭 Features

### 🗓️ 1. Personalized Itinerary Planner
- Enter your **destination**, **travel dates**, and **interests** (Adventure, Culture, Food, Nature, Shopping, Relaxation).
- Generates a **day-by-day personalized travel plan** using AI suggestions for attractions, dining, and local experiences.
- Smart scheduling ensures optimal use of your travel days.

### 💬 2. Live Translator (Text + Audio)
- Translate text instantly between multiple languages.
- Speak directly into your mic for **real-time voice translation**.
- Output displayed in translated text.
- Supports **PDF Translation** for travel guides, menus, or brochures.

### 🌦️ 3. Live Weather Integration
- Displays current weather and forecast for your travel destination.
- Helps plan your activities and packing.

### 💰 4. Travel Expense Calculator
- Estimate trip expenses based on destination, accommodation type, food, and local transport.
- Helps you plan your budget efficiently.

### 🏛️ 5. Cultural Insights
- Provides **local customs, festivals, greetings, and do’s & don’ts** for better cultural immersion.

### 🧾 6. PDF and Document Translation
- Upload PDFs (like itineraries or menus) and get translations instantly.
- Supports up to 200MB per file.

### 🧠 7. AI + Translation Integration
- Combines **AI itinerary generation** with **live translation** — a true travel companion for international explorers.

---

## 📁 Project Structure

```
TravelScope/
│
├── culture.py                 # Cultural information module
├── expenses_calculator.py     # Budget estimation logic
├── itinerary.py               # Personalized itinerary generation
├── scopee_requirements.txt    # List of dependencies
├── trail_travel.py            # Travel trail planner
├── translator_app.py          # Live translation + PDF translator
├── travel_plan.py             # Core travel planner logic
├── travel_scopee.py           # Main Streamlit app entry point
├── travel_scopee 2.py         # Backup / alternative version
├── weather.py                 # Weather API integration
└── README.md                  # Documentation (this file)
```

---

## 🖼️ Preview

### 🧩 Itinerary Planner
![Itinerary Screenshot](https://github.com/Aashritha-2005/TravelScope/assets/preview-itinerary.png)

### 🌐 Live Translator
![Translator Screenshot](https://github.com/Aashritha-2005/TravelScope/assets/preview-translator.png)

*(Replace the above URLs with your uploaded image links — or use your screenshots.)*

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Aashritha-2005/TravelScope.git
cd TravelScope
```

### 2. Create Virtual Environment (optional)
```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies
```bash
pip install -r scopee_requirements.txt
```

### 4. Run the App
```bash
streamlit run travel_scopee.py
```

---

## 🔑 APIs Used
- **OpenWeatherMap API** – for real-time weather data  
- **Google Translate / Hugging Face Translation API** – for live language translation  
- **TripAdvisor / Wikivoyage (optional)** – for travel attractions and cultural data  

---

## 🌐 Tech Stack
- **Frontend/UI**: Streamlit  
- **Backend**: Python  
- **APIs**: Google Translate, OpenWeatherMap  
- **AI/ML**: Hugging Face translation and text generation  
- **Libraries**:  
  - `streamlit`  
  - `requests`  
  - `googletrans` or `transformers`  
  - `PyPDF2` (for PDF reading)  
  - `datetime`, `json`, `os`  

---

## 🚀 Future Enhancements
- 🌎 Multi-language voice synthesis (text-to-speech)
- 🧭 AR-based local attraction mapping
- 💸 Integration with live currency converter
- 📍 Geo-aware restaurant and event recommendations
- 📱 Mobile-friendly PWA version

---

## 👩‍💻 Author
**Aashritha Lakshmi Mallampati**  
Computer Science Student | AI & Python Developer  

💼 [GitHub](https://github.com/Aashritha-2005)  
📧 Contact: *[Add your email if you want]*  
