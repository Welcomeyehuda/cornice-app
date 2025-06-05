import streamlit as st
import matplotlib.pyplot as plt
import math
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import arabic_reshaper
from bidi.algorithm import get_display
import urllib.parse
import base64

pdfmetrics.registerFont(TTFont('David', 'DavidLibre-Medium.ttf'))

st.set_page_config(page_title='דו"ח חיתוך קרניזים אישי - Welcome Design', layout="centered")

try:
    with open("logo.png", "rb") as logo_file:
        logo_bytes = logo_file.read()
        st.image(logo_bytes, width=300)
except Exception as e:
    st.warning("⚠️ לא ניתן להציג את הלוגו. ודא שהקובץ 'logo.png' קיים בתיקייה.")
    logo_bytes = None

st.title("✂️ תכנון חיתוך קרניזים אישי ומדויק")
st.caption("חישוב כמויות אוטומטי מבית Welcome Design")

mode = st.radio("בחר מצב תכנון:", ["AI פריסטייל", "תכנון ידני"], index=1)
kind = st.radio("בחר סוג קרניז:", ["2 ס״מ - 69₪", "4 ס״מ - 100₪"], index=0)
price = 69 if "2 ס״מ" in kind else 100
bar_length = 290

wall_width = st.number_input("רוחב הקיר (בס״מ)", min_value=50, value=300, step=10)
wall_height = st.number_input("גובה הקיר (בס״מ)", min_value=50, value=260, step=10)
frame_count = st.number_input("כמה מסגרות תרצה בשורה העליונה?", min_value=1, value=3, step=1)

frames_top, frames_bottom = [], []

bottom_margin, vertical_gap, side_margin = 10, 20, 10
top_margin, inter_row_gap = 20, 15


def generate_pdf(summary_text, fig):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("David", 12)
    c.rect(20, 20, A4[0] - 40, A4[1] - 40)

    reshaped_lines = [get_display(arabic_reshaper.reshape(line)) for line in summary_text.split("\n")]
    y = 800
    for line in reshaped_lines:
        c.drawRightString(550, y, line)
        y -= 20

    c.showPage()

    c.setFont("David", 16)
    c.drawCentredString(A4[0] / 2, A4[1] - 50, get_display(arabic_reshaper.reshape("תוכנית קרניזים")))

    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    img = ImageReader(img_buffer)
    c.drawImage(img, 100, 100, width=400, preserveAspectRatio=True)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# (המשך הקוד נשאר זהה, לא שונה)
