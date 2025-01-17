import streamlit as st
import os
import sqlite3
from PIL import Image

# Create a SQLite database to store file metadata
conn = sqlite3.connect('file_manager.db')
c = conn.cursor()

# Create table for storing file metadata
c.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        category TEXT,
        file_path TEXT
    )
''')

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

# Function to search for files in the database
def search_files(query):
    c.execute("SELECT * FROM files WHERE filename LIKE ?", ('%' + query + '%',))
    return c.fetchall()

# Function to delete all files from the database and file system
def delete_all_files():
    c.execute("DELETE FROM files")
    conn.commit()
    for file in os.listdir("uploads"):
        os.remove(os.path.join("uploads", file))

# Streamlit UI
st.title('CloudEase File Manager')

# File upload
uploaded_file = st.file_uploader("Choose a file to upload", type=["jpg", "jpeg", "png", "gif", "pdf", "docx", "txt", "pptx"])
if uploaded_file:
    file_name, category, file_path = handle_file_upload(uploaded_file)
    st.success(f'File {file_name} uploaded successfully!')
    st.write(f'Category: {category}')
    st.write(f'File path: {file_path}')

# Search functionality
search_query = st.text_input("Search for a file by name")
if search_query:
    results = search_files(search_query)
    if results:
        st.write("Search Results:")
        for result in results:
            st.write(f"Filename: {result[1]}, Category: {result[2]}, File Path: {result[3]}")
    else:
        st.write("No files found.")

# File management options
if st.button('Delete all files'):
    delete_all_files()
    st.success('All files have been deleted.')

# Display uploaded files
if st.button("View uploaded files"):
    st.write("Uploaded Files:")
    c.execute("SELECT * FROM files")
    files = c.fetchall()
    for file in files:
        st.write(f"Filename: {file[1]}, Category: {file[2]}, File Path: {file[3]}")
