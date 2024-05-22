import streamlit as st
import cv2
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore

# Use the downloaded private key file
cred = credentials.Certificate('face-detection-for-security-firebase-adminsdk-7rpl8-8592dd3018.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# Setup webcam
cap = cv2.VideoCapture(0)

st.title("Upload User Data for Face Recognition")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
name = st.text_input("Name")
role = st.text_input("Role")
submit = st.button("Submit")

if submit and uploaded_file and name and role:
    # Process and store the file (e.g., save to Firebase Storage and store URL in Firestore)
    # Example assumes direct Firestore storage which is not ideal for large files
    blob = uploaded_file.read()
    image_data = firestore.Blob(blob)
    doc_ref = db.collection('users').document()
    doc_ref.set({
        'name': name,
        'role': role,
        'image': image_data
    })
    st.success("Data uploaded!")

frame_slot = st.empty()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert the BGR image to RGB.
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform face detection
    results = face_detection.process(image)

    # Draw face detections
    if results.detections:
        for detection in results.detections:
            # You can refine this part to include more details or to improve the annotations
            mp.solutions.drawing_utils.draw_detection(frame, detection)

    # Display the image
    frame_slot.image(frame, channels="BGR", use_column_width=True)

# Assuming face_recognition and detection code here
recognized_name = "Recognized Name"
recognized_role = "Recognized Role"

st.write(f"Name: {recognized_name}, Role: {recognized_role}")
# Release the webcam on closing the app
cap.release()

