
# 'poly-to-mpoly' - a fix-it script for tes blockgroup and muncipalities files

This script converts every geom to a mpoly (even if it is a polygon) so that it can pass the data tests.


## Authors

asimmons-steffen

## How to run

1) Use the 'OS-only-GIS' conda env (make sure you have pyshp)
2) run `python poly-to-mpoly.py <input_filepath> <output_filepath>` 
3) ex: `python poly-to-mpoly.py Y:\CommunityReLeaf\TreeEquityScore\tes_fake_data\nationaL_2023\aws_s3\municipalities_simplified.shp Y:\CommunityReLeaf\TreeEquityScore\tes_fake_data\nationaL_2023\poly_to_mpoly_test\municipalities_simplified_MPOLY_OUTPUT.shp'` 
