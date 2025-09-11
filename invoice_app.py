import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import os
import re

# ====== دعم الكتابة بالعربية ======
def ar(txt):
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))

# ====== إعداد صفحة Streamlit ======
st.set_page_config("مولد فواتير | Begonia Pharma", "📄")
st.title("📄 مولد الفاتورة - Begonia Pharma")

if "items" not in st.session_state:
    st.session_state["items"] = []

# ---------- بيانات العميل ----------
st.header("بيانات العميل")
col1, col2, col3 = st.columns(3)
with col1:
    customer_name = st.text_input("اسم الحساب")
with col2:
    customer_code = st.text_input("كود الحساب")
with col3:
    invoice_number = st.text_input("رقم الفاتورة")
customer_address = st.text_area("العنوان")
paid_amount = st.number_input("تحصيل الدفع", min_value=0.0, step=10.0)

# ---------- إضافة الأصناف ----------
st.header("إضافة الأصناف")
with st.form("add-item"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("اسم الصنف")
    with c2:
        qty = st.number_input("الكمية", min_value=1, step=1)
    with c3:
        price = st.number_input("سعر الجمهور", min_value=0.0, step=0.5)

    c4, c5, c6 = st.columns(3)
    with c4:
        batch = st.text_input("التشغيلة")
    with c5:
        expiry = st.text_input("تاريخ الصلاحية")
    with c6:
        discount = st.number_input("الخصم", min_value=0, max_value=100)

    if st.form_submit_button("➕ إضافة"):
        st.session_state["items"].append({
            "name": name,
            "qty": qty,
            "batch": batch,
            "expiry": expiry,
            "price": price,
            "discount": discount
        })

# ---------- عرض البيانات الحالية ----------
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    df["إجمالي القيمة"] = (df["qty"] * df["price"] * (1 - df["discount"]/100)).round(2)
    st.table(df)
else:
    st.info("لم يتم إدخال أي أصناف حتى الآن.")

# ============ توليد الفاتورة PDF ============
if st.button("📥 توليد الفاتورة PDF"):

    # التحقق من وجود صورة الخلفية
    if not os.path.exists("bill.jpg"):
        st.error("❗ ملف الخلفية 'bill.jpg' غير موجود في المجلد.")
        st.stop()

    # التحقق من وجود الخط
    if not os.path.exists("Cairo-VariableFont_slnt,wght.ttf"):
        st.error("❗ ملف الخط 'Cairo-VariableFont_slnt,wght.ttf' غير موجود.")
        st.stop()

    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.image("bill.jpg", x=0, y=0, w=210, h=297)

    # استخدام خط Cairo
    pdf.add_font("Cairo", "", "Cairo-VariableFont_slnt,wght.ttf", uni=True)
    pdf.set_font("Cairo", "", 12)
    pdf.set_text_color(0, 0, 0)

    # --------- بيانات العميل ----------
    pdf.set_xy(105, 25)
    pdf.cell(60, 8, ar(customer_name), 0, 0, "R")
    pdf.set_xy(105, 35)
    pdf.cell(60, 8, ar(customer_code), 0, 0, "R")
    pdf.set_xy(105, 44)
    pdf.cell(60, 8, ar(invoice_number), 0, 0, "R")
    pdf.set_xy(20, 53)
    pdf.multi_cell(160, 6, ar(customer_address), 0, "R")
    pdf.set_xy(120, 14)
    pdf.cell(30, 8, datetime.now().strftime("%Y/%m/%d"), 0, 0, "C")

    # --------- جدول الأصناف ----------
    table_y = 80
headers = ["إجمالي القيمة", "الخصم", "سعر الجمهور", "تاريخ الصلاحية", "التشغيلة", "الكمية", "اسم الصنف"]
col_w =   [28,             18,       24,           24,               22,        16,         48]

pdf.set_font("Cairo", "", 10)
pdf.set_x(x_center)
for h, w in zip(headers, col_w):
    pdf.cell(w, 8, ar(h), 1, 0, 'C')
pdf.ln()

    def has_ar(text):
        for ch in str(text):
            if '\u0600' <= ch <= '\u06FF':
                return True
        return False

    for item in st.session_state["items"]:
        val = item["qty"] * item["price"] * (1 - item["discount"]/100)
        total += val
        total_qty += item["qty"]

        row = [
            f"{val:.2f}",
            f"{item['discount']}%",
            f"{item['price']:.2f}",
            item["expiry"],
            item["batch"],
            str(item["qty"]),
            item["name"]
        ]

        pdf.set_x(x_center)
        for val_txt, w in zip(row, col_w):
            txt = ar(val_txt) if has_ar(val_txt) else str(val_txt)
            pdf.cell(w, 9, txt, 1, 0, 'C')
        pdf.ln()

    # ---------- ملخص الفاتورة ----------
    pdf.set_font("Cairo", "", 11)
    pdf.set_xy(125, 220)
    pdf.cell(40, 8, str(len(st.session_state["items"])), 1, 0, 'C')
    pdf.cell(40, 8, ar("عدد الأصناف"), 1, 1, 'C')
    pdf.set_x(125)
    pdf.cell(40, 8, str(total_qty), 1, 0, 'C')
    pdf.cell(40, 8, ar("عدد العلب"), 1, 1, 'C')
    pdf.set_x(125)
    pdf.cell(40, 8, f"{paid_amount:.2f}", 1, 0, 'C')
    pdf.cell(40, 8, ar("تحصيل الدفع"), 1, 1, 'C')
    pdf.set_x(125)
    pdf.cell(40, 8, f"{total:.2f}", 1, 0, 'C')
    pdf.cell(40, 8, ar("إجمالي القيمة"), 1, 1, 'C')

    # ===== اسم الملف: رقم الفاتورة + التاريخ =====
    today_str = datetime.now().strftime("%Y-%m-%d")
    safe_invoice = re.sub(r'\W+', '_', invoice_number or "بدون_رقم")
    filename = f"فاتورة_{safe_invoice}_{today_str}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.success("✅ تم توليد الفاتورة!")
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename, mime="application/pdf")
