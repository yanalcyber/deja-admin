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
# --- أداة استيراد البيانات من ملف JSON ---
    st.markdown("---")
    st.subheader("📥 استيراد بيانات الأعضاء القديمة (من ملف JSON)")
    uploaded_file = st.file_uploader("ارفع ملف deja_data.JSON هنا", type=['json'])
    
    if uploaded_file is not None:
        import json
        if st.button("استيراد البيانات لقاعدة البيانات 🚀", type="primary"):
            try:
                data = json.load(uploaded_file)
                added_count = 0
                for item in data:
                    name = item.get("الاسم الثلاثي باللغة العربية", "").strip()
                    if name:  # التأكد إن الاسم موجود
                        phone = str(item.get("رقم الهاتف", ""))
                        email = str(item.get("البريد الإلكتروني", ""))
                        
                        team = item.get("الفريق", "غير محدد")
                        if not team: team = "غير محدد"
                        
                        role = item.get("الرتبة", "عضو")
                        if not role: role = "عضو"
                        
                        points = 0
                        
                        # دمج التخصص والجامعة جوا حقل "الملاحظات" عشان ما يضيعوا
                        major = item.get("التخصص الجامعي", "")
                        uni = item.get("اسم الجامعة ان وجد", "")
                        notes = item.get("ملاحظات", "")
                        final_notes = f"{notes} | {major} - {uni}".strip(" | -")

                        # إرسال البيانات لقاعدة بيانات Supabase
                        db.add_member((name, phone, email, team, role, points, final_notes))
                        added_count += 1
                
                st.success(f"✅ تم سحب وإضافة {added_count} عضو بنجاح! اعمل تحديث (Refresh) للصفحة لتشوفهم بالجدول.")
            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")
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

