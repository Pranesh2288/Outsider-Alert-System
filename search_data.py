import json
from pymongo import MongoClient
from PIL import Image
import io

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['AccessTracker']
collection = db['Entries']

def retrieve_data():
    while True:
        name = input("Enter the name to search (or type 'exit' to finish): ")
        if name.lower() == 'exit':
            break
        
        # Query the database for the user by name
        user_data = collection.find_one({'name': name})

        if user_data:
            # Display the retrieved data
            print("\nUser Data Found:")
            print(f"ID: {user_data['id']}")
            print(f"Name: {user_data['name']}")
            print(f"Access Level: {user_data['access']}")
            
            # Convert binary data back to image and display it
            photo_binary = user_data['photo']
            image = Image.open(io.BytesIO(photo_binary))
            image.show()  # Display the image

            # print(f"Encoding: {user_data['encoding']}")
            print("Entries:")
            for entry in user_data['entries']:
                print(f" - {entry}")  # Display each timestamp
            print("\n")
        else:
            print(f"No user found with the name '{name}'.\n")

if __name__ == '__main__':
    retrieve_data()
    print("Data retrieval finished.")
