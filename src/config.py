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
#PATH_TO_ICENET = PROJECT_PATH + "/forecasts/caribou_2023_north.nc"
#PATH_TO_AMSR2 = PROJECT_PATH + "/data/amsr2"

TEMP_IMG_FOLDER = PROJECT_PATH + "/TEMP_IMG_FOLDER"
VIS_SAVE_FOLDER = PROJECT_PATH + "/visualisations"

# plot folders
SIC_PLOTS_FOLDER = PROJECT_PATH + "/plots/sic_plots"


###############################
### BOUNDS OF PLOTTING DATA ###
###############################

#changing to be relevant coords for North pole
"""
central_lat = 68
central_lon = -111
lat_span = 3  # degrees
lon_span = 12  # degrees
"""
central_lat = -90
central_lon = 0
lat_span = 100  # degrees
lon_span = 78  # degrees


# Determine crop corners
lon_left = central_lon - lon_span / 2
lon_right = central_lon + lon_span / 2
lat_upper = central_lat + lat_span / 2
lat_lower = central_lat - lat_span / 2

lats = [lat_upper, lat_upper, lat_lower, lat_lower]
lons = [lon_left, lon_right, lon_left, lon_right]

# Transform from lat/lon to EASE2 (EPSG:6932)
transformer = Transformer.from_crs('epsg:4326', 'epsg:3408')

x, y = transformer.transform(lats, lons)
x = [np.min(x), np.max(x)]  # ascending
y = [np.max(y), np.min(y)]  # descending

TRANSFORM = ccrs.LambertAzimuthalEqualArea(0, 90)
PROJECTION = ccrs.LambertAzimuthalEqualArea(central_lon, 90)
PLOT_EXTENT = [lon_left, lon_right, lat_lower, lat_upper]

# c_map = mpl.cm.get_cmap("jet").copy()
c_map = mpl.cm.get_cmap("Blues_r").copy()
# c_map = mpl.cm.get_cmap("Blues_r").copy()
bg_map = cimgt.Stamen('terrain-background')
bg_map = None
#land_gdf = gpd.read_file(PROJECT_PATH + "/data/coronation_gulf_land_poly.geojson")
fill_land = True
caribou_colour = "red"

osisaf_plot_config = {
    "caribou_colour": caribou_colour,
    "c_map": c_map,
    "bg_map": bg_map,
    "fill_land": fill_land,
    "plot_extent": [lon_left, lon_right, lat_lower, lat_upper],
    "crop_x": x,
    "crop_y": y,
    "central_lon": central_lon,
    "full_name": "OSI-SAF",
    "save_name": "osisaf",
    "vmin": 0,
    "vmax": 100,
    # "levels": [0, 10, 20, 30, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
}

north_plot_config = {
    "top": 50,
    "bottom" : 325,
    "left" : 30,
    "right" : 330,
    "PATH_TO_OSISAF" : "/data/hpcdata/users/jambyr/icenet/replacement/data/osisaf/north/siconca",
    "plotting_latitude" : 90,
    "plot_title" : "Daily Arctic sea ice extent"
}

south_plot_config = {
    "top": 55,
    "bottom" : 380,
    "left" : 60,
    "right" : 385,
    "PATH_TO_OSISAF" : "/data/hpcdata/users/jambyr/icenet/replacement/data/osisaf/south/siconca",
    "plotting_latitude" : -90, 
    "plot_title" : "Daily Antarctic sea ice extent"
}