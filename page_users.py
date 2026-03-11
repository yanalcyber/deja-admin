import streamlit as st

def show_users(supabase, TEAMS):
    st.title("🔐 قاعدة بيانات الحسابات السريّة")
    st.markdown("---")
    
    try:
        users_data = supabase.table("USER").select("*").execute().data
    except:
        users_data = []

    if users_data:
        st.success(f"يوجد ({len(users_data)}) حساب تم إنشاؤه:")
        for idx, acc in enumerate(users_data, 1):
            with st.container(border=True):
                current_team = acc.get('team', 'غير محدد')
                st.markdown(f"**{idx}. 👤 الاسم:** {acc.get('name', 'بدون اسم')} | **📞 الرقم:** {acc.get('phone', 'بدون رقم')}")
                st.markdown(f"**🔑 الباسورد:** `{acc.get('password', 'غير متوفر')}` | **👥 الفريق:** `{current_team}`")
                
                with st.expander("✏️ تعديل بيانات الحساب"):
                    with st.form(key=f"edit_form_{acc['id']}"):
                        new_name = st.text_input("الاسم", value=acc.get('name', ''))
                        new_phone = st.text_input("الرقم", value=acc.get('phone', ''))
                        new_pass = st.text_input("الباسورد", value=acc.get('password', ''))
                        team_index = TEAMS.index(current_team) if current_team in TEAMS else 0
                        new_team = st.selectbox("الفريق", TEAMS, index=team_index)
                        
                        if st.form_submit_button("حفظ التعديلات ✅", use_container_width=True):
                            try:
                                supabase.table("USER").update({
                                    "name": new_name, "phone": new_phone, "password": new_pass, "team": new_team
                                }).eq("id", acc['id']).execute()
                                st.success("تم التعديل بنجاح!"); st.rerun()
                            except Exception as e:
                                st.error(f"❌ صار خطأ: {e}")
    else:
        st.warning("الجدول فارغ.")
