import os
from supabase import create_client, Client
from datetime import datetime
import streamlit as st

def get_supabase_client() -> Client:
    try:
        url = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
        key = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
    except:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
    return create_client(url, key)

def track_user_login(email: str):
    """Save or update user on login"""
    try:
        supabase = get_supabase_client()
        now = datetime.now().isoformat()

        existing = supabase.table("users").select("*").eq("email", email).execute()

        if existing.data:
            supabase.table("users").update({
                "last_login": now
            }).eq("email", email).execute()
            print(f"[INFO] Returning user: {email}")
        else:
            supabase.table("users").insert({
                "email": email,
                "first_login": now,
                "last_login": now,
                "total_queries": 0,
                "total_tokens": 0
            }).execute()
            print(f"[INFO] New user registered: {email}")

    except Exception as e:
        print(f"[ERROR] track_user_login failed: {e}")

def track_query(email: str, query: str, answer: str, tokens_used: int = 0):
    """Log every query to Supabase"""
    try:
        supabase = get_supabase_client()

        supabase.table("queries").insert({
            "email": email,
            "query": query,
            "answer": answer,
            "tokens_used": tokens_used,
            "created_at": datetime.now().isoformat()
        }).execute()

        existing = supabase.table("users").select("total_queries, total_tokens").eq("email", email).execute()
        if existing.data:
            current = existing.data[0]
            supabase.table("users").update({
                "total_queries": current["total_queries"] + 1,
                "total_tokens": current["total_tokens"] + tokens_used
            }).eq("email", email).execute()

        print(f"[INFO] Query tracked for {email}")

    except Exception as e:
        print(f"[ERROR] track_query failed: {e}")

def get_user_stats(email: str) -> dict:
    """Get stats for a specific user"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[ERROR] get_user_stats failed: {e}")
        return {}

def get_all_users() -> list:
    """Get all users — for admin monitoring"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").order("last_login", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[ERROR] get_all_users failed: {e}")
        return []

def get_all_queries(email: str = None) -> list:
    """Get all queries — optionally filter by user"""
    try:
        supabase = get_supabase_client()
        if email:
            result = supabase.table("queries").select("*").eq("email", email).order("created_at", desc=True).execute()
        else:
            result = supabase.table("queries").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[ERROR] get_all_queries failed: {e}")
        return []