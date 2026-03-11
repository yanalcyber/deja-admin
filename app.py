import streamlit as st
from supabase import create_client

# 1. إعداد الصفحة والاتصال
st.set_page_config(page_title="حسابات الموقع", layout="centered")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.session_state['user'] = None

# قائمة الفرق (بتقدر تزيد عليها أو تعدلها)
TEAMS = ["غير محدد", "إدارة", "ميديا", "IT (أمن سيبراني)", "تسويق", "دعم فني"]

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
        reg_team = st.selectbox("الفريق 👥", TEAMS) # إضافة خيار الفريق هون
        reg_pass = st.text_input("كلمة المرور (6 خانات)", type="password")
        
        if st.button("إنشاء الحساب ✍️", use_container_width=True):
            if reg_name and reg_phone and len(reg_pass) >= 6:
                try:
                    # 1. بنعمله حساب بنظام الحماية
                    supabase.auth.sign_up({"email": f"{reg_phone.strip()}@deja.com", "password": reg_pass})
                    
                    # 2. بنسجل البيانات بجدول USER مع الفريق
                    supabase.table("USER").insert({
                        "name": reg_name, 
                        "phone": reg_phone,
                        "password": reg_pass,
                        "team": reg_team
                    }).execute()
                    
                    st.success("✅ تم إنشاء الحساب بنجاح! ارجع لتبويبة الدخول وسجل دخولك.")
                except Exception as e:
                    st.error("❌ حدث خطأ! (تأكد إنك ضفت عمود team بجدول USER).")
            else:
                st.warning("⚠️ يرجى تعبئة جميع الحقول بشكل صحيح (الباسورد 6 خانات عالأقل).")

# ==========================================
# واجهة عرض الحسابات والتعديل (بعد الدخول)
# ==========================================
else:
    st.title("📱 الحسابات المسجلة من الموقع")
    if st.button("تسجيل الخروج 🚪"):
        supabase.auth.sign_out()
        st.session_state['user'] = None
        st.rerun()
        
    st.markdown("---")
    
    # ضفنا كلمة team عشان نسحبها من القاعدة
    try:
        response = supabase.table("USER").select("id, name, phone, password, team").execute()
        accounts = response.data
        
        if accounts:
            st.success(f"يوجد ({len(accounts)}) حساب تم إنشاؤه في جدول USER:")
            for idx, acc in enumerate(accounts, 1):
                
                # صندوق مرتب لكل مستخدم بيعرض كل بياناته
                with st.container(border=True):
                    current_team = acc.get('team', 'غير محدد')
                    st.markdown(f"**{idx}. 👤 الاسم:** {acc.get('name', 'بدون اسم')} | **📞 الرقم:** {acc.get('phone', 'بدون رقم')}")
                    st.markdown(f"**🔑 الباسورد:** {acc.get('password', 'غير متوفر')} | **👥 الفريق:** `{current_team}`")
                    
                    # زر التعديل
                    with st.expander("✏️ تعديل بيانات الحساب"):
                        with st.form(key=f"edit_form_{acc['id']}"):
                            new_name = st.text_input("الاسم", value=acc.get('name', ''))
                            new_phone = st.text_input("الرقم", value=acc.get('phone', ''))
                            new_pass = st.text_input("الباسورد", value=acc.get('password', ''))
                            
                            # تحديد الفريق القديم كقيمة افتراضية بالصندوق
                            team_index = TEAMS.index(current_team) if current_team in TEAMS else 0
                            new_team = st.selectbox("الفريق", TEAMS, index=team_index)
                            
                            # كبسة الحفظ
                            if st.form_submit_button("حفظ التعديلات ✅", use_container_width=True):
                                try:
                                    supabase.table("USER").update({
                                        "name": new_name,
                                        "phone": new_phone,
                                        "password": new_pass,
                                        "team": new_team
                                    }).eq("id", acc['id']).execute()
                                    
                                    st.success("تم التعديل بنجاح! جاري التحديث...")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ صار خطأ أثناء التعديل: {e}")
        else:
            st.warning("لم يقم أي شخص بإنشاء حساب في جدول USER حتى الآن.")
            
    except Exception as e:
        st.error(f"❌ لا يمكن جلب الحسابات! تأكد إنك ضفت عمود team لجدول USER. التفاصيل: {e}")
