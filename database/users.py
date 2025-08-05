from firebase_admin.firestore import firestore


class UserManager:
    def __init__(self, firestore_connection: firestore.Client):
        self.db = firestore_connection

    def create(self, user_id):
        users_col_ref = self.db.collection('users')
        user_doc_ref = users_col_ref.document(str(user_id))
        user_doc_ref.set({
            'started': True,
            'firstStartAt': firestore.SERVER_TIMESTAMP
        })

    def exists(self, user_id):
        users_col_ref = self.db.collection('users')
        user_doc_ref = users_col_ref.document(str(user_id))
        return user_doc_ref.get().exists
