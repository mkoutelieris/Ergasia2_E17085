import json, os, sys
from pymongo import MongoClient

mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose InfoSys database
db = client['InfoSys']
products_db = db['Products']
users_db = db['Users']

def insert_all():
    product_file = open('./data/products.json','r')
    product_lines = product_file.readlines()
    users_file = open('./data/users.json','r')
    users_lines = users_file.readlines()

    for line in product_lines:
        entry = None 
        try:
            entry = json.loads(line)
        except Exception as e:
            print(e)
            continue
        if entry != None:
            products_db.insert_one(entry)

    for line in users_lines:
        entry = None 
        try:
            entry = json.loads(line)
        except Exception as e:
            print(e)
            continue
        if entry != None:
            users_db.insert_one(entry)