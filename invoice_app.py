import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")

st.title("📄 مولد الفواتير - Begonia Pharma")

# تهيئة session_state للأصناف
if "items" not in st.session_state:
    st.session_state["items"] = []

# ==========================
# بيانات العميل
# ==========================
st.header("بيانات العميل")
customer_name = st.text_input("اسم الحساب")
customer_code = st.text_input("كود الحساب")
customer_address = st.text_area("العنوان")

# ==========================
# إضافة الأصناف
# ==========================
st.header("إضافة الأصناف")

with st.form("add_item"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("اسم الصنف")
    with col2:
        qty = st.number_input("الكمية", min_value=1, step=1)
    with col3:
        price = st.number_input("سعر الجمهور", min_value=0.0, step=0.5)

    col4, col5 = st.columns(2)
    with col4:
        expiry = st.text_input("تاريخ الصلاحية (مثال: 12/2025)")
    with col5:
        discount = st.number_input("الخصم (%)", min_value=0, max_value=100)

    submitted = st.form_submit_button("➕ إضافة صنف")
    if submitted and name:
        st.session_state["items"].append(
            {"name": name, "qty": qty, "price": price, "expiry": expiry, "discount": discount}
        )

# ==========================
# عرض الأصناف
# ==========================
st.subheader("الأصناف المضافة")
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    st.table(df)
else:
    st.info("لم يتم إضافة أي أصناف بعد.")

# ==========================
# توليد الفاتورة
# ==========================
if st.button("📥 توليد الفاتورة PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "فاتورة", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"اسم الحساب: {customer_name}", ln=True)
    pdf.cell(0, 10, f"كود الحساب: {customer_code}", ln=True)
    pdf.cell(0, 10, f"العنوان: {customer_address}", ln=True)
    pdf.cell(0, 10, f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)

    # جدول الفاتورة
    col_widths = [40, 25, 30, 30, 25, 40]
    headers = ["اسم الصنف", "الكمية", "تاريخ الصلاحية", "سعر الجمهور", "الخصم", "اجمالي القيمة"]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, "C")
    pdf.ln()

    total = 0
    for item in st.session_state["items"]:
        pdf.cell(col_widths[0], 10, item["name"], 1)
        pdf.cell(col_widths[1], 10, str(item["qty"]), 1)
        pdf.cell(col_widths[2], 10, item["expiry"], 1)
        pdf.cell(col_widths[3], 10, str(item["price"]), 1)
        pdf.cell(col_widths[4], 10, str(item["discount"])+"%", 1)
        value = item["qty"] * item["price"] * (1 - item["discount"]/100)
        pdf.cell(col_widths[5], 10, str(round(value, 2)), 1, ln=True)
        total += value

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"إجمالي القيمة: {round(total, 2)}", ln=True, align="R")

    filename = "invoice.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename)
