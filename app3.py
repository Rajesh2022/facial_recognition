import streamlit as st
import cv2
import face_recognition as frg
import yaml
from utils import recognize, build_dataset
from firebase_config import init_firebase
import datetime
import threading

# Initialize Firebase
db, bucket = init_firebase()

# Set page configuration
st.set_page_config(layout="centered", page_title="Face Recognition System")

# Load configuration
with open('config.yaml', 'r') as cfg_file:
    cfg = yaml.load(cfg_file, Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

# Sidebar navigation and settings
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Database"])

# Sidebar settings for face recognition
st.sidebar.title("Settings")
TOLERANCE = st.sidebar.slider("Tolerance", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Tolerance is the threshold for face recognition. The lower the tolerance, the more strict the face recognition. The higher the tolerance, the more loose the face recognition.")

# Sidebar person information display
st.sidebar.title("Person Information")
name_container = st.sidebar.empty()
id_container = st.sidebar.empty()
name_container.info('Name: Unknown')
id_container.success('ID: Unknown')

# Global variable to control the webcam thread
stop_thread = False

def start_webcam():
    global stop_thread
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_WINDOW = st.image([])

    while not stop_thread:
        ret, frame = cam.read()
        if not ret:
            st.error("Failed to capture frame from camera")
            st.info("Please turn off other camera apps and restart.")
            break
        image, name, id = recognize(frame, TOLERANCE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        name_container.info(f"Name: {name}")
        id_container.success(f"ID: {id}")
        FRAME_WINDOW.image(image)

    cam.release()

if page == "Home":
    st.title("Facial Recognition System for Secure Access Control")

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

    st.write(PICTURE_PROMPT)
    uploaded_images = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    if uploaded_images:
        for image in uploaded_images:
            image = frg.load_image_file(image)
            image, name, id = recognize(image, TOLERANCE)
            name_container.info(f"Name: {name}")
            id_container.success(f"ID: {id}")
            st.image(image)
    else:
        st.info("Please upload an image")

    st.write(WEBCAM_PROMPT)
    start_camera = st.button('Start Camera')
    stop_camera = st.button('Stop Camera')

    if start_camera:
        stop_thread = False
        t = threading.Thread(target=start_webcam)
        t.start()

    if stop_camera:
        stop_thread = True

elif page == "Database":
    st.write("Database Management Page")
    import database
    database.show()
