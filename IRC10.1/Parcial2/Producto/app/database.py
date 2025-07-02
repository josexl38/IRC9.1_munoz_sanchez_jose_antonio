from pymongo import MongoClient, errors
import os
import time
from datetime import datetime

mongo_host = os.environ.get('MONGO_HOST', 'mongodb')
mongo_port = int(os.environ.get('MONGO_PORT', 27017))
mongo_db = os.environ.get('MONGO_DB', 'ansible_platform')

# Conexión con retry
while True:
    try:
        client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/', serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ Conectado a MongoDB")
        break
    except errors.ServerSelectionTimeoutError:
        print("❌ MongoDB no disponible, reintentando en 5 segundos...")
        time.sleep(5)

db = client[mongo_db]
users = db.users
logs = db.logs

def init_db():
    users.create_index('username', unique=True)

def create_user(username, password):
    users.insert_one({'username': username, 'password': password})

def get_user(username):
    return users.find_one({'username': username})

def log_action(user, action):
    logs.insert_one({
        'user': user,
        'action': action,
        'timestamp': datetime.now()
    })

def get_logs():
    return list(logs.find().sort('timestamp', -1))

