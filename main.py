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

    reshaped_lines = [get_display(arabic_reshaper.reshape(line)) for line in summary_text.split("\n")]
    y = 800
    for line in reshaped_lines:
        c.drawRightString(550, y, line)
        y -= 20

    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    img = ImageReader(img_buffer)
    c.drawImage(img, 100, 100, width=400, preserveAspectRatio=True)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

if mode == "תכנון ידני":
    st.subheader("✏️ מידות המסגרות העליונות")
    for i in range(int(frame_count)):
        col1, col2 = st.columns(2)
        with col1:
            fw = st.number_input(f"רוחב מסגרת {i+1}", key=f"top_fw_{i}", min_value=10, value=100)
        with col2:
            fh = st.number_input(f"גובה מסגרת {i+1}", key=f"top_fh_{i}", min_value=10, value=140)
        frames_top.append((fw, fh))
else:
    default_fw, default_fh = 80, 140
    max_frames = int((wall_width - 2 * side_margin + 10) // (default_fw + 10))
    available_width = wall_width - 2 * side_margin
    spacing = (available_width - (default_fw * max_frames)) / (max_frames - 1) if max_frames > 1 else 0
    frames_top = [(default_fw, default_fh)] * max_frames

show_bottom = st.checkbox("הוסף מסגרות תחתונות")

if mode == "תכנון ידני" and show_bottom:
    st.subheader("✏️ מידות המסגרות התחתונות")
    for i in range(int(frame_count)):
        col1, col2 = st.columns(2)
        with col1:
            fw = st.number_input(f"רוחב תחתון מסגרת {i+1}", key=f"bottom_fw_{i}", min_value=10, value=100)
        with col2:
            fh = st.number_input(f"גובה תחתון מסגרת {i+1}", key=f"bottom_fh_{i}", min_value=10, value=60)
        frames_bottom.append((fw, fh))
elif mode == "AI פריסטייל" and show_bottom:
    default_fw, default_fh = 80, 60
    frames_bottom = [(default_fw, default_fh)] * len(frames_top)

available_width = wall_width - 2 * side_margin
total_frames_width = sum(f[0] for f in frames_top)
spacing = (available_width - total_frames_width) / (len(frames_top) - 1) if len(frames_top) > 1 else 0

if st.button("📐 שרטט וחשב"):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    for x in [0, wall_width]:
        ax.plot([x, x], [0, wall_height], color='gray')
    ax.plot([0, wall_width], [0, 0], color='gray')
    ax.plot([0, wall_width], [wall_height, wall_height], color='gray')

    current_x, total_perimeter = side_margin, 0
    frame_details = []

    for i, (fw, fh) in enumerate(frames_top):
        y = top_margin
        ax.add_patch(plt.Rectangle((current_x, y), fw, fh, edgecolor='blue', facecolor='none', linewidth=2))
        ax.annotate(f"ס״מ {fw}", xy=(current_x + fw / 2, y + fh + 5), ha='center', fontsize=8, color='blue')
        ax.annotate(f"ס״מ {fh}", xy=(current_x - 10, y + fh / 2), rotation=90, va='center', fontsize=8, color='blue')
        if i < len(frames_top) - 1:
            ax.annotate(f"ס״מ {int(spacing)}", xy=(current_x + fw + spacing / 2, y + fh / 2), ha='center', fontsize=8, color='green')
        perimeter = 2 * (fw + fh)
        total_perimeter += perimeter
        frame_details.append(("עליון", i + 1, fw, fh, perimeter))
        current_x += fw + spacing

    if show_bottom:
        current_x = side_margin
        for i, (fw, fh) in enumerate(frames_bottom):
            y = top_margin + frames_top[i][1] + inter_row_gap
            ax.add_patch(plt.Rectangle((current_x, y), fw, fh, edgecolor='purple', facecolor='none', linewidth=2))
            ax.annotate(f"ס״מ {fw}", xy=(current_x + fw / 2, y + fh + 5), ha='center', fontsize=8, color='purple')
            ax.annotate(f"ס״מ {fh}", xy=(current_x - 10, y + fh / 2), rotation=90, va='center', fontsize=8, color='purple')
            ax.annotate(f"רווח 15 ס""מ", xy=(current_x + fw / 2, y - inter_row_gap / 2), ha='center', fontsize=8, color='gray')
            perimeter = 2 * (fw + fh)
            total_perimeter += perimeter
            frame_details.append(("תחתון", i + 1, fw, fh, perimeter))
            current_x += fw + spacing

    st.pyplot(fig)
    st.success(f"סה\"כ היקף קרניז: {total_perimeter} ס\"מ")

    units = math.ceil(total_perimeter / bar_length)
    total_price = units * price

    summary_lines = [
        f"🎨 תכנון אישי לחיפוי קרניזים מבית Welcome Design!",
        f"\n🧱 מידות הקיר:\n• רוחב: {wall_width} ס\"מ\n• גובה: {wall_height} ס\"מ",
        f"\n📦 דגם נבחר: קרניז {kind.split(' ')[0]} – {price}₪",
        f"\n🖼️ מסגרות:"]
    for level, idx, fw, fh, perim in frame_details:
        summary_lines.append(f"{idx}. {level} – רוחב: {fw} ס\"מ | גובה: {fh} ס\"מ | היקף: {int(perim)} ס\"מ")

    summary_lines.append(f"\n🧮 סה\"כ היקף קרניזים: {int(total_perimeter)} ס\"מ")
    summary_lines.append(f"🪵 נדרשים: {units} מוטות (באורך {bar_length} ס\"מ)")
    summary_lines.append(f"\n💰 מחיר משוער: {total_price} ₪")
    summary_lines.append(f"\n📞 מחירים מיוחדים והתקנה מקצועית – דברו איתנו!")

    summary_text = "\n".join(summary_lines)
    st.text_area("📋 פירוט הדו\"ח:", summary_text, height=250)

    col1, col2 = st.columns(2)
    with col1:
        pdf_buffer = generate_pdf(summary_text, fig)
        st.download_button(
            label="📄 הורד PDF",
            data=pdf_buffer,
            file_name="cornice_summary.pdf",
            mime="application/pdf",
            type="primary"
        )
    with col2:
        link = f"https://wa.me/?text={urllib.parse.quote(summary_text)}"
        st.markdown(f"[📤 שתף בוואטסאפ]({link})")
