import streamlit as st
from modules.geometry.unit_builder import latlon_to_xy

def get_unit_inputs():
    """
    Sidebar inputs for defining a stratigraphic unit.
    """
    x0 = st.sidebar.number_input("Top X (Longitude)", value=st.session_state.get("x0", -4.0763), format="%.5f", step=0.00001)
    y0 = st.sidebar.number_input("Top Y (Latitude)", value=st.session_state.get("y0", 53.0685), format="%.5f", step=0.00001)
    z0 = st.sidebar.number_input("Top Z (Altitude)", value=st.session_state.get("z0", 1085))
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

    return {
        "anchor_point": (y0, x0, z0),
        "strike": strike,
        "dip": dip,
        "thickness": thickness,
        "name": name,
        "color": color_options[color_name]
    }

def render_region_inputs():
    """
    Sidebar inputs for region bounds.
    Defaults to a ~7 km x ~7 km box around Snowdon summit with vertical limits 0–1500 m.
    """
    lat_center, lon_center = 53.0685, -4.0763
    lat_half_span, lon_half_span = 0.0315, 0.0525  # ~7 km box

    min_x = st.number_input("Min Longitude", value=lon_center - lon_half_span, format="%.5f", step=0.00001)
    max_x = st.number_input("Max Longitude", value=lon_center + lon_half_span, format="%.5f", step=0.00001)
    min_y = st.number_input("Min Latitude", value=lat_center - lat_half_span, format="%.5f", step=0.00001)
    max_y = st.number_input("Max Latitude", value=lat_center + lat_half_span, format="%.5f", step=0.00001)
    min_alt = st.number_input("Min Elevation (m)", value=0)
    max_alt = st.number_input("Max Elevation (m)", value=1500)

    ref_lat, ref_lon = (min_y + max_y) / 2, (min_x + max_x) / 2
    x_min, y_min = latlon_to_xy(min_y, min_x, ref_lat, ref_lon)
    x_max, y_max = latlon_to_xy(max_y, max_x, ref_lat, ref_lon)

    

    return {"lat": (min_y, max_y), "lon": (min_x, max_x), "alt": (min_alt, max_alt)}
