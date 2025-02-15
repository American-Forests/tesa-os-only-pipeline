import os
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping
import geopandas as gpd
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def validate_projection(tif_crs, shp_crs):
    """Validate that the projections match."""
    if tif_crs != shp_crs:
        raise ValueError(
            "CRS mismatch between TIF file and shapefile. Ensure they have the same projection."
        )


def chunk_and_mask_tif(tif_path, shapefile_path, output_folder):
    """
    Mask and chunk the TIF file based on the shapefile boundaries.
    Save output files in the specified output folder.
    """
    # Read shapefile
    logging.info(f"Reading shapefile: {shapefile_path}")
    study_area = gpd.read_file(shapefile_path)

    # Ensure that the shapefile has a CRS
    if study_area.crs is None:
        raise ValueError("Shapefile does not have a CRS defined.")

    study_area_crs = study_area.crs
    logging.info(f"SHP CRS: {study_area_crs}")

    with rasterio.open(tif_path) as tif_src:
        tif_crs = tif_src.crs
        logging.info(f"TIF CRS: {tif_crs}")

        # Validate projections
        validate_projection(tif_crs, study_area_crs)

        # Reproject study area to match TIF CRS if necessary
        if study_area_crs != tif_crs:
            logging.info("Reprojecting shapefile to match TIF CRS.")
            study_area = study_area.to_crs(tif_crs)

        # Get TIF boundary as a shapely geometry
        tif_bounds = tif_src.bounds
        tif_bbox = box(*tif_bounds)

        # Create a GeoDataFrame of the TIF bounds
        tif_bbox_gdf = gpd.GeoDataFrame({"geometry": [tif_bbox]}, crs=tif_crs)

        # Select only polygons that intersect with the TIF boundary
        study_area = gpd.overlay(study_area, tif_bbox_gdf, how="intersection")

        if study_area.empty:
            raise ValueError("No overlapping areas between shapefile and TIF boundary.")

        # Prepare geometries for masking
        shapes = [mapping(geom) for geom in study_area.geometry]

        # Generate output file name
        original_name = os.path.splitext(os.path.basename(tif_path))[0]
        output_path = os.path.join(
            output_folder, f"{original_name}_masked_blockgroups.tif"
        )

        # Apply mask
        logging.info(f"Masking and chunking TIF: {tif_path}")
        out_image, out_transform = mask(tif_src, shapes, crop=True)
        out_meta = tif_src.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "crs": tif_crs,
                "compress": "lzw",
            }
        )

        # Save the masked TIF
        logging.info(f"Saving masked TIF to: {output_path}")
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)

    return output_path


if __name__ == "__main__":
    # Configuration
    input_folder = "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/shade_index/Austin/1200/chunked"
    # shapefile_path = "wa_state/final/study_area.shp"
    shapefile_path = "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/shade_index/Austin/1200/for-chunker2/test2.shp"
    output_folder = "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/shade_index/Austin/1200/chunked"

    os.makedirs(output_folder, exist_ok=True)

    # Process each TIF in the input folder
    logging.info("Starting processing of TIF files.")
    for tif_file in os.listdir(input_folder):
        if tif_file.endswith(".tif"):
            tif_path = os.path.join(input_folder, tif_file)
            try:
                chunk_and_mask_tif(tif_path, shapefile_path, output_folder)
                logging.info(f"Processing complete for {tif_file}.")
            except ValueError as ve:
                logging.error(f"Skipping {tif_file}: {ve}")
            except Exception as e:
                logging.error(f"Unexpected error processing {tif_file}: {e}")
    logging.info("All processing complete.")
