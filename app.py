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
    def get_all_members(self):
        res = supabase.table("members").select("*").order("id", desc=True).execute()
        return res.data
    
    # دالة جديدة للبحث عن العضو برقم الهاتف عشان الصلاحيات
    def get_member_by_phone(self, phone):
        res = supabase.table("members").select("*").eq("phone", phone).execute()
        return res.data

    def update_member(self, m_id, data):
        row = {
            "name": data[0], "phone": data[1], "team": data[2], "role": data[3],
            "House location": data[4], "points": data[5], "gender": data[6],
            "academic_year": data[7]
        }
        supabase.table("members").update(row).eq("id", m_id).execute()

    def add_member(self, data):
        row = {
            "name": data[0], "phone": data[1], "team": data[2], "role": data[3],
            "House location": data[4], "points": 0, "gender": data[5],
            "academic_year": data[6], "university": data[7]
        }
        supabase.table("members").insert(row).execute()
        
    def delete_member(self, m_id):
        supabase.table("members").delete().eq("id", m_id).execute()

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
ROLES = ["عضو", "إداري", "قائد فريق", "غير محدد"]
TASK_LEVELS = ["🟢 منخفض", "🟡 متوسط", "🔴 مرتفع"]
GENDERS = ["غير محدد", "ذكر", "أنثى"]

# ==========================================
# 3. النافذة المنبثقة للبطاقة (مربوطة بالصلاحيات)
# ==========================================
@st.dialog("🪪 بطاقة العضو الشاملة")
def member_details_dialog(member, is_admin):
    st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>{member['name']}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"📞 **الهاتف:** {member['phone']}")
        st.write(f"👥 **الفرق:** {member.get('team', 'غير محدد')}")
    with c2:
        st.write(f"⭐ **الرتبة:** {member['role']}")
        st.write(f"🏠 **السكن:** {member.get('House location', '-')}")
        
    st.write(f"💯 **النقاط:** {member.get('points', 0)}")
    st.markdown("---")
    
    # 🔒 إذا كان إداري فقط، بيقدر يشوف فورم التعديل والحذف
    if is_admin:
        with st.expander("✏️ إعدادات الإدارة (تعديل بيانات العضو)"):
            with st.form(key=f"edit_form_{member['id']}"):
                e_name = st.text_input("الاسم", value=member['name'])
                current_teams = [t.strip() for t in member.get('team', '').split(",")] if member.get('team') else []
                e_teams = st.multiselect("الفرق", TEAMS, default=[t for t in current_teams if t in TEAMS])
                e_role = st.selectbox("الرتبة", ROLES, index=ROLES.index(member['role']) if member['role'] in ROLES else 3)
                e_gender = st.selectbox("الجنس", GENDERS, index=GENDERS.index(member.get('gender', 'غير محدد')) if member.get('gender', 'غير محدد') in GENDERS else 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    e_phone = st.text_input("رقم الهاتف", value=member['phone'])
                with col2:
                    e_pts = st.number_input("النقاط", value=int(member.get('points', 0)), step=1)
                
                e_res = st.text_input("السكن", value=member.get('House location', ''))
                e_year = st.text_input("التخصص/السنة", value=member.get('academic_year', ''))
                
                if st.form_submit_button("حفظ التحديثات ✅", use_container_width=True):
                    db.update_member(member['id'], (e_name, e_phone, ", ".join(e_teams), e_role, e_res, e_pts, e_gender, e_year))
                    st.success("تم الحفظ!")
                    st.rerun()

        if st.button("حذف الحساب نهائياً ❌", type="secondary", use_container_width=True):
            db.delete_member(member['id'])
            st.rerun()

# ==========================================
# 4. واجهة الدخول وإنشاء الحساب الذكي
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab1:
            l_phone = st.text_input("رقم الهاتف", key="log_phone")
            l_pass = st.text_input("كلمة المرور", type="password", key="log_pass")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    clean_p = l_phone.strip()
                    res = supabase.auth.sign_in_with_password({"email": f"{clean_p}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    
                    # 🔍 فحص سحري: هل العضو موجود بالجدول؟ إذا لأ، ضيفه تلقائياً كـ "غير محدد"
                    existing_member = db.get_member_by_phone(clean_p)
                    if not existing_member:
                        u_name = res.user.user_metadata.get('name', 'عضو جديد')
                        # إضافة: (الاسم، الهاتف، الفريق، الرتبة، السكن، الجنس، التخصص، الجامعة)
                        db.add_member((u_name, clean_p, "غير محدد", "غير محدد", "", "غير محدد", "", ""))
                    st.rerun()
                except: st.error("❌ خطأ في البيانات")
        with tab2:
            s_name = st.text_input("الاسم الكامل", key="reg_name")
            s_phone = st.text_input("رقم الهاتف", key="reg_phone")
            s_pass = st.text_input("كلمة المرور", type="password", key="reg_pass")
            if st.button("إنشاء ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("✅ تم! سجل دخول الآن من الخانة المجاورة.")
                except: st.error("❌ حدث خطأ.")

# ==========================================
# 5. اللوحة الرئيسية (مبنية على الصلاحيات)
# ==========================================
else:
    # 🔒 سحب رتبة المستخدم الحالي لمعرفة صلاحياته
    user_phone = st.session_state['user'].email.split('@')[0]
    live_user_data = db.get_member_by_phone(user_phone)
    current_role = live_user_data[0].get('role', 'غير محدد') if live_user_data else 'غير محدد'
    is_admin = current_role in ['إداري', 'قائد فريق']

    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        st.caption(f"الرتبة: {current_role}")
        
        # 🔒 إظهار القائمة حسب الصلاحيات
        if is_admin:
            menu_options = ["📋 بطاقات المهام", "👥 بطاقات الأعضاء", "➕ إضافة عضو"]
        else:
            menu_options = ["👥 بطاقات الأعضاء"] # العضو العادي بشوف هاي بس
            
        menu = st.radio("القائمة:", menu_options)
        st.markdown("---")
        if st.button("خروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- صفحة المهام (للإدارة فقط) ---
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
                st.subheader("⏳ الانتظار")
                for t in [x for x in tasks if x['status'] == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.write(f"**{t['name']}**\n\n📍 {t['assignees']}")
                        if st.button("بدء ▶️", key=f"s_{t['id']}"):
                            db.update_task_status(t['id'], "جاري العمل"); st.rerun()
            with c2:
                st.subheader("⚙️ جاري العمل")
                for t in [x for x in tasks if x['status'] == "جاري العمل"]:
                    with st.container(border=True):
                        st.write(f"**{t['name']}**")
                        if st.button("تم ✅", key=f"d_{t['id']}"):
                            db.update_task_status(t['id'], "تم الإنجاز"); st.rerun()
            with c3:
                st.subheader("✅ أُنجزت")
                for t in [x for x in tasks if x['status'] == "تم الإنجاز"]:
                    with st.container(border=True):
                        st.write(f"**{t['name']}**")

    # --- صفحة الأعضاء (الكل بشوفها، بس الإدارة بتعدل) ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 فريق Deja")
        members = db.get_all_members()
        if members:
            cols = st.columns(3)
            for i, m in enumerate(members):
                with cols[i % 3]:
                    bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                    badges = f"<div style='background-color:#FFD700; color:black; padding:2px 8px; border-radius:10px; font-size:10px; position:absolute; left:10px; top:10px;'>{m.get('role', 'عضو')}</div>" if m.get('role') != 'عضو' and m.get('role') != 'غير محدد' else ""
                    
                    c_html = f"""
                    <div style='background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:140px; margin-bottom:10px; text-align:right;'>
                        {badges}
                        <h4 style='color:white; margin:0;'>👤 {m['name']}</h4>
                        <p style='color:#CCC; font-size:13px; margin:10px 0;'>📍 {m.get('House location', '-')}</p>
                        <p style='color:#4CAF50; font-weight:bold;'>💯 {m.get('points', 0)} نقطة</p>
                    </div>
                    """
                    st.markdown(c_html, unsafe_allow_html=True)
                    
                    if st.button("المزيد ➕", key=f"btn_{m['id']}", use_container_width=True):
                        # 🔒 تمرير صلاحية المستخدم لداخل البطاقة
                        member_details_dialog(m, is_admin)

    # --- إضافة عضو (للإدارة فقط) ---
    elif menu == "➕ إضافة عضو":
        st.title("➕ تسجيل عضو يدوياً")
        with st.form("a_form"):
            n = st.text_input("الاسم الكامل *")
            g = st.selectbox("الجنس", GENDERS)
            ts = st.multiselect("الفرق", TEAMS)
            r = st.selectbox("الرتبة", ROLES)
            p = st.text_input("رقم الهاتف")
            res = st.text_input("السكن")
            if st.form_submit_button("إضافة 🚀"):
                if n:
                    db.add_member((n, p, ", ".join(ts), r, res, g, "", ""))
                    st.success("تم!"); st.rerun()
