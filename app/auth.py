# app/auth.py
import os
from typing import Optional
from fastapi import Header, HTTPException, Depends
import firebase_admin
from firebase_admin import auth as fb_auth, credentials
from sqlalchemy.orm import Session
from .db import get_db
from .models import ApprovedUser
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("FIREBASE_CREDENTIALS")
if not firebase_admin._apps:
    if cred_path:
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    else:
        firebase_admin.initialize_app()

async def verify_firebase_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Verify Firebase token and check if user is approved"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.split(" ", 1)[1].strip()
    
    try:
        # Verify Firebase token
        decoded_token = fb_auth.verify_id_token(token)
        email = decoded_token.get("email")
        uid = decoded_token.get("uid")
        
        if not email:
            raise HTTPException(status_code=403, detail="Email not found in token")
        
        # Check if user exists in approved list
        approved_user = db.query(ApprovedUser).filter(
            ApprovedUser.email == email
        ).first()
        
        # If user doesn't exist, create them as pending approval
        if not approved_user:
            approved_user = ApprovedUser(
                email=email,
                firebase_uid=uid,
                is_active=False,  # Pending approval
                approved_by="system_auto_registered",
                notes="Auto-registered, awaiting admin approval"
            )
            db.add(approved_user)
            db.commit()
            db.refresh(approved_user)
            
            raise HTTPException(
                status_code=403, 
                detail="Account created successfully! Your account is pending approval. Please contact the administrator to get access."
            )
        
        # Check if user is active/approved
        if not approved_user.is_active:
            raise HTTPException(
                status_code=403, 
                detail="Your account is pending approval. Please contact the administrator to get access."
            )
        
        # Update firebase_uid if not set or changed
        if not approved_user.firebase_uid or approved_user.firebase_uid != uid:
            approved_user.firebase_uid = uid
            db.commit()
        
        return decoded_token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")