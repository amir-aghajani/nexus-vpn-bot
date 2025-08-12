import base64
import json

import firebase_admin
from firebase_admin import credentials, firestore

from config import settings


class FirebaseConnection:
    def __init__(self):
        decoded_json = base64.b64decode(settings.firebase_admin_sdk).decode()
        self.cred = credentials.Certificate(json.loads(decoded_json))
        self.app = firebase_admin.initialize_app(self.cred)
        self.fs_connection = firestore.client()

    def get_firestore_connection(self):
        return self.fs_connection


firebase_connection = FirebaseConnection()
firestore_connection = firebase_connection.get_firestore_connection()
