import streamlit as st
from google import genai
import os
import time
from dotenv import load_dotenv
from PIL import Image

# 1. SETUP & SECURITY
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use the more stable 2.5-flash model for 2026 free tier
STABLE_MODEL = "gemini-2.5-flash" 

# 2. PAGE STYLE (Light Blue & White)
st.set_page_config(page_title="LensAI", page_icon="📸")
st.markdown("""
    <style>
    .stApp { background-color: #ADD8E6; }
    h1, h3, p { color: black !important; font-family: 'Avenir Next', sans-serif; }
    .stButton>button { background-color: #FFFFFF; color: black; border-radius: 20px; width: 100%; font-weight: bold; }
    .stCameraInput label p { color: black !important; font-weight: 600; }
    [data-testid="stImageCaption"] { color: black !important; font-weight: 600; justify-content: center; display: flex; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1>📸 LensAI: Creative 📸</h1>', unsafe_allow_html=True)
st.markdown('<h3>Struggling to get the perfect photo?</h3>', unsafe_allow_html=True)
st.markdown('<p>Take a photo and get suggestions for lenses, captions, angles and more!</p>', unsafe_allow_html=True)

# 3. DUAL INPUT INTERFACE
st.markdown('<p style="font-weight: 600;">Upload or Take a Photo!</p>', unsafe_allow_html=True)
input_type = st.radio("Choose source:", ["Camera", "Upload File"], horizontal=True)

img_file = None
if input_type == "Camera":
    img_file = st.camera_input("Ready?")
else:
    img_file = st.file_uploader("Choose an image from your files...", type=["jpg", "jpeg", "png"])

# 4. MAIN LOGIC
if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Got it!", use_container_width=True)
    
    if st.button("Generate Suggestions"):
        # Initial Cooldown to prevent rapid double-clicks
        time.sleep(1) 
        
        with st.spinner("Analyzing your photo..."):
            prompt = """
            You are a professional photographer and social media influencer. Analyze this image and provide:
            1. A "Vibe Check": A one-sentence summary of the aesthetic.
            2. Captions: 3 captions for a post. Make them nonchalant, but creative. Don't make it cringey.
            3. Suggestions: How can I pose better? What angle should I use? Is the background good?
            Keep the tone high-energy and Gen-Z focused.
            Make the captions good like you see other people make them.
            """
            
            # --- START OF EXPONENTIAL BACKOFF LOGIC ---
            success = False
            max_retries = 3
            initial_wait = 5 # seconds
            
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=STABLE_MODEL, 
                        contents=[prompt, img]
                    )
                    st.subheader("✨ Creative Suggestions")
                    st.write(response.text)
                    success = True
                    break # Exit loop on success
                    
                except Exception as e:
                    if "429" in str(e):
                        # Exponentially increase wait time: 5s, 10s, 20s
                        wait_time = initial_wait * (2 ** attempt) 
                        st.warning(f"Quota reached. Re-trying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        st.error(f"Something went wrong: {e}")
                        break
            
            if not success:
                st.error("Still hitting limits. Google's Free Tier is very busy right now. Try again in 60 seconds!")