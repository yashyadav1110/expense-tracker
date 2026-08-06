import certifi
from pymongo import MongoClient

# MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://yashdy8900:yashyadav@cluster0.oevctw6.mongodb.net/?appName=Cluster0"

DB_NAME = "expense_tracker"

_client = None


def get_db():
    global _client

    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsCAFile=certifi.where()
        )

    return _client[DB_NAME]


def init_db():
    db = get_db()

    categories = db["categories"]

    # Create unique index
    categories.create_index("name", unique=True)

    # Seed default categories
    if categories.count_documents({}) == 0:
        defaults = [
            "Food",
            "Travel",
            "Rent",
            "Shopping",
            "Salary",
            "Other"
        ]

        categories.insert_many(
            [{"name": c} for c in defaults]
        )