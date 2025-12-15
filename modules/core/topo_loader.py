import requests
import rasterio
import numpy as np
import plotly.graph_objects as go

def fetch_dem(region_bounds, api_key, demtype="SRTMGL1", filename="dem.tif"):
    """Fetch DEM tile from OpenTopography API and save locally."""
    url = (
        f"https://portal.opentopography.org/API/globaldem?"
        f"demtype={demtype}"
        f"&south={region_bounds['lat'][0]}"
        f"&north={region_bounds['lat'][1]}"
        f"&west={region_bounds['lon'][0]}"
        f"&east={region_bounds['lon'][1]}"
        f"&outputFormat=GTiff"
        f"&API_Key={api_key}"
    )
    r = requests.get(url)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)
    return filename

from scipy.interpolate import griddata

def load_dem(filepath, x_points=100, y_points=100):
    """Load DEM from GeoTIFF and resample to 100x100 grid."""
    with rasterio.open(filepath) as src:
        dem = src.read(1)
        transform = src.transform
        height, width = dem.shape

        # Build row/col indices
        rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
        xs, ys = rasterio.transform.xy(transform, rows, cols)
        xs = np.array(xs).reshape(dem.shape)
        ys = np.array(ys).reshape(dem.shape)

        # Flatten for interpolation
        points = np.column_stack((xs.flatten(), ys.flatten()))
        values = dem.flatten()

        # Target grid (100x100)
        x_new = np.linspace(xs.min(), xs.max(), x_points)
        y_new = np.linspace(ys.min(), ys.max(), y_points)
        xi, yi = np.meshgrid(x_new, y_new)

        # Interpolate DEM onto new grid
        dem_resampled = griddata(points, values, (xi, yi), method="linear")

        return x_new, y_new, dem_resampled

def plot_dem_contour(lons, lats, dem):
    fig = go.Figure(data=go.Contour(
        z=dem,
        x=lons,
        y=lats,
        colorscale="earth",
        contours=dict(
            coloring="fill",
            showlabels=True,
            start=np.nanmin(dem),
            end=np.nanmax(dem),
            size=50
        )
    ))

    # Preserve lon/lat continuity
    fig.update_layout(
        xaxis=dict(
            scaleanchor="y",   # lock x-axis scale to y-axis
            title="Longitude"
        ),
        yaxis=dict(
            title="Latitude"
        ),
        width=800,
        height=800   # square canvas
    )
    return fig
