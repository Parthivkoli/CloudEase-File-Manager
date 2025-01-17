import streamlit as st
import os
import sqlite3
import base64
import qrcode
from io import BytesIO

# Constants
UPLOAD_DIR = "uploads"
DB_FILE = "file_manager.db"

# Create necessary directories and database
os.makedirs(UPLOAD_DIR, exist_ok=True)
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    path TEXT
)
""")
conn.commit()

# Authentication
def authenticate(username, password):
    return username == "admin" and password == "password"

# Streamlit App
st.title("Enhanced Cloud-based File Management System")
st.write("Securely upload, categorize, search, and share files.")

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password.")
    st.stop()

# File categorization function
def categorize_file(file_name):
    if file_name.endswith((".png", ".jpg", ".jpeg")):
        return "Images"
    elif file_name.endswith((".txt", ".pdf", ".csv", ".docx")):
        return "Documents"
    else:
        return "Others"

# File upload
uploaded_file = st.file_uploader("Choose a file to upload")
if uploaded_file:
    file_name = uploaded_file.name
    category = categorize_file(file_name)
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    c.execute("INSERT INTO files (name, category, path) VALUES (?, ?, ?)", (file_name, category, file_path))
    conn.commit()
    st.success(f"File '{file_name}' uploaded and categorized as '{category}'.")

# Search files
st.header("Search Files")
search_query = st.text_input("Search for a file by name")
if search_query:
    c.execute("SELECT * FROM files WHERE name LIKE ?", (f"%{search_query}%",))
    results = c.fetchall()
    if results:
        st.write("Search Results:")
        for result in results:
            st.write(f"- {result[1]} ({result[2]})")
    else:
        st.write("No files found.")

# File categories
st.header("File Categories")
categories = ["Images", "Documents", "Others"]
for category in categories:
    st.subheader(category)
    c.execute("SELECT * FROM files WHERE category = ?", (category,))
    files = c.fetchall()
    if files:
        for file in files:
            file_name = file[1]
            file_path = file[3]
            st.write(f"- {file_name}")
            
            # Provide download button
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            st.download_button(
                label="Download",
                data=file_bytes,
                file_name=file_name,
                mime="application/octet-stream"
            )
            
            # Generate QR code and link
            file_url = f"http://localhost:8501/{file_name}"  # Replace with hosted URL
            qr = qrcode.QRCode()
            qr.add_data(file_url)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            st.image(buffer.getvalue(), caption="QR Code")
            st.write(f"[Download Link]({file_url})")
    else:
        st.write("No files in this category.")

# Manage files
st.header("Manage Files")
if st.button("Delete All Files"):
    c.execute("DELETE FROM files")
    conn.commit()
    for file in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, file))
    st.success("All files deleted successfully.")
