import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; }
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea, .stRadio, .stMultiSelect {
        direction: rtl !important; text-align: right !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الربط مع قاعدة البيانات
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
    def get_all_members(self):
        res = supabase.table("members").select("*").order("id", desc=True).execute()
        return res.data
    
    def add_member(self, data):
        row = {"name": data[0], "phone": data[2], "team": data[4], "role": data[5], "residence": data[6], "points": data[11], "gender": data[13]}
        supabase.table("members").insert(row).execute()

    def add_task(self, data):
        row = {"name": data[0], "summary": data[1], "level": data[2], "assignees": data[3], "status": "قيد الانتظار"}
        supabase.table("tasks").insert(row).execute()

    def get_all_tasks(self):
        res = supabase.table("tasks").select("*").order("id", desc=True).execute()
        return res.data

    def update_task_status(self, task_id, new_status):
        supabase.table("tasks").update({"status": new_status}).eq("id", task_id).execute()

db = DatabaseManager()

TEAMS_LIST = ["فريق الإدارة", "فريق الميديا", "فريق IT", "فريق التنظيم", "فريق اللوجستك"]
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
            l_phone = st.text_input("رقم الهاتف")
            l_pass = st.text_input("كلمة المرور", type="password")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except: st.error("خطأ في البيانات")
        with tab2:
            s_name = st.text_input("الاسم الكامل")
            s_phone = st.text_input("رقم الهاتف")
            s_pass = st.text_input("كلمة مرور (6 خانات)", type="password")
            if st.button("إنشاء ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("تم! سجل دخول الآن")
                except: st.error("خطأ")

# ==========================================
# 4. لوحة التحكم (الرئيسية)
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة الرئيسية:", ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "➕ إضافة عضو جديد"])
        st.markdown("---")
        if st.button("خروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- صفحة بطاقات المهام (نظام Kanban) ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة المهام")
        
        # زر إنشاء مهمة
        with st.expander("➕ إنشاء مهمة جديدة", expanded=False):
            with st.form("new_task"):
                t_name = st.text_input("اسم المهمة *")
                t_summary = st.text_area("ملخص المهمة")
                t_level = st.select_slider("المستوى", options=TASK_LEVELS)
                m_names = [m['name'] for m in db.get_all_members()]
                t_assignees = st.multiselect("المسؤولين", options=TEAMS_LIST + m_names)
                if st.form_submit_button("إرسال المهمة 🚀"):
                    if t_name:
                        db.add_task((t_name, t_summary, t_level, ", ".join(t_assignees)))
                        st.success("تمت الإضافة!")
                        st.rerun()

        st.markdown("---")
        tasks = db.get_all_tasks()
        if tasks:
            t_col1, t_col2, t_col3 = st.columns(3)
            # ⏳ قيد الانتظار
            with t_col1:
                st.subheader("⏳ قيد الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        st.caption(f"📍 {t['assignees']}")
                        st.write(t['summary'])
                        st.info(t['level'])
                        if st.button("بدء العمل ▶️", key=f"s_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل"); st.rerun()
            # ⚙️ جاري العمل
            with t_col2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        st.caption(f"📍 {t['assignees']}")
                        st.write(t['summary'])
                        if st.button("تم الإنجاز ✅", key=f"d_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز"); st.rerun()
            # ✅ تم الإنجاز
            with t_col3:
                st.subheader("✅ تم الإنجاز")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        st.caption(f"📍 {t['assignees']}")
                        st.success("عاش يا بطل! 💪")
        else: st.info("لا يوجد مهام حالياً.")

    # --- صفحة بطاقات الأعضاء ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 أعضاء الفريق")
        m_data = db.get_all_members()
        if m_data:
            cols = st.columns(3)
            for i, m in enumerate(m_data):
                with cols[i % 3]:
                    # الألوان والأوسمة حسب الجنس والرتبة
                    bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                    badge = f"<div style='background-color:#FFD700; color:black; padding:2px 8px; border-radius:10px; font-size:10px; position:absolute; left:10px; top:10px;'>{m['role']}</div>" if m['role'] != 'عضو' else ""
                    
                    c_html = f"<div style='background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:120px; margin-bottom:10px;'>{badge}<h4 style='color:white; margin:0;'>👤 {m['name']}</h4><p style='color:#4CAF50; font-weight:bold; margin-top:10px;'>💯 {m['points']} نقطة</p></div>"
                    st.markdown(c_html, unsafe_allow_html=True)
