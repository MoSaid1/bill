import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الصفحة
st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")
st.title("📄 مولد الفواتير - Begonia Pharma")

if "items" not in st.session_state:
    st.session_state["items"] = []

def ar(txt):
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
        batch = st.text_input("التشغيلة")
    with col5:
        expiry = st.text_input("تاريخ الصلاحية (12/2025)")
    with col6:
        discount = st.number_input("الخصم (%)", min_value=0, max_value=100)

    submitted = st.form_submit_button("➕ إضافة")
    if submitted and name:
        st.session_state["items"].append(
            {"name": name, "qty": qty, "batch": batch, "expiry": expiry,
             "price": price, "discount": discount}
        )

# عرض الأصناف
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    st.table(df)

if st.button("📥 توليد الفاتورة PDF"):

    pdf = FPDF("P","mm","A4")
    pdf.add_page()

    pdf.add_font("Graphik","", "GRAPHIK ARABIC BLACK.OTF", uni=True)
    pdf.set_font("Graphik","",12)

    # ========================= HEADER =========================
    pdf.image("logo.png", x=10, y=10, w=50)  # ضع logo.png كملف
    pdf.set_xy(140,10)
    pdf.set_font("Graphik","",16)
    pdf.set_text_color(53,148,82)  # أخضر
    pdf.cell(60,10, ar("فاتورة"), align="R")

    pdf.set_text_color(0,0,0)
    pdf.set_font("Graphik","",10)
    pdf.set_xy(140,20)
    pdf.cell(60,6, ar(f"التاريخ: {datetime.now().strftime('%Y/%m/%d')}"), align="R")
    pdf.set_xy(140,27)
    pdf.cell(60,6, ar(f"اسم الحساب: {customer_name}"), align="R")
    pdf.set_xy(140,34)
    pdf.cell(60,6, ar(f"كود الحساب: {customer_code}"), align="R")
    pdf.set_xy(140,41)
    pdf.cell(60,6, ar(f"رقم الفاتورة: {invoice_number}"), align="R")

    pdf.set_xy(140,50)
    pdf.multi_cell(60,6, ar(f"العنوان: {customer_address}"), align="R")

    # بيانات الشركة
    pdf.set_font("Graphik","",9)
    pdf.set_xy(10,30)
    pdf.cell(80,6, ar("سجل تجاري رقم: 158377"), ln=1)
    pdf.set_xy(10,36)
    pdf.cell(80,6, ar("رقم التسجيل الضريبي: 174-658-610"))

    # ========================= TABLE HEADER =========================
    pdf.set_xy(10,70)
    pdf.set_font("Graphik","",11)
    pdf.set_fill_color(255,255,255)
    headers = ["اسم الصنف","الكمية","التشغيلة","تاريخ الصلاحية","سعر الجمهور","الخصم","اجمالي القيمة"]
    col_w = [45,20,25,30,25,20,30]
    for i,h in enumerate(headers):
        pdf.cell(col_w[i],10,ar(h),1,0,"C",True)
    pdf.ln()

    # ========================= TABLE DATA =========================
    total, total_qty = 0,0
    for item in st.session_state["items"]:
        value = item["qty"]*item["price"]*(1-item["discount"]/100)
        total += value
        total_qty += item["qty"]

        row = [item["name"], str(item["qty"]), item["batch"], item["expiry"],
               str(item["price"]), f"{item['discount']}%", str(round(value,2))]
        for i,c in enumerate(row):
            pdf.cell(col_w[i],10, ar(str(c)),1,0,"C")
        pdf.ln()

    # ========================= SUMMARY =========================
    pdf.ln(5)
    pdf.set_font("Graphik","",12)
    pdf.cell(50,10, ar(f"عدد الأصناف: {len(st.session_state['items'])}"), 1)
    pdf.cell(50,10, ar(f"عدد العلب: {total_qty}"), 1)
    pdf.ln()
    pdf.cell(100,10, ar(f"إجمالي القيمة: {round(total,2)}"), 1, ln=1,"C")

    # ========================= FOOTER =========================
    pdf.set_y(-25)
    pdf.set_font("Graphik","",9)
    pdf.set_text_color(255,255,255)
    pdf.set_fill_color(53,148,82)
    pdf.cell(0,10, ar("📞 01040008105 - 01289982650     🌐 begoniapharma.com     📍 34 Gamal Eldin Dewidar st. Nasr City, Cairo, Egypt"), 0,0,"C",True)

    # ========================= SAVE =========================
    filename = "invoice.pdf"
    pdf.output(filename)

    with open(filename,"rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename)
