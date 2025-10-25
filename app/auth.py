# app/auth.py
import os
from typing import Optional
from fastapi import Header, HTTPException
import firebase_admin
from firebase_admin import auth as fb_auth, credentials
from dotenv import load_dotenv

load_dotenv()

# Use service account JSON: set GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_CREDENTIALS
cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("FIREBASE_CREDENTIALS")
if not firebase_admin._apps:
    if cred_path:
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    else:
        # Fallback to ADC if configured locally
        firebase_admin.initialize_app()

async def verify_firebase_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    try:
        return fb_auth.verify_id_token(token)  # contains "uid", "email", ...
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
