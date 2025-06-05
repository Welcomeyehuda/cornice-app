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

wall_width = st.number_input("רוחב הקיר (בס״מ)", min_value=50, value=300, step=10)
wall_height = st.number_input("גובה הקיר (בס״מ)", min_value=50, value=260, step=10)
frame_count = st.number_input("כמה מסגרות תרצה בשורה העליונה?", min_value=1, value=3, step=1)

frames_top, frames_bottom = [], []

bottom_margin, vertical_gap, side_margin = 10, 20, 10
top_margin, inter_row_gap = 20, 15

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
            perimeter = 2 * (fw + fh)
            total_perimeter += perimeter
            frame_details.append(("תחתון", i + 1, fw, fh, perimeter))
            current_x += fw + spacing

    st.pyplot(fig)
    st.success(f"סה\"כ היקף קרניז: {total_perimeter} ס\"מ")

    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    mot_length = 240 if "2 ס" in kind else 200
    motim = math.ceil(total_perimeter / mot_length)
    total_price = motim * price

    text = f"תכנון קרניזים אישי - Welcome Design\nסה\"כ היקף: {total_perimeter} ס\"מ\nסה\"כ מוטות: {motim}\nסה\"כ מחיר: ₪{total_price}"
    for pos, num, fw, fh, perim in frame_details:
        text += f"\nמסגרת {pos} #{num}: {fw}×{fh} ס\"מ | היקף: {perim} ס\"מ"

    whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(text)}"
    st.markdown(f"[📤 שתף בוואטסאפ]({whatsapp_url})", unsafe_allow_html=True)

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    c.setFont("David", 14)

    if logo_bytes:
        c.drawImage(ImageReader(BytesIO(logo_bytes)), 40, 770, width=100, height=40)

    reshaped_title = arabic_reshaper.reshape("דו\"ח חיתוך קרניזים אישי")
    bidi_title = get_display(reshaped_title)
    c.drawCentredString(300, 780, bidi_title)

    y_position = 740
    for pos, num, fw, fh, perim in frame_details:
        line = f"מסגרת {pos} #{num}: {fw}×{fh} ס\"מ | היקף: {perim} ס\"מ"
        reshaped_line = arabic_reshaper.reshape(line)
        bidi_line = get_display(reshaped_line)
        c.drawRightString(550, y_position, bidi_line)
        y_position -= 20
        if y_position < 300:
            c.showPage()
            c.setFont("David", 14)
            y_position = 770

    reshaped_summary = arabic_reshaper.reshape(f"סה\"כ קרניזים: {total_perimeter} ס\"מ | נדרש {motim} מוטות ({mot_length} ס\"מ כל אחד)")
    reshaped_price = arabic_reshaper.reshape(f"סה\"כ מחיר: ₪{total_price}")
    c.drawRightString(550, y_position, get_display(reshaped_summary))
    y_position -= 20
    c.drawRightString(550, y_position, get_display(reshaped_price))
    y_position -= 40

    c.drawImage(ImageReader(buffer), 50, 20, width=500, preserveAspectRatio=True, mask='auto')
    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    st.download_button(label="📥 הורד PDF הסיכום", data=pdf_buffer, file_name="cornice_summary.pdf", mime="application/pdf")
