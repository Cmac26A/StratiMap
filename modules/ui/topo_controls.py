import streamlit as st

def get_topo_controls():
    st.subheader("Topography")
    spacing = st.number_input("Contour Interval (m)", value=100, step=10)
    generate = st.button("Generate Contour Plot")
    return spacing, generate
