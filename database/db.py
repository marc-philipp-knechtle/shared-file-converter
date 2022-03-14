from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class JsonDBStorage:
    _connection: str
    _database: str
    _collection: str

    def __init__(self, connection: str, database: str, collection: str):
        self._connection = connection
        self._database = database
        self._collection = collection

    def get_connection(self) -> Database:
        return MongoClient(self._connection).get_database(self._database)

    def get_collection(self) -> Collection:
        return self.get_connection().get_collection(self._collection)
