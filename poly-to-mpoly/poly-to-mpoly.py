import shapefile
from shapely.geometry import shape, MultiPolygon, Polygon
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


def convert_to_mpoly(input_filepath, output_filepath):
    # Read the input shapefile with specified encoding
    print(f"input_filepath: {input_filepath}")
    reader = shapefile.Reader(input_filepath, encoding="latin1")
    fields = reader.fields[1:]  # skip the deletion flag field
    field_names = [field[0] for field in fields]

    # Prepare the writer for the output shapefile
    print(f"output_filepath: {output_filepath}")
    writer = shapefile.Writer(output_filepath)
    writer.fields = reader.fields

    print("Converting polygons to multipolygons...")
    for sr in reader.shapeRecords():
        geom = shape(sr.shape.__geo_interface__)
        if isinstance(geom, Polygon):
            geom = MultiPolygon([geom])
        writer.shape(geom)
        writer.record(*[sr.record[field] for field in field_names])

    print("Conversion complete!")
    writer.close()

    # Copy auxiliary files
    copy_auxiliary_files(input_filepath, output_filepath)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python poly-to-mpoly.py <input_filepath> <output_filepath>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    convert_to_mpoly(input_filepath, output_filepath)