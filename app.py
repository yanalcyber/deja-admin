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
    .task-card {
        background-color: #1E1E1E; border-radius: 12px; padding: 15px;
        border-right: 8px solid #4CAF50; margin-bottom: 15px; transition: 0.3s;
    }
    .task-card:hover { transform: scale(1.02); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة قاعدة البيانات
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
    # --- وظائف الأعضاء ---
    def get_all_members(self):
        res = supabase.table("members").select("*").order("id", desc=True).execute()
        return res.data
    
    def add_member(self, data):
        row = {"name": data[0], "phone": data[2], "team": data[4], "role": data[5], "residence": data[6], "points": data[11], "gender": data[13]}
        supabase.table("members").insert(row).execute()

    # --- وظائف المهام (الجديدة) ---
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
        l_phone = st.text_input("رقم الهاتف")
        l_pass = st.text_input("كلمة المرور", type="password")
        if st.button("دخول 🚀", use_container_width=True, type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                st.session_state['user'] = res.user
                st.rerun()
            except: st.error("خطأ في البيانات")

# ==========================================
# 4. لوحة التحكم
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة الرئيسية:", ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "➕ إضافة عضو جديد"])
        st.markdown("---")
        if st.button("خروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- صفحة بطاقات المهام ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة المهام والمشاريع")
        
        # زر الإضافة (Modal)
        if st.button("➕ إنشاء مهمة جديدة", type="primary"):
            st.session_state.show_task_form = True

        if st.session_state.get('show_task_form'):
            with st.expander("📝 تفاصيل المهمة الجديدة", expanded=True):
                with st.form("task_form"):
                    t_name = st.text_input("اسم المهمة *")
                    t_summary = st.text_area("ملخص المهمة")
                    t_level = st.select_slider("مستوى الأهمية", options=TASK_LEVELS)
                    
                    # اختيار المسؤولين (أعضاء + فرق)
                    all_m = [m['name'] for m in db.get_all_members()]
                    t_assignees = st.multiselect("مين المسؤول؟", options=TEAMS_LIST + all_m)
                    
                    if st.form_submit_button("إرسال المهمة 🚀"):
                        if t_name:
                            db.add_task((t_name, t_summary, t_level, ", ".join(t_assignees)))
                            st.success("تمت إضافة المهمة!")
                            st.session_state.show_task_form = False
                            st.rerun()

        st.markdown("---")
        tasks = db.get_all_tasks()
        
        if tasks:
            # تقسيم المهام حسب الحالة
            t_col1, t_col2, t_col3 = st.columns(3)
            
            with t_col1:
                st.subheader("⏳ قيد الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        st.caption(f"📍 المسؤول: {t['assignees']}")
                        st.write(t['summary'])
                        st.info(f"المستوى: {t['level']}")
                        if st.button("بدء العمل ▶️", key=f"start_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل")
                            st.rerun()

            with t_col2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        st.caption(f"📍 المسؤول: {t['assignees']}")
                        st.write(t['summary'])
                        st.warning(f"المستوى: {t['level']}")
                        if st.button("تم الإنجاز ✅", key=f"done_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز")
                            st.rerun()

            with t_col3:
                st.subheader("✅ تم الإنجاز")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.markdown(f"### {t['name']}")
                        st.caption(f"📍 المسؤول: {t['assignees']}")
                        st.success(f"المستوى: {t['level']}")
                        st.write("عاش يا أبطال! 💪")
        else:
            st.info("لا يوجد مهام حالية. ابدأ بإضافة أول مهمة!")

    # --- باقي الصفحات (الأعضاء) ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 أعضاء فريق Deja")
        m_data = db.get_all_members()
        if m_data:
            cols = st.columns(3)
            for i, m in enumerate(m_data):
                with cols[i % 3]:
                    bg = "#0e2038" if m.get('gender') == "ذكر" else "#1E1E1E"
                    c_html = f"<div style='background-color:{bg}; padding:15px; border-radius:12px; border: 1px solid #444; direction:rtl; text-align:right;'><h4 style='color:#FFF; margin-top:0;'>👤 {m['name']}</h4><p style='font-size:13px; color:#4CAF50; font-weight:bold;'>💯 {m['points']} نقطة</p></div>"
                    st.markdown(c_html, unsafe_allow_html=True)
                    st.write("")
