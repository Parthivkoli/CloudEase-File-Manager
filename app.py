import streamlit as st
import os
import sqlite3
from PIL import Image

# Create or connect to SQLite database
def init_db():
    try:
        conn = sqlite3.connect('file_manager.db')
        c = conn.cursor()

        # Drop the table if it already exists to prevent schema mismatch
        c.execute("DROP TABLE IF EXISTS files")

        # Create table for storing file metadata
        c.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                category TEXT,
                file_path TEXT
            )
        ''')
        return conn, c
    except sqlite3.OperationalError as e:
        st.error(f"Error initializing database: {e}")
        return None, None

# Initialize the database connection and cursor
conn, c = init_db()
if conn is None:
    st.stop()

# Function to categorize files based on file extensions
def categorize_file(file_name):
    if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return 'Images'
    elif file_name.endswith(('.pdf', '.docx', '.txt', '.pptx')):
        return 'Documents'
    else:
        return 'Others'

# Function to handle file upload
def handle_file_upload(uploaded_file):
    try:
        # Ensure the 'uploads' directory exists
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        category = categorize_file(uploaded_file.name)
        file_path = os.path.join("uploads", uploaded_file.name)
        
        # Save the uploaded file to the "uploads" folder
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Insert file metadata into SQLite database
        c.execute("INSERT INTO files (filename, category, file_path) VALUES (?, ?, ?)",
                  (uploaded_file.name, category, file_path))
        conn.commit()

        return uploaded_file.name, category, file_path
    except Exception as e:
        st.error(f"Error uploading the file: {e}")
        return None, None, None

# Function to search for files in the database
def search_files(query):
    try:
        c.execute("SELECT * FROM files WHERE filename LIKE ?", ('%' + query + '%',))
        return c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error searching for files: {e}")
        return []

# Function to delete all files from the database and file system
def delete_all_files():
    try:
        c.execute("DELETE FROM files")
        conn.commit()
        for file in os.listdir("uploads"):
            os.remove(os.path.join("uploads", file))
    except sqlite3.Error as e:
        st.error(f"Error deleting files: {e}")

# Streamlit UI

# Personalize Greeting
st.set_page_config(page_title="CloudEase File Manager", page_icon=":cloud:", layout="centered")

# Display a friendly greeting
user_name = st.text_input("What's your name?", "Guest")
if user_name != "Guest":
    st.markdown(f"## Welcome, {user_name}! 🎉")
else:
    st.markdown("## Welcome to CloudEase File Manager! 😊")

# Instructions
st.markdown("""
    **CloudEase** lets you easily manage your files in the cloud. You can upload files, categorize them, search for them, and even share them!
    You can also delete all files if needed. Start by uploading your first file below. 👇
""")

# File upload
uploaded_file = st.file_uploader("Choose a file to upload", type=["jpg", "jpeg", "png", "gif", "pdf", "docx", "txt", "pptx"])
if uploaded_file:
    file_name, category, file_path = handle_file_upload(uploaded_file)
    if file_name:
        st.success(f'🎉 File "{file_name}" uploaded successfully!')
        st.write(f'📂 **Category**: {category}')
        st.write(f'📍 **File path**: {file_path}')

# Search functionality
search_query = st.text_input("🔍 Search for a file by name")
if search_query:
    results = search_files(search_query)
    if results:
        st.write("### Search Results:")
        for result in results:
            st.write(f"📄 **Filename**: {result[1]}")
            st.write(f"🗂️ **Category**: {result[2]}")
            st.write(f"📍 **File Path**: {result[3]}")
            st.markdown("---")
    else:
        st.write("❌ No files found with that name. Try again!")

# File management options
if st.button('🧹 Delete all files'):
    delete_all_files()
    st.success('✨ All files have been deleted successfully!')

# Display uploaded files
if st.button("📁 View uploaded files"):
    st.write("### Uploaded Files:")
    c.execute("SELECT * FROM files")
    files = c.fetchall()
    if files:
        for file in files:
            st.write(f"📄 **Filename**: {file[1]}")
            st.write(f"🗂️ **Category**: {file[2]}")
            st.write(f"📍 **File Path**: {file[3]}")
            st.markdown("---")
    else:
        st.write("No files uploaded yet! Upload your first file now. 👇")

# Custom Footer
st.markdown("""
    ---
    **CloudEase File Manager** is designed for easy and friendly file management. 
    We hope you enjoy using it! 😄
""")
