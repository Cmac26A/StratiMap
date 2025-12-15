import numpy as np
from shapely.geometry import Polygon, Point
from modules.geometry.unit_builder import latlon_to_xy

def resolve_unit_at_point(x, y, z, units, ref_lat, ref_lon):
    """
    Return the topmost unit name containing (x,y,z), prioritizing newer units.
    """
    for unit in reversed(units):
        if contains_point_in_unit(x, y, z, unit, ref_lat, ref_lon):
            return unit["name"]
    return None

def get_unit_color_map(units):
    """
    Build a dict mapping unit names to colors.
    """
    return {unit["name"]: unit["color"] for unit in units}

def contains_point_in_unit(x, y, z, unit, ref_lat, ref_lon):
    """
    Check if a point (x,y,z) lies within the unit volume.
    """
    corners = unit.get("geometry", [])
    if len(corners) != 8:
        return False

    top_xy = [latlon_to_xy(lat, lon, ref_lat, ref_lon) for lat, lon, _ in corners[:4]]
    bottom_xy = [latlon_to_xy(lat, lon, ref_lat, ref_lon) for lat, lon, _ in corners[4:]]
    top_z = [pt[2] for pt in corners[:4]]
    bottom_z = [pt[2] for pt in corners[4:]]

    polygon = Polygon(top_xy)
    if not polygon.contains(Point(x, y)):
        return False

    z_top = interpolate_plane_z(top_xy, top_z, x, y)
    z_bot = interpolate_plane_z(bottom_xy, bottom_z, x, y)

    return z_bot is not None and z_top is not None and z_bot <= z <= z_top

def interpolate_plane_z(xy_points, z_values, x, y):
    """
    Fit a plane to 4 corner points and evaluate z at (x,y).
    """
    if len(xy_points) != 4 or len(z_values) != 4:
        return None

    xs, ys = zip(*xy_points)
    A = np.vstack([xs, ys, np.ones(len(xs))]).T
    coeffs, _, _, _ = np.linalg.lstsq(A, z_values, rcond=None)
    a, b, c = coeffs
    return float(a * x + b * y + c)
