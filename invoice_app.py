import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import os
import re
import urllib.parse
import urllib.request

# جرّب استيراد segno، ولو مش موجود هنستخدم API خارجي كـ fallback
try:
    import segno  # QR code library
except Exception:
    segno = None

# ===== إصلاح الكتابة العربية =====
def fix_arabic(txt):
    reshaped = arabic_reshaper.reshape(str(txt))
    return get_display(reshaped)

# ===== توليد QR Code (segno إن وجد، وإلا API خارجي) =====
def generate_qrcode(data, filename="qrcode.png", size=200):
    data = str(data or "")
    if segno is not None:
        qr = segno.make(data)
        scale = max(2, int(size / 50))  # مقياس تقديري للحجم
        qr.save(filename, scale=scale)  # يحفظ PNG
        return filename
    # Fallback عبر API خارجي (لا يحتاج أي مكتبات إضافية)
    url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data=" + urllib.parse.quote(data)
    with urllib.request.urlopen(url, timeout=10) as resp:
        png = resp.read()
    with open(filename, "wb") as f:
        f.write(png)
    return filename

# ===== حالة الجلسة للأصناف =====
if "items" not in st.session_state:
    st.session_state["items"] = []

st.set_page_config(page_title="فاتورة مع QR | Begonia", page_icon=":page_facing_up:")
st.title("📄 مولد فاتورة - Begonia Pharma")

# ===== بيانات العميل =====
st.header("👨‍💼 بيانات العميل")
col1, col2, col3 = st.columns(3)
with col1:
    customer_name = st.text_input("اسم العميل")
with col2:
    customer_code = st.text_input("كود العميل")
with col3:
    invoice_number = st.text_input("رقم الفاتورة")

customer_address = st.text_area("📍 عنوان العميل")

# ===== المدفوعات والخصومات =====
st.header("💲 المدفوعات والخصومات")
col_a, col_b = st.columns(2)

with col_a:
    paid_amount = st.number_input("💵 تحصيل الدفع", min_value=0.0, step=10.0)

with col_b:
    apply_early = st.checkbox("📉 تفعيل خصم تعجيل الدفع؟")
    early_discount = 0.0
    if apply_early:
        early_discount = st.number_input("نسبة خصم تعجيل الدفع (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

apply_extra = st.checkbox("📦 تفعيل خصم إضافي عام؟")
extra_discount = 0.0
if apply_extra:
    extra_discount = st.number_input("نسبة خصم إضافي عام (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

# ===== تحكم في مكان QR Code داخل PDF =====
st.header("🧭 تحكم في مكان QR Code داخل PDF")
colx, coly = st.columns(2)
with colx:
    qr_x = st.number_input("📍 X (بالملّيمتر)", min_value=0, max_value=200, value=150, step=1)
with coly:
    qr_y = st.number_input("📍 Y (بالملّيمتر)", min_value=0, max_value=280, value=260, step=1)

st.caption("مولد QR المستخدم: " + ("segno (محلي)" if segno is not None else "API خارجي (بدون تثبيت مكتبات)"))

# ===== إضافة الأصناف =====
st.header("🧪 الأصناف")
with st.form("add_item"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("اسم الصنف")
    with c2:
        qty = st.number_input("الكمية", min_value=1, step=1, value=1)
    with c3:
        price = st.number_input("السعر", min_value=0.0, step=0.5, value=0.0)

    c4, c5, c6 = st.columns(3)
    with c4:
        batch = st.text_input("التشغيلة")
    with c5:
        expiry = st.text_input("تاريخ الصلاحية")
    with c6:
        discount = st.number_input("الخصم (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

    if st.form_submit_button("➕ أضف الصنف"):
        st.session_state["items"].append({
            "name": name,
            "qty": qty,
            "price": price,
            "batch": batch,
            "expiry": expiry,
            "discount": discount
        })

# ===== عرض الأصناف =====
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    df["الإجمالي"] = (df["qty"] * df["price"] * (1 - df["discount"] / 100)).round(2)
    st.table(df)
else:
    st.info("لم يتم إدخال أصناف بعد.")

# ===== توليد PDF =====
if st.button("📥 توليد الفاتورة PDF"):

    # تحقق من الملفات المطلوبة
    if not os.path.exists("bill.jpg") or not os.path.exists("Amiri-Regular.ttf"):
        st.error("❗ تأكد من وجود bill.jpg وAmiri-Regular.ttf في نفس المجلد")
        st.stop()

    # إنشاء الـ PDF وإضافة الخلفية
    pdf = FPDF()
    pdf.add_page()
    pdf.image("bill.jpg", x=0, y=0, w=210, h=297)
    pdf.add_font("Amiri", "", "Amiri-Regular.ttf", uni=True)
    pdf.set_font("Amiri", "", 11)

    # بيانات العميل
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

    # جدول الأصناف
    headers = ["الإجمالي", "الخصم", "السعر", "الصلاحية", "تشغيلة", "الكمية", "الصنف"]
    col_w = [28, 18, 24, 22, 22, 16, 48]
    x_center = (210 - sum(col_w)) / 2

    pdf.set_xy(x_center, 80)
    pdf.set_fill_color(230, 230, 230)
    for h, w in zip(headers, col_w):
        pdf.cell(w, 8, fix_arabic(h), 1, 0, 'C', fill=True)
    pdf.ln()

    total = 0.0
    total_qty = 0
    for item in st.session_state["items"]:
        subtotal = item["qty"] * item["price"] * (1 - item["discount"] / 100)
        total += subtotal
        total_qty += item["qty"]
        row = [
            fix_arabic(f"{subtotal:.2f}"),
            fix_arabic(f"{item['discount']}%"),
            fix_arabic(f"{item['price']:.2f}"),
            fix_arabic(item["expiry"]),
            fix_arabic(item["batch"]),
            fix_arabic(str(item["qty"])),
            fix_arabic(item["name"])
        ]
        pdf.set_x(x_center)
        for val, w in zip(row, col_w):
            pdf.cell(w, 9, val, 1, 0, 'C')
        pdf.ln()

    # تطبيق الخصومات
    if apply_early and early_discount > 0:
        total *= (1 - early_discount / 100)
    if apply_extra and extra_discount > 0:
        total *= (1 - extra_discount / 100)

    # ملخص الفاتورة
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

    if apply_early and early_discount > 0:
        pdf.set_x(125)
        pdf.cell(40, 8, fix_arabic(f"{early_discount}%"), 1, 0, 'C')
        pdf.cell(40, 8, fix_arabic("خصم تعجيل الدفع"), 1, 1, 'C')

    if apply_extra and extra_discount > 0:
        pdf.set_x(125)
        pdf.cell(40, 8, fix_arabic(f"{extra_discount}%"), 1, 0, 'C')
        pdf.cell(40, 8, fix_arabic("خصم إضافي عام"), 1, 1, 'C')

    pdf.set_x(125)
    pdf.cell(40, 8, fix_arabic(f"{total:.2f}"), 1, 0, 'C')
    pdf.cell(40, 8, fix_arabic("إجمالي القيمة"), 1, 1, 'C')

    # توليد وإدراج QR Code في المكان المحدد
    qr_path = generate_qrcode(invoice_number or "00000", filename="qrcode.png", size=200)
    pdf.image(qr_path, x=qr_x, y=qr_y, w=30)  # تحكم في الموقع عبر X و Y

    # حفظ وتنزيل الفاتورة
    invoice_safe = re.sub(r'\W+', '_', invoice_number or "no_number")
    filename = f"فاتورة_{invoice_safe}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.success("✅ تم إنشاء الفاتورة!")
        st.download_button("⬇️ تحميل PDF", f, file_name=filename, mime="application/pdf")
