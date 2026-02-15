import streamlit as st
from google import genai
import os
import time
from dotenv import load_dotenv
from PIL import Image

# 1. SETUP
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use the latest stable lite model for 2026
MODEL_NAME = "gemini-2.0-flash-lite" 

# 2. PAGE STYLE
st.set_page_config(page_title="LensAI", page_icon="📸")
st.markdown("""
    <style>
    .stApp { background-color: #ADD8E6; }
    h1, h3, p { color: black !important; font-family: 'Avenir Next', sans-serif; }
    .stButton>button { background-color: #FFFFFF; color: black; border-radius: 20px; width: 100%; }
    .stCameraInput label p { color: black !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "initial_analysis" not in st.session_state:
    st.session_state.initial_analysis = None

st.markdown('<h1>📸 LensAI: Creative</h1>', unsafe_allow_html=True)

# 4. IMAGE INPUT
input_type = st.radio("Choose source:", ["Camera", "Upload File"], horizontal=True)
img_file = st.camera_input("Ready?") if input_type == "Camera" else st.file_uploader("Upload", type=["jpg", "png"])

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Got it!", use_container_width=True)
    
    if st.button("✨ Generate Suggestions"):
        with st.spinner("Analyzing..."):
            prompt = "You are a Gen-Z professional photographer. Give me a vibe check, 3 nonchalant captions, and posing tips for this photo."
            try:
                # Updated to use the 2.0 stable model
                response = client.models.generate_content(model=MODEL_NAME, contents=[prompt, img])
                st.session_state.initial_analysis = response.text
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"API Error: {e}")

    # 5. PERSISTENT DISPLAY & CHAT
    if st.session_state.initial_analysis:
        st.subheader("✨ Creative Suggestions")
        st.write(st.session_state.initial_analysis)
        
        st.divider()
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_query := st.chat_input("Ask a follow-up..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                try:
                    # History-aware response
                    chat_response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=[f"Context: {st.session_state.initial_analysis}\n\nUser Question: {user_query}", img]
                    )
                    st.markdown(chat_response.text)
                    st.session_state.messages.append({"role": "assistant", "content": chat_response.text})
                except Exception as e:
                    st.error(f"Chat Error: {e}")