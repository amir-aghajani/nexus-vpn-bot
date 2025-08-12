from firebase_admin.firestore import firestore


class CategoriesDatabase:
    def __init__(self, firestore_connection: firestore.Client):
        self.db = firestore_connection
        self.col_ref = self.db.collection('categories')

    def get_category(self, category_id: str):
        doc_snapshot = self.col_ref.document(category_id).get()
        if not doc_snapshot.exists:
            return None

        return {'id': doc_snapshot.id, **doc_snapshot.to_dict()}

    def create(self, category_data: dict):
        doc_ref = self.col_ref.document()
        doc_ref.set(category_data)
        return doc_ref.id

    def update(self, category_id: str, category_data: dict):
        doc_ref = self.col_ref.document(category_id)
        doc_snapshot = doc_ref.get()
        if not doc_snapshot.exists:
            return False

        doc_ref.update(category_data)
        return True

    def delete(self, category_id: str):
        doc_ref = self.col_ref.document(category_id)
        doc_snapshot = doc_ref.get()
        if not doc_snapshot.exists:
            return False

        doc_ref.delete()
        return True
