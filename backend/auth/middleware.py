"""
Authentication middleware for FastAPI
Handles JWT token verification (local) and email validation
"""

from fastapi import HTTPException, Header
from typing import Optional
import os
from dotenv import load_dotenv
from .config import is_email_verified
import jwt

# Load environment variables from backend/.env (searches up the directory tree)
load_dotenv()

# JWT secret for local token verification (no external API calls)
jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET")

if not jwt_secret:
    print("⚠️  WARNING: SUPABASE_JWT_SECRET not set. Authentication will not work!")



async def get_current_user(authorization: str = Header(None, alias="Authorization")) -> dict:
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
        # Check if authorization header is present
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )
        
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Expected 'Bearer <token>'"
            )
        
        token = authorization.split(" ")[1]
        
        # Verify JWT token locally (no external API call)
        # This prevents excessive auth egress to Supabase
        if not jwt_secret:
            raise HTTPException(
                status_code=500,
                detail="JWT secret not configured"
            )
        
        try:
            # Decode and verify the JWT token using the secret
            # This is done locally without making external API calls
            # Supabase tokens may not have 'aud' claim, so we skip audience verification
            payload = jwt.decode(
                token, 
                jwt_secret, 
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_aud": False  # Supabase tokens don't always have audience
                }
            )
            
            email = payload.get("email")
            user_id = payload.get("sub")
            
            if not email or not user_id:
                print(f"⚠️  Token payload missing email or sub: {payload.keys()}")
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid token: missing user information"
                )
                
        except jwt.ExpiredSignatureError:
            print("⚠️  Token has expired")
            raise HTTPException(
                status_code=401, 
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            print(f"⚠️  Invalid token error: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid token: {str(e)}"
            )
        
        # Check if email is verified (in our hardcoded list)
        if not is_email_verified(email):
            raise HTTPException(
                status_code=403,
                detail="Access denied. Your email is not authorized to use this application."
            )
        
        return {
            "email": email,
            "user_id": user_id
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
