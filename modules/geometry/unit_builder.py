import numpy as np
from shapely.geometry import Polygon, Point

EARTH_RADIUS = 6371000  # meters

def latlon_to_xy(lat, lon, ref_lat, ref_lon):
    """
    Convert lat/lon (degrees) to local XY (meters) using an equirectangular approximation
    referenced at (ref_lat, ref_lon). Includes degrees→radians and cos(ref_lat).
    """
    deg2rad = np.pi / 180.0
    x = (lon - ref_lon) * deg2rad * np.cos(np.radians(ref_lat)) * EARTH_RADIUS
    y = (lat - ref_lat) * deg2rad * EARTH_RADIUS
    return x, y

def xy_to_latlon(x, y, ref_lat, ref_lon):
    """
    Convert local XY (meters) back to lat/lon (degrees) using the inverse of the
    equirectangular approximation referenced at (ref_lat, ref_lon).
    """
    rad2deg = 180.0 / np.pi
    lat = (y / EARTH_RADIUS) * rad2deg + ref_lat
    lon = (x / (np.cos(np.radians(ref_lat)) * EARTH_RADIUS)) * rad2deg + ref_lon
    return lat, lon

def create_unit(params, region_bounds):
    """
    Build a stratigraphic unit as two planes (top and bottom), each defined by
    4 corner points in lat/lon/z. Plane orientation is set by strike/dip and anchored
    at params['anchor_point'] = (lat0, lon0, alt0).
    """
    lat0, lon0, alt0 = params["anchor_point"]
    strike = np.radians(params["strike"])
    dip = np.radians(params["dip"])
    thickness = params["thickness"]

    # Project the lat/lon bounds to XY (meters) using the anchor as reference
    x_min, y_min = latlon_to_xy(region_bounds["lat"][0], region_bounds["lon"][0], lat0, lon0)
    x_max, y_max = latlon_to_xy(region_bounds["lat"][1], region_bounds["lon"][1], lat0, lon0)

    # Plane normal components in local coordinates
    n_x = np.sin(dip) * np.cos(strike)
    n_y = np.sin(dip) * np.sin(strike)
    n_z = np.cos(dip)

    # Rectangle corners (top surface footprint in XY)
    region_corners = [
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ]

    top_points = []
    bottom_points = []

    # Evaluate top/bottom z at each corner, then convert back to lat/lon+z triples
    for x, y in region_corners:
        # Top plane passes through (lat0, lon0, alt0) and follows the normal
        z_top = alt0 - (n_x * x + n_y * y) / n_z
        z_bot = z_top - (thickness / n_z)

        lat_top, lon_top = xy_to_latlon(x, y, lat0, lon0)
        lat_bot, lon_bot = xy_to_latlon(x, y, lat0, lon0)

        top_points.append((lat_top, lon_top, float(z_top)))
        bottom_points.append((lat_bot, lon_bot, float(z_bot)))

    corners = top_points + bottom_points

    return {
        "name": params["name"],
        "color": params["color"],
        "geometry": corners
    }

def contains_point_in_unit(x, y, z, unit, ref_lat, ref_lon):
    """
    Check if a point (x,y,z) lies within the unit volume.
    - Builds the top footprint polygon in XY.
    - Interpolates top/bottom planes to get z-bounds at (x,y).
    """
    corners = unit.get("geometry", [])
    if len(corners) != 8:
        return False

    # Convert stored lat/lon corners to XY relative to the same reference used to build units
    top_xy = [latlon_to_xy(lat, lon, ref_lat, ref_lon) for lat, lon, _ in corners[:4]]
    bottom_xy = [latlon_to_xy(lat, lon, ref_lat, ref_lon) for lat, lon, _ in corners[4:]]
    top_z = [pt[2] for pt in corners[:4]]
    bottom_z = [pt[2] for pt in corners[4:]]

    polygon = Polygon(top_xy)
    if not polygon.contains(Point(x, y)):
        return False

    # Plane-fit interpolation at (x,y)
    z_top = _interpolate_plane_z(top_xy, top_z, x, y)
    z_bot = _interpolate_plane_z(bottom_xy, bottom_z, x, y)

    if z_top is None or z_bot is None:
        return False

    return z_bot <= z <= z_top

def _interpolate_plane_z(xy_points, z_values, x, y):
    """
    Fit a plane to 4 corner points and evaluate z at (x,y).
    Assumes xy_points are in projected XY meters.
    """
    if len(xy_points) != 4 or len(z_values) != 4:
        return None

    xs, ys = zip(*xy_points)
    zs = z_values

    A = np.vstack([xs, ys, np.ones(4)]).T
    coeffs, _, _, _ = np.linalg.lstsq(A, zs, rcond=None)
    a, b, c = coeffs
    return float(a * x + b * y + c)
