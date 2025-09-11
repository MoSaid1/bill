import streamlit as st
from design import InvoicePDF, ar_text   # نستورد الكلاس و دالة النص العربي

# واجهة المستخدم
st.title("🧾 إنشاء فاتورة")

customer_name = st.text_input("اسم العميل")
items = []

st.subheader("إضافة الأصناف")
num_items = st.number_input("عدد الأصناف", min_value=1, max_value=20, value=1)

for i in range(num_items):
    st.markdown(f"### الصنف {i+1}")
    name = st.text_input(f"اسم الصنف {i+1}", key=f"name_{i}")
    qty = st.number_input(f"الكمية {i+1}", min_value=1, value=1, key=f"qty_{i}")
    expiry = st.text_input(f"تاريخ الصلاحية {i+1}", key=f"expiry_{i}")
    price = st.number_input(f"سعر الجمهور {i+1}", min_value=0.0, key=f"price_{i}")
    discount = st.number_input(f"الخصم {i+1}", min_value=0.0, key=f"discount_{i}")
    
    items.append({
        "name": name,
        "qty": qty,
        "expiry": expiry,
        "price": price,
        "discount": discount,
        "total": (price - discount) * qty,
    })

if st.button("إنشاء فاتورة PDF"):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_font("GraphikArabic", "", 12)

    # بيانات العميل
    pdf.cell(0, 10, ar_text(f"اسم العميل: {customer_name}"), ln=True, align="R")

    # جدول الأصناف
    pdf.ln(5)
    col_widths = [40, 20, 40, 30, 20, 30]
    headers = ["اسم الصنف", "الكمية", "تاريخ الصلاحية", "سعر الجمهور", "الخصم", "اجمالي القيمة"]

    pdf.set_font("GraphikArabic", "B", 12)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, ar_text(header), 1, 0, "C")
    pdf.ln()

    pdf.set_font("GraphikArabic", "", 12)
    for item in items:
        pdf.cell(col_widths[0], 10, ar_text(item["name"]), 1)
        pdf.cell(col_widths[1], 10, str(item["qty"]), 1, 0, "C")
        pdf.cell(col_widths[2], 10, ar_text(item["expiry"]), 1, 0, "C")
        pdf.cell(col_widths[3], 10, str(item["price"]), 1, 0, "C")
        pdf.cell(col_widths[4], 10, str(item["discount"]), 1, 0, "C")
        pdf.cell(col_widths[5], 10, str(item["total"]), 1, 0, "C")
        pdf.ln()

    # المجموع الكلي
    total_amount = sum(item["total"] for item in items)
    pdf.ln(5)
    pdf.set_font("GraphikArabic", "B", 12)
    pdf.cell(0, 10, ar_text(f"المجموع الكلي: {total_amount}"), ln=True, align="R")

    # حفظ وعرض
    file_path = "invoice.pdf"
    pdf.output(file_path)
    with open(file_path, "rb") as f:
        st.download_button("📥 تحميل الفاتورة", f, file_name="invoice.pdf")
