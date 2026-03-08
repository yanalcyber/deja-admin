import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# ==========================================
# 1. إعدادات التصميم والواجهة
# ==========================================
st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; }
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea, .stRadio, .stMultiSelect {
        direction: rtl !important; text-align: right !important;
    }
    /* تصميم بطاقة المهام */
    .task-card { background-color: #262730; border-radius: 10px; padding: 15px; border-right: 5px solid #4CAF50; margin-bottom: 10px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة قاعدة البيانات (مطابقة لصورك 100%)
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
    # جلب الأعضاء - بستخدم أسماء الأعمدة من صورك
    def get_all_members(self):
        res = supabase.table("members").select("*").order("id", desc=True).execute()
        return res.data
    
    # إضافة عضو - مطابقة لأسماء الأعمدة في Supabase
    def add_member(self, data):
        row = {
            "name": data[0], "phone": data[1], "team": data[2], "role": data[3],
            "House location": data[4], "points": 0, "gender": data[5],
            "academic_year": data[6], "university": data[7]
        }
        supabase.table("members").insert(row).execute()

    # إضافة مهمة - حل مشكلة الـ APIError
    def add_task(self, data):
        row = {"name": data[0], "summary": data[1], "level": data[2], "assignees": data[3], "status": "قيد الانتظار"}
        supabase.table("tasks").insert(row).execute()

    def get_all_tasks(self):
        res = supabase.table("tasks").select("*").order("id", desc=True).execute()
        return res.data

    def update_task_status(self, task_id, new_status):
        supabase.table("tasks").update({"status": new_status}).eq("id", task_id).execute()

db = DatabaseManager()

TEAMS = ["فريق الإدارة", "فريق الميديا", "فريق IT", "فريق التنظيم", "فريق اللوجستك"]
ROLES = ["عضو", "إداري", "قائد فريق"]
TASK_LEVELS = ["🟢 منخفض", "🟡 متوسط", "🔴 مرتفع"]

# ==========================================
# 3. واجهة الدخول (حل مشكلة Duplicate ID)
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab1:
            l_phone = st.text_input("رقم الهاتف", key="login_phone") # مفتاح فريد
            l_pass = st.text_input("كلمة المرور", type="password", key="login_pass")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except: st.error("❌ بيانات الدخول غير صحيحة.")
        with tab2:
            s_name = st.text_input("الاسم الكامل", key="signup_name")
            s_phone = st.text_input("رقم الهاتف", key="signup_phone") # مفتاح فريد لحل الأيرور
            s_pass = st.text_input("كلمة المرور", type="password", key="signup_pass")
            if st.button("إنشاء الحساب ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("✅ تم! سجل دخول الآن.")
                except: st.error("❌ حدث خطأ.")

# ==========================================
# 4. لوحة الإدارة (بعد الدخول)
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة:", ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "➕ إضافة عضو"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- صفحة المهام (Kanban) ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة مهام الفريق")
        with st.expander("➕ إنشاء مهمة جديدة"):
            with st.form("task_form"):
                t_n = st.text_input("اسم المهمة *")
                t_s = st.text_area("الملخص")
                t_l = st.selectbox("المستوى", TASK_LEVELS)
                m_names = [m['name'] for m in db.get_all_members()]
                t_a = st.multiselect("المسؤولين", options=TEAMS + m_names)
                if st.form_submit_button("إرسال المهمة 🚀"):
                    if t_n:
                        db.add_task((t_n, t_s, t_l, ", ".join(t_a)))
                        st.success("تم!"); st.rerun()

        tasks = db.get_all_tasks()
        if tasks:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("⏳ قيد الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}\n📍 {t['assignees']}")
                        st.write(t['summary'])
                        if st.button("بدء ▶️", key=f"s_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل"); st.rerun()
            with c2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        if st.button("تم ✅", key=f"d_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز"); st.rerun()
            with c3:
                st.subheader("✅ تم الإنجاز")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.write(f"### {t['name']}\nعاش يا وحش! 💪")

    # --- صفحة الأعضاء (حل مشكلة ظهور الأكواد كنصوص) ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 فريق Deja")
        members = db.get_all_members()
        if members:
            cols = st.columns(3)
            for i, m in enumerate(members):
                with cols[i % 3]:
                    # الألوان حسب الجنس
                    bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                    
                    # الأوسمة
                    badges = f"<div style='background-color:#FFD700; color:black; padding:2px 8px; border-radius:10px; font-size:10px; position:absolute; left:10px; top:10px;'>{m['role']}</div>" if m['role'] != 'عضو' else ""
                    
                    # رسم البطاقة كـ HTML
                    card_html = f"""
                    <div style='background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:140px; margin-bottom:10px; text-align:right;'>
                        {badges}
                        <h4 style='color:white; margin:0;'>👤 {m['name']}</h4>
                        <p style='color:#CCC; font-size:13px; margin:10px 0;'>📍 {m.get('House location', '-')}</p>
                        <p style='color:#4CAF50; font-weight:bold;'>💯 {m.get('points', 0)} نقطة</p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True) # تم تفعيل HTML
