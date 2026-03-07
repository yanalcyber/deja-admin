import streamlit as st
import pandas as pd
import os
import sqlite3
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="Deja Admin Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea, .stRadio {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #4CAF50;
        direction: rtl;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة قاعدة البيانات
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state:
    st.session_state['user'] = None

class DatabaseManager:
    def add_member(self, data):
        row = {
            "name": data[0], "english_name": data[1], "phone": data[2], "email": data[3],
            "team": data[4], "role": data[5], "residence": data[6], "university": data[7],
            "major": data[8], "academic_year": data[9], "sports_experience": data[10],
            "points": data[11], "notes": data[12], "gender": data[13]
        }
        supabase.table("members").insert(row).execute()

    def update_member(self, member_id, data):
        row = {
            "name": data[0], "english_name": data[1], "phone": data[2], "email": data[3],
            "team": data[4], "role": data[5], "residence": data[6], "university": data[7],
            "major": data[8], "academic_year": data[9], "sports_experience": data[10],
            "points": data[11], "notes": data[12], "gender": data[13]
        }
        supabase.table("members").update(row).eq("id", member_id).execute()

    def delete_member(self, member_id):
        supabase.table("members").delete().eq("id", member_id).execute()

    def get_all_members(self):
        response = supabase.table("members").select("*").order("id", desc=True).execute()
        return response.data

db = DatabaseManager()

TEAMS = ["غير محدد", "فريق الإدارة", "فريق الميديا", "فريق IT", "فريق التنظيم", "فريق اللوجستك"]
ROLES = ["عضو", "إداري", "قائد فريق"]
GENDERS = ["غير محدد", "ذكر", "أنثى"]

# ==========================================
# 3. النافذة المنبثقة (البطاقة الكبيرة)
# ==========================================
@st.dialog("🪪 بطاقة العضو الشاملة")
def member_details_dialog(member):
    st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>{member['name']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{member.get('english_name', '-')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"📞 **الهاتف:** {member['phone']}")
        st.write(f"👥 **الفريق:** {member['team']}")
        st.write(f"🎓 **الجامعة:** {member.get('university', '-')}")
        st.write(f"📅 **السنة:** {member.get('academic_year', '-')}")
        st.write(f"⚥ **الجنس:** {member.get('gender', 'غير محدد')}")
    with c2:
        st.write(f"📧 **الإيميل:** {member['email']}")
        st.write(f"⭐ **الرتبة:** {member['role']}")
        st.write(f"📚 **التخصص:** {member.get('major', '-')}")
        st.write(f"🏠 **السكن:** {member.get('residence', '-')}")
        
    st.write(f"💯 **النقاط:** {member['points']}")
    st.write(f"🏅 **الخبرة الرياضية:** {member.get('sports_experience', '-')}")
    st.write(f"📝 **ملاحظات:** {member.get('notes', '-')}")
    
    st.markdown("---")
    
    with st.expander("✏️ تعديل بيانات العضو"):
        with st.form(key=f"edit_form_{member['id']}"):
            e_name = st.text_input("الاسم", value=member['name'])
            e_eng = st.text_input("الاسم بالإنجليزي", value=member.get('english_name', ''))
            
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                e_phone = st.text_input("رقم الهاتف", value=member['phone'])
            with c_g2:
                g_idx = GENDERS.index(member.get('gender', 'غير محدد')) if member.get('gender', 'غير محدد') in GENDERS else 0
                e_gender = st.selectbox("الجنس", GENDERS, index=g_idx)

            e_email = st.text_input("الإيميل", value=member['email'])
            
            t_idx = TEAMS.index(member['team']) if member['team'] in TEAMS else 0
            e_team = st.selectbox("الفريق", TEAMS, index=t_idx)
            
            r_idx = ROLES.index(member['role']) if member['role'] in ROLES else 0
            e_role = st.selectbox("الرتبة", ROLES, index=r_idx)
            
            e_res = st.text_input("السكن", value=member.get('residence', ''))
            e_uni = st.text_input("الجامعة", value=member.get('university', ''))
            e_maj = st.text_input("التخصص", value=member.get('major', ''))
            e_ay = st.text_input("السنة الدراسية", value=member.get('academic_year', ''))
            e_se = st.text_area("الخبرة", value=member.get('sports_experience', ''))
            
            safe_points = int(member['points']) if member.get('points') is not None else 0
            e_pts = st.number_input("النقاط", value=safe_points, step=1)
            
            e_notes = st.text_area("ملاحظات", value=member.get('notes', ''))
            
            if st.form_submit_button("حفظ التحديثات ✅", use_container_width=True):
                try:
                    db.update_member(member['id'], (e_name, e_eng, e_phone, e_email, e_team, e_role, e_res, e_uni, e_maj, e_ay, e_se, e_pts, e_notes, e_gender))
                    st.success("تم الحفظ بنجاح! جاري تحديث الصفحة...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: هل تأكدت من إضافة عمود `gender` في Supabase؟ التفاصيل: {str(e)}")
                
    if st.button("حذف الحساب نهائياً ❌", type="secondary", use_container_width=True):
        db.delete_member(member['id'])
        st.rerun()

# ==========================================
# 4. واجهة الدخول (تم التعديل لكشف الأخطاء)
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>بوابة الإدارة المركزية</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab1:
            login_phone = st.text_input("رقم الهاتف", placeholder="مثال: 0791234567")
            login_password = st.text_input("كلمة المرور", type="password")
            if st.button("تسجيل الدخول 🚀", use_container_width=True, type="primary"):
                if login_phone and login_password:
                    try:
                        clean_phone = login_phone.replace(" ", "").strip()
                        dummy_email = f"{clean_phone}@deja.com"
                        res = supabase.auth.sign_in_with_password({"email": dummy_email, "password": login_password})
                        st.session_state['user'] = res.user
                        st.rerun()
                    except Exception as e:
                        # هون رح ينطبع الخطأ الحقيقي اللي مانعك تدخل!
                        st.error(f"❌ فشل الدخول. تفاصيل الخطأ: {str(e)}")
                else:
                    st.warning("⚠️ يرجى إدخال رقم الهاتف وكلمة المرور أولاً.")
                    
        with tab2:
            signup_name = st.text_input("الاسم الكامل")
            signup_phone = st.text_input("رقم الهاتف للتسجيل")
            signup_password = st.text_input("كلمة المرور الجديدة (6 أحرف/أرقام على الأقل)", type="password")
            if st.button("إنشاء الحساب ✍️", use_container_width=True):
                if signup_name and signup_phone and signup_password:
                    if len(signup_password) < 6:
                        st.error("❌ كلمة المرور ضعيفة! يجب أن تتكون من 6 خانات على الأقل.")
                    else:
                        try:
                            clean_phone = signup_phone.replace(" ", "").strip()
                            dummy_email = f"{clean_phone}@deja.com"
                            supabase.auth.sign_up({
                                "email": dummy_email, "password": signup_password,
                                "options": {"data": {"name": signup_name}}
                            })
                            st.success("تم الإنشاء بنجاح! يمكنك العودة لصفحة تسجيل الدخول الآن.")
                        except Exception as e:
                            st.error(f"❌ فشل إنشاء الحساب. تفاصيل الخطأ: {str(e)}")
                else:
                    st.warning("⚠️ يرجى تعبئة جميع الحقول قبل الضغط على الزر.")

# ==========================================
# 5. لوحة الإدارة الاحترافية (بعد الدخول)
# ==========================================
else:
    user_name = st.session_state['user'].user_metadata.get('name', 'مدير النظام')
    members_data = db.get_all_members()

    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{user_name}**")
        st.markdown("---")
        menu = st.radio("القائمة الرئيسية:", ["👥 بطاقات الأعضاء", "📊 لوحة القيادة", "➕ إضافة عضو جديد", "⚙️ الإعدادات"])
        
        st.markdown("---")
        st.markdown("### 🏷️ تصفية حسب الفريق")
        selected_team_filter = st.radio("عرض فريق محدد:", ["الكل"] + TEAMS)

        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

    if menu == "👥 بطاقات الأعضاء":
        col_title, col_export = st.columns([3, 1])
        with col_title:
            if selected_team_filter == "الكل":
                st.title("📇 بطاقات فريق Deja")
            else:
                st.title(f"📇 {selected_team_filter}")
                
        with col_export:
            if members_data:
                df = pd.DataFrame(members_data)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 تصدير (Excel)", data=csv, file_name='deja_team.csv', mime='text/csv', use_container_width=True)

        search_query = st.text_input("🔍 ابحث عن عضو بالاسم، الهاتف، أو السكن...", placeholder="اكتب للبحث...")
        st.markdown("---")

        if members_data:
            filtered_members = []
            for m in members_data:
                search_text = f"{m['name']} {m['phone']} {m.get('residence','')} {m['team']}".lower()
                match_search = not search_query or search_query.lower() in search_text
                match_team = (selected_team_filter == "الكل") or (m['team'] == selected_team_filter)
                
                if match_search and match_team:
                    filtered_members.append(m)

            if not filtered_members:
                st.warning("⚠️ لا يوجد أعضاء يطابقون الفلتر المختار.")
            else:
                cols = st.columns(3)
                for i, member in enumerate(filtered_members):
                    with cols[i % 3]: 
                        bg_color = "#1E1E1E" 
                        gender = member.get('gender', 'غير محدد')
                        if gender == "ذكر":
                            bg_color = "#0e2038" 
                        elif gender == "أنثى":
                            bg_color = "#361125" 

                        badges = ""
                        if member['role'] in ['إداري', 'قائد فريق']:
                            badges += f"<div style='background-color:#FFD700; color:#000; padding:4px 12px; border-radius:15px; font-size:12px; font-weight:bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>{member['role']}</div>"
                        if member['team'] == 'فريق الميديا':
                            badges += "<div style='background-color:#E53935; color:#FFF; padding:4px 12px; border-radius:15px; font-size:12px; font-weight:bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>ميديا 📸</div>"
                        if member['team'] == 'فريق IT':
                            badges += "<div style='background-color:#4CAF50; color:#FFF; padding:4px 12px; border-radius:15px; font-size:12px; font-weight:bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>IT 💻</div>"
                        
                        card_html = f"""
                        <div style="background-color:{bg_color}; padding:20px; border-radius:12px; border: 1px solid #444; position:relative; min-height:180px; margin-bottom:15px; direction:rtl; text-align:right;">
                            <div style="position:absolute; top:15px; left:15px; display:flex; flex-direction:column; gap:8px;">
                                {badges}
                            </div>
                            <h4 style="margin-top:0; margin-bottom:10px; color:#FFF; font-size: 18px;">👤 {member['name']}</h4>
                            <p style="margin:5px 0; font-size:14px; color:#DDD;"><strong>الفريق:</strong> {member['team']}</p>
                            <p style="margin:5px 0; font-size:14px; color:#DDD;"><strong>🏠 السكن:</strong> {member.get('residence', '-')}</p>
                            <p style="margin:5px 0; font-size:14px; color:#4CAF50;"><strong>💯 النقاط:</strong> {member['points']}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        if st.button("المزيد ➕", key=f"more_{member['id']}", use_container_width=True):
                            member_details_dialog(member)
        else:
            st.info("لا يوجد أعضاء في الفريق حتى الآن.")

    elif menu == "📊 لوحة القيادة":
        st.title("📊 الإحصائيات العامة")
        if members_data:
            df = pd.DataFrame(members_data)
            if selected_team_filter != "الكل":
                df = df[df['team'] == selected_team_filter]
                st.info(f"💡 هذه الإحصائيات مخصصة لـ: **{selected_team_filter}**")
            if not df.empty:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"<div class='metric-card'><h3>👥 إجمالي الأعضاء</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
                with c2:
                    admins = len(df[df['role'].isin(['إداري', 'قائد فريق'])])
                    st.markdown(f"<div class='metric-card'><h3>⭐ الإداريين</h3><h2>{admins}</h2></div>", unsafe_allow_html=True)
                with c3:
                    top_points = df['points'].max()
                    st.markdown(f"<div class='metric-card'><h3>🏆 أعلى نقاط</h3><h2>{top_points}</h2></div>", unsafe_allow_html=True)
                st.write("---")
                col_chart, col_leader = st.columns([2, 1])
                with col_chart:
                    st.subheader("📈 توزيع الأعضاء حسب الفرق")
                    team_counts = df['team'].value_counts()
                    st.bar_chart(team_counts)
                with col_leader:
                    st.subheader("🔥 أعلى 5 نقاط")
                    top_5 = df.nlargest(5, 'points')[['name', 'points']]
                    for idx, row in top_5.iterrows():
                        st.success(f"**{row['name']}** - {row['points']} نقطة")
            else:
                st.warning("⚠️ لا يوجد بيانات لهذا الفريق.")
        else:
            st.info("لا يوجد بيانات لعرض الإحصائيات بعد.")

    elif menu == "➕ إضافة عضو جديد":
        st.title("➕ تسجيل عضو جديد")
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم باللغة العربية *")
                gender = st.selectbox("الجنس", GENDERS)
                phone = st.text_input("رقم الهاتف")
                team = st.selectbox("الفريق", TEAMS)
                university = st.text_input("الجامعة")
                academic_year = st.text_input("السنة الدراسية")
            with c2:
                english_name = st.text_input("الاسم بالإنجليزية")
                email = st.text_input("البريد الإلكتروني")
                role = st.selectbox("الرتبة", ROLES)
                major = st.text_input("التخصص")
                residence = st.text_input("مكان السكن")
            
            sports_experience = st.text_area("الخبرة الرياضية")
            notes = st.text_area("ملاحظات أخرى")
            
            if st.form_submit_button("إضافة العضو للقاعدة 🚀", type="primary", use_container_width=True):
                if name.strip():
                    try:
                        db.add_member((name, english_name, phone, email, team, role, residence, university, major, academic_year, sports_experience, 0, notes, gender))
                        st.success("تمت الإضافة بنجاح!")
                    except Exception as e:
                        st.error(f"❌ خطأ: هل تأكدت من إضافة عمود `gender` في Supabase؟ التفاصيل: {str(e)}")
                else:
                    st.error("الاسم الإجباري!")

    elif menu == "⚙️ الإعدادات":
        st.title("⚙️ إعدادات النظام")
        st.info("هذا القسم مخصص للعمليات التقنية وسحب البيانات القديمة.")
        
        if os.path.exists("deja.db"):
            st.warning("⚠️ تم العثور على ملف `deja.db` القديم في الخوادم.")
            if st.button("تنزيل الأسماء من الملف 🚀", type="primary"):
                try:
                    conn = sqlite3.connect(':memory:')
                    cursor = conn.cursor()
                    with open("deja.db", "r", encoding="utf-8") as f: cursor.executescript(f.read())
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                    table_name = cursor.fetchall()[0][0]
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    cols = [d[0] for d in cursor.description]
                    count = 0
                    for row in rows:
                        d = dict(zip(cols, row))
                        n = str(d.get("الاسم_بالعربية", "")).strip()
                        if n and n != "None":
                            db.add_member((n, str(d.get("الاسم_بالانجليزية", "")).strip(), str(d.get("رقم_الهاتف", "")), "", str(d.get("الفريق", "غير محدد")), "عضو", str(d.get("مكان_السكن", "")), str(d.get("الجامعة", "")), str(d.get("التخصص", "")), str(d.get("السنة_الدراسية", "")), str(d.get("الخبرة_الرياضية", "")), 0, "", "غير محدد"))
                            count += 1
                    st.success(f"تم سحب {count} عضو!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
