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

# רישום הגופן העברי ל־PDF
pdfmetrics.registerFont(TTFont('David', 'DavidLibre-Medium.ttf'))

st.set_page_config(page_title="דו"ח חיתוך קרניזים אישי - Welcome Design", layout="centered")
st.image("לוגו חדש.png", width=300)
st.title("✂️ דו"ח חיתוך קרניזים אישי")
st.caption("מיועד ללקוח כחלק מתהליך תכנון - Welcome Design")

# קלט מידות קיר
wall_width = st.number_input("רוחב הקיר (בס״מ)", min_value=50, value=300, step=10)
wall_height = st.number_input("גובה הקיר (בס״מ)", min_value=50, value=260, step=10)

# מספר מסגרות
frame_count = st.number_input("כמה מסגרות תרצה?", min_value=1, value=3, step=1)

# קלט מסגרות
frames = []
st.subheader("מידות כל מסגרת (בס״מ)")
for i in range(int(frame_count)):
    col1, col2 = st.columns(2)
    with col1:
        fw = st.number_input(f"רוחב מסגרת {i+1}", key=f"fw_{i}", min_value=10, value=100)
    with col2:
        fh = st.number_input(f"גובה מסגרת {i+1}", key=f"fh_{i}", min_value=10, value=140)
    frames.append((fw, fh))

# מרווחים קבועים
side_margin = 10
top_margin = 20
bottom_margin = 10
available_width = wall_width - 2 * side_margin
total_frames_width = sum(f[0] for f in frames)
spacing = (available_width - total_frames_width) / (len(frames) + 1)

# כפתור פעולה
if st.button("📐 שרטט וחשב"):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    ax.plot([0, wall_width], [0, 0], color='gray')
    ax.plot([0, wall_width], [wall_height, wall_height], color='gray')
    ax.plot([0, 0], [0, wall_height], color='gray')
    ax.plot([wall_width, wall_width], [0, wall_height], color='gray')

    current_x = side_margin + spacing
    total_perimeter = 0

    for i, (fw, fh) in enumerate(frames):
        y = top_margin
        ax.add_patch(plt.Rectangle((current_x, y), fw, fh, edgecolor='blue', facecolor='none', linewidth=2))
        ax.annotate(f"ס״מ {fw}", xy=(current_x + fw / 2, y + fh + 5), ha='center', fontsize=8, color='blue')
        ax.annotate(f"ס״מ {fh}", xy=(current_x - 10, y + fh / 2), rotation=90, va='center', fontsize=8, color='blue')
        if i < len(frames) - 1:
            ax.annotate(f"ס״מ {int(spacing)}", xy=(current_x + fw + spacing / 2, y + fh / 2), ha='center', fontsize=8, color='green')
        total_perimeter += 2 * (fw + fh)
        current_x += fw + spacing

    ax.annotate(f"ס״מ {top_margin}", xy=(5, top_margin / 2), rotation=90, va='center', fontsize=8, color='red')
    ax.annotate(f"ס״מ {side_margin}", xy=(side_margin / 2, wall_height - 5), ha='center', fontsize=8, color='red')
    ax.annotate(f"ס״מ {side_margin}", xy=(wall_width - side_margin / 2, wall_height - 5), ha='center', fontsize=8, color='red')

    st.pyplot(fig)

    st.subheader("📋 סיכום כמויות:")
    for idx, (fw, fh) in enumerate(frames):
        perim = 2 * (fw + fh)
        st.write(f"🔹 מסגרת {idx+1}: היקף ס״מ {perim}")
    st.write(f"📏 סך הכול היקף: {total_perimeter} ס״מ")

    section_length_cm = 290
    required_sections = math.ceil(total_perimeter / section_length_cm)
    st.write(f"🪚 נדרש: {required_sections} יחידות קרניז (2.90 מטר)")

    kind = st.radio("בחר סוג קרניז:", ["2 ס״מ - 69₪", "4 ס״מ - 100₪"], index=0)
    price = 69 if "2 ס״מ" in kind else 100
    total_cost = required_sections * price
    st.write(f"💰 עלות משוערת: ₪{total_cost}")

    st.markdown("---")
    st.caption("*השרטוט לצורכי הדמיה בלבד – יש לוודא מדידות בשטח.*")

    def rtl(text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    def create_pdf(fig):
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='PNG')
        img_buffer.seek(0)

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawImage("לוגו חדש.png", 420, 770, width=130, preserveAspectRatio=True)
        c.setFont('David', 14)
        c.drawCentredString(300, 790, rtl('דו"ח תכנון קרניזים בהתאמה אישית'))
        c.setFont('David', 12)

        y = 750
        c.drawRightString(550, y, rtl(f'רוחב קיר: {wall_width} ס"מ    גובה קיר: {wall_height} ס"מ'))
        y -= 20

        for idx, (fw, fh) in enumerate(frames):
            perim = 2 * (fw + fh)
            c.drawRightString(550, y, rtl(f'מסגרת {idx+1}: רוחב {fw} ס"מ, גובה {fh} ס"מ, היקף כולל {perim} ס"מ'))
            y -= 18

        y -= 10
        c.drawRightString(550, y, rtl(f'סך הכול היקף: {total_perimeter} ס"מ'))
        y -= 18
        c.drawRightString(550, y, rtl(f'סך הכול נדרש: {required_sections} יחידות קרניז (2.90 מטר)'))
        y -= 18
        c.drawRightString(550, y, rtl(f'עלות משוערת: ₪{total_cost}'))

        image = ImageReader(img_buffer)
        c.drawImage(image, 50, 100, width=500, preserveAspectRatio=True)

        c.rect(30, 30, 530, 780)
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf(fig)
    st.download_button("📄 הורד PDF", data=pdf_buffer, file_name="cornice_summary.pdf", mime="application/pdf")

    share_text = f"תכנון מותאם אישית לקרניזים של Welcome Design\nהיקף כולל: {total_perimeter} ס\"מ\nנדרשות {required_sections} יחידות.\nעלות משוערת: ₪{total_cost}"
    whatsapp_link = f"https://api.whatsapp.com/send?text={share_text}"
    st.markdown(f"[📤 שתף בוואטסאפ]({whatsapp_link})")
