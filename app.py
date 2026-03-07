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
            "english_name": data[1],
            "phone": data[2],
            "email": data[3],
            "team": data[4],
            "role": data[5],
            "residence": data[6],
            "university": data[7],
            "major": data[8],
            "academic_year": data[9],
            "sports_experience": data[10],
            "points": data[11],
            "notes": data[12]
        }
        supabase.table("members").insert(row).execute()

    def update_member(self, member_id, data):
        row = {
            "name": data[0],
            "english_name": data[1],
            "phone": data[2],
            "email": data[3],
            "team": data[4],
            "role": data[5],
            "residence": data[6],
            "university": data[7],
            "major": data[8],
            "academic_year": data[9],
            "sports_experience": data[10],
            "points": data[11],
            "notes": data[12]
        }
        supabase.table("members").update(row).eq("id", member_id).execute()

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
            name = st.text_input("الاسم باللغة العربية *")
            english_name = st.text_input("الاسم بالإنجليزية")
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
            
            st.markdown("---")
            team = st.selectbox("الفريق", TEAMS)
            role = st.selectbox("الرتبة", ROLES)
            points = st.number_input("النقاط", min_value=0, value=0, step=1)
            
            st.markdown("---")
            residence = st.text_input("🏠 السكن")
            university = st.text_input("🎓 الجامعة")
            major = st.text_input("📚 التخصص")
            academic_year = st.text_input("🎓 السنة الدراسية")
            sports_experience = st.text_area("🏅 الخبرة الرياضية")
            notes = st.text_area("📝 ملاحظات أخرى")
            
            submit_btn = st.form_submit_button("إضافة الحساب ✅", use_container_width=True)
            if submit_btn:
                if not name.strip():
                    st.error("⚠️ الاسم مطلوب!")
                else:
                    db.add_member((name, english_name, phone, email, team, role, residence, university, major, academic_year, sports_experience, points, notes))
                    st.success(f"تمت إضافة {name} بنجاح!")
                    st.rerun()

    # --- زر الاستيراد لملف deja.db ---
    if os.path.exists("deja.db"):
        st.info("💡 تم العثور على ملف البيانات (deja.db).")
        if st.button("تنزيل البيانات 🚀", type="primary"):
            try:
                conn = sqlite3.connect(':memory:')
                cursor = conn.cursor()
                with open("deja.db", "r", encoding="utf-8") as f:
                    sql_script = f.read()
                cursor.executescript(sql_script)
                
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
                            eng_n = str(row_dict.get("الاسم_بالانجليزية", "")).strip()
                            p = str(row_dict.get("رقم_الهاتف", ""))
                            e = str(row_dict.get("البريد_الإلكتروني", ""))
                            t = str(row_dict.get("الفريق", "غير محدد"))
                            r = str(row_dict.get("الرتبة", "عضو"))
                            res = str(row_dict.get("مكان_السكن", ""))
                            uni = str(row_dict.get("الجامعة", ""))
                            maj = str(row_dict.get("التخصص", ""))
                            ay = str(row_dict.get("السنة_الدراسية", ""))
                            se = str(row_dict.get("الخبرة_الرياضية", ""))
                            nts = str(row_dict.get("ملاحظات", ""))
                            
                            if not t or t == "None": t = "غير محدد"
                            if not r or r == "None": r = "عضو"
                            
                            fields = [eng_n, p, e, res, uni, maj, ay, se, nts]
                            fields = ["" if f == "None" else f for f in fields]

                            db.add_member((n, fields[0], fields[1], fields[2], t, r, fields[3], fields[4], fields[5], fields[6], fields[7], 0, fields[8]))
                            added_count += 1
                conn.close()
                st.success(f"✅ تم إضافة {added_count} عضو بنجاح! جاري التحديث...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")

    # ==========================================
    # 5. عرض الأعضاء (التصميم الجديد بالموبايل ستايل)
    # ==========================================
    members_data = db.get_all_members()
    
    st.markdown(f"### 📋 قائمة الأعضاء ({len(members_data)})")
    search_query = st.text_input("🔍 ابحث بالاسم، رقم الهاتف، أو الإيميل...")
    
    # ترويسة القائمة
    header_cols = st.columns([3, 2, 3, 1])
    header_cols[0].markdown("**👤 الاسم**")
    header_cols[1].markdown("**📞 رقم الهاتف**")
    header_cols[2].markdown("**📧 البريد الإلكتروني**")
    header_cols[3].markdown("**⚙️**")
    st.markdown("---")

    if members_data:
        for member in members_data:
            # فلترة البحث
            if search_query:
                search_text = f"{member['name']} {member['phone']} {member['email']}".lower()
                if search_query.lower() not in search_text:
                    continue

            cols = st.columns([3, 2, 3, 1])
            cols[0].write(f"**{member['name']}**")
            cols[1].write(member['phone'] if member['phone'] else "-")
            cols[2].write(member['email'] if member['email'] else "-")
            
            # زر الثلاث نقاط لكل شخص
            with cols[3]:
                with st.popover("⋮"):
                    tab_info, tab_edit, tab_del = st.tabs(["🪪 معلومات", "✏️ تعديل", "🗑️ حذف"])
                    
                    # 1. معلومات الحساب
                    with tab_info:
                        st.markdown(f"**الاسم بالإنجليزي:** {member.get('english_name', '-')}")
                        st.markdown(f"**الفريق:** {member['team']} | **الرتبة:** {member['role']}")
                        st.markdown(f"**الجامعة:** {member.get('university', '-')} | **التخصص:** {member.get('major', '-')}")
                        st.markdown(f"**السنة الدراسية:** {member.get('academic_year', '-')}")
                        st.markdown(f"**السكن:** {member.get('residence', '-')}")
                        st.markdown(f"**الخبرة:** {member.get('sports_experience', '-')}")
                        st.markdown(f"**النقاط:** {member['points']}")
                        st.markdown(f"**ملاحظات:** {member.get('notes', '-')}")

                    # 2. تعديل الحساب
                    with tab_edit:
                        with st.form(key=f"edit_form_{member['id']}"):
                            e_name = st.text_input("الاسم", value=member['name'])
                            e_eng = st.text_input("الاسم بالإنجليزي", value=member.get('english_name', ''))
                            e_phone = st.text_input("رقم الهاتف", value=member['phone'])
                            e_email = st.text_input("الإيميل", value=member['email'])
                            
                            t_idx = TEAMS.index(member['team']) if member['team'] in TEAMS else 0
                            e_team = st.selectbox("الفريق", TEAMS, index=t_idx)
                            
                            r_idx = ROLES.index(member['role']) if member['role'] in ROLES else 0
                            e_role = st.selectbox("الرتبة", ROLES, index=r_idx)
                            
                            e_res = st.text_input("السكن", value=member.get('residence', ''))
                            e_uni = st.text_input("الجامعة", value=member.get('university', ''))
                            e_maj = st.text_input("التخصص", value=member.get('major', ''))
                            e_ay = st.text_input("السنة", value=member.get('academic_year', ''))
                            e_se = st.text_area("الخبرة", value=member.get('sports_experience', ''))
                            e_pts = st.number_input("النقاط", value=int(member['points']), step=1)
                            e_notes = st.text_area("ملاحظات", value=member.get('notes', ''))
                            
                            if st.form_submit_button("حفظ التعديلات ✅", use_container_width=True):
                                db.update_member(member['id'], (e_name, e_eng, e_phone, e_email, e_team, e_role, e_res, e_uni, e_maj, e_ay, e_se, e_pts, e_notes))
                                st.success("تم الحفظ! قم بتحديث الصفحة.")
                                st.rerun()

                    # 3. حذف الحساب
                    with tab_del:
                        st.warning("⚠️ هل أنت متأكد من حذف هذا الحساب؟")
                        if st.button("تأكيد الحذف ❌", key=f"del_btn_{member['id']}", use_container_width=True):
                            db.delete_member(member['id'])
                            st.rerun()
                            
            st.markdown("---") # خط فاصل بين كل عضو والتاني
