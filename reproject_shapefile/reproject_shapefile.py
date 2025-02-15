import os
import logging
import geopandas as gpd
from rasterio.crs import CRS

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def reproject_shapefile(shapefile_path, target_crs, output_path):
    """
    Reproject a shapefile to the specified target CRS.

    Parameters:
        shapefile_path (str): Path to the input shapefile.
        target_crs (str or CRS): The CRS to reproject to.
        output_path (str): Path to save the reprojected shapefile.
    """
    logging.info(f"Reading shapefile: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)

    logging.info(f"Current shapefile CRS: {gdf.crs}")
    logging.info(f"Target CRS: {target_crs}")

    # Reproject the shapefile
    gdf_reprojected = gdf.to_crs(target_crs)

    # Save the reprojected shapefile
    logging.info(f"Saving reprojected shapefile to: {output_path}")
    gdf_reprojected.to_file(output_path, driver="ESRI Shapefile")


if __name__ == "__main__":
    shapefile_path = "Y:/CommunityReLeaf\TreeEquityScore/tesa_fake_data/shade_index/Austin/1200/snippet-for-chunker-final.shp"
    target_crs = "EPSG:3857"
    output_path = "Y:/CommunityReLeaf/TreeEquityScore/tesa_fake_data/shade_index/Austin/1200/for-chunker2/test.shp"

    # Ask user if reprojection should be performed
    print(f"The current shapefile CRS does not match the target CRS ({target_crs}).")
    user_input = (
        input("Would you like to reproject the shapefile? (y/n): ").strip().lower()
    )

    if user_input == "y":
        reproject_shapefile(shapefile_path, target_crs, output_path)
        print(f"Reprojected shapefile saved to {output_path}.")
    else:
        print("No changes were made.")
