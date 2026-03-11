import streamlit as st
from supabase import create_client

# 1. إعداد الصفحة والاتصال
st.set_page_config(page_title="Deja Workspace Pro", page_icon="⚡", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.session_state['user'] = None

TEAMS = ["إدارة", "ميديا", "IT (أمن سيبراني)", "تسويق", "دعم فني", "غير محدد"]

# ==========================================
# واجهة إنشاء الحساب والدخول
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #ffeb3b;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول 🔑", "إنشاء حساب جديد ✍️"])
        
        with tab1:
            log_phone = st.text_input("رقم الهاتف")
            log_pass = st.text_input("كلمة المرور", type="password")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{log_phone.strip()}@deja.com", "password": log_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except:
                    st.error("❌ بيانات الدخول غير صحيحة.")

        with tab2:
            reg_name = st.text_input("الاسم الكامل")
            reg_phone = st.text_input("رقم الهاتف (الجديد)")
            reg_team = st.selectbox("الفريق 👥", TEAMS)
            reg_pass = st.text_input("كلمة المرور (6 خانات)", type="password")
            
            if st.button("إنشاء الحساب 🚀", use_container_width=True):
                if reg_name and reg_phone and len(reg_pass) >= 6:
                    try:
                        # 1. التسجيل بنظام الحماية
                        supabase.auth.sign_up({"email": f"{reg_phone.strip()}@deja.com", "password": reg_pass})
                        
                        # 2. إضافة لجدول USER السري
                        supabase.table("USER").insert({
                            "name": reg_name, "phone": reg_phone, "password": reg_pass, "team": reg_team
                        }).execute()
                        
                        # 3. إضافة لجدول members عشان يطلع بصفحة الموظفين والمهام
                        try:
                            supabase.table("members").insert({
                                "name": reg_name, "phone": reg_phone, "team": reg_team, "role": "عضو جديد"
                            }).execute()
                        except:
                            pass # في حال كان جدول members ما فيه هاي الأعمدة ما يضرب الكود
                            
                        st.success("✅ تم إنشاء الحساب بنجاح! ارجع لتبويبة الدخول.")
                    except:
                        st.error("❌ حدث خطأ! تأكد من البيانات.")
                else:
                    st.warning("⚠️ يرجى تعبئة الحقول بشكل صحيح.")

# ==========================================
# اللوحة الرئيسية (بعد الدخول)
# ==========================================
else:
    # --- القائمة الجانبية ---
    with st.sidebar:
        st.markdown("### 👨‍💻 أهلاً بك في مساحة العمل")
        st.markdown("---")
        menu = st.radio("القائمة الرئيسية:", ["👥 الموظفين والفرق", "📋 لوحة المهام", "🔐 إدارة حسابات (USER)"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

    # سحب بيانات جدول USER (للصفحة السرية)
    try:
        users_data = supabase.table("USER").select("*").execute().data
    except:
        users_data = []

    # سحب بيانات جدول members (للموظفين والمهام)
    try:
        members_data = supabase.table("members").select("*").execute().data
    except:
        members_data = []

    # ---------------------------------------------------------
    # 1. صفحة الموظفين والفرق (من جدول members)
    # ---------------------------------------------------------
    if menu == "👥 الموظفين والفرق":
        st.title("👥 هيكل الموظفين والفرق")
        st.markdown("---")
        
        if members_data:
            # فلترة وعرض الأعضاء حسب الفريق من جدول members
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

    # ---------------------------------------------------------
    # 2. صفحة لوحة المهام (تعتمد على members)
    # ---------------------------------------------------------
    elif menu == "📋 لوحة المهام":
        st.title("📋 إدارة مهام الفريق")
        
        # صندوق إضافة مهمة جديدة
        with st.expander("➕ إسناد مهمة جديدة للموظفين", expanded=False):
            with st.form("add_task_form"):
                task_title = st.text_input("عنوان المهمة")
                task_desc = st.text_area("تفاصيل المهمة")
                
                # جلب أسماء الموظفين من جدول members
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
                            st.error(f"❌ خطأ: تأكد من وجود جدول tasks")
        
        st.markdown("---")
        
        # عرض المهام
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

    # ---------------------------------------------------------
    # 3. صفحة إدارة الحسابات (USER) - من جدول USER
    # ---------------------------------------------------------
    elif menu == "🔐 إدارة حسابات (USER)":
        st.title("🔐 قاعدة بيانات الحسابات السريّة")
        st.markdown("---")
        
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
