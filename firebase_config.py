import json
import os
from base64 import b64decode
import firebase_admin
from firebase_admin import credentials, messaging, db


firebase_key_path = os.getenv('FIREBASE_KEY_JSON')
firebase_dict = json.loads(b64decode(firebase_key_path))
cred = credentials.Certificate(firebase_dict)
firebase_config = firebase_admin.initialize_app(cred, {
    'databaseURL':  'https://mandersdev-default-rtdb.firebaseio.com'
})