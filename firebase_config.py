import firebase_admin
from firebase_admin import credentials, messaging, db


cred = credentials.Certificate('serviceAccountKey.json')
firebase_config = firebase_admin.initialize_app(cred)