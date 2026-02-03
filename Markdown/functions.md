FUNCTIONS.md
StratiMap — Function & Module Reference
A complete reference of all functions across the StratiMap codebase, organized by module.
This document describes:

Function purpose

Parameters

Returns

Dependencies (internal + external)

Notes on usage within the app

1. stratimap.py (Main App)
This file orchestrates the entire Streamlit application.
It does not define standalone functions, but it calls functions from all other modules:

Imported functions
slice_from_dem — section_renderer

fetch_dem, load_dem, plot_dem_contour — topo_loader

get_unit_inputs, render_region_inputs — ui_controls

create_unit — unit_builder

render_units — unit_renderer

UnitManager — unit_manager

resolve_unit_at_point, get_unit_color_map — section_utils

generate_grid, slice_at_z, plot_horizontal_section — section_renderer

generate_borehole_log, plot_borehole_log — borehole_renderer

Notes
Manages Streamlit session state

Handles UI layout

Coordinates DEM fetching, unit creation, rendering, slicing, borehole generation

No functions to document here

2. core/section_utils.py
resolve_unit_at_point(x, y, z, units, ref_lat, ref_lon)
Determines which unit contains a given 3D point.

Parameters:

x, y, z — point in local coordinates

units — list of unit dictionaries

ref_lat, ref_lon — reference for XY projection

Returns:

unit_name or None

Dependencies:

contains_point_in_unit

latlon_to_xy (indirectly via unit geometry)

get_unit_color_map(units)
Builds a mapping from unit names → hex colors.

Returns:  
{name: color}

contains_point_in_unit(x, y, z, unit, ref_lat, ref_lon)
Checks whether a point lies inside a unit volume.

Returns:  
True / False

Dependencies:

Polygon, Point (shapely)

interpolate_plane_z

interpolate_plane_z(xy_points, z_values, x, y)
Fits a plane to 4 corner points and evaluates z at (x,y).

Returns:  
float z or None

3. core/topo_loader.py
fetch_dem(region_bounds, api_key, demtype="SRTMGL1", filename="dem.tif")
Fetches a DEM tile from OpenTopography and saves it locally.

Returns:  
filename (string)

Dependencies:

requests

OpenTopography API

load_dem(filepath, x_points=100, y_points=100)
Loads a GeoTIFF DEM and resamples it to a regular grid.

Returns:  
(x_new, y_new, dem_resampled)

Dependencies:

rasterio

griddata (SciPy)

plot_dem_contour(lons, lats, dem)
Creates a Plotly contour map of DEM elevation.

Returns:  
plotly.graph_objects.Figure

4. core/unit_manager.py
add_unit(unit_params)
Adds a new unit to the internal list.

get_units()
Returns list of all units.

get_unit(index)
Returns a single unit.

update_unit(index, new_params)
Replaces a unit.

delete_unit(index)
Deletes a unit by index.

reset()
Clears all units.

get_all_units()
Alias for get_units().

get_unit_color(unit_id)
Returns color for a unit by ID.

get_bounds()
Computes bounding box of all unit geometries.

5. geometry/unit_builder.py
latlon_to_xy(lat, lon, ref_lat, ref_lon)
Converts lat/lon to local XY meters using equirectangular projection.

xy_to_latlon(x, y, ref_lat, ref_lon)
Inverse of the above.

create_unit(params, region_bounds)
Constructs a stratigraphic unit as two planes (top & bottom), each with 4 corners.

Returns:  
A unit dictionary:

Code
{
  "name": ...,
  "color": ...,
  "geometry": [(lat, lon, z), ... 8 points]
}
Dependencies:

latlon_to_xy

xy_to_latlon

plane geometry math

contains_point_in_unit(...)
Duplicate of section_utils version (not used by main app).

_interpolate_plane_z(...)
Plane fitting helper.

6. ui/ui_controls.py
get_unit_inputs()
Streamlit sidebar UI for defining a unit.

Returns:  
A parameter dictionary:

Code
{
  "anchor_point": (lat, lon, z),
  "strike": ...,
  "dip": ...,
  "thickness": ...,
  "name": ...,
  "color": ...
}
render_region_inputs()
UI for selecting region bounds.

Returns:

Code
{
  "lat": (min, max),
  "lon": (min, max),
  "alt": (min, max)
}
7. visualisation/borehole_renderer.py
generate_borehole_log(lat, lon, region_bounds, units, z_step=10)
Samples unit membership vertically at a fixed lat/lon.

Returns:  
List of (z, unit_name) tuples.

plot_borehole_log(log, units, section_marker=None)
Plots a vertical borehole log using matplotlib.

8. visualisation/section_renderer.py
generate_grid(region_bounds, z_step=10, x_points=200, y_points=200)
Generates a 3D grid of (x,y,z) points.

Returns:  
grid, lat0, lon0

slice_at_z(grid, z_target, units, lat0, lon0)
Extracts unit membership at a specific elevation.

Returns:  
List of (x, y, unit_name).

slice_from_dem(lons, lats, dem, units, lat0, lon0)
Same as above but uses DEM elevation instead of fixed z.

plot_horizontal_section(slice_points, lat0, lon0, units, borehole_marker=None)
Plots a horizontal slice as a colored grid.

Returns:  
(fig, ax)

9. visualisation/surface_renderer.py
build_unit_id_grid(slice_points, nx, ny, units)
Converts slice points into a categorical ID grid.

Returns:  
unit_id_grid, colorscale

plot_3d_surface(lons, lats, dem, unit_id_grid, colorscale)
Renders a 3D surface with unit colors draped over DEM.

Returns:  
Plotly figure.

10. visualisation/topo_renderer.py
plot_units_with_topo(lons, lats, dem, units, interval=50)
Overlays unit membership on DEM with contour lines.

Returns:  
Plotly figure.

11. visualisation/unit_renderer.py
render_units(units, region_bounds, return_fig=False)
Renders all units as 3D Mesh3D blocks.

Returns:

If return_fig=True: Plotly figure

Otherwise: renders directly in Streamlit

Architecture Summary
Core pipeline
Unit creation → create_unit

Unit storage → UnitManager

Coordinate transforms → latlon_to_xy, xy_to_latlon

DEM loading → fetch_dem, load_dem

Slicing → slice_at_z, slice_from_dem

Unit resolution → resolve_unit_at_point

Rendering → render_units, plot_horizontal_section, plot_3d_surface

Boreholes → generate_borehole_log, plot_borehole_log