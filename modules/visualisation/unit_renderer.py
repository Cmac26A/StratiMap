import streamlit as st
import plotly.graph_objects as go
import numpy as np
from modules.geometry.unit_builder import latlon_to_xy

def render_units(units, region_bounds, return_fig=False):
    # Reference point for projection
    ref_lat = (region_bounds["lat"][0] + region_bounds["lat"][1]) / 2
    ref_lon = (region_bounds["lon"][0] + region_bounds["lon"][1]) / 2

    fig = go.Figure()

    for unit in units:
        corners = unit.get("geometry", [])
        if len(corners) != 8:
            continue

        lats, lons, alts = zip(*corners)

        # Convert lat/lon to XY meters
        xs, ys = [], []
        for lat, lon in zip(lats, lons):
            x, y = latlon_to_xy(lat, lon, ref_lat, ref_lon)
            xs.append(x)
            ys.append(y)

        z = list(alts)

        faces = [
            (0, 1, 2), (0, 2, 3),  # top
            (4, 5, 6), (4, 6, 7),  # bottom
            (0, 1, 5), (0, 5, 4),  # side 1
            (1, 2, 6), (1, 6, 5),  # side 2
            (2, 3, 7), (2, 7, 6),  # side 3
            (3, 0, 4), (3, 4, 7)   # side 4
        ]
        i, j, k = zip(*faces)

        fig.add_trace(go.Mesh3d(
            x=xs, y=ys, z=z,
            i=i, j=j, k=k,
            color=unit["color"],
            opacity=1,
            name=unit["name"]
        ))

    # Compute extents in meters
    x_min, y_min = latlon_to_xy(region_bounds["lat"][0], region_bounds["lon"][0], ref_lat, ref_lon)
    x_max, y_max = latlon_to_xy(region_bounds["lat"][1], region_bounds["lon"][1], ref_lat, ref_lon)
    z_min, z_max = region_bounds["alt"]

    # Anchor trace to force bounded box
    fig.add_trace(go.Scatter3d(
        x=[x_min, x_max],
        y=[y_min, y_max],
        z=[z_min, z_max],
        mode="markers",
        marker=dict(size=0.1, color="rgba(0,0,0,0)"),
        showlegend=False
    ))

    # Normalised aspect ratio: anchor to longitude span
    dx = x_max - x_min
    dy = y_max - y_min
    dz = z_max - z_min

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title="Longitude",
                range=[x_min, x_max],
                tickvals=np.linspace(x_min, x_max, 5),
                ticktext=[f"{lon:.5f}" for lon in np.linspace(region_bounds["lon"][0], region_bounds["lon"][1], 5)]
            ),
            yaxis=dict(
                title="Latitude",
                range=[y_min, y_max],
                tickvals=np.linspace(y_min, y_max, 5),
                ticktext=[f"{lat:.5f}" for lat in np.linspace(region_bounds["lat"][0], region_bounds["lat"][1], 5)]
            ),
            zaxis=dict(title="Elevation (m)", range=[z_min, z_max]),
            aspectmode="manual",
            aspectratio=dict(
                x=1,
                y=dy / dx if dx != 0 else 1,
                z=dz / dx if dx != 0 else 1
            ),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    if return_fig:
        return fig
    else:
        st.plotly_chart(fig, use_container_width=True)
