import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم (RTL & UI)
# ==========================================
st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# حل مشكلة تداخل النصوص وظهور الأكواد
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; }
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea, .stRadio, .stMultiSelect {
        direction: rtl !important; text-align: right !important;
    }
    .task-column { background-color: #1E1E1E; border-radius: 10px; padding: 15px; min-height: 400px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الربط مع Supabase
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state['user'] = None

class DatabaseManager:
    # جلب الأعضاء مع مراعاة أسماء الأعمدة في صورتك
    def get_all_members(self):
        res = supabase.table("members").select("*").order("id", desc=True).execute()
        return res.data
    
    # حل مشكلة خطأ العمود 'major'
    def update_member(self, m_id, data):
        row = {
            "name": data[0], "phone": data[1], "team": data[2], "role": data[3],
            "House location": data[4], "points": data[5], "gender": data[6]
        }
        supabase.table("members").update(row).eq("id", m_id).execute()

    # نظام المهام - حل خطأ السطر 55
    def add_task(self, data):
        row = {"name": data[0], "summary": data[1], "level": data[2], "assignees": data[3], "status": "قيد الانتظار"}
        supabase.table("tasks").insert(row).execute()

    def get_all_tasks(self):
        res = supabase.table("tasks").select("*").order("id", desc=True).execute()
        return res.data

    def update_task_status(self, t_id, status):
        supabase.table("tasks").update({"status": status}).eq("id", t_id).execute()

db = DatabaseManager()

# القوائم الأساسية
TEAMS = ["فريق الإدارة", "فريق الميديا", "فريق IT", "فريق التنظيم", "فريق اللوجستك"]
TASK_LEVELS = ["🟢 منخفض", "🟡 متوسط", "🔴 مرتفع"]

# ==========================================
# 3. واجهة الدخول
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab1:
            l_phone = st.text_input("رقم الهاتف", key="login_phone")
            l_pass = st.text_input("كلمة المرور", type="password", key="login_pass")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except: st.error("❌ خطأ في البيانات أو الحساب غير مفعل.")
        with tab2:
            s_name = st.text_input("الاسم الكامل", key="reg_name")
            s_phone = st.text_input("رقم الهاتف", key="reg_phone") # حل Duplicate ID
            s_pass = st.text_input("كلمة المرور (6 خانات)", type="password", key="reg_pass")
            if st.button("إنشاء الحساب ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("✅ تم! سجل دخول الآن.")
                except: st.error("❌ حدث خطأ أثناء التسجيل.")

# ==========================================
# 4. لوحة التحكم الرئيسية
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة:", ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "⚙️ الإعدادات"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- نظام المهام (Kanban Board) ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة مهام الفريق")
        with st.expander("➕ إنشاء مهمة جديدة"):
            with st.form("task_form"):
                t_name = st.text_input("اسم المهمة *")
                t_summary = st.text_area("ملخص")
                t_level = st.selectbox("المستوى", TASK_LEVELS)
                m_names = [m['name'] for m in db.get_all_members()]
                t_assignees = st.multiselect("المسؤولين", options=TEAMS + m_names)
                if st.form_submit_button("إرسال المهمة 🚀"):
                    if t_name:
                        db.add_task((t_name, t_summary, t_level, ", ".join(t_assignees)))
                        st.success("تمت الإضافة!"); st.rerun()

        tasks = db.get_all_tasks()
        if tasks:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("⏳ قيد الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}\n**📍 {t['assignees']}**\n\n{t['summary']}")
                        st.info(t['level'])
                        if st.button("بدء ▶️", key=f"s_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل"); st.rerun()
            with c2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}\n**📍 {t['assignees']}**")
                        if st.button("تم ✅", key=f"d_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز"); st.rerun()
            with c3:
                st.subheader("✅ تم الإنجاز")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}\n**عاش يا أبطال! 💪**")

    # --- بطاقات الأعضاء (ملونة وبها أوسمة) ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 أعضاء فريق Deja")
        members = db.get_all_members()
        if members:
            cols = st.columns(3)
            for i, m in enumerate(members):
                with cols[i % 3]:
                    # الألوان حسب الجنس
                    bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                    
                    # بناء الأوسمة
                    badges = ""
                    if m['role'] in ['إداري', 'قائد فريق']:
                        badges += f"<div style='background-color:#FFD700; color:black; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:bold; margin-bottom:5px;'>{m['role']}</div>"
                    
                    # رسم البطاقة كـ HTML حقيقي
                    card_html = f"""
                    <div style='background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:160px; margin-bottom:10px; direction:rtl; text-align:right;'>
                        <div style='position:absolute; top:10px; left:10px; display:flex; flex-direction:column; gap:3px;'>{badges}</div>
                        <h4 style='color:white; margin:0;'>👤 {m['name']}</h4>
                        <p style='color:#CCC; font-size:13px; margin:10px 0;'>📍 {m.get('House location', '-')}</p>
                        <p style='color:#4CAF50; font-weight:bold;'>💯 {m.get('points', 0)} نقطة</p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button("المزيد ➕", key=f"btn_{m['id']}", use_container_width=True):
                        # هنا تفتح نافذة التعديل المنبثقة
                        st.info("سيتم فتح تفاصيل التعديل...")
