import streamlit as st
import sqlite3
import pandas as pd
import os

# ==========================================
# 1. إعدادات الصفحة (يجب أن تكون أول سطر بعد الـ imports)
# ==========================================
st.set_page_config(page_title="Deja Admin Panel", page_icon="👥", layout="wide")


# ==========================================
# 2. إدارة قاعدة البيانات (Model Layer)
# ==========================================
class DatabaseManager:
    def __init__(self, db_name="deja_admin.db"):
        # check_same_thread=False مهمة جداً لـ Streamlit
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.setup_db()

    def setup_db(self):
        """إنشاء الجداول اللازمة مع حقل النقاط"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                team TEXT,
                role TEXT,
                notes TEXT,
                points INTEGER DEFAULT 0
            )
        ''')
        # كود ذكي لتحديث الجدول القديم إن وجد
        try:
            self.cursor.execute("ALTER TABLE members ADD COLUMN points INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # العمود موجود مسبقاً
        self.conn.commit()

    def add_member(self, data):
        query = "INSERT INTO members (name, phone, email, team, role, points, notes) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, data)
        self.conn.commit()

    def delete_member(self, member_id):
        self.cursor.execute("DELETE FROM members WHERE id=?", (member_id,))
        self.conn.commit()

    def get_all_members(self):
        self.cursor.execute("SELECT * FROM members ORDER BY id DESC")
        return [dict(row) for row in self.cursor.fetchall()]


# تهيئة قاعدة البيانات
db = DatabaseManager()

# ==========================================
# 3. إعدادات القوائم الثابتة
# ==========================================
TEAMS = ["غير محدد", "فريق ميديا", "فريق IT"]
ROLES = ["عضو", "إداري"]

# ==========================================
# 4. واجهة الموقع (Streamlit UI)
# ==========================================
st.title("👥 لوحة تحكم فريق Deja")
st.markdown("---")

# --- القائمة الجانبية (Sidebar) لإضافة حساب ---
with st.sidebar:
    st.header("➕ إضافة حساب جديد")

    with st.form("add_member_form", clear_on_submit=True):
        name = st.text_input("الاسم الثلاثي باللغة العربية *")
        phone = st.text_input("رقم الهاتف")
        email = st.text_input("البريد الإلكتروني")
        team = st.selectbox("الفريق", TEAMS)
        role = st.selectbox("الرتبة", ROLES)
        points = st.number_input("النقاط", min_value=0, value=0, step=1)
        notes = st.text_area("ملاحظات")

        submit_btn = st.form_submit_button("إضافة الحساب ✅", use_container_width=True)

        if submit_btn:
            if not name.strip():
                st.error("⚠️ الاسم مطلوب!")
            else:
                db.add_member((name, phone, email, team, role, points, notes))
                st.success(f"تمت إضافة {name} بنجاح!")
                st.rerun()  # تحديث الصفحة لإظهار البيانات الجديدة

# --- اللوحة الرئيسية (الجدول والبحث) ---
members_data = db.get_all_members()

# عرض إحصائيات سريعة
st.write(f"**إجمالي الأعضاء المسجلين:** {len(members_data)}")

if members_data:
    # تحويل البيانات إلى DataFrame لتسهيل العرض والفلترة
    df = pd.DataFrame(members_data)

    # إعادة تسمية الأعمدة لتظهر بالعربي في الجدول
    df_display = df.rename(columns={
        'id': 'الرقم',
        'name': 'الاسم',
        'phone': 'رقم الهاتف',
        'email': 'البريد الإلكتروني',
        'team': 'الفريق',
        'role': 'الرتبة',
        'points': 'النقاط',
        'notes': 'ملاحظات'
    })

    # شريط البحث
    search_query = st.text_input("🔍 ابحث بالاسم، رقم الهاتف، أو الإيميل...")

    # فلترة الجدول بناءً على البحث
    if search_query:
        # نبحث في جميع الأعمدة
        mask = df_display.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        df_display = df_display[mask]

    # عرض الجدول (المستخدم يستطيع ترتيب الأعمدة بالضغط عليها)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- قسم حذف عضو ---
    st.subheader("🗑️ إدارة الحسابات (حذف)")
    col1, col2 = st.columns([3, 1])

    with col1:
        # إنشاء قائمة منسدلة بأسماء الأعضاء لسهولة الحذف
        member_options = [f"{row['name']} (رقم: {row['id']})" for _, row in df.iterrows()]
        selected_to_delete = st.selectbox("اختر العضو المراد حذفه:", [""] + member_options)

    with col2:
        st.write("")  # مسافة لترتيب الزر
        st.write("")
        if st.button("حذف الحساب المختار ❌", type="primary", use_container_width=True):
            if selected_to_delete:
                # استخراج الـ ID من النص المختار
                member_id = int(selected_to_delete.split("(رقم: ")[1].replace(")", ""))
                db.delete_member(member_id)
                st.success("تم حذف الحساب بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى اختيار عضو أولاً.")
else:
    st.info("لا يوجد أعضاء مضافين حتى الآن. ابدأ بإضافة حسابات من القائمة الجانبية.")