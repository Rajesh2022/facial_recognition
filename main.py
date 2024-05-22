import streamlit as st
import cv2
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore, storage

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate('face-detection-for-security-firebase-adminsdk-7rpl8-8592dd3018.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'face-detection-for-security.appspot.com'
        })
    return firestore.client(), storage.bucket()

db, bucket = init_firebase()

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)


# Streamlit interface
st.title("Face Recognition System Administration")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
name = st.text_input("Name")
role = st.text_input("Role")
submit = st.button("Submit", key="submit_button")

if submit and uploaded_file and name and role:
    # Save the uploaded file to Firebase Storage
    blob = bucket.blob(f'images/{name}.jpg')
    blob.upload_from_string(uploaded_file.getvalue(), content_type='image/jpeg')
    image_url = blob.public_url
    
    # Store data in Firestore with a reference to the Storage URL
    doc_ref = db.collection('users').document()
    doc_ref.set({
        'name': name,
        'role': role,
        'image_url': image_url
    })
    st.success("User data uploaded successfully!")

# Additional Streamlit logic for face detection as before


# Live Face Detection
st.header("Live Face Detection")
start_camera = st.button('Start Camera' , key='start_camera')
frame_slot = st.empty()
cap = cv2.VideoCapture(0)

if start_camera:
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to grab frame from camera. Check your camera settings.")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)

        if results.detections:
            for detection in results.detections:
                mp.solutions.drawing_utils.draw_detection(frame, detection)

        frame_slot.image(frame, channels="BGR", use_column_width=True)

        stop_camera = st.button('Stop Camera' , key='stop_camera')
        if stop_camera:
            cap.release()
            break


