import streamlit as st
from google import genai
import os
import time
from dotenv import load_dotenv
from PIL import Image

# setup & security
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# setting up the page style 
st.set_page_config(page_title="LensAI", page_icon="📸")
st.markdown("""
    <style>
    .stApp { background-color: #ADD8E6; }
    h1 { color: #000000; font-family: 'Avenir Next', sans-serif; }
    .stButton>button { background-color: #FFFFFF; color: black; border-radius: 20px; }
    .stCameraInput label p { color: black !important; font-weight: 600;}
    [data-testid="stImageCaption"] { color: black !important; font-weight: 600; justify-content: center; display: flex;}
    </style>
    """, unsafe_allow_html=True)

# Helper function for the chat
def generate_chat_response(user_input, history, original_img):
    # This combines the history and the original image so Gemini stays in context
    messages = [{"role": "user", "parts": [user_input, original_img]}]
    response = client.models.generate_content(
        model='gemini-2.0-flash-lite', 
        contents=history + [user_input, original_img]
    )
    return response.text

st.markdown('<h1 style="color: black;">📸LensAI: Creative📸</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="color: black;">Struggling to get the perfect photo?</h3>', unsafe_allow_html=True)
st.markdown('<p style="color: black;">Take a photo and get suggestions for lenses, captions, angles and more!</p>', unsafe_allow_html=True)

input_type = st.radio("Choose source:", ["Camera", "Upload File"], horizontal=True)

img_file = None
if input_type == "Camera":
    img_file = st.camera_input("Ready?")
else:
    img_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Initialize session state for chat and results
if "messages" not in st.session_state:
    st.session_state.messages = []
if "initial_analysis" not in st.session_state:
    st.session_state.initial_analysis = None

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Got it!", use_container_width=True)
    
    # 1. INITIAL ANALYSIS BUTTON
    if st.button("Generate Suggestions"):
        with st.spinner("Analyzing your photo..."):
            system_prompt = """
            You are a professional photographer and social media influencer. Analyze this image and provide:
            1. A "Vibe Check": A one-sentence summary of the aesthetic.
            2. Captions: 3 captions for a post. Make them nonchalant, but creative. 
            3. Suggestions: How can I pose better? What angle should I use? Is the background good?
            Keep the tone high-energy and Gen-Z focused.
            """
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash-lite', 
                    contents=[system_prompt, img]
                )
                st.session_state.initial_analysis = response.text
                # Add to history so the chat knows what was already said
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

    # Display initial results if they exist
    if st.session_state.initial_analysis:
        st.subheader("✨ Creative Suggestions")
        st.write(st.session_state.initial_analysis)
        
        st.divider()
        st.markdown("### 💬 Chat with your Assistant")

        # 2. CHAT INTERFACE (Lives outside the button)
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if chat_input := st.chat_input("Ask a follow-up question..."):
            # Add user message to state and display
            st.session_state.messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            # Generate AI response
            with st.chat_message("assistant"):
                # We pass the image every time in the background so it can "see" what you're talking about
                ai_response = generate_chat_response(chat_input, [], img)
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})