import streamlit as st
import pandas as pd
from fpdf import FPDF
from PyPDF2 import PdfReader
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import os

def ar(txt):
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))

st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")
st.title("📄 مولد الفواتير - Begonia Pharma")

if "items" not in st.session_state:
    st.session_state["items"] = []

# ============== بيانات العميل ==============
st.header("بيانات العميل")
colA, colB, colC = st.columns(3)
with colA:
    customer_name = st.text_input("اسم الحساب")
with colB:
    customer_code = st.text_input("كود الحساب")
with colC:
    invoice_number = st.text_input("رقم الفاتورة")

customer_address = st.text_area("العنوان")
paid_amount = st.number_input("تحصيل الدفع", min_value=0.0, step=10.0)

# ============== إضافة الأصناف ==============
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
    df = pd.DataFrame(st.session_state["items"])
    df["إجمالي القيمة"] = (df["qty"] * df["price"] * (1 - df["discount"]/100)).round(2)
    st.table(df)
else:
    st.info("لم يتم إضافة أي أصناف بعد.")

# ============== توليد PDF ==============
if st.button("📥 توليد الفاتورة PDF"):

    # التأكد من وجود الملف
    if not os.path.exists("bill.pdf"):
        st.error("⚠️ ملف تصميم الفاتورة bill.pdf غير موجود.")
        st.stop()

    # ====== إعداد PDF ======
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # قراءة خلفية pdf وتحويل الصفحة الأولى كصورة
    from fpdf import template
    from fpdf.template import Template

    template_path = "bill.pdf"

    # تحميل الخط
    pdf.add_font("Amiri", "", "Amiri-Regular.ttf", uni=True)
    pdf.set_font("Amiri", "", 12)

    # إضافة الصفحة الأولى بالخلفية
    pdf.add_page()
    pdf.set_font("Amiri", "", 12)

    # ✅ إدراج الخلفية باستخدام pdf.image من صورة، نحتاج تحويل الصفحة الأولى من bill.pdf إلى صورة مؤقتة
    from pdf2image import convert_from_path

    pages = convert_from_path("bill.pdf", dpi=200)
    bg_path = "bg_temp.jpg"
    pages[0].save(bg_path, "JPEG")

    pdf.image(bg_path, x=0, y=0, w=210, h=297)

    # ✅ الكتابة فوق الفاتورة
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Amiri", "", 12)

    pdf.set_xy(133, 27)
    pdf.cell(60, 8, ar(customer_name), 0, 0, "R")
    pdf.set_xy(133, 35)
    pdf.cell(60, 8, ar(customer_code), 0, 0, "R")
    pdf.set_xy(133, 43)
    pdf.cell(60, 8, ar(invoice_number), 0, 0, "R")
    pdf.set_xy(30, 51)
    pdf.multi_cell(160, 6, ar(customer_address), 0, "R")

    # التاريخ
    pdf.set_xy(165, 18)
    pdf.cell(30, 8, datetime.now().strftime("%Y/%m/%d"), 0, 0, "C")

    # ========== جدول الأصناف =============
    pdf.set_xy(10, 80)
    pdf.set_font("Amiri", "", 10)

    headers = ["اسم الصنف", "الكمية", "التشغيلة", "تاريخ الصلاحية", "سعر الجمهور", "الخصم", "إجمالي القيمة"]
    col_w = [50, 18, 24, 28, 22, 16, 28]

    for h, w in zip(headers, col_w):
        pdf.cell(w, 8, ar(h), 1, 0, 'C')
    pdf.ln()

    total, total_qty = 0.0, 0

    def has_ar(text):
        if not text:
            return False
        for ch in str(text):
            if '\u0600' <= ch <= '\u06FF':
                return True
        return False

    for item in st.session_state["items"]:
        value = float(item["qty"]) * float(item["price"]) * (1 - float(item["discount"]) / 100)
        total += value
        total_qty += int(item["qty"])

        row = [
            item["name"],
            str(item["qty"]),
            item["batch"],
            item["expiry"],
            f"{item['price']:.2f}",
            f"{item['discount']}%",
            f"{value:.2f}"
        ]

        for txt, w in zip(row, col_w):
            pdf.cell(w, 9, ar(txt) if has_ar(txt) else txt, 1, 0, 'C')
        pdf.ln()

    # ========== ملخص الفاتورة ==========
    pdf.set_font("Amiri", "", 11)
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

    # ======== حفظ وتحميل ========
    filename = f"فاتورة_{invoice_number or datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename, mime="application/pdf")

    # حذف الصورة المؤقتة
    os.remove(bg_path)
