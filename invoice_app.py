import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import barcode
from barcode.writer import ImageWriter
import os
import re

# ========== إعداد ==========
st.set_page_config("مولد فاتورة بباركود", ":bookmark_tabs:")
st.title("📄 مولد الفاتورة - مع باركود")

# ========== دالة تصليح النص العربي ==========
def fix_arabic(txt: str) -> str:
    if not txt: return ""
    reshaped = arabic_reshaper.reshape(str(txt))
    return get_display(reshaped)

# ========== دالة توليد باركود ==========
def generate_barcode(data, filename="barcode"):
    code128 = barcode.get_barcode_class('code128')
    bar = code128(data, writer=ImageWriter(), add_checksum=False)
    fullpath = bar.save(filename)
    return fullpath

# ========== تخزين الأصناف ==========
if "items" not in st.session_state:
    st.session_state["items"] = []

# ========== بيانات العميل ==========
st.header("👨‍💼 بيانات العميل")
col1, col2, col3 = st.columns(3)
with col1:
    customer_name = st.text_input("اسم الحساب")
with col2:
    customer_code = st.text_input("كود الحساب")
with col3:
    invoice_number = st.text_input("رقم الفاتورة")

customer_address = st.text_area("📍 العنوان")

# ========== خصومات ==========
st.header("💲 المدفوعات والخصومات")
colp1, colp2 = st.columns(2)
with colp1:
    paid_amount = st.number_input("تحصيل الدفع", min_value=0.0, step=10.0)

with colp2:
    apply_early = st.checkbox("📉 تفعيل خصم تعجيل الدفع")
    early_discount = 0.0
    if apply_early:
        early_discount = st.number_input("نسبة خصم تعجيل الدفع (%)", min_value=0.0, max_value=100.0, step=0.5)

apply_extra = st.checkbox("📦 تفعيل خصم إضافي")
extra_discount = 0.0
if apply_extra:
    extra_discount = st.number_input("نسبة خصم إضافي (%)", min_value=0.0, max_value=100.0, step=0.5)

# ========== تحكم في الباركود ==========
st.header("🏷️ إعدادات الباركود")
col_x, col_y = st.columns(2)
with col_x:
    barcode_x = st.number_input("📍 إحداثي X", min_value=0, max_value=200, value=150)
with col_y:
    barcode_y = st.number_input("📍 إحداثي Y", min_value=0, max_value=280, value=260)

# ========== الأصناف ==========
st.header("🧪 إضافة الأصناف")
with st.form("add_item"):
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
        discount = st.number_input("الخصم (%)", min_value=0.0, max_value=100.0, step=0.5)

    if st.form_submit_button("➕ أضف"):
        st.session_state["items"].append({
            "name": name,
            "qty": qty,
            "batch": batch,
            "expiry": expiry,
            "price": price,
            "discount": discount
        })

# ========== عرض الأصناف ==========
if st.session_state["items"]:
    df = pd.DataFrame(st.session_state["items"])
    df["إجمالي"] = (df["qty"] * df["price"] * (1 - df["discount"] / 100)).round(2)
    st.table(df)
else:
    st.info("لم يتم إدخال أصناف بعد.")

# ========== توليد الفاتورة ==========
if st.button("📄 توليد الفاتورة PDF"):
    if not os.path.exists("bill.jpg"):
        st.error("❌ الخلفية bill.jpg غير موجودة")
        st.stop()

    if not os.path.exists("Amiri-Regular.ttf"):
        st.error("❌ الخط Amiri-Regular.ttf غير موجود")
        st.stop()

    pdf = FPDF()
    pdf.add_page()
    pdf.image("bill.jpg", x=0, y=0, w=210, h=297)

    pdf.add_font("Amiri", "", "Amiri-Regular.ttf", uni=True)
    pdf.set_font("Amiri", "", 12)

    # ========== بيانات العميل ==========
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
    headers = ["إجمالي", "الخصم", "السعر", "الصلاحية", "تشغيلة", "الكمية", "اسم الصنف"]
    col_w = [28, 18, 24, 22, 22, 16, 48]
    x_center = (210 - sum(col_w)) / 2
    pdf.set_xy(x_center, 80)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Amiri", "", 9)
    for h, w in zip(headers, col_w):
        pdf.cell(w, 8, fix_arabic(h), 1, 0, 'C', fill=True)
    pdf.ln()

    total = 0
    total_qty = 0
    for item in st.session_state["items"]:
        val = item['qty'] * item['price'] * (1 - item['discount'] / 100)
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
        for val, w in zip(row, col_w):
            pdf.cell(w, 9, val, 1, 0, 'C')
        pdf.ln()

    # الخصومات
    original_total = total
    if apply_early and early_discount > 0:
        total *= (1 - early_discount / 100)

    if apply_extra and extra_discount > 0:
        total *= (1 - extra_discount / 100)

    # ملخص الفاتورة
    pdf.set_font("Amiri", "", 10)
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

    # توليد الباركود من رقم الفاتورة
    barcode_path = generate_barcode(invoice_number or "00000", "barcode_image")
    pdf.image(barcode_path, x=barcode_x, y=barcode_y, w=40)

    today_str = datetime.now().strftime("%Y-%m-%d")
    safe_invoice = re.sub(r'\W+', '_', invoice_number or "no_number")
    filename = f"فاتورة_{safe_invoice}_{today_str}.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.success("✅ تم توليد الفاتورة مع الباركود!")
        st.download_button("⬇️ تحميل PDF", f, file_name=filename, mime="application/pdf")
