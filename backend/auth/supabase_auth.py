"""
Backend-only authentication using Supabase
Handles all Supabase auth operations server-side so frontend doesn't need credentials
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase client with SERVICE ROLE key (server-only)
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

# Create admin client (can bypass RLS, manage users, etc.)
supabase: Client = create_client(supabase_url, supabase_service_key)


def sign_in_user(email: str, password: str) -> Dict[str, Any]:
    """
    Sign in a user with email and password (server-side)
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        Dictionary with user info and access token
        
    Raises:
        Exception: If sign-in fails
    """
    try:
        # Use Supabase admin API to sign in user
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                },
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at
            }
        else:
            raise Exception("Sign-in failed: No user or session returned")
            
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if "invalid" in error_msg.lower() or "credentials" in error_msg.lower():
            raise Exception("Invalid email or password")
        elif "not confirmed" in error_msg.lower():
            raise Exception("Email not confirmed. Please check your email for verification link.")
        else:
            raise Exception(f"Sign-in failed: {error_msg}")


def sign_up_user(email: str, password: str) -> Dict[str, Any]:
    """
    Sign up a new user with email and password (server-side)
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        Dictionary with user info and access token (if email confirmation disabled)
        
    Raises:
        Exception: If sign-up fails
    """
    try:
        # Use Supabase admin API to create user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            result = {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                },
                "message": "User created successfully"
            }
            
            # If session exists (email confirmation disabled), include tokens
            if response.session:
                result["access_token"] = response.session.access_token
                result["refresh_token"] = response.session.refresh_token
                result["expires_at"] = response.session.expires_at
            else:
                result["message"] = "User created. Please check your email for verification link."
            
            return result
        else:
            raise Exception("Sign-up failed: No user returned")
            
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            raise Exception("Email already registered")
        elif "password" in error_msg.lower() and "weak" in error_msg.lower():
            raise Exception("Password is too weak. Use at least 6 characters.")
        else:
            raise Exception(f"Sign-up failed: {error_msg}")


def sign_out_user(access_token: str) -> bool:
    """
    Sign out a user (server-side)
    
    Args:
        access_token: User's access token
        
    Returns:
        True if successful
        
    Raises:
        Exception: If sign-out fails
    """
    try:
        # Revoke the token
        supabase.auth.sign_out()
        return True
    except Exception as e:
        raise Exception(f"Sign-out failed: {str(e)}")


def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh an access token (server-side)
    
    Args:
        refresh_token: User's refresh token
        
    Returns:
        Dictionary with new access token and user info
        
    Raises:
        Exception: If refresh fails
    """
    try:
        # Refresh the session
        response = supabase.auth.refresh_session(refresh_token)
        
        if response.session and response.user:
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                },
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at
            }
        else:
            raise Exception("Token refresh failed")
            
    except Exception as e:
        raise Exception(f"Token refresh failed: {str(e)}")


def get_user_from_token(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from access token (server-side)
    
    Args:
        access_token: User's access token
        
    Returns:
        User dictionary or None if token is invalid
    """
    try:
        # Set the session with the token
        response = supabase.auth.get_user(access_token)
        
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email
            }
        return None
    except Exception:
        return None
