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


def read_csv_as_datetime_geometry(path_to_csv: str,
                                  source_crs: str = "epsg:4326") -> object:
    """
    Load caribou tracking data and convert to datetime indexed geopandas dataframe
    :param path_to_csv: path to the tracking data csv file
    :param source_crs: reference system of the tracking dataset
    :return: datetime indexed geopandas dataframe
    """
    # read data with datetime column
    raw_df = pd.read_csv(path_to_csv, index_col=0, parse_dates=["FixDateTime"])

    # convert datetime to index
    raw_df["t"] = pd.to_datetime(raw_df["FixDateTime"], format="%Y-%m-%d %H:%M")
    raw_df = raw_df.set_index("t")  # .tz_localize("UTC")

    # convert long lat to geometry points
    raw_gdf = gpd.GeoDataFrame(raw_df.drop(["Longitude", "Latitude", "FixDateTime"], axis=1), crs=source_crs,
                               geometry=[Point(xy) for xy in zip(raw_df.Longitude, raw_df.Latitude)])

    return raw_gdf


def load_osisaf(path_to_data: str,
                date: str) -> object:
    """

    :param path_to_data: path to osisaf data folder
    :param date: date in
    :return:
    """

    file_path = f"{path_to_data}/{date.year}.nc"
    sic_data = xr.open_mfdataset(file_path).load()

    # day of year indexing
    doy = date.day_of_year - 1
    sic_data = sic_data["ice_conc"].sel(time=date.strftime("%Y-%m-%d"))
    

    #mask_array = np.load(config.LAND_MASK_PATH)
    #sic_data = sic_data.where(mask_array == 0)
    sic_data = sic_data.assign_coords(xc=sic_data.xc * 1e3, yc=sic_data.yc * 1e3)

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


def load_osisaf_year(path_to_data: str) -> object:
    """

    :param path_to_data:
    :return:
    """
    # load osisaf xarray and mask
    sic_data = xr.open_mfdataset(path_to_data)
    land_mask = np.load(config.LAND_MASK_PATH)

    # apply mask
    sic_data = sic_data.where(land_mask == 0)

    # convert coordinates
    sic_data = sic_data.assign_coords(xc=sic_data.xc * 1e3, yc=sic_data.yc * 1e3)
    return sic_data


def load_icenet(xr_forecast: object,
                year: int,
                season: str,
                date: str) -> object:
    """

    :param xr_forecast:
    :param year:
    :param season:
    :param date:
    :return:
    """
    if season == "spring":
        start_date = pd.Timestamp(f'{year}-03-01')
    elif season == "autumn":
        start_date = pd.Timestamp(f'{year}-10-01')
    else:
        print(f"Input invalid season <{season}>, should be either spring or autumn")

    leadtime = (date - start_date).days

    icenet_pred = xr_forecast["sic_mean"].sel(time=start_date.strftime("%Y-%m-%d")).sel(leadtime=leadtime)
    #TODO: NEED TO CHANGE!
    # How to mask data properly? For now mask zero values
    icenet_pred = icenet_pred.where(icenet_pred != 0)
    icenet_pred = icenet_pred.assign_coords(xc=icenet_pred.xc * 1e3, yc=icenet_pred.yc * 1e3)

    return icenet_pred


# def load_modis(date, plot_extent):
#
#     create_modis_xml(date)
#     options_list = [
#         "-of GTiff",
#         "-projwin $plot_extent[0] $plot_extent[3] $plot_extent[1] $plot_extent[2]"
#     ]
#     options_string = " ".join(options_list)
#     out_ds = gdal.Translate("bands.xml", f"modis_{date}.tiff", options=options_string)
#     #im = gdal.Open(f"modis_{date}.tiff")
#     arr = out_ds.ReadAsArray()
#     modis_xr = build_modis_xarray(arr, plot_extent)
#
#     return modis_xr



