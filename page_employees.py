import streamlit as st

def show_employees(supabase, TEAMS):
    st.title("👥 هيكل الموظفين والفرق")
    st.markdown("---")
    
    try:
        members_data = supabase.table("members").select("*").execute().data
    except:
        members_data = []

    # 🎨 قاموس الألوان: كل فريق وإله لون خاص فيه
    TEAM_COLORS = {
        "إدارة": "#1e3d59",             # أزرق كحلي فخم
        "ميديا": "#7a1e3d",            # خمري / أحمر داكن
        "IT (أمن سيبراني)": "#134e2a", # أخضر سايبر سري
        "تسويق": "#a65217",            # برتقالي/بني دافئ
        "دعم فني": "#3d3d3d",          # رمادي داكن
        "غير محدد": "#212121"          # أسود باهت
    }

    if members_data:
        for team_name in TEAMS:
            team_members = [m for m in members_data if m.get('team') == team_name]
            if team_members:
                st.subheader(f"📌 فريق الـ {team_name} ({len(team_members)} موظف)")
                cols = st.columns(3)
                
                for i, member in enumerate(team_members):
                    with cols[i % 3]:
                        # بنسحب اللون حسب اسم الفريق، وإذا ما لقاه بحط لون رمادي كاحتياط
                        bg_color = TEAM_COLORS.get(team_name, "#2b2b2b")
                        
                        # تصميم البطاقة مع إضافة تأثير الظل (Box Shadow) عشان تبرز
                        card_html = f"""
                        <div style="background-color: {bg_color}; padding: 15px; border-radius: 12px; border: 1px solid #555; margin-bottom: 15px; box-shadow: 0px 4px 6px rgba(0,0,0,0.3); transition: 0.3s;">
                            <h4 style="color: #ffc13b; margin: 0; font-size: 18px;">👤 {member.get('name', 'بدون اسم')}</h4>
                            <p style="color: #e0e0e0; margin: 8px 0 0 0; font-size: 14px;">📞 {member.get('phone', '-')}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("لا يوجد موظفين في جدول members حتى الآن.")
