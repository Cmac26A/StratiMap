import numpy as np
import plotly.graph_objects as go
from modules.geometry.unit_builder import latlon_to_xy
from modules.core.section_utils import resolve_unit_at_point, get_unit_color_map

def plot_units_with_topo(lons, lats, dem, units, interval=50):
    """
    Same methodology as 2D section:
    - For each DEM grid point, resolve unit at (x,y,z).
    - Build categorical grid of unit names.
    - Plot units with their defined colours.
    - Overlay topo contours (lines only).
    """

    # Build unit colour map
    unit_colors = get_unit_color_map(units)
    color_list = list(unit_colors.values())

    z_units = np.empty(dem.shape, dtype=object)

    # Traverse DEM grid
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            # Convert to local XY using the same utility as section plot
            x, y = latlon_to_xy(lat, lon, units[0]["geometry"][0][0], units[0]["geometry"][0][1])
            z = dem[i, j]
            unit_name = resolve_unit_at_point(x, y, z, units,
                                              units[0]["geometry"][0][0],
                                              units[0]["geometry"][0][1])
            z_units[i, j] = unit_name

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=z_units,
        x=lons,
        y=lats,
        colorscale=[[i/len(color_list), c] for i, c in enumerate(color_list)],
        showscale=False,
        name="Units"
    ))
    fig.add_trace(go.Contour(
        z=dem,
        x=lons,
        y=lats,
        colorscale="Greys",
        contours=dict(coloring="lines", showlabels=True,
                      start=np.nanmin(dem), end=np.nanmax(dem), size=interval),
        line=dict(width=1),
        name="Topo contours"
    ))
    fig.update_layout(
        xaxis=dict(scaleanchor="y", title="Longitude"),
        yaxis=dict(title="Latitude"),
        width=800, height=800
    )
    return fig