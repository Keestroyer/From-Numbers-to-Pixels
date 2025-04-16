import streamlit as st
import subprocess

st.set_page_config(page_title="Pygame Games in Streamlit", layout="wide")

st.title("🎮 Streamlit Game Hub")

tabs = st.tabs(["Fractals", "Optimization and Pathfinding","Vectors",'Probability'])

game_files = ["fractals.py", "optimization.py","vector.py","crit_hit.py"]

for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"Play Game {i+1}")
        if st.button(f"Launch Game {i+1}"):
            subprocess.Popen(["python", game_files[i]])
            st.info("Game is launching in a new window!")
