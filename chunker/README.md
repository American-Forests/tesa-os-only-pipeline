
# 'chunker' - a TIFF resizing process script

This script reads a shapefile (and checks the crs against the tiff file *note: you MUST be in the same crs*) and creates a mask tiff based on the shapefile. Then it masks the tiff.


## Authors

asimmons-steffen

## Deployment

### Prerequisites

Make sure you have the following installed on your machine:
•	Python 3.6 or later
•	Conda (Anaconda or Miniconda)


### Script Structure

The script consists of the following main parts:
1.	Reads shapefile from input directory, and ALL tiff files from the 'input_folder'
2.	Compares the crs of the tiff and the shapefile (if they are NOT the same script will terminate - use the reproj script to fix this)
3.	Creates mask
4.	'Chunks' tiff file (i.e. applies mask to tiff and saves it to an output folder)


### Setting Up the environment

* Install Required Packages (should be part of the environment.yml in the base folder of this repo)
Make sure you have the following Python libraries installed:
```
•	geopandas
•	rasterio
•	rasterio-mask
•	shapely
•	geopandas
•	logging
```

## Steps to Run Script

1.	Activate Your Environment: Ensure you're in the correct conda environment.
`conda activate os-only-gis`

2. Run the file with 'shapefile_path= <location of shapefile to mask by>' and 'input_folder = <location of tiff files>' and 'output_folder = <location of output tiff's>'.
`python chunker.py`



