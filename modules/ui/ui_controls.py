import streamlit as st
from modules.geometry.unit_builder import latlon_to_xy

def get_unit_inputs():
    x0 = st.sidebar.number_input("Top X (Longitude)", value=st.session_state.get("x0", -4.031), format="%.5f", step=0.00001)
    y0 = st.sidebar.number_input("Top Y (Latitude)", value=st.session_state.get("y0", 53.0405), format="%.5f", step=0.00001)
    z0 = st.sidebar.number_input("Top Z (Altitude)", value=st.session_state.get("z0", 1000))
    strike = st.sidebar.slider("Strike (°)", 0, 360, value=st.session_state.get("strike", 0))
    dip = st.sidebar.slider("Dip (°)", 0, 90, value=st.session_state.get("dip", 10))
    thickness = st.sidebar.number_input("Thickness (m)", value=st.session_state.get("thickness", 200.0))
    name = st.sidebar.text_input("Unit Name", value=st.session_state.get("name", "Demo Unit"))

    color_options = {
        "Red": "#ff7c7c", "Orange": "#FFbc7c", "Yellow": "#FFda7c", "Green": "#B9FF84",
        "Teal": "#76FFD8", "Blue": "#8FC7FF", "Indigo": "#D293FF", "Purple": "#FF81FF",
        "Pink": "#FD95C9", "Brown": "#A47661", "Gray": "#A5AFB9", "Black": "#000000",
        "White": "#FFFFFF", "Gold": "#F4C95D", "Cyan": "#D2FFFF"
    }

    color_name = st.sidebar.selectbox("Unit Color", options=list(color_options.keys()), index=0)
    color = color_options[color_name]

    return {
        "anchor_point": (y0, x0, z0),
        "strike": strike,
        "dip": dip,
        "thickness": thickness,
        "name": name,
        "color": color
    }

def render_region_inputs():
    min_x = st.number_input("Min Longitude", value=-4.0310, format="%.5f", step=0.00001)
    max_x = st.number_input("Max Longitude", value=-4.03, format="%.5f", step=0.00001)
    min_y = st.number_input("Min Latitude", value=53.04, format="%.5f", step=0.00001)
    max_y = st.number_input("Max Latitude", value=53.041, format="%.5f", step=0.00001)
    min_alt = st.number_input("Min Elevation (m)", value=0)

    ref_lat = (min_y + max_y) / 2
    ref_lon = (min_x + max_x) / 2

    x_min, y_min = latlon_to_xy(min_y, min_x, ref_lat, ref_lon)
    x_max, y_max = latlon_to_xy(max_y, max_x, ref_lat, ref_lon)

    x_range = abs(x_max - x_min)
    y_range = abs(y_max - y_min)
    z_range = max(x_range, y_range)

    max_alt = min_alt + z_range

    return {
        "lat": (min_y, max_y),
        "lon": (min_x, max_x),
        "alt": (min_alt, max_alt)
    }
