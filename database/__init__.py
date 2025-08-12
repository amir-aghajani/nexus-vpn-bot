from database.servers import ServerManager
from database.users import UserManager
from database.categories import CategoriesDatabase
from firebase import firestore_connection

users_db = UserManager(firestore_connection=firestore_connection)
servers_db = ServerManager(firestore_connection=firestore_connection)
categories_db = CategoriesDatabase(firestore_connection=firestore_connection)
