import streamlit as st

def show_tasks(supabase):
    st.title("📋 إدارة مهام الفريق")
    try:
        members_data = supabase.table("members").select("*").execute().data
    except:
        members_data = []
        
    with st.expander("➕ إسناد مهمة جديدة للموظفين", expanded=False):
        with st.form("add_task_form"):
            task_title = st.text_input("عنوان المهمة")
            task_desc = st.text_area("تفاصيل المهمة")
            employee_names = [m.get('name', 'مجهول') for m in members_data]
            task_assignee = st.selectbox("المسؤول عن المهمة 👤", employee_names if employee_names else ["لا يوجد موظفين"])
            
            if st.form_submit_button("إضافة المهمة 🚀", use_container_width=True):
                if task_title:
                    try:
                        supabase.table("tasks").insert({
                            "title": task_title, "description": task_desc, "assignee": task_assignee, "status": "قيد الانتظار"
                        }).execute()
                        st.success("تمت إضافة المهمة بنجاح!"); st.rerun()
                    except Exception as e:
                        st.error("❌ خطأ: تأكد من وجود جدول tasks")
    
    st.markdown("---")
    
    try:
        tasks_data = supabase.table("tasks").select("*").execute().data
        if tasks_data:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("<h3 style='text-align:center; color:#ff9800;'>⏳ قيد الانتظار</h3>", unsafe_allow_html=True)
                for t in [x for x in tasks_data if x.get('status') == "قيد الانتظار"]:
                    with st.container(border=True):
                        st.write(f"**{t.get('title')}**\n\n🎯 لـ: {t.get('assignee')}")
                        if st.button("بدء العمل ▶️", key=f"start_{t['id']}", use_container_width=True):
                            supabase.table("tasks").update({"status": "جاري العمل"}).eq("id", t['id']).execute()
                            st.rerun()
            with c2:
                st.markdown("<h3 style='text-align:center; color:#2196f3;'>⚙️ جاري العمل</h3>", unsafe_allow_html=True)
                for t in [x for x in tasks_data if x.get('status') == "جاري العمل"]:
                    with st.container(border=True):
                        st.write(f"**{t.get('title')}**\n\n🎯 لـ: {t.get('assignee')}")
                        if st.button("إنجاز ✅", key=f"done_{t['id']}", use_container_width=True):
                            supabase.table("tasks").update({"status": "مكتملة ✅"}).eq("id", t['id']).execute()
                            st.rerun()
            with c3:
                st.markdown("<h3 style='text-align:center; color:#4caf50;'>✅ مكتملة</h3>", unsafe_allow_html=True)
                for t in [x for x in tasks_data if x.get('status') == "مكتملة ✅"]:
                    with st.container(border=True):
                        st.write(f"**{t.get('title')}**\n\n🎯 لـ: {t.get('assignee')}")
                        if st.button("حذف 🗑️", key=f"del_{t['id']}", use_container_width=True):
                            supabase.table("tasks").delete().eq("id", t['id']).execute()
                            st.rerun()
        else:
            st.info("لا يوجد مهام حالياً. الفريق مرتاح! 😎")
    except:
        st.error("لم يتم العثور على جدول المهام (tasks).")
