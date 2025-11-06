import numpy as np

EARTH_RADIUS = 6371000  # meters

def latlon_to_xy(lat, lon, ref_lat, ref_lon):
    x = (lon - ref_lon) * np.cos(np.radians(ref_lat)) * EARTH_RADIUS
    y = (lat - ref_lat) * EARTH_RADIUS
    return x, y

def xy_to_latlon(x, y, ref_lat, ref_lon):
    lat = y / EARTH_RADIUS + ref_lat
    lon = x / (np.cos(np.radians(ref_lat)) * EARTH_RADIUS) + ref_lon
    return lat, lon

def create_unit(params, region_bounds):
    lat0, lon0, alt0 = params["anchor_point"]
    strike = np.radians(params["strike"])
    dip = np.radians(params["dip"])
    thickness = params["thickness"]

    x_min, y_min = latlon_to_xy(region_bounds["lat"][0], region_bounds["lon"][0], lat0, lon0)
    x_max, y_max = latlon_to_xy(region_bounds["lat"][1], region_bounds["lon"][1], lat0, lon0)

    n_x = np.sin(dip) * np.cos(strike)
    n_y = np.sin(dip) * np.sin(strike)
    n_z = np.cos(dip)
    normal = np.array([n_x, n_y, n_z])

    region_corners = [
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ]

    top_points = []
    bottom_points = []

    for x, y in region_corners:
        z_top = alt0 - (n_x * x + n_y * y) / n_z
        z_bot = z_top - (thickness / n_z)

        lat_top, lon_top = xy_to_latlon(x, y, lat0, lon0)
        lat_bot, lon_bot = xy_to_latlon(x, y, lat0, lon0)

        top_points.append((lat_top, lon_top, z_top))
        bottom_points.append((lat_bot, lon_bot, z_bot))

    corners = top_points + bottom_points

    return {
        "name": params["name"],
        "color": params["color"],
        "geometry": corners
    }

from shapely.geometry import Polygon, Point

def contains_point_in_unit(x, y, z, unit):
    corners = unit.get("geometry", [])
    if len(corners) != 8:
        return False  # malformed unit

    # Extract top surface polygon (first 4 points)
    top_xy = [(latlon_to_xy(lat, lon, corners[0][0], corners[0][1])) for lat, lon, _ in corners[:4]]
    top_z = [pt[2] for pt in corners[:4]]
    bottom_z = [pt[2] for pt in corners[4:]]

    z_top = np.mean(top_z)
    z_bot = np.mean(bottom_z)

    # Check vertical bounds
    if not (z_bot <= z <= z_top):
        return False

    # Check horizontal footprint
    polygon = Polygon(top_xy)
    point = Point(x, y)
    return polygon.contains(point)
