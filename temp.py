import streamlit as st
import google.generativeai as genai
from PIL import Image
import sqlite3
from googletrans import Translator
from gtts import gTTS
import os
import datetime
import urllib.parse  # For encoding WhatsApp messages

# Configure API key
API_KEY = "AIzaSyCf1hLjW3bip8_GtR-7Ltkwz3yeqpGhY5M"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Translator
translator = Translator()

# ✅ Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Ensure users table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Ensure captions table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS captions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            user_prompt TEXT,
            generated_caption TEXT,
            audio_path TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ✅ Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Save uploaded image
def save_uploaded_image(image, username):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    image_path = f"uploads/{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    image.save(image_path)
    return image_path

# Save generated captions to DB
def save_caption(username, image_path, user_prompt, generated_caption, audio_path):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    user_id = get_user_id(username)
    if user_id:
        cursor.execute("""
            INSERT INTO captions (user_id, image_path, user_prompt, generated_caption, audio_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, image_path, user_prompt, generated_caption, audio_path, datetime.datetime.now()))
        conn.commit()
    conn.close()

# Fetch user history
def get_user_history(username):
    user_id = get_user_id(username)
    if user_id:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT image_path, user_prompt, generated_caption, audio_path, timestamp FROM captions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        history = cursor.fetchall()
        conn.close()
        return history
    return []

# Get user ID
def get_user_id(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

# ✅ Generate audio file
def generate_audio(text, username):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    audio_filename = f"uploads/{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(audio_filename)
    return audio_filename

# User Authentication
def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# ✅ Navigation Bar
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Home", "History", "Logout"])

# ✅ Logout functionality
if page == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

# ✅ User Login/Signup
if not st.session_state.logged_in:
    st.title("🔑 Welcome to ProVision AI")
    st.write("ProVision AI generates smart captions for images using AI.")
    option = st.radio("Select an option:", ["Login", "Signup"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if option == "Login":
        if st.button("Login", use_container_width=True):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password!")
    elif option == "Signup":
        if st.button("Signup", use_container_width=True):
            if register_user(username, password):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists. Try a different one.")
    st.stop()

# ✅ Home Page (Image Upload & Captioning)
if page == "Home":
    st.title("📸 ProVision AI - Image Captioning with Audio & WhatsApp Share")
    uploaded_file = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"])
    user_prompt = st.text_area("Enter your prompt:")

    if uploaded_file and st.button("Generate Response"):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        image_path = save_uploaded_image(image, st.session_state.username)

        # Generate AI response
        response = model.generate_content([{"mime_type": "image/png", "data": open(image_path, "rb").read()}, user_prompt])
        translated_text = translator.translate(response.text, dest="en").text

        st.subheader("📝 Generated Response:")
        st.write(translated_text)

        # ✅ Generate and display audio
        audio_path = generate_audio(translated_text, st.session_state.username)
        st.audio(audio_path, format="audio/mp3")

        # ✅ Share on WhatsApp Feature
        encoded_message = urllib.parse.quote(f"Check this AI-generated caption: {translated_text}")
        whatsapp_link = f"https://api.whatsapp.com/send?text={encoded_message}"
        st.markdown(f"[📲 Share on WhatsApp]({whatsapp_link})", unsafe_allow_html=True)

        # Save caption to database
        save_caption(st.session_state.username, image_path, user_prompt, translated_text, audio_path)

# ✅ History Page (Past Captions & Audio)
elif page == "History":
    st.title("📜 Caption History")
    history = get_user_history(st.session_state.username)
    for entry in history:
        with st.expander(f"🕒 {entry[4]} - {entry[1]}"):
            st.image(entry[0], caption="Uploaded Image", use_column_width=True)
            st.write(f"Prompt: {entry[1]}")
            st.write(f"Generated Caption: {entry[2]}")
            if entry[3]:  # Play audio if available
                st.audio(entry[3], format="audio/mp3")