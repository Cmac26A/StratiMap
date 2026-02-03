StratiMap — System Architecture Overview
StratiMap is a modular geological visualization and modelling system built around Streamlit.
Its architecture is organized into five major layers:

UI Layer (Streamlit interface)

Core Logic Layer (unit management, DEM handling, section utilities)

Geometry Layer (coordinate transforms + unit construction)

Rendering Layer (2D/3D visualization)

Application Orchestration (stratimap.py)

This document explains how these layers interact and how data flows through the system.

1. High‑Level Architecture Diagram
Code
                ┌────────────────────────────┐
                │        stratimap.py        │
                │  (Application Orchestrator)│
                └──────────────┬─────────────┘
                               │
                               ▼
        ┌────────────────────────────────────────────────┐
        │                    UI Layer                    │
        │  ui_controls.py  •  Streamlit widgets          │
        └──────────────┬─────────────────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────────────────┐
        │                 Core Logic Layer               │
        │  unit_manager.py                               │
        │  section_utils.py                              │
        │  topo_loader.py                                │
        └──────────────┬─────────────────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────────────────┐
        │                 Geometry Layer                  │
        │              unit_builder.py                    │
        │  (lat/lon ↔ XY, plane geometry, unit volumes)   │
        └──────────────┬─────────────────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────────────────────┐
        │                Rendering Layer                  │
        │  section_renderer.py                            │
        │  borehole_renderer.py                           │
        │  surface_renderer.py                            │
        │  topo_renderer.py                               │
        │  unit_renderer.py                               │
        └─────────────────────────────────────────────────┘
2. Data Flow Overview
2.1 Unit Creation Pipeline
User enters parameters in sidebar → get_unit_inputs()

Parameters passed to → create_unit()

create_unit() constructs:

top plane (4 corners)

bottom plane (4 corners)

full 3D geometry (8 points)

Unit stored in → UnitManager

Key dependencies:  
latlon_to_xy, xy_to_latlon, plane math, region bounds

2.2 DEM Pipeline
User fetches DEM → fetch_dem()

DEM loaded → load_dem()

DEM visualized → plot_dem_contour()

DEM used to generate geological map → slice_from_dem()

Key dependencies:  
OpenTopography API, rasterio, SciPy griddata

2.3 Slicing Pipeline (Horizontal Sections)
Grid generated → generate_grid()

Slice extracted → slice_at_z() or slice_from_dem()

Unit membership resolved → resolve_unit_at_point()

Slice visualized → plot_horizontal_section()

Key dependencies:  
contains_point_in_unit, shapely, coordinate transforms

2.4 Borehole Pipeline
User selects lat/lon

Borehole sampled vertically → generate_borehole_log()

Unit membership resolved at each depth

Log visualized → plot_borehole_log()

2.5 3D Rendering Pipeline
Units converted to XY → latlon_to_xy()

Mesh3D objects created → render_units()

Optional DEM draping → plot_3d_surface()

3. Module Responsibilities
3.1 UI Layer
ui_controls.py
Sidebar inputs for units

Region bounds selection

Converts user input → parameter dictionaries

3.2 Core Logic Layer
unit_manager.py
Stores units

CRUD operations

Computes bounding boxes

section_utils.py
Determines which unit contains a point

Plane interpolation

Color mapping

topo_loader.py
Fetches DEM

Loads and resamples DEM

Contour plotting

3.3 Geometry Layer
unit_builder.py
Converts lat/lon ↔ XY

Builds planar units

Computes top/bottom surfaces

Defines full 3D geometry

This is the mathematical backbone of the system.

3.4 Rendering Layer
section_renderer.py
Grid generation

Horizontal slicing

2D map visualization

borehole_renderer.py
Vertical sampling

Borehole log visualization

surface_renderer.py
DEM + unit ID grid

3D surface draping

topo_renderer.py
DEM + unit overlay

Contour lines

unit_renderer.py
3D Mesh3D rendering of units

4. Architectural Strengths
✓ Modular and clean
Each module has a single responsibility.

✓ Geometry and rendering are decoupled
Unit creation is independent of visualization.

✓ UI is thin
Streamlit only handles layout and user input.

✓ Extensible
Easy to add:

faults

folds

intrusive bodies

stochastic unit variations

machine learning inversion

5. Architectural Weaknesses / Opportunities
1. Duplicate logic
contains_point_in_unit exists in both:

section_utils.py

unit_builder.py

→ Should be unified.

2. Unit geometry is planar only
Future work will require:

fault offsets

fold curvature

unconformities

3. Region bounds are global
Better to encapsulate region bounds in a class.

4. No caching
DEM loading, slicing, and unit resolution could be cached for speed.

5. No separation between model and view
Streamlit code and logic intermingle in stratimap.py..

6. Recommended Refactor (Optional)
Introduce a GeologyModel class
Handles:

units

DEM

slicing

boreholes

Introduce a Renderer class
Handles:

2D maps

3D meshes

DEM overlays

Introduce a CoordinateSystem class
Handles:

lat/lon ↔ XY

reference points

projection consistency

7. Summary
StratiMap’s architecture is clean, modular, and well‑structured for a research prototype.
The separation between:

UI

core logic

geometry

rendering

…makes it easy to extend into a more advanced geological modelling system.