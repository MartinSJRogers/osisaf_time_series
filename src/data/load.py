import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from osgeo import gdal

# from data_utils import create_modis_xml, build_modis_xarray
import sys
sys.path.append("../../")
from src import config


def load_osisaf(path_to_data: str,
                date: str) -> object:
    """

    :param path_to_data: path to osisaf data folder
    :param date: date in
    :return: xarray Dataset object
    """

    file_path = f"{path_to_data}/{date.year}.nc"
    sic_data = xr.open_mfdataset(file_path).load()

    # day of year indexing
    doy = date.day_of_year - 1
    #subset sic for that day
    sic_data = sic_data["ice_conc"].sel(time=date.strftime("%Y-%m-%d"))

    #assign coords
    sic_data = sic_data.assign_coords(xc=sic_data.xc * 1e3, yc=sic_data.yc * 1e3)
    #convert sic to [0,100]
    sic_data = sic_data * 100

    # assign attributes to match direct download
    sic_data = sic_data.assign_attrs({
        'long_name': 'fully filtered concentration of '
                     'sea ice using atmospheric correction of brightness '
                     'temperatures and open water filters',
        'standard_name': 'sea_ice_area_fraction',
        'units': '%',
        'valid_min': 0,
        'valid_max': 10000,
        'grid_mapping': 'Lambert_Azimuthal_Grid',
        'ancillary_variables': 'total_standard_error status_flag',
        'comment': 'this field is the primary sea ice concentration '
                   'estimate for this climate data record',
        '_ChunkSizes': np.array([1, 432, 432])})

    return sic_data

### If we have time to move onto AMSR2 data ####
def load_amsr2(path_to_data: str,
                date: str) -> object:
    """

    :param path_to_data: path to amsr2 data folder
    :param date: date in
    :return:
    """

    # load dataframe for specified year
    format_date = f"{date.year}{date.month:02d}{date.day:02d}"
    file_path = f"{path_to_data}/asi-AMSR2-n6250-{format_date}-v5.4.nc"
    sic_data = xr.open_dataset(file_path).load()

    return sic_data







