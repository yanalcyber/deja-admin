import streamlit as st
from supabase import create_client

# استدعاء الملفات الخارجية (الترتيب والاحتراف)
from page_employees import show_employees
from page_tasks import show_tasks
from page_users import show_users

st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.session_state['user'] = None

TEAMS = ["إدارة", "ميديا", "IT (أمن سيبراني)", "تسويق", "دعم فني", "غير محدد"]

# ==========================================
# واجهة إنشاء الحساب والدخول
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #ffeb3b;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول 🔑", "إنشاء حساب جديد ✍️"])
        
        with tab1:
            log_phone = st.text_input("رقم الهاتف")
            log_pass = st.text_input("كلمة المرور", type="password")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{log_phone.strip()}@deja.com", "password": log_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except:
                    st.error("❌ بيانات الدخول غير صحيحة.")

        with tab2:
            reg_name = st.text_input("الاسم الكامل")
            reg_phone = st.text_input("رقم الهاتف (الجديد)")
            reg_team = st.selectbox("الفريق 👥", TEAMS)
            reg_pass = st.text_input("كلمة المرور (6 خانات)", type="password")
            
            if st.button("إنشاء الحساب 🚀", use_container_width=True):
                if reg_name and reg_phone and len(reg_pass) >= 6:
                    try:
                        supabase.auth.sign_up({"email": f"{reg_phone.strip()}@deja.com", "password": reg_pass})
                        supabase.table("USER").insert({"name": reg_name, "phone": reg_phone, "password": reg_pass, "team": reg_team}).execute()
                        try:
                            supabase.table("members").insert({"name": reg_name, "phone": reg_phone, "team": reg_team, "role": "عضو جديد"}).execute()
                        except:
                            pass
                        st.success("✅ تم إنشاء الحساب بنجاح! ارجع لتبويبة الدخول.")
                    except:
                        st.error("❌ حدث خطأ! تأكد من البيانات.")
                else:
                    st.warning("⚠️ يرجى تعبئة الحقول بشكل صحيح.")

# ==========================================
# اللوحة الرئيسية وإدارة التوجيه
# ==========================================
else:
    with st.sidebar:
        st.markdown("### 👨‍💻 أهلاً بك في مساحة العمل")
        st.markdown("---")
        menu = st.radio("القائمة الرئيسية:", ["👥 الموظفين والفرق", "📋 لوحة المهام", "🔐 إدارة حسابات (USER)"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

    # التوجيه (هون السحر! بننادي الكود من الملفات الثانية)
    if menu == "👥 الموظفين والفرق":
        show_employees(supabase, TEAMS)
        
    elif menu == "📋 لوحة المهام":
        show_tasks(supabase)
        
    elif menu == "🔐 إدارة حسابات (USER)":
        show_users(supabase, TEAMS)
