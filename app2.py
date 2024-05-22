import streamlit as st
import cv2
import mediapipe as mp
from firebase_config import init_firebase
import datetime

# Initialize Firebase
db, bucket = init_firebase()

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# Placeholder for face recognition logic
def recognize_face(face_image):
    # Placeholder function for recognizing face
    # You need to implement this using a face recognition model
    # For now, it returns a dummy name and role
    return "John Doe", "Employee"

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
        st.experimental_rerun()

    if st.session_state['camera_active']:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera.")
        else:
            while st.session_state['camera_active']:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to grab frame from camera. Check your camera settings.")
                    break

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(image)

                if results.detections:
                    for detection in results.detections:
                        mp_drawing.draw_detection(frame, detection)
                        
                        # Extract the bounding box
                        bboxC = detection.location_data.relative_bounding_box
                        ih, iw, _ = frame.shape
                        (x, y, w, h) = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                        
                        # Extract face image
                        face_image = frame[y:y+h, x:x+w]
                        
                        # Recognize face
                        name, role = recognize_face(face_image)
                        
                        # Draw name and role
                        cv2.putText(frame, f"{name}, {role}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

                frame_slot.image(frame, channels="BGR", use_column_width=True)

            cap.release()

elif page == "Database":
    st.write("Database Management Page")
    import database
    database.show()
