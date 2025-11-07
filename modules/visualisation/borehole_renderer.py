import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from modules.core.section_utils import resolve_unit_at_point, get_unit_color_map
from modules.geometry.unit_builder import latlon_to_xy

def generate_borehole_log(lat, lon, region_bounds, units, z_step=10):
    """
    Samples unit membership vertically at a fixed lat/lon location.
    Returns a list of (z, unit_name) tuples.
    """
    lat0 = np.mean(region_bounds["lat"])
    lon0 = np.mean(region_bounds["lon"])
    x, y = latlon_to_xy(lat, lon, lat0, lon0)

    z_vals = np.arange(region_bounds["alt"][0], region_bounds["alt"][1], z_step)
    log = []

    for z in z_vals:
        unit_name = resolve_unit_at_point(x, y, z, units, lat0, lon0)
        log.append((z, unit_name))

    return log

def plot_borehole_log(log, units):
    """
    Renders a vertical borehole log showing unit membership by elevation.
    """
    name_to_color = get_unit_color_map(units)
    zs = [z for z, _ in log]
    colors = [name_to_color.get(name, "#ffffff") for _, name in log]

    fig, ax = plt.subplots(figsize=(2, 6))
    for i in range(len(zs) - 1):
        ax.fill_betweenx([zs[i], zs[i+1]], 0, 1, color=colors[i])

    ax.set_ylim(min(zs), max(zs))
    ax.set_xlim(0, 1)
    ax.set_ylabel("Elevation (m)")
    ax.set_xticks([])
    ax.set_title("Artificial Borehole")
    st.pyplot(fig)
