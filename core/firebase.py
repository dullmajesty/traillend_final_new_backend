import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "firebase_key.json"
        )
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("🔥 Firebase initialized")
    else:
        print("🔥 Firebase already initialized")
