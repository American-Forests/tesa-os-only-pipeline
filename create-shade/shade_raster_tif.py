import os
import glob
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine
from osgeo import gdal, ogr, osr
import time


def log(message):
    """Print messages with ✅ identifier."""
    print(f"✅ {message}")


def mask_raster_for_zero_values(input_raster, output_raster):
    """Create a new raster where only 0 values are retained, others set to NoData."""
    start_time = time.time()

    with rasterio.open(input_raster) as src:
        data = src.read(1)
        profile = src.profile

        # Mask everything except 0 values
        masked_data = np.where(data == 0, 0, profile["nodata"])
        profile.update(dtype=rasterio.float32, crs="EPSG:3857")  # Explicitly set CRS

        with rasterio.open(output_raster, "w", **profile) as dst:
            dst.write(masked_data, 1)

    elapsed_time = time.time() - start_time
    log(
        f"Step 1 - Masking raster for {os.path.basename(input_raster)} completed in {elapsed_time:.2f}s → {output_raster}"
    )
    return output_raster, elapsed_time


def resample_raster(input_raster, output_raster, target_resolution=0.3048):
    """Resample the raster to a target resolution of 1ft (0.3048 meters)."""
    start_time = time.time()

    with rasterio.open(input_raster) as src:
        # ORIGINAL pixel size in meters
        original_x_res, original_y_res = src.res

        # Compute correct scaling factors
        scale_x = target_resolution / original_x_res  # 1ft / original resolution
        scale_y = target_resolution / original_y_res  # 1ft / original resolution

        # Calculate the new dimensions
        new_width = int(src.width * (original_x_res / target_resolution))
        new_height = int(src.height * (original_y_res / target_resolution))

        # Create the new affine transform (dividing instead of multiplying)
        new_transform = src.transform * Affine.scale(scale_x, scale_y)

        # Update raster profile for new resolution
        profile = src.profile.copy()
        profile.update(
            transform=new_transform,
            height=new_height,
            width=new_width,
            dtype=rasterio.float32,
            compress="lzw",  # Optional compression
            crs="EPSG:3857",  # Explicitly set CRS
        )

        # Perform resampling
        data = src.read(
            out_shape=(src.count, new_height, new_width),
            resampling=Resampling.bilinear,  # Better for continuous data
        )

        with rasterio.open(output_raster, "w", **profile) as dst:
            dst.write(data)

    elapsed_time = time.time() - start_time
    log(
        f"Step 2 - Resampled {os.path.basename(input_raster)} to 1ft resolution ({target_resolution}m) in {elapsed_time:.2f}s → {output_raster}"
    )
    return output_raster, elapsed_time


def raster_to_vector(input_raster, output_shapefile):
    """Convert raster to vector while excluding NoData values and setting correct projection."""
    start_time = time.time()

    # Open raster
    src_ds = gdal.Open(input_raster)
    src_band = src_ds.GetRasterBand(1)

    # Read raster as an array
    raster_array = src_band.ReadAsArray()

    # Create a binary mask where value = 0
    mask = np.where(raster_array == 0, 1, 0).astype(np.uint8)

    # Create in-memory raster
    driver = gdal.GetDriverByName("MEM")
    mem_ds = driver.Create("", src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
    mem_ds.SetGeoTransform(src_ds.GetGeoTransform())  # Preserve georeferencing
    mem_ds.SetProjection(src_ds.GetProjection())  # Preserve projection

    # Write mask to the new raster band
    mem_band = mem_ds.GetRasterBand(1)
    mem_band.WriteArray(mask)
    mem_band.SetNoDataValue(0)  # Set no-data value for cleaner output
    mem_band.FlushCache()

    # Create output vector
    shp_driver = ogr.GetDriverByName("ESRI Shapefile")
    out_ds = shp_driver.CreateDataSource(output_shapefile)

    # Assign spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3857)  # ✅ Assign EPSG:3857 (Web Mercator)

    out_layer = out_ds.CreateLayer(
        "raster_to_polygon", geom_type=ogr.wkbPolygon, srs=srs
    )  # ✅ Set spatial reference

    # Add attribute field
    field_defn = ogr.FieldDefn("Value", ogr.OFTInteger)
    out_layer.CreateField(field_defn)

    # Convert masked raster to vector
    gdal.Polygonize(mem_band, None, out_layer, 0, [], callback=None)

    # Cleanup
    out_ds = None  # Close vector file
    mem_ds = None  # Close in-memory raster

    elapsed_time = time.time() - start_time
    log(
        f"Step 3 - Vectorizing raster (only value=0) for {os.path.basename(input_raster)} completed in {elapsed_time:.2f}s → {output_shapefile}"
    )
    return output_shapefile, elapsed_time


def process_raster_folder(input_folder, output_folder):
    """Process all .tif files in the input folder and log execution time."""
    total_start_time = time.time()

    os.makedirs(output_folder, exist_ok=True)
    tif_files = glob.glob(os.path.join(input_folder, "*.tif"))

    log(f"Processing {len(tif_files)} raster files in folder: {input_folder}")

    total_mask_time = 0
    total_resample_time = 0
    total_vector_time = 0

    for tif_file in tif_files:
        base_filename = os.path.splitext(os.path.basename(tif_file))[0]

        # Step 1: Mask raster for 0 values
        masked_raster = os.path.join(output_folder, f"{base_filename}_masked.tif")
        masked_raster, mask_time = mask_raster_for_zero_values(tif_file, masked_raster)
        total_mask_time += mask_time

        # Step 2: Resample to 1ft resolution
        resampled_raster = os.path.join(output_folder, f"{base_filename}_resampled.tif")
        resampled_raster, resample_time = resample_raster(
            masked_raster, resampled_raster
        )
        total_resample_time += resample_time

        # Step 3: Convert raster to vector (polygon shapefile)
        vector_file = os.path.join(output_folder, f"{base_filename}_vector.shp")
        vector_file, vector_time = raster_to_vector(resampled_raster, vector_file)
        total_vector_time += vector_time

    total_elapsed_time = time.time() - total_start_time

    # Log summary
    log("\n===== PROCESSING SUMMARY =====")
    log(f"Total files processed: {len(tif_files)}")
    log(f"Total masking time: {total_mask_time:.2f} seconds")
    log(f"Total resampling time: {total_resample_time:.2f} seconds")
    log(f"Total vector conversion time: {total_vector_time:.2f} seconds")
    log(f"Total elapsed time: {total_elapsed_time:.2f} seconds")


input_folder = "/Volumes/Work/Github/Python/ecs_ec2_create_tree_layer_from_base_landcover/shade-project/chunked"
output_folder = "/Volumes/Work/Github/Python/ecs_ec2_create_tree_layer_from_base_landcover/shade-project/processed"
process_raster_folder(input_folder, output_folder)
