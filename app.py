import streamlit as st
from google import genai
import os
import time
from dotenv import load_dotenv
from PIL import Image

# 1. SETUP & SECURITY
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. PAGE STYLE
st.set_page_config(page_title="LensAI", page_icon="📸")
st.markdown("""
    <style>
    .stApp { background-color: #ADD8E6; }
    h1, h3, p { color: black !important; font-family: 'Avenir Next', sans-serif; }
    .stButton>button { background-color: #FFFFFF; color: black; border-radius: 20px; width: 100%; }
    .stCameraInput label p { color: black !important; font-weight: 600; }
    [data-testid="stImageCaption"] { color: black !important; font-weight: 600; justify-content: center; display: flex; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIALIZE SESSION STATE (Crucial for persistence)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# UI Headers
st.markdown('<h1>📸 LensAI: Creative</h1>', unsafe_allow_html=True)
st.markdown('<h3>Struggling to get the perfect photo?</h3>', unsafe_allow_html=True)
st.markdown('<p>Take a photo and get suggestions for lenses, captions, angles and more!</p>', unsafe_allow_html=True)

# 4. DUAL INPUT INTERFACE
input_type = st.radio("Choose source:", ["Camera", "Upload File"], horizontal=True)
img_file = None

if input_type == "Camera":
    img_file = st.camera_input("Ready?")
else:
    img_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# 5. MAIN LOGIC
if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Got it!", use_container_width=True)
    
    # Generate Suggestions Button
    if st.button("✨ Generate Suggestions"):
        with st.spinner("Analyzing your photo..."):
            prompt = """
            You are a professional photographer and social media influencer. Analyze this image and provide:
            1. A 'Vibe Check': A one-sentence summary of the aesthetic.
            2. Captions: 3 captions for a post. Make them nonchalant, but creative. 
            3. Suggestions: How can I pose better? What angle should I use? Is the background good?
            Tone: High-energy, Gen-Z focused.
            """
            
            try:
                # Use gemini-1.5-flash-lite for better free-tier stability
                response = client.models.generate_content(
                    model='gemini-1.5-flash-lite', 
                    contents=[prompt, img]
                )
                
                # Save result to state so it stays on screen during chat
                st.session_state.initial_analysis = response.text
                st.session_state.analysis_done = True
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                if "429" in str(e):
                    st.error("🚨 Quota Limit Hit! Google's free tier is busy. Try again in 30s.")
                else:
                    st.error(f"Error: {e}")

    # 6. CHAT INTERFACE (Displays only after analysis)
    if st.session_state.analysis_done:
        st.divider()
        st.subheader("✨ Creative Suggestions")
        st.write(st.session_state.initial_analysis)
        
        st.markdown("### 💬 Ask follow-up questions")
        
        # Display existing chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # New user chat input
        if user_query := st.chat_input("Ask about angles, lighting, or more captions..."):
            # Add user message to state
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            # Generate and display AI response
            with st.chat_message("assistant"):
                try:
                    # Pass the image + history + new prompt
                    chat_response = client.models.generate_content(
                        model='gemini-1.5-flash-lite',
                        contents=[f"Based on the photo analysis provided earlier, answer this: {user_query}", img]
                    )
                    st.markdown(chat_response.text)
                    st.session_state.messages.append({"role": "assistant", "content": chat_response.text})
                except Exception as e:
                    st.error(f"Chat Error: {e}")