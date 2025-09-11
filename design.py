from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

# دالة لمعالجة النصوص العربية
def ar_text(txt):
    if not txt:  # لو النص فاضي
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))

# كلاس تصميم الفاتورة
class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)  # استخدم خط أساسي متاح
        self.cell(0, 10, ar_text("فاتورة"), border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, ar_text("صفحة ") + str(self.page_no()), align="C")

    def customer_info(self, name, code, address, date=None):
        self.set_font("Helvetica", "", 12)
        self.cell(0, 10, ar_text("اسم الحساب: ") + ar_text(name), ln=True)
        self.cell(0, 10, ar_text("كود الحساب: ") + ar_text(code), ln=True)
        self.cell(0, 10, ar_text("العنوان: ") + ar_text(address), ln=True)
        if not date:
            date = datetime.now().strftime("%d-%m-%Y")
        self.cell(0, 10, ar_text("التاريخ: ") + ar_text(date), ln=True)
        self.ln(5)

    def invoice_table(self, data):
        # العناوين
        self.set_font("Helvetica", "B", 12)
        col_widths = [40, 25, 25, 35, 25, 30]
        headers = ["اسم صنف", "كمية", "تاريخ صلاحية", "سعر اجمالي", "الخصم", "إجمالي القيمة"]

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, ar_text(header), border=1, align="C")
        self.ln()

        # الصفوف
        self.set_font("Helvetica", "", 12)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, ar_text(str(item)), border=1, align="C")
            self.ln()
