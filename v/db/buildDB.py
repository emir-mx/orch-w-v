from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://emires:Pepies2020@cluster0.xlbgx.mongodb.net/checks?retryWrites=true&w=majority"
)
db = client["checks"]

collections = db.get_collection("collection_checks")


class DataBase:
    def __init__(self, platforms):
        self.platforms = platforms

    def get_db(self) -> dict:
        db = {}
        for platform in self.platforms:
            temp = collections.find(
                {f"platform.{platform}.method.cli": {"$exists": "true"}}
            )
            db[platform] = temp[0]["platform"][platform]["method"]["cli"]
        return db
