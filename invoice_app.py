import streamlit as st
import pandas as pd
from design import InvoicePDF  # نستورد التصميم
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")
st.title("📄 مولد الفواتير - Begonia Pharma")

# session_state للأصناف
if "items" not in st.session_state:
    st.session_state["items"] = []

# بيانات العميل
st.header("بيانات العميل")
customer_name = st.text_input("اسم الحساب")
customer_code = st.text_input("كود الحساب")
customer_address = st.text_area("العنوان")

# إضافة الأصناف
st.header("إضافة الأصناف")
with st.form("add_item"):
    col1, col2, col3 = st.columns(3)
    with col1: name = st.text_input("اسم الصنف")
    with col2: qty = st.number_input("الكمية", min_value=1, step=1)
    with col3: price = st.number_input("سعر الجمهور", min_value=0.0, step=0.5)

    col4, col5 = st.columns(2)
    with col4: expiry = st.text_input("تاريخ الصلاحية (مثال: 12/2025)")
    with col5: discount = st.number_input("الخصم (%)", min_value=0, max_value=100)

    submitted = st.form_submit_button("➕ إضافة صنف")
    if submitted and name:
        st.session_state["items"].append(
            {"name": name, "qty": qty, "price": price, "expiry": expiry, "discount": discount}
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
    pdf = InvoicePDF()
    pdf.add_page()

    # الخطوط العربية
    pdf.add_font("Graphik", "", "GRAPHIK ARABIC BLACK.OTF", uni=True)
    pdf.add_font("Graphik", "B", "GRAPHIK ARABIC BLACK.OTF", uni=True)

    pdf.customer_info(customer_name, customer_code, customer_address)
    total = pdf.items_table(st.session_state["items"])
    pdf.total_amount(total)

    filename = "invoice.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename)
