import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم (حل مشكلة التداخل)
# ==========================================
st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# تصميم CSS لضمان تناسق الخطوط والاتجاهات
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
# 2. إدارة قاعدة البيانات (تطابق مع جداولك الحقيقية)
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
    
    # حل مشكلة خطأ العمود 'major' والعمود 'residence'
    def update_member(self, m_id, data):
        # لاحظ استخدام 'House location' و 'academic_year' كما في صورتك
        row = {
            "name": data[0], "phone": data[1], "team": data[2], "role": data[3],
            "House location": data[4], "points": data[5], "gender": data[6],
            "academic_year": data[7] # استخدام هذا العمود للتخصص كما يظهر في بياناتك
        }
        supabase.table("members").update(row).eq("id", m_id).execute()

    # نظام المهام
    def add_task(self, data):
        row = {"name": data[0], "summary": data[1], "level": data[2], "assignees": data[3], "status": "قيد الانتظار"}
        supabase.table("tasks").insert(row).execute()

    def get_all_tasks(self):
        res = supabase.table("tasks").select("*").order("id", desc=True).execute()
        return res.data

    def update_task_status(self, t_id, status):
        supabase.table("tasks").update({"status": status}).eq("id", t_id).execute()

db = DatabaseManager()

TEAMS = ["فريق الإدارة", "فريق الميديا", "فريق IT", "فريق التنظيم", "فريق اللوجستك"]
TASK_LEVELS = ["🟢 منخفض", "🟡 متوسط", "🔴 مرتفع"]

# ==========================================
# 3. واجهة الدخول (حل مشكلة العناصر المتكررة)
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab1:
            l_phone = st.text_input("رقم الهاتف", key="log_phone") # استخدام key فريد
            l_pass = st.text_input("كلمة المرور", type="password", key="log_pass")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except: st.error("❌ خطأ في البيانات")
        with tab2:
            s_name = st.text_input("الاسم الكامل", key="reg_name")
            s_phone = st.text_input("رقم الهاتف", key="reg_phone") # حل خطأ التكرار
            s_pass = st.text_input("كلمة المرور", type="password", key="reg_pass")
            if st.button("إنشاء ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("✅ تم! سجل دخول الآن")
                except: st.error("❌ خطأ")

# ==========================================
# 4. لوحة الإدارة (بعد الدخول)
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة:", ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "➕ إضافة عضو"])
        st.markdown("---")
        if st.button("خروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- نظام المهام (Kanban) ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة مهام الفريق")
        with st.expander("➕ إنشاء مهمة جديدة"):
            with st.form("t_form"):
                t_n = st.text_input("اسم المهمة")
                t_s = st.text_area("الملخص")
                t_l = st.selectbox("المستوى", TASK_LEVELS)
                m_names = [m['name'] for m in db.get_all_members()]
                t_a = st.multiselect("المسؤولين", options=TEAMS + m_names)
                if st.form_submit_button("إرسال المهمة 🚀"):
                    db.add_task((t_n, t_s, t_l, ", ".join(t_a))); st.success("تم!"); st.rerun()

        tasks = db.get_all_tasks()
        if tasks:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("⏳ قيد الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.write(f"### {t['name']}")
                        st.caption(f"📍 {t['assignees']}")
                        st.info(t['level'])
                        if st.button("بدء ▶️", key=f"s_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل"); st.rerun()
            with c2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.write(f"### {t['name']}")
                        if st.button("تم ✅", key=f"d_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز"); st.rerun()
            with c3:
                st.subheader("✅ تم الإنجاز")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.write(f"### {t['name']}")
                        st.success("عاش يا بطل! 💪")

    # --- بطاقات الأعضاء (حل مشكلة ظهور الأكواد كنصوص) ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 أعضاء فريق Deja")
        members = db.get_all_members()
        if members:
            cols = st.columns(3)
            for i, m in enumerate(members):
                with cols[i % 3]:
                    # الألوان حسب الجنس
                    bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                    
                    # الأوسمة
                    badges = ""
                    if m['role'] != 'عضو':
                        badges += f"<div style='background-color:#FFD700; color:black; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:bold;'>{m['role']}</div>"
                    
                    # رسم البطاقة باستخدام HTML حقيقي
                    c_html = f"""
                    <div style='background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:160px; margin-bottom:10px; text-align:right;'>
                        <div style='position:absolute; top:10px; left:10px;'>{badges}</div>
                        <h4 style='color:white; margin:0;'>👤 {m['name']}</h4>
                        <p style='color:#CCC; font-size:13px; margin:10px 0;'>📍 {m.get('House location', '-')}</p>
                        <p style='color:#4CAF50; font-weight:bold;'>💯 {m.get('points', 0)} نقطة</p>
                    </div>
                    """
                    # السطر السحري لحل مشكلة ظهور الكود كنص
                    st.markdown(c_html, unsafe_allow_html=True)
                    
                    if st.button("المزيد ➕", key=f"btn_{m['id']}", use_container_width=True):
                        st.info(f"عرض تفاصيل {m['name']}...")
