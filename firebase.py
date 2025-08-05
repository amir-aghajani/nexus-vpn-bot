import firebase_admin
from firebase_admin import firestore, credentials

from config import settings


class FirebaseConnection:
    def __init__(self):
        self.cred = credentials.Certificate(settings.firebase_admin_sdk_path)
        self.app = firebase_admin.initialize_app(self.cred)
        self.fs_connection = firestore.client()

    def get_firestore_connection(self):
        return self.fs_connection


firebase_connection = FirebaseConnection()
firestore_connection = firebase_connection.get_firestore_connection()
