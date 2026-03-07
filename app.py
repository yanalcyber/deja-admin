import streamlit as st
import pandas as pd
import os
import sqlite3
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="Deja Admin Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# تصميم CSS احترافي (معدل لحل مشكلة تداخل الخطوط)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    /* تطبيق الخط على كامل الموقع */
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    /* توجيه النصوص لليمين بشكل آمن بدون تخريب الأعمدة */
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* تصميم البطاقات للإحصائيات */
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #4CAF50;
        direction: rtl;
    }
    
    /* إخفاء أدوات المطور الافتراضية */
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
            "points": data[11], "notes": data[12]
        }
        supabase.table("members").insert(row).execute()

    def update_member(self, member_id, data):
        row = {
            "name": data[0], "english_name": data[1], "phone": data[2], "email": data[3],
            "team": data[4], "role": data[5], "residence": data[6], "university": data[7],
            "major": data[8], "academic_year": data[9], "sports_experience": data[10],
            "points": data[11], "notes": data[12]
        }
        supabase.table("members").update(row).eq("id", member_id).execute()

    def delete_member(self, member_id):
        supabase.table("members").delete().eq("id", member_id).execute()

    def get_all_members(self):
        response = supabase.table("members").select("*").order("id", desc=True).execute()
        return response.data

db = DatabaseManager()

TEAMS = ["غير محدد", "فريق ميديا", "فريق IT"]
ROLES = ["عضو", "إداري"]

# ==========================================
# 3. النافذة المنبثقة (البطاقة الكبيرة للتفاصيل والتعديل)
# ==========================================
@st.dialog("🪪 بطاقة العضو الشاملة")
def member_details_dialog(member):
    # عرض المعلومات الأساسية بشكل مرتب
    st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>{member['name']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{member.get('english_name', '-')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"📞 **الهاتف:** {member['phone']}")
        st.write(f"👥 **الفريق:** {member['team']}")
        st.write(f"🎓 **الجامعة:** {member.get('university', '-')}")
        st.write(f"📅 **السنة:** {member.get('academic_year', '-')}")
    with c2:
        st.write(f"📧 **الإيميل:** {member['email']}")
        st.write(f"⭐ **الرتبة:** {member['role']}")
        st.write(f"📚 **التخصص:** {member.get('major', '-')}")
        st.write(f"🏠 **السكن:** {member.get('residence', '-')}")
        
    st.write(f"💯 **النقاط:** {member['points']}")
    st.write(f"🏅 **الخبرة الرياضية:** {member.get('sports_experience', '-')}")
    st.write(f"📝 **ملاحظات:** {member.get('notes', '-')}")
    
    st.markdown("---")
    
    # قسم التعديل داخل البطاقة
    with st.expander("✏️ تعديل بيانات العضو"):
        with st.form(key=f"edit_form_{member['id']}"):
            e_name = st.text_input("الاسم", value=member['name'])
            e_eng = st.text_input("الاسم بالإنجليزي", value=member.get('english_name', ''))
            e_phone = st.text_input("رقم الهاتف", value=member['phone'])
            e_email = st.text_input("الإيميل", value=member['email'])
            
            t_idx = TEAMS.index(member['team']) if member['team'] in TEAMS else 0
            e_team = st.selectbox("الفريق", TEAMS, index=t_idx)
            
            r_idx = ROLES.index(member['role']) if member['role'] in ROLES else 0
            e_role = st.selectbox("الرتبة", ROLES, index=r_idx)
            
            e_res = st.text_input("السكن", value=member.get('residence', ''))
            e_uni = st.text_input("الجامعة", value=member.get('university', ''))
            e_maj = st.text_input("التخصص", value=member.get('major', ''))
            e_ay = st.text_input("السنة", value=member.get('academic_year', ''))
            e_se = st.text_area("الخبرة", value=member.get('sports_experience', ''))
            e_pts = st.number_input("النقاط", value=int(member['points']), step=1)
            e_notes = st.text_area("ملاحظات", value=member.get('notes', ''))
            
            if st.form_submit_button("حفظ التحديثات ✅", use_container_width=True):
                db.update_member(member['id'], (e_name, e_eng, e_phone, e_email, e_team, e_role, e_res, e_uni, e_maj, e_ay, e_se, e_pts, e_notes))
                st.rerun()
                
    # زر الحذف في أسفل البطاقة
    if st.button("حذف الحساب نهائياً ❌", type="secondary", use_container_width=True):
        db.delete_member(member['id'])
        st.rerun()

# ==========================================
# 4. واجهة الدخول 
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
                    except:
                        st.error("❌ بيانات الدخول غير صحيحة.")
        with tab2:
            signup_name = st.text_input("الاسم الكامل")
            signup_phone = st.text_input("رقم الهاتف للتسجيل")
            signup_password = st.text_input("كلمة المرور الجديدة", type="password")
            if st.button("إنشاء الحساب ✍️", use_container_width=True):
                if signup_name and signup_phone and signup_password:
                    try:
                        clean_phone = signup_phone.replace(" ", "").strip()
                        dummy_email = f"{clean_phone}@deja.com"
                        supabase.auth.sign_up({
                            "email": dummy_email, "password": signup_password,
                            "options": {"data": {"name": signup_name}}
                        })
                        st.success("تم الإنشاء بنجاح! يمكنك تسجيل الدخول الآن.")
                    except:
                        st.error("❌ حدث خطأ، تأكد من البيانات.")

# ==========================================
# 5. لوحة الإدارة الاحترافية (بعد الدخول)
# ==========================================
else:
    user_name = st.session_state['user'].user_metadata.get('name', 'مدير النظام')
    members_data = db.get_all_members()

    # القائمة الجانبية القابلة للطي (Sidebar)
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{user_name}**")
        st.markdown("---")
        menu = st.radio("القائمة الرئيسية:", ["👥 بطاقات الأعضاء", "📊 لوحة القيادة", "➕ إضافة عضو جديد", "⚙️ الإعدادات"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

    # ------------------------------------------
    # الصفحة 1: بطاقات الأعضاء (نظام البطاقات الجديد)
    # ------------------------------------------
    if menu == "👥 بطاقات الأعضاء":
        col_title, col_export = st.columns([3, 1])
        with col_title:
            st.title("📇 بطاقات فريق Deja")
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
                if not search_query or search_query.lower() in search_text:
                    filtered_members.append(m)

            cols = st.columns(3)
            for i, member in enumerate(filtered_members):
                with cols[i % 3]: 
                    with st.container(border=True): 
                        st.markdown(f"#### 👤 {member['name']}")
                        st.markdown(f"**الفريق:** {member['team']}")
                        st.markdown(f"**🏠 السكن:** {member.get('residence', '-')}")
                        st.markdown(f"**💯 النقاط:** {member['points']}")
                        
                        if st.button("المزيد ➕", key=f"more_{member['id']}", use_container_width=True):
                            member_details_dialog(member)
        else:
            st.info("لا يوجد أعضاء في الفريق حتى الآن.")

    # ------------------------------------------
    # الصفحة 2: لوحة القيادة (Dashboard)
    # ------------------------------------------
    elif menu == "📊 لوحة القيادة":
        st.title("📊 الإحصائيات العامة")
        
        if members_data:
            df = pd.DataFrame(members_data)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='metric-card'><h3>👥 إجمالي الأعضاء</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            with c2:
                admins = len(df[df['role'] == 'إداري'])
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
            st.info("لا يوجد بيانات لعرض الإحصائيات بعد.")

    # ------------------------------------------
    # الصفحة 3: إضافة عضو جديد
    # ------------------------------------------
    elif menu == "➕ إضافة عضو جديد":
        st.title("➕ تسجيل عضو جديد")
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم باللغة العربية *")
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
                    db.add_member((name, english_name, phone, email, team, role, residence, university, major, academic_year, sports_experience, 0, notes))
                    st.success("تمت الإضافة بنجاح!")
                else:
                    st.error("الاسم الإجباري!")

    # ------------------------------------------
    # الصفحة 4: الإعدادات (الأدوات)
    # ------------------------------------------
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
                            db.add_member((n, str(d.get("الاسم_بالانجليزية", "")).strip(), str(d.get("رقم_الهاتف", "")), "", str(d.get("الفريق", "غير محدد")), "عضو", str(d.get("مكان_السكن", "")), str(d.get("الجامعة", "")), str(d.get("التخصص", "")), str(d.get("السنة_الدراسية", "")), str(d.get("الخبرة_الرياضية", "")), 0, ""))
                            count += 1
                    st.success(f"تم سحب {count} عضو!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
