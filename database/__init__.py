from database.client import DatabaseClient
from database.users import UserManager
from firebase import firestore_connection

users_db = UserManager(firestore_connection=firestore_connection)
db_client = DatabaseClient(firestore_client=firestore_connection)
