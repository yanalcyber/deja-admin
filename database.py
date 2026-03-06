# --- أداة استيراد البيانات من ملف SQLite ---
    st.subheader("📥 استيراد بيانات الأعضاء من ملف SQLite القديم")
    uploaded_sqlite = st.file_uploader("ارفع ملف قاعدة البيانات (.db أو .sqlite) هنا", type=['db', 'sqlite', 'sqlite3'])
    
    if uploaded_sqlite is not None:
        if st.button("سحب البيانات لقاعدة Supabase 🚀", type="primary", use_container_width=True):
            import sqlite3
            import tempfile
            import os

            # 1. حفظ الملف مؤقتاً في السيرفر عشان نقدر نقرأه
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                tmp.write(uploaded_sqlite.getvalue())
                tmp_path = tmp.name

            try:
                # 2. الاتصال بملف SQLite
                conn = sqlite3.connect(tmp_path)
                cursor = conn.cursor()

                # 3. البحث عن اسم الجدول جوا الملف (عشان لو كان اسمه مختلف)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = cursor.fetchall()

                if not tables:
                    st.error("⚠️ الملف المرفوع فارغ أو لا يحتوي على جداول.")
                else:
                    table_name = tables[0][0] # نأخذ أول جدول نلاقيه
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    # جلب أسماء الأعمدة عشان نربطها صح
                    column_names = [description[0] for description in cursor.description]
                    
                    added_count = 0
                    for row in rows:
                        row_dict = dict(zip(column_names, row))
                        
                        # سحب البيانات (الكود بيبحث عن الاسم الإنجليزي أو العربي عشان ما يعطي خطأ)
                        name = str(row_dict.get("name", row_dict.get("الاسم", ""))).strip()
                        
                        if name and name != "None": # يتأكد إنه في اسم فعلاً
                            phone = str(row_dict.get("phone", row_dict.get("رقم الهاتف", "")))
                            email = str(row_dict.get("email", row_dict.get("البريد الإلكتروني", "")))
                            team = str(row_dict.get("team", row_dict.get("الفريق", "غير محدد")))
                            role = str(row_dict.get("role", row_dict.get("الرتبة", "عضو")))
                            notes = str(row_dict.get("notes", row_dict.get("ملاحظات", "")))
                            
                            # تنظيف القيم الفارغة
                            if phone == "None": phone = ""
                            if email == "None": email = ""
                            if team == "None" or not team: team = "غير محدد"
                            if role == "None" or not role: role = "عضو"
                            if notes == "None": notes = ""
                            
                            points_raw = row_dict.get("points", row_dict.get("النقاط", 0))
                            points = int(points_raw) if str(points_raw).isdigit() else 0

                            # 4. إرسال البيانات لقاعدة بيانات Supabase
                            db.add_member((name, phone, email, team, role, points, notes))
                            added_count += 1
                    
                    st.success(f"✅ تم سحب وإضافة {added_count} عضو بنجاح! اعمل تحديث (Refresh) للصفحة.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
            finally:
                conn.close()
                os.remove(tmp_path) # مسح الملف المؤقت لتنظيف السيرفر
    st.markdown("---")
