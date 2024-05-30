from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['my_database']

users_collection = db['users']
products_collection = db['products']
orders_collection = db['orders']
counters_collection = db['counters']

def get_next_sequence_value(sequence_name):
    sequence_document = counters_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=True,
        upsert=True
    )
    return sequence_document['sequence_value']
