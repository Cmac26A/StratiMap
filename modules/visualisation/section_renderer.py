import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from shapely.geometry import Polygon, Point

from modules.core.section_utils import resolve_unit_at_point, get_unit_color_map
from modules.geometry.unit_builder import latlon_to_xy, xy_to_latlon

EARTH_RADIUS = 6371000  # meters

def generate_grid(region_bounds, z_step=10, x_points=100, y_points=100):
    lat0 = np.mean(region_bounds["lat"])
    lon0 = np.mean(region_bounds["lon"])
    x_min, y_min = latlon_to_xy(region_bounds["lat"][0], region_bounds["lon"][0], lat0, lon0)
    x_max, y_max = latlon_to_xy(region_bounds["lat"][1], region_bounds["lon"][1], lat0, lon0)

    x_vals = np.linspace(x_min, x_max, x_points)
    y_vals = np.linspace(y_min, y_max, y_points)
    z_vals = np.arange(region_bounds["alt"][0], region_bounds["alt"][1], z_step)

    grid = [(x, y, z) for z in z_vals for y in y_vals for x in x_vals]
    return grid, lat0, lon0

def slice_at_z(grid, z_target, units, lat0, lon0):
    slice_points = []
    for x, y, z in grid:
        if abs(z - z_target) <= 5:  # tolerance
            unit_name = resolve_unit_at_point(x, y, z, units, lat0, lon0)
            slice_points.append((x, y, unit_name))
    return slice_points


def plot_horizontal_section(slice_points, lat0, lon0, units):
    name_to_color = get_unit_color_map(units)
    xs, ys, colors = [], [], []

    for x, y, name in slice_points:
        lat, lon = xy_to_latlon(x, y, lat0, lon0)
        xs.append(lon)
        ys.append(lat)
        colors.append(name_to_color.get(name, "#ffffff"))  # white for blank

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(xs, ys, c=colors, s=40, edgecolors='none',marker='s')
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Horizontal Section")
    ax.grid(True)
    st.pyplot(fig)
