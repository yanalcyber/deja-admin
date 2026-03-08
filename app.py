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
# 3. نافذة تفاصيل وتفعيل الأعضاء
# ==========================================
@st.dialog("🪪 إدارة بيانات العضو")
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
    
    if is_admin:
        with st.expander("✏️ تفعيل وتعديل الصلاحيات (للإدارة فقط)", expanded=True):
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
                
                if st.form_submit_button("حفظ وتفعيل ✅", use_container_width=True):
                    db.update_member(member['id'], (e_name, e_phone, ", ".join(e_teams), e_role, e_res, e_pts, e_gender, e_year))
                    st.success("تم التفعيل والحفظ بنجاح!")
                    st.rerun()

        if st.button("حذف الحساب نهائياً ❌", type="secondary", use_container_width=True):
            db.delete_member(member['id'])
            st.rerun()

# ==========================================
# 4. واجهة الدخول وإنشاء الحساب (النسخة الخارقة)
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    
    # أداة سحرية لتحويل الأرقام العربية إلى إنجليزية تلقائياً
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        
        # --- تبويبة الدخول ---
        with tab1:
            l_phone = st.text_input("رقم الهاتف", key="log_phone")
            l_pass = st.text_input("كلمة المرور", type="password", key="log_pass")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                if l_phone and l_pass:
                    try:
                        # تنظيف وتوحيد لغة الأرقام
                        clean_p = l_phone.translate(arabic_to_english).replace(" ", "").strip()
                        generated_email = f"{clean_p}@deja.com"
                        
                        res = supabase.auth.sign_in_with_password({"email": generated_email, "password": l_pass})
                        st.session_state['user'] = res.user
                        st.rerun()
                    except Exception as e:
                        st.error("❌ كلمة المرور أو رقم الهاتف غير صحيح.")
                else:
                    st.warning("⚠️ يرجى تعبئة الحقول أولاً.")
                    
        # --- تبويبة إنشاء حساب (مع دخول تلقائي) ---
        with tab2:
            s_name = st.text_input("الاسم الكامل", key="reg_name")
            s_phone = st.text_input("رقم الهاتف", key="reg_phone")
            s_pass = st.text_input("كلمة المرور (6 خانات على الأقل)", type="password", key="reg_pass")
            if st.button("إنشاء حساب 🚀", use_container_width=True):
                if s_name and s_phone and s_pass:
                    if len(s_pass) < 6:
                        st.error("❌ كلمة المرور ضعيفة! يجب أن تكون 6 خانات على الأقل.")
                    else:
                        try:
                            # تنظيف وتوحيد لغة الأرقام
                            clean_p = s_phone.translate(arabic_to_english).replace(" ", "").strip()
                            generated_email = f"{clean_p}@deja.com"
                            
                            # إنشاء الحساب في Supabase
                            res = supabase.auth.sign_up({"email": generated_email, "password": s_pass, "options": {"data": {"name": s_name}}})
                            
                            # إضافة للقاعدة إذا مش موجود
                            if not db.get_member_by_phone(clean_p):
                                db.add_member((s_name, clean_p, "غير محدد", "غير محدد", "", "غير محدد", "", ""))
                            
                            # الدخول التلقائي المباشر!
                            if res.session:
                                st.session_state['user'] = res.user
                                st.rerun()
                            else:
                                st.warning("⚠️ تم إنشاء الحساب، ولكن خيار (تأكيد الإيميل) لا يزال يعمل في Supabase! يرجى إيقافه.")
                        except Exception as e:
                            if "already registered" in str(e).lower():
                                st.error("❌ هذا الرقم مسجل مسبقاً! جرب تسجل دخول من الخانة المجاورة.")
                            else:
                                st.error(f"❌ حدث خطأ: {str(e)}")
                else:
                    st.warning("⚠️ يرجى تعبئة جميع الحقول.")
# ==========================================
# 5. اللوحة الرئيسية (صلاحيات الإدارة)
# ==========================================
else:
    user_phone = st.session_state['user'].email.split('@')[0]
    live_user_data = db.get_member_by_phone(user_phone)
    current_role = live_user_data[0].get('role', 'غير محدد') if live_user_data else 'غير محدد'
    is_admin = current_role in ['إداري', 'قائد فريق']

    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        st.caption(f"الرتبة: {current_role}")
        
        # إضافة الخانة الجديدة للإدارة فقط
        if is_admin:
            menu_options = ["👥 بطاقات الأعضاء", "📋 بطاقات المهام", "➕ إضافة عضو يدوياً", "🔔 طلبات الانضمام"]
        else:
            menu_options = ["👥 بطاقات الأعضاء"]
            
        menu = st.radio("القائمة:", menu_options)
        st.markdown("---")
        if st.button("خروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    # --- 1. صفحة المهام ---
    if menu == "📋 بطاقات المهام":
        st.title("📋 إدارة مهام الفريق")
        with st.expander("➕ إنشاء مهمة جديدة"):
            with st.form("t_form"):
                t_n = st.text_input("اسم المهمة")
                t_s = st.text_area("الملخص")
                t_l = st.selectbox("المستوى", TASK_LEVELS)
                m_names = [m['name'] for m in db.get_all_members() if m.get('role') != 'غير محدد']
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
    # --- 2. صفحة الأعضاء (مع محرك البحث والفلاتر) ---
    elif menu == "👥 بطاقات الأعضاء":
        st.title("👥 فريق Deja المفعلين")
        members = db.get_all_members()
        
        if members:
            # استخراج الأعضاء المفعلين فقط
            active_members = [m for m in members if m.get('role') != 'غير محدد']
            
            if active_members:
                # ---------------------------------------------
                # 🔍 صندوق البحث والفلاتر الذكي
                # ---------------------------------------------
                with st.expander("🔍 أدوات البحث والفلترة", expanded=True):
                    f_col1, f_col2, f_col3 = st.columns(3)
                    with f_col1:
                        search_name = st.text_input("البحث بالاسم 🔎")
                    with f_col2:
                        filter_team = st.selectbox("تصفية حسب الفريق 👥", ["الكل"] + TEAMS)
                    with f_col3:
                        filter_role = st.selectbox("تصفية حسب الرتبة ⭐", ["الكل"] + [r for r in ROLES if r != 'غير محدد'])
                
                # تطبيق الفلاتر برمجياً
                filtered_members = active_members
                
                if search_name:
                    filtered_members = [m for m in filtered_members if search_name in m['name']]
                if filter_team != "الكل":
                    filtered_members = [m for m in filtered_members if m.get('team') and filter_team in m['team']]
                if filter_role != "الكل":
                    filtered_members = [m for m in filtered_members if m.get('role') == filter_role]

                st.markdown("---")
                
                # ---------------------------------------------
                # 🪪 عرض البطاقات بعد الفلترة
                # ---------------------------------------------
                if filtered_members:
                    cols = st.columns(3)
                    for i, m in enumerate(filtered_members):
                        with cols[i % 3]:
                            bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                            
                            badges = f'<div style="background-color:#FFD700; color:black; padding:2px 8px; border-radius:10px; font-size:10px; position:absolute; left:10px; top:10px;">{m.get("role")}</div>' if m.get('role') not in ['عضو', 'غير محدد'] else ""
                            c_html = f'<div style="background-color:{bg}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:140px; margin-bottom:10px; text-align:right;">{badges}<h4 style="color:white; margin:0px;">👤 {m["name"]}</h4><p style="color:#CCC; font-size:13px; margin:10px 0px;">📍 {m.get("House location", "-")}</p><p style="color:#4CAF50; font-weight:bold;">💯 {m.get("points", 0)} نقطة</p></div>'
                            
                            st.markdown(c_html, unsafe_allow_html=True)
                            
                            if st.button("المزيد ➕", key=f"btn_{m['id']}", use_container_width=True):
                                member_details_dialog(m, is_admin)
                else:
                    st.warning("⚠️ لم يتم العثور على أعضاء يطابقون شروط البحث.")
            else:
                st.info("لا يوجد أعضاء مفعلين حتى الآن.")
        # --- 3. الخانة الجديدة: طلبات الانضمام (للإدارة فقط) ---
    elif menu == "🔔 طلبات الانضمام":
        st.title("🔔 الحسابات بانتظار التفعيل")
        members = db.get_all_members()
        
        if members:
            new_accounts = [m for m in members if m.get('role') == 'غير محدد']
            if new_accounts:
                st.warning(f"يوجد ({len(new_accounts)}) حسابات جديدة بحاجة إلى تحديد رتبة.")
                cols_new = st.columns(3)
                for i, m in enumerate(new_accounts):
                    with cols_new[i % 3]:
                        new_card = f'<div style="background-color:#4a1c1c; padding:15px; border-radius:10px; border: 2px solid #ff9800; margin-bottom:10px; text-align:right;"><h4 style="color:#ff9800; margin:0px;">🆕 {m["name"]}</h4><p style="color:#CCC; font-size:13px; margin:5px 0px;">📞 {m["phone"]}</p></div>'
                        st.markdown(new_card, unsafe_allow_html=True)
                        # زر تفعيل الحساب
                        if st.button("⚙️ ترقية وتفعيل", key=f"act_{m['id']}", use_container_width=True):
                            member_details_dialog(m, is_admin)
            else:
                st.success("🎉 لا يوجد طلبات انضمام جديدة. جميع الأعضاء تم تفعيلهم!")

    # --- 4. إضافة يدوية ---
    elif menu == "➕ إضافة عضو يدوياً":
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

