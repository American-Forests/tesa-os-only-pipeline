
# 'reproject_shapefile.py' - a reprojection process script

This script reads a shapefile and reprojects it to the CRS you specify.

This file was written to deal with the very common problem you sometimes get when reprojecting in ArcGIS or PostgreSQL (which occassionally has a different projection definitions) and trying to read/compare/modify projections using GDAL etc. 

Example of error:
"
2024-12-14 11:06:37,029 - INFO - GDAL signalled an error: err_no=1, msg='PROJ: proj_identify: C:\\Program Files\\PostgreSQL\\13\\share\\contrib\\postgis-3.1\\proj\\proj.db lacks DA
TABASE.LAYOUT.VERSION.MAJOR / DATABASE.LAYOUT.VERSION.MINOR metadata. It comes from another PROJ installation.'
"

## Authors

asimmons-steffen


### Prerequisites

Make sure you have the following installed on your machine:
•	Python 3.6 or later
•	Conda (Anaconda or Miniconda)


### Script Structure

The script consists of the following main parts:
1.	Reads shapefile from input directory, and reprojects based on the CRS you specify


## Steps to Run Script

1.	Activate Your Environment: Ensure you're in the correct conda environment.
`conda activate os-only-gis`

2. Run the file with 'shapefile_path= <location of shapefile you need to reproj>' and 'target_crs = <EPSG code of the CRS desired>' and 'output_folder = <location of reprojected file>'.
`python reproject_shapefile.py`



