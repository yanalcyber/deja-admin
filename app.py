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

    # --- زر الاستيراد السحري لملف deja.db ---
    if os.path.exists("deja.db"):
        st.info("💡 تم العثور على ملف البيانات (deja.db).")
        if st.button("تنزيل البيانات إلى الجدول 🚀", type="primary"):
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

    # --- عرض البيانات المختصرة ---
    members_data = db.get_all_members()
    st.write(f"**إجمالي الأعضاء المسجلين:** {len(members_data)}")

    if members_data:
        df = pd.DataFrame(members_data)
        df_display = df.rename(columns={
            'id': 'الرقم', 'name': 'الاسم', 'english_name': 'الاسم بالانجليزية',
            'phone': 'رقم الهاتف', 'email': 'البريد الإلكتروني',
            'team': 'الفريق', 'role': 'الرتبة',
            'residence': 'السكن', 'university': 'الجامعة',
            'major': 'التخصص', 'academic_year': 'السنة الدراسية',
            'sports_experience': 'الخبرة الرياضية',
            'points': 'النقاط', 'notes': 'ملاحظات'
        })
        
        search_query = st.text_input("🔍 ابحث بالاسم، رقم الهاتف، أو الإيميل...")
        if search_query:
            mask = df_display.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            df_display = df_display[mask]

        # 1. الجدول المختصر والنظيف
        st.dataframe(
            df_display[['الرقم', 'الاسم', 'الفريق', 'الرتبة']], 
            use_container_width=True, 
            hide_index=True
        )
        
        st.markdown("---")
        st.subheader("⚙️ لوحة إدارة الأعضاء التفصيلية")
        
        # 2. اللوحة السفلية (معلومات، تعديل، حذف)
        tab_info, tab_edit, tab_del = st.tabs(["🪪 معلومات العضو", "✏️ تعديل البيانات", "🗑️ حذف حساب"])
        
        member_options = [f"{row['الاسم']} (رقم: {row['الرقم']})" for _, row in df_display.iterrows()]
        
        # قسم عرض المعلومات
        with tab_info:
            selected_info = st.selectbox("🔍 اختر العضو لعرض كافة تفاصيله:", [""] + member_options, key="sel_info")
            if selected_info:
                member_id = int(selected_info.split("(رقم: ")[1].replace(")", ""))
                row = df_display[df_display['الرقم'] == member_id].iloc[0]
                
                st.info(f"**الاسم:** {row['الاسم']} | **الاسم بالإنجليزي:** {row.get('الاسم بالانجليزية', '')}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"📞 **الهاتف:** {row['رقم الهاتف']}")
                    st.write(f"📧 **الإيميل:** {row['البريد الإلكتروني']}")
                    st.write(f"🏠 **السكن:** {row.get('السكن', '')}")
                with c2:
                    st.write(f"🎓 **الجامعة:** {row.get('الجامعة', '')}")
                    st.write(f"📚 **التخصص:** {row.get('التخصص', '')}")
                    st.write(f"📅 **السنة:** {row.get('السنة الدراسية', '')}")
                with c3:
                    st.write(f"👥 **الفريق:** {row['الفريق']}")
                    st.write(f"⭐ **الرتبة:** {row['الرتبة']}")
                    st.write(f"💯 **النقاط:** {row['النقاط']}")
                
                st.write(f"🏅 **الخبرة الرياضية:** {row.get('الخبرة الرياضية', '')}")
                st.write(f"📝 **ملاحظات:** {row.get('ملاحظات', '')}")

        # قسم التعديل
        with tab_edit:
            selected_edit = st.selectbox("✏️ اختر العضو لتعديل بياناته:", [""] + member_options, key="sel_edit")
            if selected_edit:
                member_id = int(selected_edit.split("(رقم: ")[1].replace(")", ""))
                current_data = df_display[df_display['الرقم'] == member_id].iloc[0]
                
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        e_name = st.text_input("الاسم", value=current_data['الاسم'])
                        e_eng = st.text_input("الاسم بالإنجليزي", value=current_data.get('الاسم بالانجليزية', ''))
                        e_phone = st.text_input("رقم الهاتف", value=current_data['رقم الهاتف'])
                        e_email = st.text_input("البريد الإلكتروني", value=current_data['البريد الإلكتروني'])
                        
                        team_idx = TEAMS.index(current_data['الفريق']) if current_data['الفريق'] in TEAMS else 0
                        e_team = st.selectbox("الفريق", TEAMS, index=team_idx)
                        
                        role_idx = ROLES.index(current_data['الرتبة']) if current_data['الرتبة'] in ROLES else 0
                        e_role = st.selectbox("الرتبة", ROLES, index=role_idx)
                        
                        e_points = st.number_input("النقاط", value=int(current_data['النقاط']), step=1)
                    with col2:
                        e_res = st.text_input("السكن", value=current_data.get('السكن', ''))
                        e_uni = st.text_input("الجامعة", value=current_data.get('الجامعة', ''))
                        e_maj = st.text_input("التخصص", value=current_data.get('التخصص', ''))
                        e_ay = st.text_input("السنة الدراسية", value=current_data.get('السنة الدراسية', ''))
                        e_se = st.text_area("الخبرة الرياضية", value=current_data.get('الخبرة الرياضية', ''))
                        e_notes = st.text_area("ملاحظات", value=current_data.get('ملاحظات', ''))
                    
                    if st.form_submit_button("حفظ التعديلات 💾", type="primary", use_container_width=True):
                        db.update_member(member_id, (e_name, e_eng, e_phone, e_email, e_team, e_role, e_res, e_uni, e_maj, e_ay, e_se, e_points, e_notes))
                        st.success("✅ تم التعديل بنجاح!")
                        st.rerun()

        # قسم الحذف
        with tab_del:
            selected_del = st.selectbox("🗑️ اختر العضو للحذف:", [""] + member_options, key="sel_del")
            if st.button("حذف الحساب نهائياً ❌", type="secondary", use_container_width=True):
                if selected_del:
                    del_member_id = int(selected_del.split("(رقم: ")[1].replace(")", ""))
                    db.delete_member(del_member_id)
                    st.success("تم حذف الحساب بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى اختيار عضو أولاً.")
    else:
        st.info("لا يوجد أعضاء مضافين حتى الآن. ابدأ بإضافة حسابات من القائمة الجانبية.")
