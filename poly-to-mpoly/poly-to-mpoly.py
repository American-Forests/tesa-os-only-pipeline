import fiona
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
import sys
import os
import shutil


def copy_auxiliary_files(input_filepath, output_filepath):
    base_input = os.path.splitext(input_filepath)[0]
    base_output = os.path.splitext(output_filepath)[0]
    extensions = [".prj", ".cpg", ".sbx", ".sbn"]

    for ext in extensions:
        input_file = base_input + ext
        output_file = base_output + ext
        if os.path.exists(input_file):
            shutil.copy(input_file, output_file)


def convert_polygons_to_multipolygons(input_filepath, output_filepath):
    print("0 starting conversion...")
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_filepath)
    print(f"1 output_dir === {output_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the input shapefile
    with fiona.open(input_filepath, "r") as input_shp:
        print(f"2 input_filepath === {input_filepath}")
        # Define the schema for the output shapefile
        schema = input_shp.schema.copy()
        schema["geometry"] = "MultiPolygon"

        # Open the output shapefile
        with fiona.open(
            output_filepath,
            "w",
            driver=input_shp.driver,
            crs=input_shp.crs,
            schema=schema,
        ) as output_shp:
            print(f"3 output_filepath === {output_filepath}")
            print("4 converting polygons to multipolygons...")
            for feature in input_shp:
                geom = shape(feature["geometry"])
                if isinstance(geom, Polygon):
                    geom = MultiPolygon([geom])
                feature["geometry"] = mapping(geom)
                output_shp.write(
                    {
                        "geometry": feature["geometry"],
                        "properties": feature["properties"],
                    }
                )
                # Debugging statement to check the geometry type
                # print(f"converted geometry === {feature['geometry']['type']}")
            print("5 polygons converted to multipolygons...")

    # Copy auxiliary files
    copy_auxiliary_files(input_filepath, output_filepath)
    print(f"6 output saved === {output_filepath}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python poly-to-mpoly.py <input_filepath> <output_filepath>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    convert_polygons_to_multipolygons(input_filepath, output_filepath)
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    convert_to_mpoly(input_filepath, output_filepath)
