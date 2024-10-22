import cv2
import face_recognition
from pymongo import MongoClient
import numpy as np
from datetime import datetime

# MongoDB setup
client = MongoClient('mongodb+srv://pranesh:UFFzS8o0Rs7DMgR9@cluster0.hc7zj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['AccessTracker']
collection = db['Entries']

def retrieve_encodings():
    """Retrieve all user encodings from the MongoDB collection."""
    encodings_dict = {user['id']: user['encoding'] for user in collection.find()}
    return encodings_dict

def identify_face(face_encoding, encodings_dict):
    """Identify a face by comparing it to known encodings in the database."""
    for user_id, stored_encoding in encodings_dict.items():
        if face_recognition.compare_faces([stored_encoding], face_encoding)[0]:
            return user_id
    return None

def process_frame(frame, encodings_dict):
    """Process the current frame to detect and identify faces."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        user_id = identify_face(face_encoding, encodings_dict)
        draw_bounding_box(frame, face_location, user_id)
        print_person(user_id)

def print_person(user_id):
    if user_id:
        user_data = collection.find_one({'id': user_id})
        user_name = user_data['name']
        user_access = user_data['access'].lower()
        if user_access == 'admin':
            print(f"Admin {user_name} is accessing the room.")
        elif user_access == 'student':
            print(f"Student {user_name} is trying to access the room.")
    else:
        print("Unknown person detected.")

def draw_bounding_box(frame, face_location, user_id):
    """Draw a bounding box around the face and display user information."""
    top, right, bottom, left = face_location
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    
    label = str(user_id) if user_id else "Unknown"
    color = (255, 0, 0) if user_id else (0, 0, 255)
    cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

def main():
    """Main function to capture video and identify faces."""
    encodings_dict = retrieve_encodings()
    video_capture = cv2.VideoCapture(0)
    frame_counter, frame_interval = 0, 5

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame.")
            break
        
        if frame_counter % frame_interval == 0:
            process_frame(frame, encodings_dict)
            cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame_counter += 1

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
