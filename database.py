import streamlit as st
from firebase_config import init_firebase

# Initialize Firebase
db, bucket = init_firebase()

def show():
    # Streamlit interface for managing database
    st.title("Database Management")

    # Fetch all users from Firestore
    users_ref = db.collection('users')
    users = users_ref.stream()

    # Display users in a table
    for user in users:
        user_data = user.to_dict()
        st.write(f"**Name:** {user_data['name']}")
        st.write(f"**Role:** {user_data['role']}")

        # Check if the image URL exists and is accessible
        image_url = user_data.get('image_url')
        st.write(f"Image URL: {image_url}")  # Debug print
        if image_url:
            try:
                st.image(image_url, width=150)
            except Exception as e:
                st.write(f"Error loading image: {e}")
        else:
            st.write("No image available")

        delete_button = st.button(f"Delete {user_data['name']}", key=user.id)

        if delete_button:
            # Delete image from Firebase Storage
            blob = bucket.blob(f'images/{user_data["name"]}.jpg')
            blob.delete()

            # Delete user document from Firestore
            users_ref.document(user.id).delete()
            st.success(f"Deleted {user_data['name']} successfully!")
            st.experimental_rerun()
