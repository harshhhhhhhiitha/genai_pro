import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure API key
API_KEY = "AIzaSyCf1hLjW3bip8_GtR-7Ltkwz3yeqpGhY5M"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit UI
st.title("📸 ProVision AI - Image Captioning")
st.write("Upload an image and choose how you want the caption to be!")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

caption_style = st.selectbox("Select caption style:",
                             ["Formal", "Funny", "Detailed", "Poetic"])

generate_button = st.button("Generate Caption")

if uploaded_file and generate_button:
    # Open image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Convert image to bytes
    image_data = io.BytesIO()
    image.save(image_data, format=image.format)
    image_bytes = image_data.getvalue()
    
    # Generate Caption based on style
    prompt_map = {
        "Formal": "Provide a clear and professional caption for this image.",
        "Funny": "Make a humorous caption for this image.",
        "Detailed": "Describe this image in detail, including objects, text, and context.",
        "Poetic": "Write a poetic description of this image."
    }
    
    response = model.generate_content([
        {"mime_type": "image/png", "data": image_bytes},
        prompt_map[caption_style]
    ])
    
    st.subheader("📝 Generated Caption:")
    st.write(response.text)
