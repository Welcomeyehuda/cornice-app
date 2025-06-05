import streamlit as st
import matplotlib.pyplot as plt
import math
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# רישום הגופן העברי ל־PDF
pdfmetrics.registerFont(TTFont('David', 'david.ttf'))

st.set_page_config(page_title="תכנון קרניזים", layout="centered")
st.title("\ud83d\udccf תכנון קרניזים חכם + סיכום PDF")

# קלט מידות קיר
wall_width = st.number_input("רוחב הקיר (בס\u05e1\u05b4\u05dd)", min_value=50, value=300, step=10)
wall_height = st.number_input("גובה הקיר (בס\u05e1\u05b4\u05dd)", min_value=50, value=260, step=10)

# מספר מסגרות
frame_count = st.number_input("כמה מסגרות תרצה?", min_value=1, value=3, step=1)

# קלט מסגרות
frames = []
st.subheader("מידות כל מסגרת (בס\u05e1\u05b4\u05dd)")
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
if st.button("\ud83d\udcd0 שרטט וחשב"):
    # ציור
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    # קיר
    ax.plot([0, wall_width], [0, 0], color='gray')
    ax.plot([0, wall_width], [wall_height, wall_height], color='gray')
    ax.plot([0, 0], [0, wall_height], color='gray')
    ax.plot([wall_width, wall_width], [0, wall_height], color='gray')

    current_x = side_margin + spacing
    total_perimeter = 0

    for i, (fw, fh) in enumerate(frames):
        y = top_margin
        ax.add_patch(plt.Rectangle((current_x, y), fw, fh, edgecolor='blue', facecolor='none', linewidth=2))
        ax.annotate(f"\u05e1\u05b4\u05dd {fw}", xy=(current_x + fw / 2, y + fh + 5), ha='center', fontsize=8, color='blue')
        ax.annotate(f"\u05e1\u05b4\u05dd {fh}", xy=(current_x - 10, y + fh / 2), rotation=90, va='center', fontsize=8, color='blue')
        if i < len(frames) - 1:
            ax.annotate(f"\u05e1\u05b4\u05dd {int(spacing)}", xy=(current_x + fw + spacing / 2, y + fh / 2), ha='center', fontsize=8, color='green')
        total_perimeter += 2 * (fw + fh)
        current_x += fw + spacing

    ax.annotate(f"\u05e1\u05b4\u05dd {top_margin}", xy=(5, top_margin / 2), rotation=90, va='center', fontsize=8, color='red')
    ax.annotate(f"\u05e1\u05b4\u05dd {side_margin}", xy=(side_margin / 2, wall_height - 5), ha='center', fontsize=8, color='red')
    ax.annotate(f"\u05e1\u05b4\u05dd {side_margin}", xy=(wall_width - side_margin / 2, wall_height - 5), ha='center', fontsize=8, color='red')

    st.pyplot(fig)

    # סיכום טקסטואלי
    st.subheader("\ud83d\udccb סיכום כמויות:")
    for idx, (fw, fh) in enumerate(frames):
        perim = 2 * (fw + fh)
        st.write(f"\ud83d\udd39 מסגרת {idx+1}: היקף ס\u05b4\u05dd {perim}")
    st.write(f"\ud83e\uddee סך הכול היקף: ס\u05b4\u05dd {total_perimeter}")

    section_length_cm = 290
    required_sections = math.ceil(total_perimeter / section_length_cm)
    st.write(f"\ud83e\ude9a נדרש: {required_sections} מקטעי קרניז (כל מקטע באורך 2.90 מ׳)")

    def create_pdf():
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont('David', 14)
        x_right = 500
        y = 800

        c.drawRightString(x_right, y, "דו\"ח תכנון קרניזים")
        y -= 25
        c.drawRightString(x_right, y, f"רוחב קיר: {wall_width} ס\"מ    גובה קיר: {wall_height} ס\"מ")
        y -= 30

        for idx, (fw, fh) in enumerate(frames):
            perim = 2 * (fw + fh)
            c.drawRightString(x_right, y, f"מסגרת {idx+1}: רוחב {fw} ס\"מ, גובה {fh} ס\"מ, היקף כולל {perim} ס\"מ")
            y -= 22

        y -= 10
        c.drawRightString(x_right, y, f"סה\"כ היקף: {total_perimeter} ס\"מ")
        y -= 20
        c.drawRightString(x_right, y, f"סה\"כ מקטעי קרניז נדרשים: {required_sections} (באורך 2.90 מטר)")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf()
    st.download_button("\ud83d\udcc4 הורד PDF עם הסיכום", data=pdf_buffer, file_name="cornice_summary.pdf", mime="application/pdf")
