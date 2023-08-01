import os
from pyproj import Transformer
import numpy as np
import cartopy.io.img_tiles as cimgt
import matplotlib as mpl
import geopandas as gpd
import cartopy.crs as ccrs


constants_path = os.path.realpath(__file__)
SRC_PATH = os.path.dirname(constants_path)
PROJECT_PATH = os.path.dirname(SRC_PATH)


SOURCE_CRS = "epsg:4326"  # reference system of the caribou tracking data
INTERP_FREQ = "6H"  # interpolation frequency for tracking data
TIME_COL = "FixDateTime"  # time column name

# path to downloaded osisaf data- will need to change this to osisaf/south/sicona
PATH_TO_OSISAF = "/data/hpcdata/users/jambyr/icenet/replacement/data/osisaf/south/siconca"
PATH_TO_AMSR2 = PROJECT_PATH + ""

TEMP_IMG_FOLDER = PROJECT_PATH + "/TEMP_IMG_FOLDER"
VIS_SAVE_FOLDER = PROJECT_PATH + "/visualisations"

# plot folders
SIC_PLOTS_FOLDER = PROJECT_PATH + "/plots/sic_plots"


###############################
### BOUNDS OF PLOTTING DATA ###
###############################

#Unhash to use coords for Northern hemisphere
"""
central_lat = 68
central_lon = -111
lat_span = 3  # degrees
lon_span = 12  # degrees
"""

#Southern hemisphere coords
central_lat = -90
central_lon = 0
lat_span = 100  # degrees
lon_span = 78  # degrees

# Determine crop corners
lon_left = central_lon - lon_span / 2
lon_right = central_lon + lon_span / 2
lat_upper = central_lat + lat_span / 2
lat_lower = central_lat - lat_span / 2

north_hem_config = {
    "top": 50,
    "bottom" : 325,
    "left" : 30,
    "right" : 330,
    "PATH_TO_OSISAF" : "",
}

south_hem_config = {
    "top": 55,
    "bottom" : 370,
    "left" : 70,
    "right" : 375,
    "PATH_TO_OSISAF" : "",
}