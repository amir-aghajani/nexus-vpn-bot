from firebase_admin.firestore import firestore

from utils import make_json_serializable


class DatabaseClient:
    def __init__(self, firestore_client: firestore.Client):
        self.db = firestore_client

    def fetch_all(self, collection: str) -> list:
        docs = self.db.collection(collection).stream()
        return [make_json_serializable({'id': doc.id, **doc.to_dict()}) for doc in docs]

    def fetch(self, collection: str, document_id) -> dict | None:
        doc_ref = self.db.collection(collection).document(str(document_id))
        doc = doc_ref.get()
        if not doc.exists:
            return None

        return make_json_serializable({'id': doc.id, **doc.to_dict()})

    def create(self, collection: str, data: dict) -> dict:
        update_time, doc_ref = self.db.collection(collection).add({
            **data,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        return self.fetch(collection, doc_ref.id)

    def update(self, collection: str, document_id, data: dict) -> dict:
        doc_ref = self.db.collection(collection).document(str(document_id))
        doc_ref.update(data)
        return self.fetch(collection, str(document_id))

    def delete(self, collection: str, document_id) -> bool:
        doc_ref = self.db.collection(collection).document(str(document_id))
        doc_ref.delete()
        return True

    def exists(self, collection: str, document_id) -> bool:
        doc_ref = self.db.collection(collection).document(str(document_id))
        return doc_ref.get().exists
