import streamlit as st
from supabase import create_client

# 1. إعداد الصفحة والاتصال
st.set_page_config(page_title="حسابات الموقع", layout="centered")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.session_state['user'] = None

# ==========================================
# واجهة إنشاء الحساب والدخول
# ==========================================
if st.session_state['user'] is None:
    st.title("⚡ تسجيل الدخول للموقع")
    
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
    
    with tab1:
        log_phone = st.text_input("رقم الهاتف (للدخول)")
        log_pass = st.text_input("كلمة المرور", type="password")
        if st.button("دخول 🚀", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": f"{log_phone.strip()}@deja.com", "password": log_pass})
                st.session_state['user'] = res.user
                st.rerun()
            except:
                st.error("❌ بيانات الدخول غير صحيحة.")

    with tab2:
        reg_name = st.text_input("الاسم الكامل")
        reg_phone = st.text_input("رقم الهاتف")
        reg_pass = st.text_input("كلمة المرور (6 خانات)", type="password")
        
        if st.button("إنشاء الحساب ✍️", use_container_width=True):
            if reg_name and reg_phone and len(reg_pass) >= 6:
                try:
                    # 1. بنعمله حساب بنظام الحماية
                    supabase.auth.sign_up({"email": f"{reg_phone.strip()}@deja.com", "password": reg_pass})
                    
                    # 2. الخدعة: بنسجل الاسم والرقم والباسورد كمان بجدول USER
                    supabase.table("USER").insert({
                        "name": reg_name, 
                        "phone": reg_phone,
                        "password": reg_pass  # تم إضافة حفظ الباسورد هون
                    }).execute()
                    
                    st.success("✅ تم إنشاء الحساب بنجاح! ارجع لتبويبة الدخول وسجل دخولك.")
                except Exception as e:
                    st.error(f"❌ حدث خطأ! (تأكد إنك ضفت عمود password بجدول USER).")
            else:
                st.warning("⚠️ يرجى تعبئة جميع الحقول بشكل صحيح (الباسورد 6 خانات عالأقل).")

# ==========================================
# واجهة عرض الحسابات (بعد الدخول)
# ==========================================
else:
    st.title("📱 الحسابات المسجلة من الموقع")
    if st.button("تسجيل الخروج 🚪"):
        supabase.auth.sign_out()
        st.session_state['user'] = None
        st.rerun()
        
    st.markdown("---")
    
    # سحب الحسابات من جدول USER وعرضها مع الباسورد
    try:
        # ضفنا كلمة password عشان يسحبها من الداتا بيز
        response = supabase.table("USER").select("name, phone, password").execute()
        accounts = response.data
        
        if accounts:
            st.success(f"يوجد ({len(accounts)}) حساب تم إنشاؤه في جدول USER:")
            for idx, acc in enumerate(accounts, 1):
                # عرض الباسورد جوا البطاقة
                st.info(f"**{idx}. 👤 الاسم:** {acc.get('name', 'بدون اسم')} | **📞 الرقم:** {acc.get('phone', 'بدون رقم')} | **🔑 الباسورد:** {acc.get('password', 'غير متوفر')}")
        else:
            st.warning("لم يقم أي شخص بإنشاء حساب في جدول USER حتى الآن.")
            
    except Exception as e:
        st.error("❌ لا يمكن جلب الحسابات! تأكد إنك ضفت عمود password لجدول USER.")
