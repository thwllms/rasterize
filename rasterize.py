# rasterize.py
# --------------------
# ArcGIS version: 10.0
# Python version: 2.6.5
# NumPy version: 1.3.0
# ---------------------
# Converts a polygon feature class to raster. Resulting cell values are
# area-weighted.

import arcpy
import numpy


def rasterize(polygon, field, cellsize, output_raster,
              value_to_nodata=-9999.0):

    # Determine geographic extent
    desc = arcpy.Describe(polygon)
    extent = desc.extent
    xmin = extent.XMin
    xmax = extent.XMax
    ymin = extent.YMin
    ymax = extent.YMax
    lowerleft = arcpy.Point(xmin, ymin)

    # Create empty numpy array
    width = int((xmax - xmin) / cellsize) + 1
    height = int((ymax - ymin) / cellsize) + 1
    array_int = numpy.zeros((height, width), 'uint32')
    value = 1

    # Increment array values by 1 at each cell. This way when we convert to
    # polygons, the shape of each individual cell is preserved. The arcpy
    # RasterToPolygon tool lumps adjacent cells together into single
    # polygons if they have the same value. We don't want that; we have to 
    # trick arcpy.
    for row in range(0, array_int.shape[0]):
        for col in range(0, array_int.shape[1]):
            array_int[row][col] = value
            value += 1

    # Convert numpy array to raster
    raster_int = arcpy.NumPyArrayToRaster(array_int, lowerleft,
                                          cellsize, cellsize)
    # Convert raster to polygon
    polygrid = 'in_memory/polygrid'
    arcpy.RasterToPolygon_conversion(raster_int, polygrid,
                                     'NO_SIMPLIFY', 'VALUE')
    # Intersect
    intersected = 'in_memory/intersected'
    arcpy.Intersect_analysis([polygrid, polygon], intersected)

    # Calculate area-weighted values at each cell.
    # Loop through the "intersected" layer and increment values in a numpy
    # array. Since arcpy doesn't recognize masked numpy arrays, we need to
    # build our own version of a mask. The "mask" array keeps track of which
    # cells need to be masked or unmasked. After the calculations take place,
    # all remaining "masked" cells are set to NoData.
    array = numpy.zeros((height, width), 'float32')
    mask = numpy.zeros((height, width), 'bool')
    sc = arcpy.SearchCursor(intersected)
    for featrow in sc:
        gridID = featrow.getValue('FID_polygrid') - 1
        value = featrow.getValue(field)
        value_weighted = value * (featrow.shape.area / cellsize**2)
        row = gridID // width
        col = gridID % width
        array[row][col] += value_weighted
        mask[row][col] = 1 # if a cell value is incremented, unmask the cell.

    # Set all masked cells to NoData
    for row in range(0, array.shape[0]):
        for col in range(0, array.shape[1]):
            if mask[row][col] == 0:
                array[row][col] = value_to_nodata

    output = arcpy.NumPyArrayToRaster(array, lowerleft, cellsize, cellsize,
                                      value_to_nodata)
    output.save(output_raster)

    # Cleanup
    arcpy.Delete_management(polygrid)
    arcpy.Delete_management(intersected)

if __name__ == "__main__":

    # ArcToolbox interface
    polygonFeatureClass = arcpy.GetParameterAsText(0)
    fieldName = arcpy.GetParameterAsText(1)
    cellsize = arcpy.GetParameterAsText(2)
    outputRaster = arcpy.GetParameterAsText(3)

    rasterize(polygonFeatureClass, fieldName, float(cellsize), outputRaster)
