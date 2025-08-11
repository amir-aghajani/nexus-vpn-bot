from firebase_admin.firestore import firestore


class ServerManager:
    def __init__(self, firestore_connection: firestore.Client):
        self.db = firestore_connection

    def create(self, server_data):
        servers_col_ref = self.db.collection('servers')
        server_doc_ref = servers_col_ref.document()
        server_doc_ref.set(server_data)
        return server_doc_ref.id

    def exists(self, server_id):
        servers_col_ref = self.db.collection('servers')
        server_doc_ref = servers_col_ref.document(str(server_id))
        return server_doc_ref.get().exists

    def update(self, server_id, server_data):
        servers_col_ref = self.db.collection('servers')
        server_doc_ref = servers_col_ref.document(str(server_id))
        server_doc_ref.update(server_data)

    def delete(self, server_id):
        servers_col_ref = self.db.collection('servers')
        server_doc_ref = servers_col_ref.document(str(server_id))
        server_doc_ref.delete()
