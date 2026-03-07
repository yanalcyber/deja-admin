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
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; }
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stTextInput, .stSelectbox, .stTextArea, .stRadio, .stMultiSelect {
        direction: rtl !important; text-align: right !important;
    }
    .metric-card {
        background-color: #1E1E1E; border-radius: 10px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
        border-top: 4px solid #4CAF50; direction: rtl;
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

TEAMS = ["فريق الإدارة", "فريق الميديا", "فريق IT", "فريق التنظيم", "فريق اللوجستك"]
ROLES = ["عضو", "إداري", "قائد فريق"]
GENDERS = ["غير محدد", "ذكر", "أنثى"]

# ==========================================
# 3. النافذة المنبثقة (البطاقة الكبيرة)
# ==========================================
@st.dialog("🪪 بطاقة العضو الشاملة")
def member_details_dialog(member):
    st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>{member['name']}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"📞 **الهاتف:** {member['phone']}")
        st.write(f"👥 **الفرق:** {member['team']}")
        st.write(f"🎓 **الجامعة:** {member.get('university', '-')}")
    with c2:
        st.write(f"⭐ **الرتبة:** {member['role']}")
        st.write(f"📚 **التخصص:** {member.get('major', '-')}")
        st.write(f"🏠 **السكن:** {member.get('residence', '-')}")
        
    st.write(f"💯 **النقاط:** {member['points']}")
    st.write(f"📝 **ملاحظات:** {member.get('notes', '-')}")
    
    st.markdown("---")
    
    with st.expander("✏️ تعديل بيانات العضو"):
        with st.form(key=f"edit_form_{member['id']}"):
            e_name = st.text_input("الاسم", value=member['name'])
            
            # تحويل النص المخزن في القاعدة لقائمة عشان الملتيسيلكت يفهمها
            current_teams = [t.strip() for t in member['team'].split(",")] if member['team'] else []
            e_teams = st.multiselect("الفرق (يمكنك اختيار أكثر من فريق)", TEAMS, default=[t for t in current_teams if t in TEAMS])
            
            e_role = st.selectbox("الرتبة", ROLES, index=ROLES.index(member['role']) if member['role'] in ROLES else 0)
            e_gender = st.selectbox("الجنس", GENDERS, index=GENDERS.index(member.get('gender', 'غير محدد')) if member.get('gender', 'غير محدد') in GENDERS else 0)
            
            c1, c2 = st.columns(2)
            with c1:
                e_phone = st.text_input("رقم الهاتف", value=member['phone'])
                e_res = st.text_input("السكن", value=member.get('residence', ''))
            with c2:
                e_pts = st.number_input("النقاط", value=int(member['points']), step=1)
                e_uni = st.text_input("الجامعة", value=member.get('university', ''))
            
            e_notes = st.text_area("ملاحظات", value=member.get('notes', ''))
            
            if st.form_submit_button("حفظ التحديثات ✅", use_container_width=True):
                # دمج الفرق في نص واحد مفصول بفاصلة للتخزين
                teams_str = ", ".join(e_teams)
                db.update_member(member['id'], (e_name, member.get('english_name',''), e_phone, member.get('email',''), teams_str, e_role, e_res, e_uni, member.get('major',''), member.get('academic_year',''), member.get('sports_experience',''), e_pts, e_notes, e_gender))
                st.success("تم الحفظ!")
                st.rerun()

    if st.button("حذف الحساب نهائياً ❌", type="secondary", use_container_width=True):
        db.delete_member(member['id'])
        st.rerun()

# ==========================================
# 4. واجهة الدخول 
# ==========================================
if st.session_state['user'] is None:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ Deja Workspace</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab1:
            l_phone = st.text_input("رقم الهاتف")
            l_pass = st.text_input("كلمة المرور", type="password")
            if st.button("دخول 🚀", use_container_width=True, type="primary"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": f"{l_phone.strip()}@deja.com", "password": l_pass})
                    st.session_state['user'] = res.user
                    st.rerun()
                except Exception as e: st.error("خطأ في البيانات")
        with tab2:
            s_name = st.text_input("الاسم")
            s_phone = st.text_input("رقم الهاتف للتسجيل")
            s_pass = st.text_input("كلمة المرور (6 خانات)", type="password")
            if st.button("إنشاء ✍️", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": f"{s_phone.strip()}@deja.com", "password": s_pass, "options": {"data": {"name": s_name}}})
                    st.success("تم! سجل دخول الآن")
                except: st.error("خطأ")

# ==========================================
# 5. لوحة الإدارة (بعد الدخول)
# ==========================================
else:
    members_data = db.get_all_members()

    with st.sidebar:
        st.markdown(f"### 👨‍💻 أهلاً، **{st.session_state['user'].user_metadata.get('name', 'المدير')}**")
        menu = st.radio("القائمة:", ["👥 بطاقات الأعضاء", "📊 لوحة القيادة", "➕ إضافة عضو جديد"])
        st.markdown("---")
        st.markdown("### 🏷️ تصفية الفريق")
        f_team = st.selectbox("عرض فريق:", ["الكل"] + TEAMS)
        if st.button("خروج 🚪", use_container_width=True):
            supabase.auth.sign_out(); st.session_state['user'] = None; st.rerun()

    if menu == "👥 بطاقات الأعضاء":
        st.title(f"📇 {f_team if f_team != 'الكل' else 'أعضاء فريق Deja'}")
        search = st.text_input("🔍 بحث بالاسم...")
        st.markdown("---")

        if members_data:
            filtered = [m for m in members_data if (f_team == "الكل" or f_team in m['team']) and (not search or search.lower() in m['name'].lower())]
            
            cols = st.columns(3)
            for i, m in enumerate(filtered):
                with cols[i % 3]:
                    # 1. تحديد لون البطاقة حسب الجنس
                    bg = "#0e2038" if m.get('gender') == "ذكر" else ("#361125" if m.get('gender') == "أنثى" else "#1E1E1E")
                    
                    # 2. بناء الأوسمة (Badges) بناءً على الرتبة وكل الفرق المختارة
                    b_html = ""
                    if m['role'] in ['إداري', 'قائد فريق']:
                        b_html += f"<div style='background-color:#FFD700; color:#000; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:bold;'>{m['role']}</div>"
                    
                    m_teams = [t.strip() for t in m['team'].split(",")] if m['team'] else []
                    for t in m_teams:
                        color = "#E53935" if "ميديا" in t else ("#4CAF50" if "IT" in t else ("#00BCD4" if "إدارة" in t else "#9C27B0"))
                        b_html += f"<div style='background-color:{color}; color:#FFF; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:bold;'>{t}</div>"
                    
                    # 3. رسم البطاقة
                    c_html = f"<div style='background-color:{bg}; padding:15px; border-radius:12px; border: 1px solid #444; position:relative; min-height:180px; margin-bottom:10px; direction:rtl; text-align:right;'><div style='position:absolute; top:10px; left:10px; display:flex; flex-direction:column; gap:5px;'>{b_html}</div><h4 style='color:#FFF;'>👤 {m['name']}</h4><p style='font-size:13px; color:#CCC;'>📍 {m.get('residence', '-')}</p><p style='font-size:13px; color:#4CAF50;'>💯 {m['points']} نقطة</p></div>"
                    st.markdown(c_html, unsafe_allow_html=True)
                    if st.button("المزيد ➕", key=f"btn_{m['id']}", use_container_width=True):
                        member_details_dialog(m)

    elif menu == "➕ إضافة عضو جديد":
        st.title("➕ تسجيل عضو")
        with st.form("a_form", clear_on_submit=True):
            n = st.text_input("الاسم *")
            g = st.selectbox("الجنس", GENDERS)
            ts = st.multiselect("الفرق", TEAMS)
            r = st.selectbox("الرتبة", ROLES)
            p = st.text_input("الهاتف")
            res = st.text_input("السكن")
            if st.form_submit_button("إضافة 🚀", use_container_width=True):
                if n:
                    db.add_member((n, "", p, "", ", ".join(ts), r, res, "", "", "", "", 0, "", g))
                    st.success("تمت الإضافة!")
