import streamlit as st
import pandas as pd
import os
import sqlite3
from supabase import create_client, Client

# ==========================================
# 1. إعدادات الصفحة والتصميم (العالمي)
# ==========================================
st.set_page_config(page_title="Deja Admin Pro", page_icon="⚡", layout="wide")

# تصميم CSS احترافي (خطوط، ألوان، وإخفاء أدوات Streamlit الافتراضية)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #4CAF50;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
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
# 3. واجهة الدخول 
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
# 4. لوحة الإدارة الاحترافية (بعد الدخول)
# ==========================================
else:
    user_name = st.session_state['user'].user_metadata.get('name', 'مدير النظام')
    members_data = db.get_all_members()
    df = pd.DataFrame(members_data) if members_data else pd.DataFrame()

    # القائمة الجانبية (Navigation)
    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{user_name}**")
        st.markdown("---")
        menu = st.radio("القائمة الرئيسية:", ["📊 لوحة القيادة", "👥 إدارة الأعضاء", "➕ إضافة عضو جديد", "⚙️ أدوات النظام"])
        st.markdown("---")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

    # ------------------------------------------
    # الصفحة 1: لوحة القيادة (Dashboard)
    # ------------------------------------------
    if menu == "📊 لوحة القيادة":
        st.title("📊 الإحصائيات العامة")
        
        if not df.empty:
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
                st.subheader("🔥 لوحة الشرف (أعلى 5)")
                top_5 = df.nlargest(5, 'points')[['name', 'points']]
                for idx, row in top_5.iterrows():
                    st.success(f"**{row['name']}** - {row['points']} نقطة")
        else:
            st.info("لا يوجد بيانات لعرض الإحصائيات بعد.")

    # ------------------------------------------
    # الصفحة 2: إدارة الأعضاء
    # ------------------------------------------
    elif menu == "👥 إدارة الأعضاء":
        col_title, col_export = st.columns([3, 1])
        with col_title:
            st.title("👥 إدارة فريق Deja")
        with col_export:
            if not df.empty:
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 تصدير البيانات (Excel/CSV)", data=csv, file_name='deja_team.csv', mime='text/csv', use_container_width=True)

        search_query = st.text_input("🔍 ابحث بالاسم، رقم الهاتف، أو الإيميل...", placeholder="اكتب للبحث السريع...")
        
        # ترويسة الجدول الاحترافي
        st.markdown("---")
        header_cols = st.columns([3, 2, 3, 1])
        header_cols[0].markdown("**👤 الاسم**")
        header_cols[1].markdown("**📞 رقم الهاتف**")
        header_cols[2].markdown("**📧 البريد الإلكتروني**")
        header_cols[3].markdown("**⚙️ الإجراءات**")
        st.markdown("---")

        if not df.empty:
            for _, member in df.iterrows():
                if search_query:
                    search_text = f"{member['name']} {member['phone']} {member['email']}".lower()
                    if search_query.lower() not in search_text:
                        continue

                cols = st.columns([3, 2, 3, 1])
                cols[0].write(f"**{member['name']}**")
                cols[1].write(member['phone'] if member['phone'] else "-")
                cols[2].write(member['email'] if member['email'] else "-")
                
                with cols[3]:
                    with st.popover("⋮"):
                        tab_info, tab_edit, tab_del = st.tabs(["🪪 التفاصيل", "✏️ تعديل", "🗑️ حذف"])
                        
                        with tab_info:
                            st.write(f"**الجامعة:** {member.get('university', '-')} | **الفريق:** {member['team']}")
                            st.write(f"**التخصص:** {member.get('major', '-')} | **السنة:** {member.get('academic_year', '-')}")
                            st.write(f"**السكن:** {member.get('residence', '-')}")
                            st.write(f"**النقاط:** {member['points']}")
                            st.write(f"**الخبرة:** {member.get('sports_experience', '-')}")

                        with tab_edit:
                            with st.form(key=f"form_{member['id']}"):
                                e_name = st.text_input("الاسم", value=member['name'])
                                e_phone = st.text_input("رقم الهاتف", value=member['phone'])
                                e_team = st.selectbox("الفريق", TEAMS, index=TEAMS.index(member['team']) if member['team'] in TEAMS else 0)
                                e_points = st.number_input("النقاط", value=int(member['points']), step=1)
                                
                                if st.form_submit_button("حفظ التحديث ✅", use_container_width=True):
                                    db.update_member(member['id'], (e_name, member.get('english_name',''), e_phone, member['email'], e_team, member['role'], member.get('residence',''), member.get('university',''), member.get('major',''), member.get('academic_year',''), member.get('sports_experience',''), e_points, member.get('notes','')))
                                    st.rerun()

                        with tab_del:
                            if st.button("تأكيد الحذف ❌", key=f"del_{member['id']}", use_container_width=True, type="secondary"):
                                db.delete_member(member['id'])
                                st.rerun()
                st.markdown("---")

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
    # الصفحة 4: أدوات النظام (للمطورين)
    # ------------------------------------------
    elif menu == "⚙️ أدوات النظام":
        st.title("⚙️ الصيانة والأدوات")
        st.info("هذا القسم مخصص للعمليات التقنية وسحب البيانات القديمة.")
        
        if os.path.exists("deja.db"):
            st.warning("⚠️ تم العثور على ملف `deja.db` القديم في الخوادم.")
            if st.button("سحب الأسماء من الملف لقاعدة البيانات الحية 🚀", type="primary"):
                # (نفس كود السحب القديم موجود هنا وتلقائي بيشتغل)
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
                except Exception as e:
                    st.error(f"خطأ: {e}")
