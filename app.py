import streamlit as st
from supabase import create_client, Client
import pandas as pd

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="Deja Admin Panel", page_icon="👥", layout="wide")

# ==========================================
# 2. إدارة قاعدة البيانات والمصادقة (Supabase Layer)
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# تهيئة حالة الجلسة (Session State) لمعرفة إذا المستخدم مسجل دخول
if 'user' not in st.session_state:
    st.session_state['user'] = None

class DatabaseManager:
    def add_member(self, data):
        row = {
            "name": data[0],
            "phone": data[1],
            "email": data[2],
            "team": data[3],
            "role": data[4],
            "points": data[5],
            "notes": data[6]
        }
        supabase.table("members").insert(row).execute()

    def delete_member(self, member_id):
        supabase.table("members").delete().eq("id", member_id).execute()

    def get_all_members(self):
        response = supabase.table("members").select("*").order("id", desc=True).execute()
        return response.data

db = DatabaseManager()

# ==========================================
# 3. واجهة تسجيل الدخول / إنشاء حساب (Auth UI)
# ==========================================
if st.session_state['user'] is None:
    st.title("🔐 مرحباً بك في نظام Deja")
    st.markdown("يرجى تسجيل الدخول أو إنشاء حساب للوصول إلى لوحة التحكم.")
    
    # تقسيم الشاشة إلى تبويبات
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
    
    with tab1:
        st.subheader("تسجيل الدخول")
        login_email = st.text_input("البريد الإلكتروني", key="login_email")
        login_password = st.text_input("كلمة المرور", type="password", key="login_pass")
        if st.button("دخول 🚀", use_container_width=True):
            try:
                # محاولة تسجيل الدخول عبر Supabase
                res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state['user'] = res.user
                st.success("تم تسجيل الدخول بنجاح! جاري التوجيه...")
                st.rerun()
            except Exception as e:
                st.error("❌ البريد الإلكتروني أو كلمة المرور غير صحيحة.")

    with tab2:
        st.subheader("إنشاء حساب جديد")
        signup_email = st.text_input("البريد الإلكتروني", key="signup_email")
        signup_password = st.text_input("كلمة المرور (6 أحرف على الأقل)", type="password", key="signup_pass")
        if st.button("إنشاء حساب ✍️", use_container_width=True):
            try:
                # إنشاء حساب جديد في Supabase
                res = supabase.auth.sign_up({"email": signup_email, "password": signup_password})
                st.success("✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول من التبويب الأول.")
            except Exception as e:
                st.error(f"❌ حدث خطأ: {str(e)}")

# ==========================================
# 4. واجهة لوحة التحكم (تظهر فقط بعد تسجيل الدخول)
# ==========================================
else:
    # --- شريط علوي للمستخدم ---
    col1, col2 = st.columns([8, 2])
    with col1:
        st.write(f"👋 أهلاً بك، **{st.session_state['user'].email}**")
    with col2:
        if st.button("تسجيل الخروج 🚪", use_container_width=True, type="secondary"):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()
            
    st.markdown("---")

    TEAMS = ["غير محدد", "فريق ميديا", "فريق IT"]
    ROLES = ["عضو", "إداري"]

    st.title("👥 لوحة تحكم فريق Deja")

    # --- القائمة الجانبية (Sidebar) لإضافة حساب ---
    with st.sidebar:
        st.header("➕ إضافة حساب جديد")
        
        with st.form("add_member_form", clear_on_submit=True):
            name = st.text_input("الاسم الثلاثي باللغة العربية *")
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
            team = st.selectbox("الفريق", TEAMS)
            role = st.selectbox("الرتبة", ROLES)
            points = st.number_input("النقاط", min_value=0, value=0, step=1)
            notes = st.text_area("ملاحظات")
            
            submit_btn = st.form_submit_button("إضافة الحساب ✅", use_container_width=True)
            
            if submit_btn:
                if not name.strip():
                    st.error("⚠️ الاسم مطلوب!")
                else:
                    db.add_member((name, phone, email, team, role, points, notes))
                    st.success(f"تمت إضافة {name} بنجاح!")
                    st.rerun()

    # --- اللوحة الرئيسية (الجدول والبحث) ---
    members_data = db.get_all_members()

    st.write(f"**إجمالي الأعضاء المسجلين:** {len(members_data)}")

    if members_data:
        df = pd.DataFrame(members_data)
        
        df_display = df.rename(columns={
            'id': 'الرقم',
            'name': 'الاسم',
            'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني',
            'team': 'الفريق',
            'role': 'الرتبة',
            'points': 'النقاط',
            'notes': 'ملاحظات'
        })
        
        search_query = st.text_input("🔍 ابحث بالاسم، رقم الهاتف، أو الإيميل...")
        
        if search_query:
            mask = df_display.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            df_display = df_display[mask]

        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        st.subheader("🗑️ إدارة الحسابات (حذف)")
        del_col1, del_col2 = st.columns([3, 1])
        
        with del_col1:
            member_options = [f"{row['name']} (رقم: {row['id']})" for _, row in df.iterrows()]
            selected_to_delete = st.selectbox("اختر العضو المراد حذفه:", [""] + member_options)
            
        with del_col2:
            st.write("")
            st.write("")
            if st.button("حذف الحساب المختار ❌", type="primary", use_container_width=True):
                if selected_to_delete:
                    member_id = int(selected_to_delete.split("(رقم: ")[1].replace(")", ""))
                    db.delete_member(member_id)
                    st.success("تم حذف الحساب بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى اختيار عضو أولاً.")
    else:
        st.info("لا يوجد أعضاء مضافين حتى الآن. ابدأ بإضافة حسابات من القائمة الجانبية.")
