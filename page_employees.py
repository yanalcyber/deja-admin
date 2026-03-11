import streamlit as st

def show_employees(supabase, TEAMS):
    st.title("👥 هيكل الموظفين والفرق")
    st.markdown("---")
    
    try:
        members_data = supabase.table("members").select("*").execute().data
    except:
        members_data = []

    if members_data:
        for team_name in TEAMS:
            team_members = [m for m in members_data if m.get('team') == team_name]
            if team_members:
                st.subheader(f"📌 فريق الـ {team_name} ({len(team_members)} موظف)")
                cols = st.columns(3)
                
                for i, member in enumerate(team_members):
                    with cols[i % 3]:
                        # 1. إصلاح مشكلة الجنس (معالجة قيمة None أو الفراغ)
                        raw_gender = member.get('gender')
                        if raw_gender is None or str(raw_gender).strip().lower() == 'none' or raw_gender == '':
                            gender = 'ذكر'  # القيمة الافتراضية إذا كان الحقل فارغ
                        else:
                            gender = raw_gender

                        # 2. تحديد الألوان بناءً على الجنس بشكل صحيح
                        if gender == 'ذكر':
                            bg_color = "#1e3d59" # أزرق داكن للذكور
                            gender_icon = "👨"
                            border_color = "#3a7bd5"
                        elif gender == 'أنثى':
                            bg_color = "#7a1e3d" # خمري/وردي داكن للإناث
                            gender_icon = "👩"
                            border_color = "#f8a5c2"
                        else: # لون محايد في حال وجود خطأ آخر
                            bg_color = "#3d3d3d"
                            gender_icon = "👤"
                            border_color = "#777777"

                        # 3. تحسين التصميم وإضافة dir="rtl" عشان العربي يطلع مرتب
                        card_html = f"""
                        <div dir="rtl" style="background-color: {bg_color}; padding: 15px; border-radius: 12px 12px 0 0; 
                                    border: 1px solid {border_color}; border-bottom: none; margin-bottom: 0px; 
                                    box-shadow: 0px 4px 6px rgba(0,0,0,0.3); text-align: right;">
                            <h4 style="color: #ffc13b; margin: 0; font-size: 18px;">{gender_icon} {member.get('name', 'بدون اسم')}</h4>
                            <p style="color: #e0e0e0; margin: 8px 0 0 0; font-size: 14px;">📞 {member.get('phone', 'لا يوجد رقم')}</p>
                            <p style="color: #bdbdbd; margin: 4px 0 0 0; font-size: 12px;">الجنس: {gender}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # 4. تحسين شكل الأزرار (إضافة use_container_width=True عشان تعبي المكان بشكل متناسق)
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("👁️ عرض", key=f"view_{member['id']}", use_container_width=True):
                                st.session_state['selected_member'] = member
                                # st.rerun() # شيل الـ Comment عنها إذا بدك الصفحة تعمل ريفريش
                        with btn_col2:
                            if st.button("📝 تعديل", key=f"edit_{member['id']}", use_container_width=True):
                                st.session_state['edit_member_id'] = member['id']
                                st.success(f"جاري الانتقال لتعديل بيانات: {member['name']}")

                        st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("لا يوجد موظفين في جدول members حتى الآن.")
