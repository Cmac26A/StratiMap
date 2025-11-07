import numpy as np
from shapely.geometry import Polygon, Point
from modules.geometry.unit_builder import latlon_to_xy

def resolve_unit_at_point(x, y, z, units, lat0, lon0):
    for unit in reversed(units):  # newest unit has priority
        if contains_point_in_unit(x, y, z, unit, lat0, lon0):
            return unit["name"]
    return None

def get_unit_color_map(units):
    return {unit["name"]: unit["color"] for unit in units}

def contains_point_in_unit(x, y, z, unit, lat0, lon0):
    corners = unit.get("geometry", [])
    if len(corners) != 8:
        return False

    # Convert top and bottom corners to projected x/y
    top_xy = [latlon_to_xy(lat, lon, lat0, lon0) for lat, lon, _ in corners[:4]]
    bottom_xy = [latlon_to_xy(lat, lon, lat0, lon0) for lat, lon, _ in corners[4:]]
    top_z = [pt[2] for pt in corners[:4]]
    bottom_z = [pt[2] for pt in corners[4:]]

    # Create horizontal footprint polygon
    polygon = Polygon(top_xy)
    point = Point(x, y)
    if not polygon.contains(point):
        return False

    # Interpolate top and bottom surface elevations at (x, y)
    z_top = interpolate_plane_z(top_xy, top_z, x, y)
    z_bot = interpolate_plane_z(bottom_xy, bottom_z, x, y)

    if z_bot is None or z_top is None:
        return False

    return z_bot <= z <= z_top

def interpolate_plane_z(xy_points, z_values, x, y):
    """
    Fit a plane to the given 4 corner points and evaluate z at (x, y).
    Assumes xy_points are in projected coordinates.
    """
    if len(xy_points) != 4 or len(z_values) != 4:
        return None

    xs, ys = zip(*xy_points)
    zs = z_values

    A = np.vstack([xs, ys, np.ones(4)]).T
    coeffs, _, _, _ = np.linalg.lstsq(A, zs, rcond=None)
    a, b, c = coeffs

    return a * x + b * y + c
