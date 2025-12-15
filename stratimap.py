import streamlit as st
import numpy as np
from modules.ui.ui_controls import get_unit_inputs, render_region_inputs
from modules.geometry.unit_builder import create_unit, latlon_to_xy
from modules.visualisation.unit_renderer import render_units
from modules.core.unit_manager import UnitManager
from modules.core.section_utils import resolve_unit_at_point, get_unit_color_map
from modules.visualisation.section_renderer import generate_grid, slice_at_z, plot_horizontal_section
from modules.visualisation.borehole_renderer import generate_borehole_log, plot_borehole_log

# Initialize session state
if "unit_manager" not in st.session_state:
    st.session_state.unit_manager = UnitManager()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "region_bounds" not in st.session_state:
    st.session_state.region_bounds = None

st.set_page_config(layout="wide")
st.image("images/snowdon.jpeg", width="stretch")

st.title("StratiMap Version 1.1.1")
st.markdown("Created by C.J. McAteer 2025")

# Sidebar: Unit editing and creation
st.sidebar.header("Input new geological unit")
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffd9f1;
        }
    </style>
""", unsafe_allow_html=True)

region_bounds = render_region_inputs()
st.session_state.region_bounds = region_bounds

saved_units = st.session_state.unit_manager.get_units()
unit_names = [unit["name"] for unit in saved_units]
selected_name = st.sidebar.selectbox("Edit Existing Unit", ["None"] + unit_names)

# Load selected unit into session state
if selected_name != "None":
    st.session_state.edit_index = unit_names.index(selected_name)
    selected_unit = saved_units[st.session_state.edit_index]
    for key, val in zip(
        ["x0", "y0", "z0", "strike", "dip", "thickness", "name", "color"],
        [selected_unit["anchor_point"][1], selected_unit["anchor_point"][0], selected_unit["anchor_point"][2],
         selected_unit["strike"], selected_unit["dip"], selected_unit["thickness"],
         selected_unit["name"], selected_unit["color"]]):
        st.session_state[key] = val
else:
    st.session_state.edit_index = None

# Get current unit parameters from sidebar
unit_params = get_unit_inputs()
unit_preview = create_unit(unit_params, st.session_state.region_bounds)

# Save or update unit
if st.sidebar.button("Save Unit"):
    if st.session_state.edit_index is not None:
        st.session_state.unit_manager.update_unit(st.session_state.edit_index, unit_params)
    else:
        st.session_state.unit_manager.add_unit(unit_params)
    st.session_state.edit_index = None

# Delete selected unit
if st.session_state.edit_index is not None:
    if st.sidebar.button("Delete This Unit"):
        st.session_state.unit_manager.delete_unit(st.session_state.edit_index)
        st.session_state.edit_index = None

# Reset all units
if st.sidebar.button("Reset All Units"):
    st.session_state.unit_manager = UnitManager()
    st.session_state.edit_index = None

# Sidebar: Color preview
st.sidebar.markdown("### Saved Units")
for i, saved in enumerate(saved_units):
    st.sidebar.color_picker(f"{saved['name']}", saved["color"], key=f"color_{i}")

# Create layout columns
col_main, col_borehole = st.columns([3, 1])

with col_main:
    st.subheader("3D Unit Visualisation")
    render_list = [create_unit(u, st.session_state.region_bounds) for u in st.session_state.unit_manager.get_units()]
    render_list.append(unit_preview)
    render_units(render_list, st.session_state.region_bounds)

    st.subheader("Horizontal Section Viewer")
    units = [create_unit(u, st.session_state.region_bounds) for u in saved_units]
    grid, lat0, lon0 = generate_grid(region_bounds)

    z_value = st.slider("Select Elevation (m)", min_value=int(region_bounds["alt"][0]), max_value=int(region_bounds["alt"][1]), step=10)

    if st.button("Generate Horizontal Section"):
        st.session_state.slice_points = slice_at_z(grid, z_value, units, lat0, lon0)
        st.session_state.z_value = z_value

    if "slice_points" in st.session_state:
        plot_horizontal_section(
            st.session_state.slice_points,
            lat0, lon0, units,
            borehole_marker=(st.session_state.get("bore_lat"), st.session_state.get("bore_lon"))
        )




with col_borehole:
    st.subheader("Artificial Borehole Tool")

    lat_min, lat_max = region_bounds["lat"]
    lon_min, lon_max = region_bounds["lon"]

    bore_lat = st.slider("Borehole Latitude", min_value=float(lat_min), max_value=float(lat_max),
                         value=float((lat_min + lat_max) / 2), step=1e-6, format="%.6f")
    bore_lon = st.slider("Borehole Longitude", min_value=float(lon_min), max_value=float(lon_max),
                         value=float((lon_min + lon_max) / 2), step=1e-6, format="%.6f")

    if st.button("Generate Borehole Log"):
        st.session_state.borehole_log = generate_borehole_log(bore_lat, bore_lon, region_bounds, units)
        st.session_state.bore_lat = bore_lat
        st.session_state.bore_lon = bore_lon

    if "borehole_log" in st.session_state:
        plot_borehole_log(
            st.session_state.borehole_log,
            units,
            section_marker=st.session_state.get("z_value")
        )


