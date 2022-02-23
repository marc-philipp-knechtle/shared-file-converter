from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class JsonDBStorage:
    _connection: str
    _collection: str
    _database: str

    def __init__(self, connection: str, database: str, collection: str):
        self._database = database
        self._connection = connection
        self._collection = collection

    def get_connection(self) -> Database:
        return MongoClient(self._connection).get_database(self._collection)

    def get_collection(self) -> Collection:
        return self.get_connection().get_collection(self._collection)
