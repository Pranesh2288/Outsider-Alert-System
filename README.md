# Unauthorized Entry Alert System 

## Installation

To install this project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Pranesh2288/Unauthorized-Entry-Alert-System
2. Change directory to Unauthorized-Entry-Alert-System:
   ```bash
   cd Unauthorized-Entry-Alert-System/
3. Create Conda Environment:
   ```bash
   conda env create -f environment.yml
4. Activate Environment:
   ```bash
   conda activate UEAS

## Usage

- To start the application, run:
  ```bash
   streamlit run app.py

## Features
- Real-time Face Detection: Captures live video frames from a webcam and detects faces in real time.
- Face Recognition: Compares detected faces to stored user encodings in the MongoDB database.
- MongoDB Integration: Retrieves face encodings, user names, and access levels from a MongoDB collection.
- User Identification: Displays information such as the person's ID, name, and access level.
- Unknown Detection: Flags any detected faces that are not recognized as "Unknown" in the live feed.
