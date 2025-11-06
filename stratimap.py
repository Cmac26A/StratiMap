import streamlit as st
import numpy as np
from modules.ui.ui_controls import get_unit_inputs, render_region_inputs
from modules.geometry.unit_builder import create_unit
from modules.visualisation.unit_renderer import render_units
from modules.core.unit_manager import UnitManager

# Initialize session state
if "unit_manager" not in st.session_state:
    st.session_state.unit_manager = UnitManager()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "region_bounds" not in st.session_state:
    st.session_state.region_bounds = None

st.set_page_config(layout="wide")

st.image("images/snowdon.jpeg", width="stretch")

# Main area: Region bounding box inputs
st.title("StratiMap Version 1.1.1")#

st.markdown("""

Created by C.J. McAteer 2025            
            """)
st.subheader("Region Configuration")
region_bounds = render_region_inputs()
st.session_state.region_bounds = region_bounds
st.subheader("3D Unit Visualisation")

# Sidebar: Unit editing and creation
st.sidebar.header("Input new geological unit")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffd9f1;
        }
    </style>
""", unsafe_allow_html=True)


saved_units = st.session_state.unit_manager.get_units()
unit_names = [unit["name"] for unit in saved_units]
selected_name = st.sidebar.selectbox("Edit Existing Unit", ["None"] + unit_names)

# Load selected unit into session state
if selected_name != "None":
    st.session_state.edit_index = unit_names.index(selected_name)
    selected_unit = saved_units[st.session_state.edit_index]

    st.session_state["x0"] = selected_unit["anchor_point"][1]
    st.session_state["y0"] = selected_unit["anchor_point"][0]
    st.session_state["z0"] = selected_unit["anchor_point"][2]
    st.session_state["strike"] = selected_unit["strike"]
    st.session_state["dip"] = selected_unit["dip"]
    st.session_state["thickness"] = selected_unit["thickness"]
    st.session_state["name"] = selected_unit["name"]
    st.session_state["color"] = selected_unit["color"]
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

# Render all saved units + current preview
render_list = [create_unit(u, st.session_state.region_bounds) for u in st.session_state.unit_manager.get_units()]
render_list.append(unit_preview)  # Always show current preview
render_units(render_list, st.session_state.region_bounds)

# Sidebar: Color preview
st.sidebar.markdown("### Saved Units")
for i, saved in enumerate(saved_units):
    st.sidebar.color_picker(f"{saved['name']}", saved["color"], key=f"color_{i}")


from modules.ui.topo_controls import get_topo_controls
from modules.geometry.topo_loader import get_elevation_grid
from modules.visualisation.topo_renderer import render_contours

spacing, generate = get_topo_controls()

if generate:
    with st.spinner("Querying elevation and generating contours..."):
        topo_data = get_elevation_grid(st.session_state.region_bounds)


        st.write("Elevation range:",
         "min =", np.min(topo_data["elevation"]),
         "max =", np.max(topo_data["elevation"]),
         "mean =", np.mean(topo_data["elevation"]))

        render_contours(topo_data, st.session_state.region_bounds, spacing)
