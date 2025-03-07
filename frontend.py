import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure API Key
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Streamlit UI ---
st.set_page_config(page_title="📸 ProVision AI", page_icon="📷", layout="wide")

# Sidebar
with st.sidebar:
    st.title("📸 ProVision AI")
    st.write("AI-Powered Image Captioning")
    
    # Upload Image
    uploaded_file = st.file_uploader("📂 Upload an image", type=["png", "jpg", "jpeg"])

    # Caption Style Selection
    caption_style = st.radio("🎨 Select Caption Style:", 
                             ["Formal", "Funny", "Detailed", "Poetic"])

    # Generate Button
    generate_button = st.button("🚀 Generate Caption", use_container_width=True)

# Main Section
st.markdown("<h1 style='text-align: center;'>✨ AI-Powered Image Captioning ✨</h1>", unsafe_allow_html=True)

# Display Image
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼 Uploaded Image", use_column_width=True)

# Generate Caption
if uploaded_file and generate_button:
    with st.spinner("✨ Generating Caption..."):
        # Convert image to bytes
        image_data = io.BytesIO()
        image.save(image_data, format=image.format)
        image_bytes = image_data.getvalue()
        
        # Define prompt
        prompt_map = {
            "Formal": "Provide a clear and professional caption for this image.",
            "Funny": "Make a humorous caption for this image.",
            "Detailed": "Describe this image in detail, including objects, text, and context.",
            "Poetic": "Write a poetic description of this image."
        }
        
        # AI Response
        response = model.generate_content([
            {"mime_type": "image/png", "data": image_bytes},
            prompt_map[caption_style]
        ])
    
    # Display Caption
    st.success("✅ Caption Generated!")
    st.subheader("📝 Your Caption:")
    st.write(f"**{response.text}**")

# Footer
st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Made with ❤️ by Team ProVision AI</p>", unsafe_allow_html=True)

