import streamlit as st
from supabase import create_client

# 1. الاتصال بقاعدة البيانات
st.set_page_config(page_title="Deja Workspace", layout="centered")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.session_state['user'] = None

# 2. شاشة الدخول وإنشاء الحساب
if st.session_state['user'] is None:
    st.title("⚡ Deja Workspace")
    
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
    
    with tab1:
        l_phone = st.text_input("رقم الهاتف")
        l_pass = st.text_input("كلمة المرور", type="password")
        if st.button("دخول 🚀", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                st.session_state['user'] = res.user
                st.rerun()
            except:
                st.error("❌ الرقم أو كلمة المرور خطأ.")

    with tab2:
        s_name = st.text_input("الاسم الكامل")
        s_phone = st.text_input("رقم الهاتف الجديد")
        s_pass = st.text_input("كلمة المرور الجديدة", type="password")
        if st.button("إنشاء حساب ✍️", use_container_width=True):
            try:
                # بيعمل الحساب بنظام الحماية
                supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass})
                
                # بيسجل الاسم والرقم بجدول الأعضاء عشان يظهروا بالموقع
                supabase.table("members").insert({"name": s_name, "phone": s_phone, "role": "عضو جديد"}).execute()
                
                st.success("✅ تم الإنشاء! روح سجل دخول هسه.")
            except Exception as e:
                st.error(f"❌ صار خطأ: يمكن الرقم موجود أصلاً.")

# 3. شاشة الموقع (بعد ما تسجل دخول)
else:
    st.title("👋 أهلاً بك في الموقع")
    if st.button("تسجيل خروج 🚪"):
        supabase.auth.sign_out()
        st.session_state['user'] = None
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 👥 الأشخاص اللي سجلوا بالموقع:")
    
    # هون بنسحب كل الناس اللي عملوا حسابات وبنعرضهم
    try:
        response = supabase.table("members").select("name, phone").execute()
        users = response.data
        
        if users:
            for u in users:
                st.info(f"👤 الاسم: {u['name']} | 📞 الرقم: {u['phone']}")
        else:
            st.warning("ما في حد مسجل لسه!")
    except Exception as e:
        st.error("لازم تطفي حماية RLS من Supabase عشان تقدر تشوف الأسماء!")
