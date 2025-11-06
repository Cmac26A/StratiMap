import streamlit as st
import plotly.graph_objects as go

def render_units(units, region_bounds, return_fig=False):
    fig = go.Figure()

    for unit in units:
        corners = unit["geometry"]
        lats, lons, alts = zip(*corners)

        x = list(lons)
        y = list(lats)
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
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=unit["color"],
            opacity=1,
            name=unit["name"]
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Longitude", range=list(region_bounds["lon"])),
            yaxis=dict(title="Latitude", range=list(region_bounds["lat"])),
            zaxis=dict(title="Elevation (m)", range=list(region_bounds["alt"])),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    if return_fig:
        return fig
    else:
        st.plotly_chart(fig, use_container_width=True)
