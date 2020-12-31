import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
JWT_SECRET = os.environ.get('JWT_SECRET')

payload = {
        "iss": "paczkaplus",
        "aud": "paczkaplus",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=31536000),
        "sub": "",
        "usertype": "courier",
    }
token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
print(token)
