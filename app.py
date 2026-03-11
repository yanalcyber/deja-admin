import streamlit as st
from supabase import create_client

# ==========================================
# 1. إعدادات الصفحة والاتصال بقاعدة البيانات
# ==========================================
st.set_page_config(page_title="Deja Workspace", page_icon="⚡", layout="centered")

# جلب بيانات الاتصال
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ==========================================
# 2. دوال قاعدة البيانات (بسيطة جداً)
# ==========================================
class Database:
    def get_all_members(self):
        try:
            res = supabase.table("members").select("*").execute()
            return res.data
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {e}")
            return []

    def add_member(self, name, phone):
        # وضعنا قيم افتراضية عشان السيرفر ما يعطي أي خطأ
        row = {
            "name": name,
            "phone": phone,
            "role": "قيد الانتظار",
            "team": "غير محدد",
            "House location": "غير محدد",
            "gender": "غير محدد",
            "points": 0
        }
        supabase.table("members").insert(row).execute()

    def update_role(self, member_id, new_role):
        supabase.table("members").update({"role": new_role}).eq("id", member_id).execute()

db = Database()

# ==========================================
# 3. إدارة الجلسة (تسجيل الدخول)
# ==========================================
if 'user' not in st.session_state:
    st.session_state['user'] = None

arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

# ==========================================
# 4. واجهة الدخول وإنشاء الحساب
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["تسجيل الدخول 🔑", "إنشاء حساب ✍️"])
    
    with tab1:
        l_phone = st.text_input("رقم الهاتف", key="l_phone")
        l_pass = st.text_input("كلمة المرور", type="password", key="l_pass")
        if st.button("دخول 🚀", use_container_width=True, type="primary"):
            if l_phone and l_pass:
                try:
                    clean_p = l_phone.translate(arabic_to_english).replace(" ", "").strip()
                    res = supabase.auth.sign_in_with_password({"email": f"{clean_p}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except:
                    st.error("❌ بيانات الدخول غير صحيحة.")
            else:
                st.warning("⚠️ يرجى تعبئة الحقول.")

    with tab2:
        s_name = st.text_input("الاسم الكامل", key="s_name")
        s_phone = st.text_input("رقم الهاتف", key="s_phone")
        s_pass = st.text_input("كلمة المرور (6 خانات على الأقل)", type="password", key="s_pass")
        if st.button("إنشاء الحساب 🚀", use_container_width=True):
            if s_name and s_phone and len(s_pass) >= 6:
                try:
                    clean_p = s_phone.translate(arabic_to_english).replace(" ", "").strip()
                    # إنشاء بالحماية
                    supabase.auth.sign_up({"email": f"{clean_p}@deja.com", "password": s_pass})
                    # إنشاء بالجدول
                    db.add_member(s_name, clean_p)
                    st.success("✅ تم إرسال طلبك للإدارة! يرجى الانتظار حتى يتم تفعيل حسابك.")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أو الرقم مسجل مسبقاً.")
            else:
                st.warning("⚠️ يرجى تعبئة جميع الحقول بشكل صحيح.")

# ==========================================
# 5. اللوحة الرئيسية (بعد تسجيل الدخول)
# ==========================================
else:
    # جلب بيانات المستخدم الحالي
    current_phone = st.session_state['user'].email.split('@')[0]
    all_members = db.get_all_members()
    current_user_data = next((m for m in all_members if m['phone'] == current_phone), None)
    
    my_role = current_user_data['role'] if current_user_data else "قيد الانتظار"
    is_admin = my_role == "إداري"

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.markdown(f"### أهلاً، {current_user_data['name'] if current_user_data else 'عضو جديد'}")
        st.caption(f"الرتبة: {my_role}")
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

    # --- واجهة الحسابات الموقوفة / بانتظار التفعيل ---
    if my_role == "قيد الانتظار":
        st.warning("⏳ حسابك قيد المراجعة. يرجى الانتظار حتى يقوم الإداري بتفعيل حسابك لرؤية محتوى الموقع.")
        st.stop() # يوقف الكود هون وما بخليه يشوف أي اشي تحت

    # --- واجهة الإدارة والأعضاء المفعلين ---
    if is_admin:
        pending_members = [m for m in all_members if m['role'] == "قيد الانتظار"]
        active_members = [m for m in all_members if m['role'] != "قيد الانتظار"]

        st.title("🛡️ لوحة الإدارة")
        
        # 1. قسم طلبات الانضمام
        st.header("🔔 طلبات الانضمام الجديدة")
        if pending_members:
            for m in pending_members:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{m['name']}** | 📞 {m['phone']}")
                    with col2:
                        if st.button("تفعيل كعضو ✅", key=f"act_{m['id']}"):
                            db.update_role(m['id'], "عضو")
                            st.rerun()
        else:
            st.success("لا يوجد طلبات جديدة.")

        st.markdown("---")
        
        # 2. قسم الأعضاء المفعلين
        st.header("👥 أعضاء الفريق")
        for m in active_members:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{m['name']}** | ⭐ {m['role']}")
                with col2:
                    if m['role'] != "إداري":
                        if st.button("ترقية لإداري 👑", key=f"up_{m['id']}"):
                            db.update_role(m['id'], "إداري")
                            st.rerun()
    else:
        # واجهة العضو العادي
        st.title("👋 أهلاً بك في الفريق")
        st.info("حسابك مفعل كعضو. سيتم إضافة المهام والميزات هنا قريباً!")
