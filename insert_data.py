import json
import face_recognition
import cv2
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client = MongoClient('mongodb+srv://pranesh:UFFzS8o0Rs7DMgR9@cluster0.hc7zj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['EntryTracker']
collection = db['Entries']

data = {
    'id': [],
    'name': [],
    'access': [],
    'photo': [],  # This will now hold binary data instead of paths
    'encoding': [],
    'entries': []  # List to store timestamps for each user
}

def collect_data():
    while True:
        # Collect user input
        user_id = input("Enter ID (or type 'exit' to finish): ")
        if user_id.lower() == 'exit':
            break
        
        name = input("Enter name: ")
        access = input("Enter access level: ")
        
        # Get photo input
        photo_path = input("Enter the path to the jpg photo: ")
        
        # Load the image and get its encoding
        img = face_recognition.load_image_file(photo_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(img)

        # Check if encoding is found
        if len(encoding) > 0:
            # Read the photo as binary data
            with open(photo_path, 'rb') as photo_file:
                photo_binary = photo_file.read()

            # Get the current timestamp
            timestamp = datetime.now().isoformat()  # ISO format for consistency

            # Append data to lists
            data['id'].append(user_id)
            data['name'].append(name)
            data['access'].append(access)
            data['photo'].append(photo_binary)  # Store binary data
            data['encoding'].append(encoding[0].tolist())  # Convert numpy array to list for JSON compatibility
            data['entries'].append([timestamp])  # Initialize entries with the current timestamp

            # Insert data into MongoDB
            collection.insert_one({
                'id': user_id,
                'name': name,
                'access': access,
                'photo': photo_binary,  # Store photo binary data
                'encoding': encoding[0].tolist(),  # Store encoding as list
                'entries': [timestamp]  # Store initial timestamp
            })
            print(f"Data for {name} added successfully!")
        else:
            print("No face encoding found. Please provide a photo with at least one face.")

if __name__ == '__main__':
    collect_data()
    print("Data collection finished.")
