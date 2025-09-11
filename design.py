from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

# دالة تجهيز النص العربي
def ar_text(txt):
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(txt))

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # لو عندك ملف خط عربي (مثلاً GraphikArabic.ttf)
        try:
            self.add_font("Graphik", "", "GraphikArabic.ttf", uni=True)
            self.add_font("Graphik", "B", "GraphikArabic-Bold.ttf", uni=True)
            self.set_font("Graphik", "", 12)
        except:
            # fallback للخط الافتراضي
            self.set_font("Helvetica", "", 12)

    def header(self):
        self.set_font("Graphik", "B", 18)
        self.cell(0, 10, ar_text("فاتورة مبيعات"), ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Graphik", "I", 8)
        self.cell(0, 10, f"{ar_text('صفحة')} {self.page_no()}", align="C")

    def customer_info(self, name, code, address):
        self.set_font("Graphik", "", 12)
        self.cell(0, 10, ar_text("اسم الحساب: ") + ar_text(name), ln=True)
        self.cell(0, 10, ar_text("كود الحساب: ") + ar_text(code), ln=True)
        self.cell(0, 10, ar_text("العنوان: ") + ar_text(address), ln=True)
        self.cell(0, 10, ar_text("التاريخ: ") + ar_text(datetime.now().strftime("%Y-%m-%d")), ln=True)
        self.ln(5)

    def invoice_table(self, items):
        self.set_font("Graphik", "B", 12)
        # عناوين الجدول
        self.cell(40, 10, ar_text("الكمية"), 1, 0, "C")
        self.cell(40, 10, ar_text("السعر"), 1, 0, "C")
        self.cell(80, 10, ar_text("الوصف"), 1, 1, "C")

        self.set_font("Graphik", "", 12)
        for item in items:
            self.cell(40, 10, ar_text(str(item['quantity'])), 1, 0, "C")
            self.cell(40, 10, ar_text(str(item['price'])), 1, 0, "C")
            self.cell(80, 10, ar_text(item['description']), 1, 1, "C")

    def total_amount(self, total):
        self.set_font("Graphik", "B", 12)
        self.cell(0, 10, ar_text("الإجمالي: ") + ar_text(str(total)), ln=True, align="R")
