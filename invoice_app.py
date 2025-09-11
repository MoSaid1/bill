import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# -------- إعداد الصفحة --------
st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")
st.title("📄 مولد الفواتير - Begonia Pharma")

if "items" not in st.session_state:
    st.session_state["items"] = []

# دالة لمعالجة النص العربي
def ar(txt):
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))

# -------- إدخال بيانات العميل --------
st.header("بيانات العميل")
customer_name = st.text_input("اسم الحساب")
customer_code = st.text_input("كود الحساب")
invoice_number = st.text_input("رقم الفاتورة")
customer_address = st.text_area("العنوان")

# -------- إضافة الأصناف --------
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
        expiry = st.text_input("تاريخ الصلاحية (مثال: 12/2025)")
    with col6:
        discount = st.number_input("الخصم (%)", min_value=0, max_value=100)

    submitted = st.form_submit_button("➕ إضافة")
    if submitted and name:
        st.session_state["items"].append(
            {"name": name, "qty": qty, "batch": batch, "expiry": expiry,
             "price": price, "discount": discount}
        )

if st.session_state["items"]:
    st.table(pd.DataFrame(st.session_state["items"]))

# -------- إنشاء الفاتورة --------
if st.button("📥 توليد الفاتورة PDF"):

    pdf = FPDF("P","mm","A4")
    pdf.add_page()

    # تحميل خط
    pdf.add_font("Graphik","", "GRAPHIK ARABIC BLACK.OTF", uni=True)
    pdf.set_font("Graphik","",12)

    # ---- Header ----
    pdf.image("logo.png", x=10, y=10, w=50)
    pdf.set_xy(170,15)
    pdf.set_font("Graphik","",16)
    pdf.set_text_color(53,148,82)
    pdf.cell(30,10, ar("فاتورة"), align="R")
    pdf.set_text_color(0,0,0)
    pdf.set_font("Graphik","",10)

    # بيانات العميل
    pdf.set_xy(140,30); pdf.cell(60,8, ar("التاريخ:"), border=1, align="R")
    pdf.set_xy(140,30); pdf.cell(-5,8, datetime.now().strftime('%Y/%m/%d'), align="L")

    pdf.set_xy(140,38); pdf.cell(60,8, ar("اسم الحساب:"), border=1, align="R")
    pdf.set_xy(140,38); pdf.cell(-5,8, customer_name, align="L")

    pdf.set_xy(140,46); pdf.cell(60,8, ar("كود الحساب:"), border=1, align="R")
    pdf.set_xy(140,46); pdf.cell(-5,8, customer_code, align="L")

    pdf.set_xy(140,54); pdf.cell(60,8, ar("رقم الفاتورة:"), border=1, align="R")
    pdf.set_xy(140,54); pdf.cell(-5,8, invoice_number, align="L")

    pdf.set_xy(140,62); pdf.multi_cell(60,8, ar("العنوان:") + " " + customer_address, border=1, align="R")

    # بيانات الشركة
    pdf.set_font("Graphik","",9)
    pdf.set_xy(15,55); pdf.cell(80,6, ar("سجل تجاري رقم: 158377"))
    pdf.set_xy(15,61); pdf.cell(80,6, ar("رقم التسجيل الضريبي: 174-658-610"))

    # ---- Table Header ----
    y_table = 90
    pdf.set_xy(10,y_table)
    pdf.set_font("Graphik","",11)
    headers = ["اسم الصنف","الكمية","التشغيلة","تاريخ الصلاحية","سعر الجمهور","الخصم","اجمالي القيمة"]
    col_w = [45,20,25,30,25,20,30]
    for h, w in zip(headers, col_w):
        pdf.cell(w,10, ar(h),1,0,"C")
    pdf.ln()

    # ---- Table Data ----
    total, total_qty = 0,0
    pdf.set_font("Graphik","",10)
    for item in st.session_state["items"]:
        value = item["qty"]*item["price"]*(1-item["discount"]/100)
        total += value
        total_qty += item["qty"]

        row = [
            item["name"], 
            str(item["qty"]), 
            item["batch"], 
            item["expiry"],
            str(item["price"]), 
            f"{item['discount']}%", 
            str(round(value,2))
        ]
        pdf.set_x(10)
        for txt, w in zip(row, col_w):
            if any("\u0600" <= ch <= "\u06FF" for ch in txt):
                pdf.cell(w,10, ar(txt),1,0,"C")
            else:
                pdf.cell(w,10, txt,1,0,"C")
        pdf.ln()

    # ---- Summary ----
    pdf.ln(8)
    pdf.set_font("Graphik","",12)

    # عدد الأصناف
    pdf.cell(40,10, ar("عدد الأصناف:"), border=1, align="R")
    pdf.cell(25,10, str(len(st.session_state['items'])), border=1, align="C")

    # عدد العلب
    pdf.cell(40,10, ar("عدد العلب:"), border=1, align="R")
    pdf.cell(25,10, str(total_qty), border=1, align="C")

    # اجمالي القيمة
    pdf.cell(40,10, ar("إجمالي القيمة:"), border=1, align="R")
    pdf.cell(25,10, str(round(total,2)), border=1, align="C", ln=1)

    # ---- Footer ----
    pdf.set_y(-20)
    pdf.set_font("Graphik","",9)
    pdf.set_text_color(255,255,255)
    pdf.set_fill_color(47,105,151)
    pdf.cell(
        0,8,
        ar("📞 01040008105 - 01289982650     🌐 begoniapharma.com     📍 34 Gamal Eldin Dewidar st. With Zaker Heussin st. Nasr City, Cairo, Egypt"),
        0,0,"C",True
    )

    # Output
    filename = "invoice.pdf"
    pdf.output(filename)

    with open(filename,"rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename)
