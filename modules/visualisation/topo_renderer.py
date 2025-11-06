import streamlit as st
import plotly.graph_objects as go
import numpy as np 

def render_contours(topo_data, region_bounds, spacing):
    fig = go.Figure()

    fig.add_trace(go.Contour(
    z=topo_data["elevation"],
    x=topo_data["lon_grid"][0],     # longitude axis
    y=topo_data["lat_grid"][:, 0],  # latitude axis
    contours=dict(
        coloring="lines",
        showlabels=True,
        start=np.min(topo_data["elevation"]),
        end=np.max(topo_data["elevation"]),
        size=spacing
    ),
    line=dict(width=1, color="black"),
    showscale=False
))


    fig.update_layout(
        title="Topographic Contours",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        margin=dict(l=0, r=0, t=30, b=0),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
