from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import torch

from config import BLIP_MODEL_ID

# Load BLIP model
processor = BlipProcessor.from_pretrained(BLIP_MODEL_ID)
blip_model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL_ID)

def load_image(image_file):
    """Load image from file and convert to PIL Image."""
    image = Image.open(image_file).convert("RGB")
    return image

def image_to_bytes(image):
    """Convert image to byte format for API processing."""
    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    return image_data.getvalue()

def generate_blip_caption(image):
    """Generate image caption using BLIP model."""
    inputs = processor(image, return_tensors="pt")
    caption_ids = blip_model.generate(**inputs)
    return processor.batch_decode(caption_ids, skip_special_tokens=True)[0]
