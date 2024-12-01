import streamlit as st
import cv2
import numpy as np
import io
from PIL import Image
from pymongo import MongoClient
import face_recognition
import main  # Import the existing main script

client = MongoClient('mongodb://localhost:27017/')
db = client['AccessTracker']
collection = db['Entries']

TOKEN = '7864945720:AAHsZaT4S-ZqBR7rYfa1Jz-Tjl6Uc8fe6X4'
chatID = '-4571261231'

def add_user():
    """Streamlit page to add a new user."""
    st.header("Add New User")
    
    # Input fields for new user
    user_id = st.text_input("User ID")
    name = st.text_input("Name")
    access_level = st.selectbox("Access Level", ["Student", "Admin"])
    
    # Image upload for face encoding
    uploaded_file = st.file_uploader("Upload User Image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Convert uploaded file to numpy array
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Convert to RGB for face recognition
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect face and get encoding
        face_locations = face_recognition.face_locations(rgb_img)
        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
            
            # Read the photo as binary data
            uploaded_file.seek(0)
            photo_binary = uploaded_file.read()
            
            # Prepare user data for MongoDB
            user_data = {
                'id': user_id,
                'name': name,
                'access': access_level,
                'photo': photo_binary,
                'encoding': face_encoding.tolist(),
                'entries': [datetime.now().isoformat()]
            }
            
            # Insert user data
            if st.button("Save User"):
                try:
                    # Check if user ID already exists
                    existing_user = collection.find_one({'id': user_id})
                    if existing_user:
                        st.warning(f"User with ID {user_id} already exists!")
                    else:
                        collection.insert_one(user_data)
                        st.success(f"User {name} added successfully!")
                except Exception as e:
                    st.error(f"Error adding user: {e}")
        else:
            st.warning("No face detected in the uploaded image.")

def view_users():
    """Streamlit page to view existing users."""
    st.header("Registered Users")
    
    # Search functionality
    search_type = st.selectbox("Search By", ["All Users", "Search by Name", "Search by ID"])
    
    if search_type == "All Users":
        users = list(collection.find())
    elif search_type == "Search by Name":
        name_query = st.text_input("Enter Name to Search")
        users = list(collection.find({'name': {'$regex': name_query, '$options': 'i'}})) if name_query else []
    else:  # Search by ID
        id_query = st.text_input("Enter User ID to Search")
        users = list(collection.find({'id': {'$regex': id_query, '$options': 'i'}})) if id_query else []
    
    # Display users in a table
    if users:
        user_data = []
        for user in users:
            # Prepare user row
            row = {
                'ID': user['id'], 
                'Name': user['name'], 
                'Access Level': user['access'], 
                'Entry Count': len(user.get('entries', []))
            }
            user_data.append(row)
        
        # Display dataframe
        df = st.dataframe(user_data)
        
        # Selected user details
        if search_type != "All Users":
            selected_user = st.selectbox("Select a User", [user['name'] for user in users])
            
            # Find the selected user's full details
            user = next(user for user in users if user['name'] == selected_user)
            
            # Display user photo
            if 'photo' in user and user['photo']:
                try:
                    image = Image.open(io.BytesIO(user['photo']))
                    st.image(image, caption=f"Photo of {user['name']}", width=200)
                except Exception as e:
                    st.error(f"Error displaying photo: {e}")
            
            # Display entries
            st.subheader("Entry Timestamps")
            for entry in user.get('entries', []):
                st.write(entry)
    else:
        st.warning("No users found.")

def update_user():
    """Streamlit page to update user information."""
    st.header("Update User Information")
    
    # Find user to update
    search_id = st.text_input("Enter User ID to Update")
    
    if search_id:
        # Find the user
        user = collection.find_one({'id': search_id})
        
        if user:
            # Display current information
            st.subheader("Current User Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {user['name']}")
                st.write(f"**Access Level:** {user['access']}")
            
            # Input for new information
            new_name = st.text_input("New Name", value=user['name'])
            new_access = st.selectbox("New Access Level", ["Student", "Admin"], index=0 if user['access'].lower() == 'student' else 1)
            
            # Photo update
            update_photo = st.checkbox("Update Photo")
            new_photo_binary = None
            
            if update_photo:
                uploaded_file = st.file_uploader("Upload New Photo", type=['jpg', 'jpeg', 'png'])
                
                if uploaded_file is not None:
                    # Convert uploaded file to numpy array
                    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    
                    # Convert to RGB for face recognition
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    # Detect face and get encoding
                    face_locations = face_recognition.face_locations(rgb_img)
                    if face_locations:
                        # Read the photo as binary data
                        uploaded_file.seek(0)
                        new_photo_binary = uploaded_file.read()
                        
                        # Get new face encoding
                        face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
                        new_encoding = face_encoding.tolist()
                    else:
                        st.warning("No face detected in the new image.")
                        new_encoding = user['encoding']
                        new_photo_binary = user['photo']
            else:
                new_encoding = user['encoding']
                new_photo_binary = user['photo']
            
            # Update button
            if st.button("Update User"):
                try:
                    # Update the database
                    collection.update_one(
                        {'id': search_id},
                        {'$set': {
                            'name': new_name,
                            'access': new_access,
                            'photo': new_photo_binary,
                            'encoding': new_encoding
                        }}
                    )
                    st.success(f"User {new_name} updated successfully!")
                except Exception as e:
                    st.error(f"Error updating user: {e}")
        else:
            st.warning(f"No user found with ID {search_id}")

def delete_user():
    """Streamlit page to delete a user."""
    st.header("Delete User")
    
    # Find user to delete
    search_id = st.text_input("Enter User ID to Delete")
    
    if search_id:
        # Find the user
        user = collection.find_one({'id': search_id})
        
        if user:
            # Display user information
            st.subheader("User Information")
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Access Level:** {user['access']}")
            
            # Confirmation
            confirm = st.checkbox("I confirm I want to delete this user")
            
            if confirm:
                if st.button("Delete User"):
                    try:
                        # Delete the user
                        collection.delete_one({'id': search_id})
                        st.success(f"User {user['name']} deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting user: {e}")
        else:
            st.warning(f"No user found with ID {search_id}")

def live_face_recognition():
    st.header("Live Face Recognition")
    
    encodings_dict = main.retrieve_encodings()
    
    video_capture = cv2.VideoCapture(0)
    
    frame_placeholder = st.empty()
    stop_button = st.button("Stop Face Recognition")
    
    while video_capture.isOpened() and not stop_button:
        ret, frame = video_capture.read()
        if not ret:
            st.error("Failed to capture frame")
            break
        
        main.process_frame(frame, encodings_dict)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB")
    
    video_capture.release()

def log_access(user_id):
    if user_id:
        user = collection.find_one({'id': user_id})
        last_entry = datetime.strptime(user['entries'][-1], "%Y-%m-%dT%H:%M:%S.%f")
        if (datetime.now() - last_entry).total_seconds() > 60:
            message = f"{user['access']} {user['name']} accessed the room."
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chatID}&text={message}"
            requests.get(url)

            collection.update_one(
                {'id': user_id},
                {'$push': {'entries': datetime.now().isoformat()}}
            )

def main_app():
    """Main Streamlit application."""
    st.title("Face Recognition Access Control System")
    
    # Sidebar navigation
    menu = ["Live Recognition", "Add User", "View Users", "Update User", "Delete User"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    # Route to appropriate function based on menu choice
    if choice == "Live Recognition":
        live_face_recognition()
    elif choice == "Add User":
        add_user()
    elif choice == "View Users":
        view_users()
    elif choice == "Update User":
        update_user()
    elif choice == "Delete User":
        delete_user()

if __name__ == "__main__":
    from datetime import datetime
    main_app()
