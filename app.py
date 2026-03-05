{\rtf1}import streamlit as st
from auth import show_login_screen
from dashboard import show_dashboard_screen

# إعدادات الصفحة لازم تكون أول سطر
st.set_page_config(page_title="Deja Admin Panel", page_icon="👥", layout="wide")

# تهيئة الجلسة
if 'user' not in st.session_state:
    st.session_state['user'] = None

# التوجيه (Routing)
if st.session_state['user'] is None:
    show_login_screen()
else:
    show_dashboard_screen()