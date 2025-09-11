import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import os
import re

# --- دالة لإصلاح النص العربي (توصيل + اتجاه) ---
def fix_arabic(txt: str) -> str:
    if not txt:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(txt))
        return get_display(reshaped)
    except Exception as e:
        print(f"Error in Arabic reshaping: {e}")
        return str(txt)

# Streamlit إعداد
st.set_page_config("مولد فواتير | Begonia Pharma", ":page_facing_up:")
st.title("📄 مولد الفاتورة - Begonia Pharma")

if "items" not in st.session_state:
    st.session_state["items"] = []

# ===== إدخال بيانات العميل =====
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

# ===== إدخال الأصناف =====
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
        discount = st.number_input("الخصم (%)", min_value=0, max_value=100)

    if st.form_submit_button("➕ إضافة"):
        st.session_state["items"].append({
            "name": name,
            "qty": qty,
            "batch": batch,
            "expiry": expiry,
            "price": price,
            "discount": discount
        })

# ===== عرض الأصناف =====
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    df["إجمالي القيمة"] = (
        df["qty"] * df["price"] * (1 - df["discount"] / 100)
    ).round(2)
    st.table(df)
else:
    st.info("لم يتم إدخال أي أصناف حتى الآن.")

# ===== توليد الفاتورة PDF =====
if st.button("📥 توليد الفاتورة PDF"):

    # التحقق من وجود الملفات
    if not os.path.exists("bill.jpg"):
        st.error("❗ يجب وجود ملف الخلفية bill.jpg")
        st.stop()

    if not os.path.exists("Amiri-Regular.ttf"):
        st.error("❗ يجب وجود ملف الخط Amiri-Regular.ttf")
        st.stop()

    pdf = FPDF()
    pdf.add_page()

    # الخلفية
    pdf.image("bill.jpg", x=0, y=0, w=210, h=297)

    # تحميل الخط العربي
    try:
        pdf.add_font("Amiri", "", "Amiri-Regular.ttf", uni=True)
        pdf.set_font("Amiri", "", 12)
    except Exception as e:
        st.error(f"فشل تحميل خط Amiri: {e}")
        st.stop()

    # --- بيانات العميل ---
    pdf.set_xy(105, 25)
    pdf.cell(60, 8, fix_arabic(customer_name), 0, 0, "R")
    pdf.set_xy(105, 35)
    pdf.cell(60, 8, fix_arabic(customer_code), 0, 0, "R")
    pdf.set_xy(105, 44)
    pdf.cell(60, 8, fix_arabic(invoice_number), 0, 0, "R")
    pdf.set_xy(20, 53)
    pdf.multi_cell(160, 6, fix_arabic(customer_address), 0, "R")
    pdf.set_xy(120, 14)
    pdf.cell(30, 8, datetime.now().strftime("%Y/%m/%d"), 0, 0, "C")

    # --- جدول الأصناف ---
    headers = [
        "إجمالي القيمة",
        "الخصم",
        "سعر الجمهور",
        "تاريخ الصلاحية",
        "التشغيلة",
        "الكمية",
        "اسم الصنف"
    ]
    col_w = [28, 18, 24, 24, 22, 16, 48]
    table_width = sum(col_w)
    x_center = (210 - table_width) / 2
    table_y = 80

    total = 0.0
    total_qty = 0

    pdf.set_xy(x_center, table_y)
    pdf.set_font("Amiri", "", 10)
    pdf.set_x(x_center)
    pdf.set_fill_color(230, 230, 230)

    for h, w in zip(headers, col_w):
        pdf.cell(w, 8, fix_arabic(h), 1, 0, 'C', fill=True)
    pdf.ln()

    pdf.set_fill_color(255, 255, 255)

    for item in st.session_state["items"]:
        val = item["qty"] * item["price"] * (1 - item["discount"] / 100)
        total += val
        total_qty += item["qty"]

        row = [
            fix_arabic(f"{val:.2f}"),
            fix_arabic(f"{item['discount']}%"),
            fix_arabic(f"{item['price']:.2f}"),
            fix_arabic(item["expiry"]),
            fix_arabic(item["batch"]),
            fix_arabic(str(item["qty"])),
            fix_arabic(item["name"])
        ]

        pdf.set_x(x_center)
        for text, w in zip(row, col_w):
            pdf.cell(w, 9, text, 1, 0, 'C')
        pdf.ln()

    # --- ملخص الفاتورة ---
    pdf.set_font("Amiri", "", 11)
    pdf.set_xy(125, 220)
    pdf.cell(40, 8, fix_arabic(str(len(st.session_state["items"]))), 1, 0, 'C')
    pdf.cell(40, 8, fix_arabic("عدد الأصناف"), 1, 1, 'C')
    pdf.set_x(125)
    pdf.cell(40, 8, fix_arabic(str(total_qty)), 1, 0, 'C')
    pdf.cell(40, 8, fix_arabic("عدد العلب"), 1, 1, 'C')
    pdf.set_x(125)
    pdf.cell(40, 8, fix_arabic(f"{paid_amount:.2f}"), 1, 0, 'C')
    pdf.cell(40, 8, fix_arabic("تحصيل الدفع"), 1, 1, 'C')
    pdf.set_x(125)
    pdf.cell(40, 8, fix_arabic(f"{total:.2f}"), 1, 0, 'C')
    pdf.cell(40, 8, fix_arabic("إجمالي القيمة"), 1, 1, 'C')

    # --- اسم الملف ---
    today_str = datetime.now().strftime("%Y-%m-%d")
    safe_invoice = re.sub(r'\W+', '_', invoice_number or "بدون_رقم")
    filename = f"فاتورة_{safe_invoice}_{today_str}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.success("✅ تم توليد الفاتورة!")
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename, mime="application/pdf")
