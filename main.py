import cv2
import face_recognition
from pymongo import MongoClient
import numpy as np
from datetime import datetime
import requests

# Telegram Bot setup
TOKEN = '7864945720:AAHsZaT4S-ZqBR7rYfa1Jz-Tjl6Uc8fe6X4'
chatID = '-4571261231'

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1312811725740966101/heYkhyyB2xEpm4EiN3cqhfdsPFZW-o1qpecQlO4c6p9mZt32RfoWoFWytZn8yWaFVCtE"


# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['AccessTracker']
collection = db['Entries']

def send_discord_alert(message):
    """Send an alert message to a Discord channel."""
    data = {
        "content": message,
        "username": "Access Alert Bot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png"  # Optional bot avatar
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Discord alert sent successfully!")
    else:
        print(f"Failed to send Discord alert. Status code: {response.status_code}, Response: {response.text}")

def retrieve_encodings():
    """Retrieve all user encodings from the MongoDB collection."""
    return {user['id']: user['encoding'] for user in collection.find()}

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
        last_entry_time = datetime.strptime(user_data['entries'][-1], "%Y-%m-%dT%H:%M:%S.%f")
        time_since_last_entry = (datetime.now() - last_entry_time).total_seconds()

        if time_since_last_entry > 60:  # Avoid spamming notifications
            message = f"{user_access.capitalize()} {user_name} is accessing the room."
            # Send Telegram alert
            telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chatID}&text={message}"
            requests.get(telegram_url)
            print(message)

            # Send Discord alert
            send_discord_alert(message)

            # Update database with the new entry
            collection.update_one(
                {'id': user_id}, 
                {'$push': {'entries': datetime.now().isoformat()}}
            )
    else:
        print("Unknown person detected.")
        send_discord_alert("Unknown person detected in the camera feed!")

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