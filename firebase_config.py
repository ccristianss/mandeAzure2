import json
import zlib
import os
from base64 import b64decode

import firebase_admin
from firebase_admin import credentials, messaging, db

google_credentials = os.getenv("GOOGLE_CERTIFICATE")
decoded_data = b64decode(google_credentials)
decompressed_data = zlib.decompress(decoded_data)
google_data = json.loads(decompressed_data.decode('utf-8'))

cred = credentials.Certificate(google_data)
firebase_config = firebase_admin.initialize_app(cred, {
    'databaseURL':  'https://mandersdev-default-rtdb.firebaseio.com'
})