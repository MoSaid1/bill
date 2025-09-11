import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# ---------------------- دالة تجهيز النص العربي ----------------------
def ar(txt):
    if txt is None:
        return ""
    s = str(txt)
    if not s:
        return ""
    return get_display(arabic_reshaper.reshape(s))

# ---------------------- إعداد Streamlit ----------------------
st.set_page_config(page_title="مولد الفواتير - Begonia Pharma", page_icon="📄")
st.title("📄 مولد الفواتير - Begonia Pharma")

if "items" not in st.session_state:
    st.session_state["items"] = []

# ---------------------- إدخال بيانات العميل ----------------------
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

# ---------------------- إضافة الأصناف ----------------------
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
    df_prev = pd.DataFrame(st.session_state["items"])
    df_prev["إجمالي القيمة"] = (df_prev["qty"] * df_prev["price"] * (1 - df_prev["discount"]/100)).round(2)
    st.table(df_prev)
else:
    st.info("لم يتم إضافة أي أصناف بعد.")

# ---------------------- توليد الفاتورة ----------------------
if st.button("📥 توليد الفاتورة PDF"):

    # ألوان وهوامش
    GREEN = (53, 148, 82)
    DARK = (60, 60, 60)
    LIGHT_GREY = (245, 245, 245)
    PAGE_W, PAGE_H = 210, 297
    MARGIN = 10
    CONTENT_W = PAGE_W - 2*MARGIN

    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_auto_page_break(False)

    # خط عربي
    pdf.add_font("Amiri", "", "Amiri-Regular.ttf", uni=True)
    pdf.set_font("Amiri", "", 12)

    # ---------------- Header background band ----------------
    pdf.set_fill_color(*LIGHT_GREY)
    pdf.rect(MARGIN, MARGIN, CONTENT_W, 50, "F")

    # ---------------- Logo ----------------
    try:
        pdf.image("logo.png", x=MARGIN+5, y=MARGIN+4, w=60)
    except:
        # لو اللوجو مش موجود نطبع اسم الشركة مكانه
        pdf.set_text_color(*GREEN)
        pdf.set_font("Amiri","",22)
        pdf.set_xy(MARGIN+5, MARGIN+10)
        pdf.cell(60, 12, ar("Begonia Pharma"), 0, 0, "L")

    # سجلات الشركة تحت اللوجو
    pdf.set_font("Amiri","",10)
    pdf.set_text_color(0,0,0)
    pdf.set_xy(MARGIN+5, MARGIN+32)
    pdf.cell(90, 5, ar("سجل تجاري رقم: 158377"), 0, 2, "L")
    pdf.set_x(MARGIN+5)
    pdf.cell(90, 5, ar("رقم التسجيل الضريبي: 174-658-610"), 0, 0, "L")

    # ---------------- Title (فاتورة) ----------------
    pdf.set_font("Amiri","",20)
    pdf.set_text_color(*GREEN)
    pdf.set_xy(PAGE_W - MARGIN - 50, MARGIN + 6)
    pdf.cell(50, 12, ar("فاتورة"), 0, 0, "R")

    # ---------------- Date ----------------
    pdf.set_font("Amiri","",12)
    pdf.set_text_color(0,0,0)
    pdf.set_xy(PAGE_W - MARGIN - 85, MARGIN + 22)
    pdf.cell(30, 8, ar("التاريخ:"), 0, 0, "R")
    pdf.cell(55, 8, datetime.now().strftime("%Y/%m/%d"), 0, 0, "L")

    # ---------------- Customer info box (right side) ----------------
    box_row_h = 8
    w_label = 35
    w_value = 62
    box_w = w_label + w_value
    box_x = MARGIN + CONTENT_W - box_w
    box_y = MARGIN + 30

    pdf.set_draw_color(*GREEN)
    pdf.set_line_width(0.5)
    pdf.set_font("Amiri","",12)

    # row 1
    pdf.set_xy(box_x, box_y)
    pdf.cell(w_value, box_row_h, ar(customer_name), 1, 0, "R")
    pdf.cell(w_label, box_row_h, ar("اسم الحساب:"), 1, 1, "R")
    # row 2
    pdf.set_x(box_x)
    pdf.cell(w_value, box_row_h, ar(customer_code), 1, 0, "R")
    pdf.cell(w_label, box_row_h, ar("كود الحساب:"), 1, 1, "R")
    # row 3
    pdf.set_x(box_x)
    pdf.cell(w_value, box_row_h, ar(invoice_number), 1, 0, "R")
    pdf.cell(w_label, box_row_h, ar("رقم الفاتورة:"), 1, 1, "R")

    # ---------------- Address line ----------------
    y_addr = box_y + box_row_h*3 + 6
    # سطر سفلي خفيف كخط إدخال
    pdf.set_draw_color(200,200,200)
    pdf.line(MARGIN, y_addr + 9, MARGIN + CONTENT_W, y_addr + 9)

    # عنوان: على اليمين + النص على اليسار
    pdf.set_text_color(0,0,0)
    pdf.set_font("Amiri","",12)
    # العنوان label
    pdf.set_xy(PAGE_W - MARGIN - 30, y_addr)
    pdf.cell(30, 8, ar("العنوان:"), 0, 0, "R")
    # قيمة العنوان
    pdf.set_xy(MARGIN, y_addr)
    pdf.cell(CONTENT_W - 40, 8, ar(customer_address), 0, 0, "R")

    # ---------------- Items table ----------------
    y_table = y_addr + 16
    pdf.set_xy(MARGIN, y_table)

    headers = ["اسم الصنف","الكمية","التشغيلة","تاريخ الصلاحية","سعر الجمهور","الخصم","إجمالي القيمة"]
    # مجموعها = 190
    col_w = [50, 18, 24, 30, 28, 18, 22]

    pdf.set_draw_color(*GREEN)
    pdf.set_line_width(0.5)
    pdf.set_text_color(0,0,0)

    # رؤوس الأعمدة
    pdf.set_font("Amiri","",11)
    for h, w in zip(headers, col_w):
        pdf.cell(w, 10, ar(h), 1, 0, "C")
    pdf.ln()

    # بيانات الأصناف
    total, total_qty = 0.0, 0
    pdf.set_font("Amiri","",10)

    def has_ar(s):
        if s is None:
            return False
        for ch in str(s):
            if "\u0600" <= ch <= "\u06FF":
                return True
        return False

    for item in st.session_state["items"]:
        value = float(item["qty"]) * float(item["price"]) * (1 - float(item["discount"])/100)
        total += value
        total_qty += int(item["qty"])
        row_vals = [
            item["name"],
            f"{item['qty']}",
            item["batch"],
            item["expiry"],
            f"{item['price']:.2f}",
            f"{item['discount']}%",
            f"{value:.2f}",
        ]
        pdf.set_x(MARGIN)
        for txt, w in zip(row_vals, col_w):
            if has_ar(txt):
                pdf.cell(w, 9, ar(txt), 1, 0, "C")
            else:
                pdf.cell(w, 9, str(txt), 1, 0, "C")
        pdf.ln()

    # صفوف فارغة لتجميل الجدول (حتى 8 صفوف)
    max_rows = 8
    current_rows = len(st.session_state["items"])
    empty_rows = max(0, max_rows - current_rows)
    for _ in range(empty_rows):
        pdf.set_x(MARGIN)
        for w in col_w:
            pdf.cell(w, 9, "", 1, 0, "C")
        pdf.ln()

    # ---------------- Summary table (يمين/يسار كما بالصورة) ----------------
    pdf.ln(6)
    summary_y = pdf.get_y()
    pdf.set_draw_color(*GREEN)
    pdf.set_line_width(0.5)
    pdf.set_font("Amiri","",12)

    # جدول من عمودين
    sum_x = MARGIN + 20
    sum_w_right = 70   # خلية اليمين (العناوين)
    sum_w_left  = 70   # خلية اليسار (القيم/عنوانين إضافية)
    row_h = 10

    # الصف 1: عدد الاصناف | عدد العلب
    pdf.set_xy(sum_x, summary_y)
    pdf.cell(sum_w_left, row_h, ar("عدد العلب"), 1, 0, "C")
    pdf.cell(sum_w_right, row_h, ar("عدد الاصناف"), 1, 1, "C")

    # الصف 2: قيم عدد العلب/الاصناف
    pdf.set_x(sum_x)
    pdf.cell(sum_w_left, row_h, str(total_qty), 1, 0, "C")
    pdf.cell(sum_w_right, row_h, str(len(st.session_state["items"])), 1, 1, "C")

    # الصف 3: تحصيل الدفع | إجمالي القيمة
    pdf.set_x(sum_x)
    pdf.cell(sum_w_left, row_h, f"{paid_amount:.2f}", 1, 0, "C")
    pdf.cell(sum_w_right, row_h, ar("تحصيل الدفع"), 1, 1, "C")

    pdf.set_x(sum_x)
    pdf.cell(sum_w_left, row_h, f"{total:.2f}", 1, 0, "C")
    pdf.cell(sum_w_right, row_h, ar("إجمالي القيمة"), 1, 1, "C")

    # ---------------- Footer ----------------
    footer_h = 14
    footer_y = PAGE_H - MARGIN - footer_h
    pdf.set_fill_color(*GREEN)
    pdf.rect(MARGIN, footer_y, CONTENT_W, footer_h, "F")

    pdf.set_text_color(255,255,255)
    pdf.set_font("Amiri","",11)
    pdf.set_xy(MARGIN, footer_y + 3)
    pdf.cell(
        CONTENT_W, 8,
        ar("📞 01040008105 - 01289982650     🌐 begoniapharma.com     📍 34 Gamal Eldin Dewidar st. With Zaker Heussin st. Nasr City, Cairo, Egypt"),
        0, 0, "C"
    )

    # ---------------- إخراج الملف ----------------
    filename = "invoice.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("⬇️ تحميل الفاتورة", f, file_name=filename)
