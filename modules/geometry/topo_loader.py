import numpy as np
import requests
from scipy.interpolate import griddata
import streamlit as st

def get_elevation_grid(region_bounds, resolution=100, coarse_res=99):
    lat_min, lat_max = region_bounds["lat"]
    lon_min, lon_max = region_bounds["lon"]

    # Fine grid for interpolation
    lats = np.linspace(lat_min, lat_max, resolution)
    lons = np.linspace(lon_min, lon_max, resolution)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Coarse grid for API sampling
    lats_coarse = np.linspace(lat_min, lat_max, coarse_res)
    lons_coarse = np.linspace(lon_min, lon_max, coarse_res)
    lonc, latc = np.meshgrid(lons_coarse, lats_coarse)

    coords = [{"latitude": float(lat), "longitude": float(lon)} for lat, lon in zip(latc.ravel(), lonc.ravel())]

    elevations = []
    for i in range(0, len(coords), 100):
        chunk = coords[i:i+100]
        response = requests.post("https://api.open-elevation.com/api/v1/lookup", json={"locations": chunk})
        try:
            results = response.json()["results"]
            elevations.extend([pt["elevation"] for pt in results])
        except:
            elevations.extend([0] * len(chunk))

    zz_coarse = np.array(elevations).reshape(lonc.shape)
    zz_interp = griddata((lonc.ravel(), latc.ravel()), zz_coarse.ravel(), (lon_grid, lat_grid), method='cubic')



    return {
        "lat_grid": lat_grid,
        "lon_grid": lon_grid,
        "elevation": np.nan_to_num(zz_interp, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float64)
    }

