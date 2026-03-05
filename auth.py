import streamlit as st
from database import supabase

def show_login_screen():
    st.title("🔐 مرحباً بك في نظام Deja")
    st.markdown("يرجى تسجيل الدخول أو إنشاء حساب للوصول إلى لوحة التحكم.")
    
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
    
    with tab1:
        st.subheader("تسجيل الدخول")
        login_phone = st.text_input("رقم الهاتف", key="login_phone", placeholder="مثال: 0791234567")
        login_password = st.text_input("كلمة المرور", type="password", key="login_pass")
        
        if st.button("دخول 🚀", use_container_width=True):
            if login_phone and login_password:
                try:
                    clean_phone = login_phone.replace(" ", "").strip()
                    dummy_email = f"{clean_phone}@deja.com"
                    res = supabase.auth.sign_in_with_password({"email": dummy_email, "password": login_password})
                    st.session_state['user'] = res.user
                    st.success("تم تسجيل الدخول بنجاح! جاري التوجيه...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ رقم الهاتف أو كلمة المرور غير صحيحة. (الخطأ: {str(e)})")
            else:
                st.warning("يرجى إدخال رقم الهاتف وكلمة المرور.")

    with tab2:
        st.subheader("إنشاء حساب جديد")
        signup_name = st.text_input("الاسم الكامل", key="signup_name", placeholder="اسمك الثلاثي")
        signup_phone = st.text_input("رقم الهاتف", key="signup_phone", placeholder="مثال: 0791234567")
        signup_password = st.text_input("كلمة المرور (6 أحرف/أرقام على الأقل)", type="password", key="signup_pass")
        
        if st.button("إنشاء حساب ✍️", use_container_width=True):
            if signup_name and signup_phone and signup_password:
                try:
                    clean_phone = signup_phone.replace(" ", "").strip()
                    dummy_email = f"{clean_phone}@deja.com"
                    res = supabase.auth.sign_up({
                        "email": dummy_email, 
                        "password": signup_password,
                        "options": {"data": {"name": signup_name, "phone": clean_phone}}
                    })
                    st.success(f"✅ تم إنشاء حسابك يا {signup_name} بنجاح! يمكنك الآن تسجيل الدخول.")
                except Exception as e:
                    st.error(f"❌ حدث خطأ، تأكد من كلمة المرور (6 أحرف) وأن الرقم غير مسجل. (الخطأ: {str(e)})")
            else:
                st.warning("يرجى تعبئة جميع الحقول.")
