import streamlit as st
from google import genai
import os
import time
from dotenv import load_dotenv
from PIL import Image

# setup & scurity
load_dotenv()
# use the latest google-genai Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# setting up the page style 
st.set_page_config(page_title="LensAI", page_icon="📸")
st.markdown("""
    <style>
    .stApp { background-color: #ADD8E6; }
    h1 { color: #FFFFFF; font-family: 'Avenir Next', sans-serif; }
    .stButton>button { background-color: #FFFFFF; color: black; border-radius: 20px; }
    /* This targets the label of the camera input specifically */
    .stCameraInput label p {
    color: black !important;
    font-weight: 600;}
    [data-testid="stImageCaption"] {
        color: black !important;
        font-weight: 600;
        justify-content: center; /* Optional: centers the text */
        display: flex;}
}
    </style>
    """, unsafe_allow_html=True)


st.markdown('<h1 style="color: black;">📸LensAI: Creative📸</h1>', unsafe_allow_html=True)

st.markdown('<h3 style="color: black;">Struggling to get the perfect photo?</h3>', unsafe_allow_html=True)

st.markdown('<p style="color: black;">Take a photo and get suggestions for lenses, captions, angles and more!</p>', unsafe_allow_html=True)

# 3. Camera Interface
img_file = st.camera_input("Ready?")

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Got it!", width='stretch') # Fixes the container width warning
    
    # 4. The "Snap" AI Logic with Retry Mechanism
    if st.button("Generate Suggestions"):
        with st.spinner("Analyzing your snap..."):
            prompt = """
            You are a professional photographer and social media influencer. Analyze this image and provide:
            1. A "Vibe Check": A one-sentence summary of the aesthetic.
            2. Suggested Lenses: 3 creative AR lens ideas (e.g., 'Vintage Grain', 'Neon Glow').
            3. Captions: 3 trendy captions for a Snap Story.
            4. Suggestions: How can I pose better? What angle should I use? 
            Keep the tone high-energy and Gen-Z focused. Don't be cringey. 
            """
            
            # Robust error handling for 429 Quota issues
            success = False
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Switched to 2.5-flash-lite for better quota stability
                    response = client.models.generate_content(
                        model='gemini-2.5-flash-lite', 
                        contents=[prompt, img]
                    )
                    st.subheader("✨ Creative Suggestions")
                    st.write(response.text)
                    success = True
                    break # Exit the loop if successful
                except Exception as e:
                    if "429" in str(e):
                        wait_time = (attempt + 1) * 5 # Exponential backoff
                        st.warning(f"Quota reached. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        st.error(f"Something went wrong: {e}")
                        break
            
            if not success:
                st.error("Still hitting limits. Try again in 60 seconds!")