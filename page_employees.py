import streamlit as st

def show_employees(supabase, TEAMS):
    st.title("👥 هيكل الموظفين والفرق")
    st.markdown("---")
    
    try:
        # تأكد أن جدول members يحتوي على أعمدة (gender, details, etc.)
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
                        # تحديد الجنس والأيقونة واللون
                        gender = member.get('gender', 'ذكر')  # القيمة الافتراضية
                        if gender == 'ذكر':
                            bg_color = "#1e3d59" # أزرق داكن للذكور
                            gender_icon = "👨"
                            border_color = "#3a7bd5"
                        else:
                            bg_color = "#7a1e3d" # خمري/وردي داكن للإناث
                            gender_icon = "👩"
                            border_color = "#f8a5c2"

                        # تصميم البطاقة
                        card_html = f"""
                        <div style="background-color: {bg_color}; padding: 15px; border-radius: 12px 12px 0 0; 
                                    border: 1px solid {border_color}; margin-bottom: 0px; 
                                    box-shadow: 0px 4px 6px rgba(0,0,0,0.3);">
                            <h4 style="color: #ffc13b; margin: 0; font-size: 18px;">{gender_icon} {member.get('name', 'بدون اسم')}</h4>
                            <p style="color: #e0e0e0; margin: 8px 0 0 0; font-size: 14px;">📞 {member.get('phone', '-')}</p>
                            <p style="color: #bdbdbd; margin: 4px 0 0 0; font-size: 12px;">الجنس: {gender}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # إضافة أزرار التحكم (التعديل والعرض) مباشرة تحت البطاقة
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button(f"👁️ عرض", key=f"view_{member['id']}"):
                                st.session_state['selected_member'] = member
                                st.rerun() # أو افتح Modal لعرض التفاصيل
                        with btn_col2:
                            if st.button(f"📝 تعديل", key=f"edit_{member['id']}"):
                                st.session_state['edit_member_id'] = member['id']
                                # هنا تضع منطق الانتقال لصفحة التعديل
                                st.success(f"جاري الانتقال لتعديل {member['name']}")

                        st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("لا يوجد موظفين في جدول members حتى الآن.")
