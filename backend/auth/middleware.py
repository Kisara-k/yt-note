"""
Authentication middleware for FastAPI
Handles Supabase JWT token verification and email validation
"""

from fastapi import HTTPException, Header
from typing import Optional
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from .config import is_email_verified
import jwt

# Load environment variables from backend/.env (searches up the directory tree)
load_dotenv()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET")
supabase: Client = create_client(url, key)


async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Verify JWT token and extract user information
    Also checks if the user's email is in the verified list
    
    Args:
        authorization: Bearer token from request header
        
    Returns:
        User information dict with email and user_id
        
    Raises:
        HTTPException: If token is invalid or email not verified
    """
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Expected 'Bearer <token>'"
            )
        
        token = authorization.split(" ")[1]
        
        # Verify token with Supabase
        try:
            user_response = supabase.auth.get_user(token)
            if not user_response or not user_response.user:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user = user_response.user
            email = user.email
            
        except Exception as e:
            # Fallback to JWT decoding if Supabase API call fails
            if jwt_secret:
                try:
                    payload = jwt.decode(token, jwt_secret, algorithms=["HS256"], options={"verify_signature": True})
                    email = payload.get("email")
                    user_id = payload.get("sub")
                except jwt.InvalidTokenError:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")
            else:
                raise HTTPException(status_code=401, detail="Authentication failed")
        
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        # Check if email is verified (in our hardcoded list)
        if not is_email_verified(email):
            raise HTTPException(
                status_code=403,
                detail="Access denied. Your email is not authorized to use this application."
            )
        
        return {
            "email": email,
            "user_id": user.id if 'user' in locals() else user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Optional authentication - returns user if token is valid, None otherwise
    Useful for endpoints that can work with or without authentication
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except:
        return None
