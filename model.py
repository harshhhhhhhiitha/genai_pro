import google.generativeai as genai
from utils import image_to_bytes

# Load Google Generative AI Model
g_model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_image(image):
    """Analyze image using Google Gemini Vision Pro."""
    image_bytes = image_to_bytes(image)

    response_description = g_model.generate_content([
        {"mime_type": "image/png", "data": image_bytes},
        "Describe this image in detail. Identify objects, text, and context."
    ])

    response_objects = g_model.generate_content([
        {"mime_type": "image/png", "data": image_bytes},
        "List all objects visible in this image."
    ])

    response_text = g_model.generate_content([
        {"mime_type": "image/png", "data": image_bytes},
        "Extract all visible text from this image."
    ])

    return {
        "description": response_description.text,
        "objects": response_objects.text,
        "text": response_text.text
    }

def merge_results(blip_caption, analysis_results):
    """Merge BLIP and Gemini descriptions into a refined caption."""
    final_prompt = f"""
    Merge these descriptions into a single improved caption:
    1️⃣ BLIP Caption: "{blip_caption}"
    2️⃣ Google Vision Description: "{analysis_results['description']}"
    3️⃣ Objects Detected: "{analysis_results['objects']}"
    4️⃣ Text Extracted (if any): "{analysis_results['text']}"
    Create a natural, detailed, and well-structured description.
    """

    merged_response = g_model.generate_content(final_prompt)
    return merged_response.text
