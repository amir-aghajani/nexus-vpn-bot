from firebase_admin.firestore import firestore


class UserManager:
    def __init__(self, firestore_connection: firestore.Client):
        self.db = firestore_connection

    def exists(self, user_id):
        users_col_ref = self.db.collection('users')
        user_doc_ref = users_col_ref.document(str(user_id))
        return user_doc_ref.get().exists

    def change_status(self, user_id, action):
        if action == 'banUser':
            status = 'banned'
        elif action == 'unbanUser':
            status = 'active'

        users_col_ref = self.db.collection('users')
        user_doc_ref = users_col_ref.document(str(user_id))
        user_doc_ref.update({
            'status': status,
        })

        return
