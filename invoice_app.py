import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الصفحة
st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")

st.title("📄 مولد الفواتير - Begonia Pharma")

# تهيئة session_state للأصناف
if "items" not in st.session_state:
    st.session_state["items"] = []

# دالة لمعالجة النص العربي
def ar_text(txt):
    return get_display(arabic_reshaper.reshape(txt))

# بيانات العميل
st.header("بيانات العميل")
customer_name = st.text_input("اسم الحساب")
customer_code = st.text_input("كود الحساب")
invoice_number = st.text_input("رقم الفاتورة")
customer_address = st.text_area("العنوان")

# إضافة الأصناف
st.header("إضافة الأصناف")
with st.form("add_item"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("اسم الصنف")
    with col2:
        qty = st.number_input("الكمية", min_value=1, step=1)
    with col3:
        price = st.number_input("سعر الجمهور", min_value=0.0, step=0.5)

    col4, col5, col6 = st.columns(3)
    with col4:
        expiry = st.text_input("تاريخ الصلاحية (مثال: 12/2025)")
    with col5:
        batch = st.text_input("التشغيلة")  # إضافة التشغيلة
    with col6:
        discount = st.number_input("الخصم (%)", min_value=0, max_value=100)

    submitted = st.form_submit_button("➕ إضافة صنف")
    if submitted and name:
        st.session_state["items"].append(
            {"name": name, "qty": qty, "price": price, "expiry": expiry, "batch": batch, "discount": discount}
        )

# عرض الأصناف
st.subheader("الأصناف المضافة")
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    st.table(df)
else:
    st.info("لم يتم إضافة أي أصناف بعد.")

# توليد الفاتورة
if st.button("📥 توليد الفاتورة PDF"):
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()

    # إضافة الخلفية (تصميم الفاتورة كصورة)
    pdf.image("invoice_template.png", x=0, y=0, w=210, h=297)

    # تحميل الخط العربي
    pdf.add_font("Graphik", "", "GRAPHIK ARABIC BLACK.OTF", uni=True)
    pdf.set_font("Graphik", "", 12)

    # بيانات العميل
    pdf.set_xy(150, 35)
    pdf.cell(0, 10, ar_text(f"{datetime.now().strftime('%Y/%m/%d')}"))

    pdf.set_xy(150, 45)
    pdf.cell(0, 10, ar_text(customer_name))

    pdf.set_xy(150, 55)
    pdf.cell(0, 10, ar_text(customer_code))

    pdf.set_xy(150, 65)
    pdf.cell(0, 10, ar_text(invoice_number))

    pdf.set_xy(150, 75)
    pdf.multi_cell(40, 10, ar_text(customer_address))

    # جدول الأصناف
    start_y = 100
    row_height = 10
    total = 0
    total_qty = 0

    for item in st.session_state["items"]:
        pdf.set_xy(15, start_y)
        pdf.cell(35, row_height, ar_text(item["name"]), border=1)

        pdf.cell(20, row_height, str(item["qty"]), border=1, align="C")
        pdf.cell(25, row_height, ar_text(item["batch"]), border=1, align="C")
        pdf.cell(30, row_height, ar_text(item["expiry"]), border=1, align="C")
        pdf.cell(25, row_height, str(item["price"]), border=1, align="C")
        pdf.cell(20, row_height, str(item["discount"]) + "%", border=1, align="C")

        value = item["qty"] * item["price"] * (1 - item["discount"] / 100)
        pdf.cell(30, row_height, str(round(value, 2)), border=1, align="C")

        start_y += row_height
        total += value
        total_qty += item["qty"]

    # قسم الإجمالي
    pdf.set_xy(150, 210)
    pdf.cell(40, 10, str(len(st.session_state["items"])), border=1, align="C")  # عدد الأصناف
    pdf.set_xy(110, 210)
    pdf.cell(40, 10, str(total_qty), border=1, align="C")  # عدد العلب
    pdf.set_xy(150, 230)
    pdf.cell(40, 10, str(round(total, 2)), border=1, align="C")  # إجمالي القيمة

    filename = "invoice.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename)
