import streamlit as st
import pandas as pd
import os
import sqlite3
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="Deja Admin Panel", page_icon="👥", layout="wide")

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
# 3. واجهة تسجيل الدخول
# ==========================================
if st.session_state['user'] is None:
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
                    st.error("❌ رقم الهاتف أو كلمة المرور غير صحيحة.")
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
                    st.error("❌ حدث خطأ، تأكد من كلمة المرور وأن الرقم غير مسجل.")
            else:
                st.warning("يرجى تعبئة جميع الحقول.")

# ==========================================
# 4. لوحة التحكم 
# ==========================================
else:
    user_name = st.session_state['user'].user_metadata.get('name', 'عضو فريق Deja')
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.write(f"👋 أهلاً بك يا بطل، **{user_name}**")
    with col2:
        if st.button("تسجيل الخروج 🚪", use_container_width=True, type="secondary"):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()
            
    st.markdown("---")
    st.title("👥 لوحة تحكم فريق Deja")

    TEAMS = ["غير محدد", "فريق ميديا", "فريق IT"]
    ROLES = ["عضو", "إداري"]

    with st.sidebar:
        st.header("➕ إضافة حساب جديد للمشروع")
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

    # --- زر الاستيراد السحري المحدث (لصيغة النصوص) ---
    if os.path.exists("deja.db"):
        st.info("💡 تم العثور على ملف البيانات (deja.db).")
        if st.button("تنزيل البيانات إلى الجدول 🚀", type="primary"):
            try:
                # إنشاء قاعدة بيانات وهمية بالذاكرة
                conn = sqlite3.connect(':memory:')
                cursor = conn.cursor()
                
                # قراءة الملف وتشغيل الأكواد اللي جواته
                with open("deja.db", "r", encoding="utf-8") as f:
                    sql_script = f.read()
                
                cursor.executescript(sql_script)
                
                # سحب البيانات بعد ما ترتبت
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = cursor.fetchall()
                
                if tables:
                    table_name = tables[0][0]
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    column_names = [description[0] for description in cursor.description]
                    
                    added_count = 0
                    for row in rows:
                        row_dict = dict(zip(column_names, row))
                        
                        n = str(row_dict.get("الاسم_بالعربية", "")).strip()
                        
                        if n and n != "None":
                            p = str(row_dict.get("رقم_الهاتف", ""))
                            e = str(row_dict.get("البريد_الإلكتروني", ""))
                            t = str(row_dict.get("الفريق", "غير محدد"))
                            r = str(row_dict.get("الرتبة", "عضو"))
                            nts = str(row_dict.get("ملاحظات", ""))
                            
                            if not t or t == "None": t = "غير محدد"
                            if not r or r == "None": r = "عضو"
                            if p == "None": p = ""
                            if e == "None": e = ""
                            if nts == "None": nts = ""

                            db.add_member((n, p, e, t, r, 0, nts))
                            added_count += 1
                            
                conn.close()
                st.success(f"✅ تم إضافة {added_count} عضو بنجاح! جاري التحديث...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")

    # --- عرض الجدول ---
    members_data = db.get_all_members()
    st.write(f"**إجمالي الأعضاء المسجلين:** {len(members_data)}")

    if members_data:
        df = pd.DataFrame(members_data)
        df_display = df.rename(columns={
            'id': 'الرقم', 'name': 'الاسم', 'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني', 'team': 'الفريق', 'role': 'الرتبة',
            'points': 'النقاط', 'notes': 'ملاحظات'
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
