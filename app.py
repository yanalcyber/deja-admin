import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم الاحترافي
# ==========================================
st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; }
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea, .stRadio, .stMultiSelect {
        direction: rtl !important; text-align: right !important;
    }
    /* تحسين شكل بطاقات المهام */
    .task-container {
        background-color: #262730; border-radius: 10px; padding: 15px; border-top: 5px solid #4CAF50; margin-bottom: 20px;
    }
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
    # --- الأعضاء ---
    def get_all_members(self):
        res = supabase.table("members").select("*").order("id", desc=True).execute()
        return res.data
    
    def update_member(self, member_id, data):
        row = {"name": data[0], "phone": data[2], "team": data[4], "role": data[5], "residence": data[6], "points": data[11], "gender": data[13]}
        supabase.table("members").update(row).eq("id", member_id).execute()

    def add_member(self, data):
        row = {"name": data[0], "phone": data[2], "team": data[4], "role": data[5], "residence": data[6], "points": 0, "gender": data[13]}
        supabase.table("members").insert(row).execute()

    # --- المهام ---
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
ROLES = ["عضو", "إداري", "قائد فريق"]
GENDERS = ["غير محدد", "ذكر", "أنثى"]
TASK_LEVELS = ["🟢 منخفض", "🟡 متوسط", "🔴 مرتفع"]

# ==========================================
# 3. واجهة الدخول والخروج
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
                except: st.error("❌ خطأ في البيانات أو الحساب غير مفعل.")
        with tab2:
            s_name = st.text_input("الاسم الكامل")
            s_phone = st.text_input("رقم الهاتف")
            s_pass = st.text_input("كلمة المرور (6 خانات)", type="password")
            if st.button("إنشاء الحساب ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("✅ تم الإنشاء! جرب الدخول الآن.")
                except: st.error("❌ حدث خطأ أثناء التسجيل.")

# ==========================================
# 4. لوحة الإدارة الرئيسية
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة الرئيسية:", ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "➕ إضافة عضو جديد"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- الصفحة 1: بطاقات المهام (Kanban) ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة المهام")
        with st.expander("➕ إنشاء مهمة جديدة"):
            with st.form("new_task"):
                t_name = st.text_input("اسم المهمة *")
                t_summary = st.text_area("ملخص المهمة")
                t_level = st.select_slider("المستوى", options=TASK_LEVELS)
                all_m = [m['name'] for m in db.get_all_members()]
                t_assignees = st.multiselect("المسؤولين", options=TEAMS_LIST + all_m)
                if st.form_submit_button("إرسال المهمة 🚀"):
                    if t_name:
                        db.add_task((t_name, t_summary, t_level, ", ".join(t_assignees)))
                        st.success("✅ تمت الإضافة!")
                        st.rerun()

        st.markdown("---")
        tasks = db.get_all_tasks()
        if tasks:
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                st.subheader("⏳ قيد الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.markdown(f"**{t['name']}**")
                        st.caption(f"📍 {t['assignees']}")
                        st.write(t['summary'])
                        st.info(t['level'])
                        if st.button("بدء ▶️", key=f"s_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل"); st.rerun()
            with t_col2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.markdown(f"**{t['name']}**")
                        st.caption(f"📍 {t['assignees']}")
                        st.write(t['summary'])
                        if st.button("تم ✅", key=f"d_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز"); st.rerun()
            with t_col3:
                st.subheader("✅ تم الإنجاز")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.markdown(f"**{t['name']}**")
                        st.success("عاش يا وحش! 💪")
        else: st.info("لا يوجد مهام حالياً.")

    # --- الصفحة 2: بطاقات الأعضاء (ملونة وبها أوسمة) ---
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
                        badges += f"<div style='background-color:#FFD700; color:#000; padding:2px 8px; border-radius:10px; font-size:10px; margin-bottom:5px; font-weight:bold;'>{m['role']}</div>"
                    m_teams = [t.strip() for t in m['team'].split(",")] if m['team'] else []
                    for t in m_teams:
                        color = "#E53935" if "ميديا" in t else ("#4CAF50" if "IT" in t else "#00BCD4")
                        badges += f"<div style='background-color:{color}; color:#FFF; padding:2px 8px; border-radius:10px; font-size:10px; margin-bottom:5px;'>{t}</div>"

                    card_html = f"""
                    <div style='background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:160px; margin-bottom:15px; direction:rtl; text-align:right;'>
                        <div style='position:absolute; top:10px; left:10px; display:flex; flex-direction:column; gap:3px;'>{badges}</div>
                        <h4 style='color:#FFF; margin-top:0;'>👤 {m['name']}</h4>
                        <p style='font-size:14px; color:#CCC;'>📍 {m.get('residence', '-')}</p>
                        <p style='font-size:14px; color:#4CAF50; font-weight:bold;'>💯 {m['points']} نقطة</p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True) # تم التأكد من تفعيل HTML
                    
                    # زر "المزيد" لفتح نافذة التعديل
                    if st.button("المزيد ➕", key=f"btn_{m['id']}", use_container_width=True):
                        st.session_state.selected_member = m
                        st.rerun()

    elif menu == "➕ إضافة عضو جديد":
        st.title("➕ تسجيل عضو")
        with st.form("add_member"):
            n = st.text_input("الاسم الكامل *")
            g = st.selectbox("الجنس", GENDERS)
            ts = st.multiselect("الفرق", TEAMS_LIST)
            r = st.selectbox("الرتبة", ROLES)
            res = st.text_input("مكان السكن")
            if st.form_submit_button("إرسال للعضوية 🚀"):
                if n:
                    db.add_member((n, "", "", "", ", ".join(ts), r, res, "", "", "", "", 0, "", g))
                    st.success("✅ تمت الإضافة!")
