import json
import geopandas as gpd
import os
import time
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import Resampling
from osgeo import gdal


print("0 Loading function ===")


def calculate_run_time(base_time, task_name):
    elapsed_time = time.time() - base_time
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"{task_name} Time: {int(minutes)} minutes {seconds} seconds")


def handler(event, context):
    # create tree layer from landcover file
    """
    Parameters
    cfg: the config file for the TESA location config object
    """

    cfg = event["cfg"]
    start_time = time.time()

    try:
        # creating tree data
        print("1 Subsetting trees from landcover ===")
        full_landcover_path = os.path.join(
            cfg.get("LANDCOVER_FOLDER"), cfg.get("landcover_path")
        )
        canopy_classes = cfg.get("landcover").get("canopy_cols")
        numbers = [i.split("_")[1] for i in canopy_classes]
        numbers = [int(num) for num in numbers]  # Convert to integers for comparison

        with rasterio.open(full_landcover_path) as src:
            landcover_data = src.read(1)  # Read the first band

        # Perform the conditional operation
        trees_data = np.where(np.isin(landcover_data, numbers), 1, 0)

        # Write the result back to a new raster
        trees_path = os.path.join(cfg.get("PROCESSED"), "trees.tif")
        with rasterio.open(
            trees_path,
            "w",
            driver="GTiff",
            height=landcover_data.shape[0],
            width=landcover_data.shape[1],
            count=1,
            dtype=str(trees_data.dtype),
            crs=src.crs,
            transform=src.transform,
        ) as dst:
            dst.write(trees_data, 1)

        calculate_run_time(start_time, "Creating tree data")

        # clip trees to study area
        print("2 Clipping trees to study area ===")
        study_area = gpd.read_file(os.path.join(cfg.get("FINAL"), "study_area.shp"))
        study_area = [json.loads(study_area.to_json())["features"][0]["geometry"]]

        with rasterio.open(trees_path) as src:
            out_image, out_transform = mask(src, study_area, crop=True)
            out_meta = src.meta

        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

        clipped_trees = os.path.join(cfg.get("FINAL"), "trees_clipped.tif")

        with rasterio.open(clipped_trees, "w", **out_meta) as dest:
            dest.write(out_image)

        calculate_run_time(time.time(), "Clipping trees to study area")

        # resample to necessary resolution based on unit (ex: 1m)
        print("3 Resampling trees ===")
        trees_resampled = os.path.join(cfg.get("PROCESSED"), "trees_resampled.tif")

        with rasterio.open(clipped_trees) as src:
            data = src.read(
                out_shape=(
                    src.count,
                    int(src.height * cfg.get("raster_resolution")),
                    int(src.width * cfg.get("raster_resolution")),
                ),
                resampling=Resampling.nearest,
            )

            transform = src.transform * src.transform.scale(
                (src.width / data.shape[-1]), (src.height / data.shape[-2])
            )

        with rasterio.open(
            trees_resampled,
            "w",
            driver="GTiff",
            height=data.shape[1],
            width=data.shape[2],
            count=1,
            dtype=str(data.dtype),
            crs=src.crs,
            transform=transform,
        ) as dst:
            dst.write(data)

        calculate_run_time(time.time(), "Resampling trees")

        # create vector file
        print("4 Converting trees to vector ===")
        final_file = os.path.join(cfg.get("FINAL"), "trees.shp")

        gdal.UseExceptions()
        src_ds = gdal.Open(trees_resampled)
        band = src_ds.GetRasterBand(1)
        band.SetNoDataValue(0)
        gdal.Polygonize(band, None, final_file, -1, [], callback=None)

        calculate_run_time(time.time(), "Converting trees to vector")

        # reproject to 4326
        print("5 Reprojecting trees ===")
        trees = gpd.read_file(final_file).to_crs("EPSG:4326")
        trees.to_file(final_file)
        calculate_run_time(time.time(), "Reprojecting trees")

        print("6 Done ===")
        calculate_run_time(start_time, "Total")

        return {
            "statusCode": 200,
            "status": "true",
            "message": "Trees created successfully",
        }
    except Exception as e:
        print(f"Error: {e}")
        raise e


# call the function
cfg = {
    "LANDCOVER_FOLDER": "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/wa_state/raw/landcover",
    "landcover_path": "WA_land_53069_Wahkiakum.tif",
    "PROCESSED": "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/wa_state/processed",
    "FINAL": "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/wa_state/final",
    "raster_resolution": 1,
    "landcover": {"canopy_cols": ["canopy_1", "canopy_2", "canopy_3"]},
}

event = {"cfg": cfg}

handler(event, None)
