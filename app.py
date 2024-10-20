import io
import base64
import streamlit as st
import os
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
import json
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import time

# Set page configuration
st.set_page_config(
    page_title="TeleGuide | AI Telecom Assistant",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load Lottie animations
def load_lottie(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Apply custom CSS for styling and animations
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .css-1r6slb0 {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3D59;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-in;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(45deg, #2193b0, #6dd5ed);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px;
        background-color: white;
    }
    .css-1d391kg {
        background: linear-gradient(180deg, #1E3D59 0%, #2193b0 100%);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 1s ease-in;
    }
    .success-message {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with Hugging Face secrets for API key
@st.cache_resource
def get_openai_client():
    try:
        # Fetch the API key from Hugging Face secrets
        api_key = st.secrets["api_key"]
        return OpenAI(api_key=api_key, base_url="https://api.together.xyz")
    except Exception as e:
        st.error(f"Error initializing API client: {str(e)}")
        return None

client = get_openai_client()

# Load animations
lottie_telecom = load_lottie("https://assets4.lottiefiles.com/packages/lf20_qz3tpn4w.json")
lottie_analysis = load_lottie("https://assets4.lottiefiles.com/packages/lf20_xh83pj1k.json")

# Process text query function
def process_text_query(query, model="meta-llama/Llama-3.2-3B-Instruct-Turbo"):
    try:
        with st.spinner("Processing your query..."):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are TeleGuide, an expert AI assistant specialized in telecommunication tasks. Provide detailed, practical, and accurate information."},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None

# Process image query function
def process_image_query(image_base64, query, model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"):
    try:
        with st.spinner("Analyzing image..."):
            system_message = "You are TeleGuide, an expert AI assistant in telecommunications infrastructure analysis."
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None

# Convert image to base64
def image_to_base64(image):
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        st.error(f"Error converting image: {str(e)}")
        return None

# Sidebar content
with st.sidebar:
    st.title("🛰️ TeleGuide")
    st_lottie(lottie_telecom, height=200)
    st.markdown("---")
    st.info("Your AI-powered telecommunication assistant, providing expert analysis and insights.")
    st.markdown("### Features")
    st.markdown("""
    - 📝 Text Analysis
    - 📄 Document Processing
    - 🖼️ Image Analysis
    - 📡 Infrastructure Planning
    """)
    st.markdown("---")
    st.markdown("#### Powered by Advanced AI")
    st.caption("Using Llama 3.2 Models")

# Main content
st.markdown('<h1 class="main-header">Welcome to TeleGuide</h1>', unsafe_allow_html=True)

# Navigation menu
selected = option_menu(
    menu_title=None,
    options=["Text Analysis", "Document Processing", "Image Analysis"],
    icons=["chat-dots", "file-text", "image"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "#1E3D59", "font-size": "25px"},
        "nav-link": {
            "font-size": "20px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#eee",
        },
        "nav-link-selected": {"background-color": "#2193b0", "color": "white"},
    }
)

# Handle different options from the navigation menu
if selected == "Text Analysis":
    st.markdown("### 💬 Text Analysis")
    st_lottie(lottie_analysis, height=200)
    
    query = st.text_area("Enter your telecommunications query:", height=100)
    if st.button("Process Query", key="text_query"):
        if query:
            response = process_text_query(query)
            if response:
                st.markdown('<div class="success-message">✅ Query processed successfully!</div>', unsafe_allow_html=True)
                st.markdown("### Response:")
                st.write(response)
        else:
            st.warning("Please enter a query.")

elif selected == "Document Processing":
    st.markdown("### 📄 Document Analysis")
    document_type = st.selectbox(
        "Select Document Type",
        ["Regulatory Document", "Technical Specification", "Network Planning", "Customer Inquiry"]
    )
    
    text_input = st.text_area("Enter document text:", height=150)
    if st.button("Analyze Document"):
        if text_input:
            response = process_text_query(f"Analyze the following {document_type}: {text_input}")
            if response:
                st.markdown('<div class="success-message">✅ Document analyzed successfully!</div>', unsafe_allow_html=True)
                st.markdown("### Response:")
                st.write(response)
        else:
            st.warning("Please enter some text to analyze.")

elif selected == "Image Analysis":
    st.markdown("### 🖼️ Image Analysis")
    image_file = st.file_uploader("Upload an image for analysis", type=["jpg", "jpeg", "png"])
    
    if image_file:
        image = Image.open(image_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        query = st.text_input("Enter your query about this image:")
        
        if st.button("Analyze Image"):
            image_base64 = image_to_base64(image)
            if image_base64 and query:
                response = process_image_query(image_base64, query)
                if response:
                    st.markdown('<div class="success-message">✅ Image analyzed successfully!</div>', unsafe_allow_html=True)
                    st.markdown("### Response:")
                    st.write(response)
            else:
                st.warning("Please upload an image and enter a query.")

# Footer
st.markdown("---")
st.caption("🚀 Powered by OpenAI | Streamlit | Llama Models")

