import numpy as np
import plotly.graph_objects as go
from modules.core.section_utils import get_unit_color_map

def build_unit_id_grid(slice_points, nx, ny, units):
    """
    slice_points: list of (x, y, unit_name)
    Returns:
        unit_id_grid: (ny, nx) integer grid
        colorscale: list for Plotly mapping IDs -> hex colours
    """
    # 1. Map unit names to integer IDs
    unit_names = [u["name"] for u in units]
    name_to_id = {name: i for i, name in enumerate(unit_names)}

    # 2. Map names to hex colours
    name_to_color = get_unit_color_map(units)

    # 3. Flat list of IDs
    ids = [name_to_id.get(name, -1) for (_, _, name) in slice_points]
    unit_id_grid = np.array(ids).reshape((ny, nx))

    # 4. Build colorscale (normalized 0–1)
    n = len(unit_names)
    colorscale = []
    if n > 1:
        for name, idx in name_to_id.items():
            t = idx / (n - 1)
            colorscale.append([t, name_to_color[name]])
    else:
        # single unit edge case
        only_name = unit_names[0]
        colorscale = [
            [0.0, name_to_color[only_name]],
            [1.0, name_to_color[only_name]],
        ]

    return unit_id_grid, colorscale

def plot_3d_surface(lons, lats, dem, unit_id_grid, colorscale):
    fig = go.Figure(
        data=[
            go.Surface(
                x=lons,
                y=lats,
                z=dem,
                surfacecolor=unit_id_grid,
                colorscale=colorscale,
                cmin=np.nanmin(unit_id_grid),
                cmax=np.nanmax(unit_id_grid),
                showscale=False,
            )
        ]
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            zaxis_title="Elevation (m)",
            
        ),
        height=800,
    )

    return fig

