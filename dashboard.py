import streamlit as st
import pandas as pd
from database import db, supabase

def show_dashboard_screen():
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

    # --- أداة استيراد البيانات من ملف SQLite ---
    st.markdown("---")
    st.subheader("📥 استيراد بيانات الأعضاء من ملف SQLite القديم")
    uploaded_sqlite = st.file_uploader("ارفع ملف قاعدة البيانات (.db أو .sqlite) هنا", type=['db', 'sqlite', 'sqlite3'])
    
    if uploaded_sqlite is not None:
        if st.button("سحب البيانات لقاعدة Supabase 🚀", type="primary", use_container_width=True):
            import sqlite3
            import tempfile
            import os

            # 1. حفظ الملف مؤقتاً في السيرفر عشان نقدر نقرأه
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                tmp.write(uploaded_sqlite.getvalue())
                tmp_path = tmp.name

            try:
                # 2. الاتصال بملف SQLite
                conn = sqlite3.connect(tmp_path)
                cursor = conn.cursor()

                # 3. البحث عن اسم الجدول جوا الملف (عشان لو كان اسمه مختلف)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = cursor.fetchall()

                if not tables:
                    st.error("⚠️ الملف المرفوع فارغ أو لا يحتوي على جداول.")
                else:
                    table_name = tables[0][0] # نأخذ أول جدول نلاقيه
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    # جلب أسماء الأعمدة عشان نربطها صح
                    column_names = [description[0] for description in cursor.description]
                    
                    added_count = 0
                    for row in rows:
                        row_dict = dict(zip(column_names, row))
                        
                        # سحب البيانات (الكود بيبحث عن الاسم الإنجليزي أو العربي عشان ما يعطي خطأ)
                        name = str(row_dict.get("name", row_dict.get("الاسم", ""))).strip()
                        
                        if name and name != "None": # يتأكد إنه في اسم فعلاً
                            phone = str(row_dict.get("phone", row_dict.get("رقم الهاتف", "")))
                            email = str(row_dict.get("email", row_dict.get("البريد الإلكتروني", "")))
                            team = str(row_dict.get("team", row_dict.get("الفريق", "غير محدد")))
                            role = str(row_dict.get("role", row_dict.get("الرتبة", "عضو")))
                            notes = str(row_dict.get("notes", row_dict.get("ملاحظات", "")))
                            
                            # تنظيف القيم الفارغة
                            if phone == "None": phone = ""
                            if email == "None": email = ""
                            if team == "None" or not team: team = "غير محدد"
                            if role == "None" or not role: role = "عضو"
                            if notes == "None": notes = ""
                            
                            points_raw = row_dict.get("points", row_dict.get("النقاط", 0))
                            points = int(points_raw) if str(points_raw).isdigit() else 0

                            # 4. إرسال البيانات لقاعدة بيانات Supabase
                            db.add_member((name, phone, email, team, role, points, notes))
                            added_count += 1
                    
                    st.success(f"✅ تم سحب وإضافة {added_count} عضو بنجاح! اعمل تحديث (Refresh) للصفحة.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
            finally:
                conn.close()
                os.remove(tmp_path) # مسح الملف المؤقت لتنظيف السيرفر
    st.markdown("---")

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
