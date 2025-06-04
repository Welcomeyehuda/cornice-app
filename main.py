import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="תכנון קרניזים", layout="centered")

st.title("🧱 תכנון קרניזים לפי קיר")
st.write("הזן את מידות הקיר ומסגרות הקרניז שתרצה")

# קלט מידות קיר
wall_width = st.number_input("רוחב הקיר (בס״מ)", min_value=50, step=1)
wall_height = st.number_input("גובה הקיר (בס״מ)", min_value=50, step=1)

# מספר מסגרות
frame_count = st.number_input("כמה מסגרות תרצה?", min_value=1, step=1)

# נתוני המסגרות
frames = []
st.subheader("מידות כל מסגרת (בס״מ)")
for i in range(int(frame_count)):
    col1, col2 = st.columns(2)
    with col1:
        fw = st.number_input(f"רוחב מסגרת {i+1}", key=f"fw_{i}", min_value=10, step=1)
    with col2:
        fh = st.number_input(f"גובה מסגרת {i+1}", key=f"fh_{i}", min_value=10, step=1)
    frames.append((fw, fh))

# כפתור שרטוט
if st.button("📐 שרטט"):
    fig, ax = plt.subplots()
    ax.set_xlim(0, wall_width)
    ax.set_ylim(0, wall_height)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    margin = 10
    total_width = sum(f[0] for f in frames) + margin * (len(frames) + 1)
    start_x = (wall_width - total_width) / 2
    y = wall_height / 3

    for fw, fh in frames:
        ax.add_patch(plt.Rectangle((start_x, y), fw, fh, edgecolor='blue', facecolor='none', linewidth=2))
        start_x += fw + margin

    st.pyplot(fig)
