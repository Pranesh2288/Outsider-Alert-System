import json
import face_recognition
import cv2
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client = MongoClient('mongodb+srv://pranesh:UFFzS8o0Rs7DMgR9@cluster0.hc7zj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['EntryTracker']
collection = db['Entries']

def update_user_data():
    user_id = input("Enter ID of the user to update (or type 'exit' to quit): ")
    if user_id.lower() == 'exit':
        return

    # Find the user by id
    user = collection.find_one({'id': user_id})
    
    if user:
        print(f"User found: {user['name']}")
        
        # Collect new data, if any
        new_name = input(f"Enter new name (or press Enter to keep '{user['name']}'): ") or user['name']
        new_access = input(f"Enter new access level (or press Enter to keep '{user['access']}'): ") or user['access']
        
        update_photo = input("Do you want to update the photo? (yes/no): ").lower() == 'yes'
        
        if update_photo:
            photo_path = input("Enter the path to the new jpg photo: ")
            
            # Load the image and get its encoding
            img = face_recognition.load_image_file(photo_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encoding = face_recognition.face_encodings(img)
            
            if len(encoding) > 0:
                # Read the photo as binary data
                with open(photo_path, 'rb') as photo_file:
                    photo_binary = photo_file.read()
                
                # Update photo and encoding
                new_photo = photo_binary
                new_encoding = encoding[0].tolist()  # Convert numpy array to list for MongoDB compatibility
            else:
                print("No face encoding found. Keeping the existing photo and encoding.")
                new_photo = user['photo']
                new_encoding = user['encoding']
        else:
            new_photo = user['photo']
            new_encoding = user['encoding']

        # Update the database with the new values
        collection.update_one(
            {'id': user_id}, 
            {'$set': {
                'name': new_name,
                'access': new_access,
                'photo': new_photo,
                'encoding': new_encoding,
                'entries': user['entries']  # Retain the original entries
            }}
        )
        
        print(f"User {new_name} updated successfully!")
    else:
        print("User not found with the given ID.")

if __name__ == '__main__':
    while True:
        update_user_data()
        cont = input("Do you want to update another user? (yes/no): ").lower()
        if cont != 'yes':
            break
    print("Update process finished.")
