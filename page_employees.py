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
                        bg_color = "#1e3d59" if team_name == "إدارة" else "#2b2b2b"
                        card_html = f"""
                        <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border: 1px solid #555; margin-bottom: 15px;">
                            <h4 style="color: #ffc13b; margin: 0;">👤 {member.get('name', 'بدون اسم')}</h4>
                            <p style="color: #ccc; margin: 5px 0;">📞 {member.get('phone', '-')}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("لا يوجد موظفين في جدول members حتى الآن.")
