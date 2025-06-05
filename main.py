import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="תכנון קרניזים", layout="centered")
st.title("🎯 תכנון קרניזים אוטומטי עם מרווחים")

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
        fw = st.number_input(f"רוחב מסגרת {i+1}", key=f"fw_{i}", min_value=10, value=60)
    with col2:
        fh = st.number_input(f"גובה מסגרת {i+1}", key=f"fh_{i}", min_value=10, value=120)
    frames.append((fw, fh))

# כפתור שרטוט
if st.button("📐 שרטט"):
    # הגדרות מרווחים קבועים
    side_margin = 10  # ס״מ מימין ושמאל
    top_margin = 20   # ס״מ מהתקרה
    bottom_margin = 10  # נחשב בהמשך אוטומטית

    # שטח זמין לפריסה
    available_width = wall_width - 2 * side_margin
    total_frames_width = sum(f[0] for f in frames)
    spacing = (available_width - total_frames_width) / (len(frames) + 1)

    # ציור
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    # ציור קיר
    ax.plot([0, wall_width], [0, 0], color='gray')
    ax.plot([0, wall_width], [wall_height, wall_height], color='gray')
    ax.plot([0, 0], [0, wall_height], color='gray')
    ax.plot([wall_width, wall_width], [0, wall_height], color='gray')

    # ציור מסגרות + מידות
    current_x = side_margin + spacing
    for i, (fw, fh) in enumerate(frames):
        y = top_margin
        ax.add_patch(plt.Rectangle((current_x, y), fw, fh, edgecolor='blue', facecolor='none', linewidth=2))
        
        # מידת רוחב
        ax.annotate(f"{fw} ס״מ", xy=(current_x + fw / 2, y + fh + 5), ha='center', fontsize=8, color='blue')
        # מיקום בין מסגרות
        if i < len(frames) - 1:
            ax.annotate(f"{int(spacing)} ס״מ", xy=(current_x + fw + spacing / 2, y + fh / 2), ha='center', fontsize=8, color='green')

        current_x += fw + spacing

    # מידת גובה המסגרת הראשונה
    ax.annotate(f"{frames[0][1]} ס״מ", xy=(side_margin + spacing - 10, top_margin + frames[0][1] / 2),
                rotation=90, va='center', fontsize=8, color='blue')

    # רווח מהתקרה
    ax.annotate(f"{top_margin} ס״מ", xy=(5, top_margin / 2), rotation=90, va='center', fontsize=8, color='red')

    # רווח צדדים
    ax.annotate(f"{side_margin} ס״מ", xy=(side_margin / 2, wall_height - 5), ha='center', fontsize=8, color='red')
    ax.annotate(f"{side_margin} ס״מ", xy=(wall_width - side_margin / 2, wall_height - 5), ha='center', fontsize=8, color='red')

    st.pyplot(fig)
