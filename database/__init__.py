from database.users import UserManager
from firebase import firestore_connection

users_db = UserManager(firestore_connection=firestore_connection)
