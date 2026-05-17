import json
import os
from datetime import datetime
import streamlit as st

TRACKER_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def track_user(user_info: dict):
    """Save user info and track their usage"""
    data = load_user_data()
    email = user_info.get("email", "unknown")

    if email not in data:
        # New user — save their info
        data[email] = {
            "name": user_info.get("name", ""),
            "email": email,
            "picture": user_info.get("picture", ""),
            "first_login": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "total_queries": 0,
            "total_tokens_used": 0,
            "sessions": []
        }
        print(f"[INFO] New user registered: {email}")
    else:
        # Existing user — update last login
        data[email]["last_login"] = datetime.now().isoformat()

    save_user_data(data)
    return data[email]

def track_query(email: str, query: str, tokens_used: int = 0):
    """Track each query made by the user"""
    data = load_user_data()

    if email in data:
        data[email]["total_queries"] += 1
        data[email]["total_tokens_used"] += tokens_used
        data[email]["sessions"].append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens_used
        })
        save_user_data(data)

def get_user_stats(email: str) -> dict:
    """Get stats for a specific user"""
    data = load_user_data()
    return data.get(email, {})

def get_all_users() -> list:
    """Get all registered users — for admin view"""
    data = load_user_data()
    return [
        {
            "name": v["name"],
            "email": k,
            "total_queries": v["total_queries"],
            "total_tokens": v["total_tokens_used"],
            "first_login": v["first_login"],
            "last_login": v["last_login"]
        }
        for k, v in data.items()
    ]