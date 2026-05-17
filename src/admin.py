import streamlit as st
from src.db import get_all_users, get_all_queries
from datetime import datetime

ADMIN_EMAIL = "apcodes04@gmail.com"

def show_admin_dashboard(user_email: str):
    """Only show to admin"""
    if user_email != ADMIN_EMAIL:
        return

    st.divider()
    st.markdown("### 🔐 Admin Dashboard")

    tab1, tab2 = st.tabs(["👥 Users", "💬 Queries"])

    with tab1:
        users = get_all_users()
        st.markdown(f"**Total users: {len(users)}**")

        # Summary stats
        col1, col2, col3 = st.columns(3)
        total_queries = sum(u.get("total_queries", 0) for u in users)
        total_tokens = sum(u.get("total_tokens", 0) for u in users)

        with col1:
            st.metric("Total Users", len(users))
        with col2:
            st.metric("Total Queries", total_queries)
        with col3:
            st.metric("Total Tokens Used", f"{total_tokens:,}")

        st.markdown("---")

        # Users table
        for user in users:
            with st.expander(f"👤 {user.get('name', 'Unknown')} — {user.get('email', '')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"📧 **Email:** {user.get('email', '')}")
                    st.write(f"💬 **Total Queries:** {user.get('total_queries', 0)}")
                    st.write(f"🔢 **Tokens Used:** {user.get('total_tokens', 0):,}")
                with col2:
                    st.write(f"🕐 **First Login:** {user.get('first_login', '')[:10]}")
                    st.write(f"🕐 **Last Login:** {user.get('last_login', '')[:10]}")

    with tab2:
        queries = get_all_queries()
        st.markdown(f"**Total queries logged: {len(queries)}**")

        for q in queries[:50]:  # show latest 50
            with st.expander(f"💬 {q.get('email', '')} — {q.get('created_at', '')[:16]}"):
                st.write(f"**Question:** {q.get('query', '')}")
                st.write(f"**Answer:** {q.get('answer', '')[:300]}...")
                st.write(f"**Tokens:** {q.get('tokens_used', 0)}")