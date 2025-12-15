import streamlit as st
import numpy as np
import os 

from modules.visualisation.section_renderer import slice_from_dem
from modules.core.topo_loader import fetch_dem, load_dem, plot_dem_contour
from modules.ui.ui_controls import get_unit_inputs, render_region_inputs
from modules.geometry.unit_builder import create_unit
from modules.visualisation.unit_renderer import render_units
from modules.core.unit_manager import UnitManager
from modules.core.section_utils import resolve_unit_at_point, get_unit_color_map
from modules.visualisation.section_renderer import generate_grid, slice_at_z, plot_horizontal_section
from modules.visualisation.borehole_renderer import generate_borehole_log, plot_borehole_log


# -------------------------------
# Session state initialization
# -------------------------------
if "unit_manager" not in st.session_state:
    st.session_state.unit_manager = UnitManager()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "region_bounds" not in st.session_state:
    st.session_state.region_bounds = None

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(layout="wide")
st.image("images/snowdon.jpeg", use_column_width=True)

st.title("StratiMap Version 1.1.4")
st.markdown("Created by C.J. McAteer 2025")

# -------------------------------
# Sidebar styling
# -------------------------------
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffd9f1;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Region bounds (Snowdon defaults)
# -------------------------------
region_bounds = render_region_inputs()
st.session_state.region_bounds = region_bounds

# -------------------------------
# Sidebar: Unit editing and creation
# -------------------------------
st.sidebar.header("Input new geological unit")

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

# -------------------------------
# Layout columns
# -------------------------------
col_main, col_borehole = st.columns([3, 1])

# -------------------------------
# Main column: 3D + horizontal sections
# -------------------------------
with col_main:
    st.subheader("3D Unit Visualisation")
    render_list = [create_unit(u, st.session_state.region_bounds) for u in st.session_state.unit_manager.get_units()]
    render_list.append(unit_preview)
    render_units(render_list, st.session_state.region_bounds)

    st.subheader("Horizontal Section Viewer")
    units = [create_unit(u, st.session_state.region_bounds) for u in saved_units]
    grid, lat0, lon0 = generate_grid(region_bounds)

    z_value = st.slider(
        "Select Elevation (m)",
        min_value=int(region_bounds["alt"][0]),
        max_value=int(region_bounds["alt"][1]),
        step=10
    )

    if st.button("Generate Horizontal Section"):
        st.session_state.slice_points = slice_at_z(grid, z_value, units, lat0, lon0)
        st.session_state.z_value = z_value

    if "slice_points" in st.session_state:
        fig, ax = plot_horizontal_section(
            st.session_state.slice_points,
            lat0, lon0, units,
            borehole_marker=(st.session_state.get("bore_lat"), st.session_state.get("bore_lon"))
        )
        st.pyplot(fig)   # show here
        

# -------------------------------
# Borehole column
# -------------------------------
with col_borehole:
    st.subheader("Artificial Borehole Tool")

    lat_min, lat_max = region_bounds["lat"]
    lon_min, lon_max = region_bounds["lon"]

    bore_lat = st.slider(
        "Borehole Latitude",
        min_value=float(lat_min), max_value=float(lat_max),
        value=float((lat_min + lat_max) / 2),
        step=1e-6, format="%.6f"
    )
    bore_lon = st.slider(
        "Borehole Longitude",
        min_value=float(lon_min), max_value=float(lon_max),
        value=float((lon_min + lon_max) / 2),
        step=1e-6, format="%.6f"
    )

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

API_KEY = "22010917bbd6f57d868e52ea3c8b4dbf"
# Sidebar inputs → dynamic region bounds




DEM_FILE = "dem.tif"

# Button 1: Fetch DEM
if st.button("Fetch Topography"):
    try:
        dem_file = fetch_dem(region_bounds, API_KEY, demtype="SRTMGL1", filename=DEM_FILE)
        st.session_state["dem_file"] = dem_file
        st.success(f"DEM fetched and saved to {dem_file}")
    except Exception as e:
        st.error(f"Failed to fetch DEM: {e}")

# Button 2: Generate Topography
if st.button("Show Existing Topography"):
    if os.path.exists(DEM_FILE):
        lons, lats, dem = load_dem(DEM_FILE)
        st.session_state["lons"] = lons
        st.session_state["lats"] = lats
        st.session_state["dem"] = dem

        fig = plot_dem_contour(lons, lats, dem)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No DEM file found. Please fetch topography first.")

# Button 3: Generate DEM Section
if st.button("Unit intersection with topography"):
    import numpy as np
    import rasterio

    # Check if DEM is already in session_state
    if "lons" in st.session_state and "lats" in st.session_state and "dem" in st.session_state:
        lons = st.session_state["lons"]
        lats = st.session_state["lats"]
        dem = st.session_state["dem"]

    else:
        # Fallback: load DEM from disk
        DEM_FILE = "dem.tif"   # adjust to your filename/path
        with rasterio.open(DEM_FILE) as src:
            dem = src.read(1)
            lons = np.linspace(src.bounds.left, src.bounds.right, src.width)
            lats = np.linspace(src.bounds.bottom, src.bounds.top, src.height)

        # Store back into session_state for reuse
        st.session_state["lons"] = lons
        st.session_state["lats"] = lats
        st.session_state["dem"] = dem
        st.info("DEM reloaded from disk.")

    # Build slice points from DEM
    slice_points_dem = slice_from_dem(lons, lats, dem, units, lat0, lon0)
    st.session_state["slice_points_dem"] = slice_points_dem

    # Get base horizontal section figure
    fig, ax = plot_horizontal_section(
        slice_points_dem,
        lat0, lon0, units,
        borehole_marker=(st.session_state.get("bore_lat"), st.session_state.get("bore_lon"))
    )


    # Overlay DEM contours at multiples of 100 m
    max_elev = np.nanmax(dem)
    contour_levels = np.arange(0, max_elev + 100, 100)  # 0, 100, 200, ...
    contours = ax.contour(
        lons, lats, dem,
        levels=contour_levels,
        colors="black",
        linewidths=0.5,
        alpha=0.6
    )


    # Label the contours
    ax.clabel(
        contours,
        inline=True,          # labels sit nicely on the line
        fontsize=8,           # adjust text size
        fmt="%d m"            # format labels, e.g. "100 m"
    )

    lat_min, lat_max = region_bounds["lat"]
    lon_min, lon_max = region_bounds["lon"]

    ax.autoscale(False)  # lock limits
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_title("Forward modelled geological map")
    
    # Show combined figure
    st.pyplot(fig)


st.markdown("---")

st.markdown(
    """
    Instructions:
    
    StratiMap is a tool currently capable of forward modelling the trace of geological units on topography maps. To create your own model, follow these steps:
    1. **Define Region Bounds**: Use the region input controls to set the latitude, longitude, and altitude bounds for your area of interest.
    2. **Input Geological Units**: In the sidebar, select lithology, color and structural parameters for each unit and then save your units.
    3. **Section and Borehole tool**: Use these tools to view a horizontal slice or generate a synthetic borehole log through your model.
    4. **Fetch Topography**: Use the 'Fetch Topography' button to download DEM data for your region.
    5. **Show Existing Topography**: Load and visualize the DEM data as contours.
    6. **Unit Intersection with Topography**: Generate a geological, showing your inputted units intersecting the topography.

    Compare your model an existing geological map and try your best to reproduce the geology of the area.
    
    
    """)
