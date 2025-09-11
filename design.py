from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

def ar_text(txt):
    """تهيئة النص العربي ليظهر بشكل صحيح"""
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))

class InvoicePDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # تسجيل خط Graphik Arabic
        self.add_font("GraphikArabic", "", "fonts/GRAPHIK ARABIC SEMIBOLD.OTF", uni=True)

    def header(self):
        self.set_font("GraphikArabic", "", 18)
        self.cell(0, 10, ar_text("فاتورة"), border=False, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("GraphikArabic", "", 8)
        self.cell(0, 10, ar_text(f"صفحة {self.page_no()}"), align="C")
