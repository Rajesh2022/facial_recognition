import firebase_admin
from firebase_admin import credentials, firestore, storage

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate('face-detection-for-security-firebase-adminsdk-7rpl8-8592dd3018.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'face-detection-for-security.appspot.com'
        })
    return firestore.client(), storage.bucket()
