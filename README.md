rasterize
=========

ArcGIS / Python: Area-weighted polygon to raster conversion. Cell values are calculated based on the amount of each polygon falling into each cell.

Requires:
- ArcGIS 10.0+
- NumPy 10.0+

Usage:
```python
from rasterize import rasterize

polygon = 'C:\polygon.shp'
field = 'TREECANOPY' # numeric fields only!
cellsize = 100
output_raster = 'C:\rasterized'
value_to_nodata=-9999.0 # optional parameter; -9999.0 by default

rasterize(polygon, field, cellsize, output_raster, value_to_nodata)
```
