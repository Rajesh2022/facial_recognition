import streamlit as st
import cv2
import mediapipe as mp
from firebase_config import init_firebase
import datetime


# Initialize Firebase
db, bucket = init_firebase()

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# Streamlit interface
st.title("Face Recognition System Administration")

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Database"])

if page == "Home":
    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    name = st.text_input("Name")
    role = st.text_input("Role")
    submit = st.button("Submit")

    if submit:
        if uploaded_file is not None and name and role:
            # Save the uploaded file to Firebase Storage
            blob = bucket.blob(f'images/{name}.jpg')
            blob.upload_from_string(uploaded_file.getvalue(), content_type='image/jpeg')
            
            # Generate signed URL
            image_url = blob.generate_signed_url(expiration=datetime.timedelta(days=7))
            st.write(f"Uploaded Image URL: {image_url}")  # Debug print
            
            # Store data in Firestore with a reference to the Storage URL
            doc_ref = db.collection('users').document()
            doc_ref.set({
                'name': name,
                'role': role,
                'image_url': image_url
            })
            st.success("User data uploaded successfully!")
        else:
            st.error("Please provide an image, name, and role.")

    # Live Face Detection
    st.header("Live Face Detection")
    start_camera = st.button('Start Camera')
    stop_camera = st.button('Stop Camera')
    frame_slot = st.empty()

    if 'camera_active' not in st.session_state:
        st.session_state['camera_active'] = False

    if start_camera:
        st.session_state['camera_active'] = True

    if stop_camera:
        st.session_state['camera_active'] = False
        cap.release()
        st.stop()

    if st.session_state['camera_active']:
        cap = cv2.VideoCapture(0)
        while st.session_state['camera_active']:
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

elif page == "Database":
    st.write("Database Management Page")
    import database
    database.show()
