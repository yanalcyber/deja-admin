import streamlit as st

def show_employees(supabase, TEAMS):
    st.title("👥 هيكل الموظفين والفرق")
    st.markdown("---")

    # 1️⃣ التحقق إذا كنا في وضع "التعديل"
    if 'editing_member' in st.session_state:
        member = st.session_state['editing_member']
        st.subheader(f"✏️ تعديل بيانات الموظف: {member.get('name')}")
        
        # إنشاء نموذج (Form) للتعديل
        with st.form("edit_form"):
            new_name = st.text_input("الاسم", value=member.get('name', ''))
            new_phone = st.text_input("رقم الهاتف", value=member.get('phone', ''))
            
            # تحديد الجنس الحالي لعرضه كقيمة افتراضية
            current_gender = member.get('gender')
            if current_gender is None or current_gender == '' or str(current_gender).lower() == 'none':
                current_gender = 'ذكر'
            gender_index = 0 if current_gender == 'ذكر' else 1
            new_gender = st.selectbox("الجنس", ["ذكر", "أنثى"], index=gender_index)
            
            # تحديد الفريق الحالي
            current_team = member.get('team')
            team_index = TEAMS.index(current_team) if current_team in TEAMS else 0
            new_team = st.selectbox("الفريق", TEAMS, index=team_index)

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 حفظ التعديلات", use_container_width=True)
            with col2:
                # زر إضافي لإلغاء العملية والرجوع
                cancel = st.form_submit_button("❌ إلغاء", use_container_width=True)

            if submitted:
                # كود تحديث البيانات في Supabase
                try:
                    supabase.table("members").update({
                        "name": new_name,
                        "phone": new_phone,
                        "gender": new_gender,
                        "team": new_team
                    }).eq("id", member['id']).execute()
                    
                    st.success("✅ تم تحديث بيانات الموظف بنجاح!")
                    del st.session_state['editing_member'] # إنهاء وضع التعديل
                    st.rerun() # عمل ريفريش للصفحة عشان تظهر التعديلات الجديدة
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء التحديث: {e}")
            
            if cancel:
                del st.session_state['editing_member']
                st.rerun()
                
        # إيقاف عرض باقي الصفحة (البطاقات) طول ما إحنا جوا شاشة التعديل
        return 

    # 2️⃣ كود عرض البطاقات (الوضع الطبيعي)
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
                        raw_gender = member.get('gender')
                        if raw_gender is None or str(raw_gender).strip().lower() == 'none' or raw_gender == '':
                            gender = 'ذكر'
                        else:
                            gender = raw_gender

                        if gender == 'ذكر':
                            bg_color = "#1e3d59" 
                            gender_icon = "👨"
                            border_color = "#3a7bd5"
                        elif gender == 'أنثى':
                            bg_color = "#7a1e3d" 
                            gender_icon = "👩"
                            border_color = "#f8a5c2"
                        else: 
                            bg_color = "#3d3d3d"
                            gender_icon = "👤"
                            border_color = "#777777"

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
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("👁️ عرض", key=f"view_{member['id']}", use_container_width=True):
                                st.session_state['viewing_member'] = member
                                st.rerun()
                        with btn_col2:
                            # 🔴 التعديل المهم هنا: لما نضغط زر التعديل، بنحفظ الموظف وبنعمل ريفريش
                            if st.button("📝 تعديل", key=f"edit_{member['id']}", use_container_width=True):
                                st.session_state['editing_member'] = member
                                st.rerun() 

                        st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("لا يوجد موظفين في جدول members حتى الآن.")
