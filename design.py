from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

# دالة لمعالجة النص العربي
def ar_text(txt):
    return get_display(arabic_reshaper.reshape(txt))

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Graphik", "B", 18)
        self.cell(0, 10, ar_text("فاتورة"), ln=True, align="C")
        self.ln(5)

    def customer_info(self, name, code, address):
        self.set_font("Graphik", "", 12)
        self.cell(0, 10, ar_text(f"اسم الحساب: {name}"), ln=True)
        self.cell(0, 10, ar_text(f"كود الحساب: {code}"), ln=True)
        self.cell(0, 10, ar_text(f"العنوان: {address}"), ln=True)
        self.cell(0, 10, ar_text(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"), ln=True)
        self.ln(5)

    def items_table(self, items):
        col_widths = [40, 25, 30, 30, 25, 40]
        headers = ["اسم الصنف", "الكمية", "تاريخ الصلاحية", "سعر الجمهور", "الخصم", "اجمالي القيمة"]

        # الهيدر
        self.set_font("Graphik", "B", 12)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, ar_text(header), 1, 0, "C")
        self.ln()

        # الأصناف
        total = 0
        self.set_font("Graphik", "", 11)
        for item in items:
            self.cell(col_widths[0], 10, ar_text(item["name"]), 1)
            self.cell(col_widths[1], 10, str(item["qty"]), 1)
            self.cell(col_widths[2], 10, ar_text(item["expiry"]), 1)
            self.cell(col_widths[3], 10, str(item["price"]), 1)
            self.cell(col_widths[4], 10, str(item["discount"])+"%", 1)
            value = item["qty"] * item["price"] * (1 - item["discount"]/100)
            self.cell(col_widths[5], 10, str(round(value, 2)), 1, ln=True)
            total += value
        return total

    def total_amount(self, total):
        self.ln(5)
        self.set_font("Graphik", "B", 14)
        self.cell(0, 10, ar_text(f"إجمالي القيمة: {round(total, 2)}"), ln=True, align="R")
