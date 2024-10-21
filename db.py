import pymongo
import traceback

class MongoDB:

    def __init__(self) -> None:
        self.mongo_url = "mongodb+srv://msreddygone:k1sLGwf1ASvC3zfZ@persona.ss0ns.mongodb.net/?appName=persona"
        self.mongo_conn = pymongo.MongoClient(self.mongo_url)
    
    def prechecks(self, db, collection):
        if db in [None,""," "] or collection in [None, "", " "]:
            return ValueError("db or collection should not be empty")
        return self.mongo_conn[db][collection]

    def insert(self, db, collection, records, many=False):
        coll = self.prechecks(db, collection)
        
        try:

            if isinstance(records, dict) and many ==  True:
                records = [records]
            
            if not many:
                return coll.insert_one(records)
            else:
                return coll.insert_many(records)
        except Exception as e:
            print(traceback.format_exc())
            return ValueError(e)
    
    def find(self, db, collection, filters, many=False, projection={}):
        coll = self.prechecks(db, collection)

        try:
            if not many:
                return coll.find_one(filter=filters, projection=projection)
            else:
                return coll.find(filter=filters, projection=projection)
        except Exception as e:
            print(traceback.format_exc())
            return ValueError(e)

