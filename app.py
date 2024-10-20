import io
import base64
import streamlit as st
import os
from groq import Groq
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="TeleGuide | AI Telecom Assistant",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for styling
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

# Initialize GROQ client with API key from secrets
@st.cache_resource
def get_groq_client():
    try:
        # Fetch the API key from secrets
        api_key = st.secrets["GROQ_API_KEY"]
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing GROQ client: {str(e)}")
        return None

client = get_groq_client()

# Function to process text query with LLaMA
def process_text_query(query, model="llama-3.2-90b-vision-preview"):
    try:
        with st.spinner("Processing your query..."):
            response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": query}
                ],
                model=model,
            )
            return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None

# Function to extract text from image using LLaVA
def extract_text_from_image(image_base64):
    try:
        with st.spinner("Extracting text from image..."):
            response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"Extract text from the following image data: {image_base64}"}
                ],
                model="llava-v1.5-7b-4096-preview",  # Use LLaVA model ID
            )
            return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error extracting text from image: {str(e)}")
        return None

# Function to process image query using LLaMA after extracting text from the image
def process_image_query(image_base64, query, model="llama-3.2-90b-vision-preview"):
    try:
        extracted_text = extract_text_from_image(image_base64)  # Extract text from image first
        if extracted_text:
            full_query = f"{query}. The extracted text from the image is: {extracted_text}"
            with st.spinner("Processing your image query..."):
                response = client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": full_query}
                    ],
                    model=model,
                )
                return response.choices[0].message.content
        else:
            st.error("No text extracted from the image.")
            return None
    except Exception as e:
        st.error(f"Error processing image query: {str(e)}")
        return None

# Convert image to base64 format
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
    st.caption("Using GROQ Models")

# Main content
st.markdown('<h1 class="main-header">Welcome to TeleGuide</h1>', unsafe_allow_html=True)

# Navigation menu
selected = st.selectbox(
    "Choose Analysis Type:",
    options=["Text Analysis", "Document Processing", "Image Analysis"]
)

# Handle different options from the navigation menu
if selected == "Text Analysis":
    st.markdown("### 💬 Text Analysis")
    
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
st.caption("🚀 Powered by GROQ | Streamlit | LLaVA and LLaMA Models")
