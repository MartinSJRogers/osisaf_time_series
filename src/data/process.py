import pandas as pd
import geopandas as gpd
import movingpandas as mpd
import numpy as np
import os

import sys
sys.path.append("../../")
from src import config


def interpolate_gps_data(traj_collection: object,
                         year: int,
                         season: str,
                         interp_freq: str = "6H",
                         source_crs: str = "epsg:4326",
                         save: bool = False) -> object:
    """

    :param traj_collection:
    :param year:
    :param season:
    :param interp_freq:
    :param source_crs:
    :param save:
    :return:
    """

    # # get first and last observation date from all trajectories
    # begin = traj_collection.to_point_gdf().index.min()
    # finish = traj_collection.to_point_gdf().index.max()

    if season == "autumn":
        begin = pd.Timestamp(f'{year}-10-15-00-00-00')
        finish = pd.Timestamp(f'{year}-12-15-00-00-00')
    elif season == "spring":
        begin = pd.Timestamp(f'{year}-03-15-00-00-00')
        ## TODO: change so takes min/max for each year - new dates for spring
        finish = pd.Timestamp(f'{year}-05-25-00-00-00')
    else:
        print(f"Invalid season - {season} - entered!")

    # make time intervals every interp_freq with start and end dates (normalized to midnight)
    date_times = pd.date_range(begin, finish, freq=interp_freq, normalize=True).tz_convert(None)

    full_point_list = list()
    full_segs_list = list()
    print(f"{len(date_times)} dates to interpolate...")
    for index, date_time in enumerate(date_times):

        if index % 50 == 0:
            print(f"Completed {index} of {len(date_times)}")

        point_list = list()
        seg_list = list()

        # not possible to do for whole traj collection, so loop through individuals
        for traj in traj_collection:
            # get mover start and end times
            traj_end = traj.get_end_time()
            traj_start = traj.get_start_time()

            #### POINTS ####
            # interpolate position at specific time
            interp_loc = traj.interpolate_position_at(date_time)
            # add extra detail of whether interpolation past last observation (for plotting)
            if traj_start <= date_time <= traj_end:
                point_row = {"id": traj.id, "time": date_time, "geometry": interp_loc, "past_end": 0}
            elif date_time < traj_start:
                point_row = {"id": traj.id, "time": date_time, "geometry": interp_loc, "past_end": -1}
            elif date_time > traj_end:
                point_row = {"id": traj.id, "time": date_time, "geometry": interp_loc, "past_end": 1}

            point_list.append(point_row)

            #### SEGMENTS ####
            if date_time > traj_start:
                line_seg = traj.get_linestring_between(traj_start, date_time)
            else:
                line_seg = np.nan
            seg_row = {"id": traj.id, "time": date_time, "geometry": line_seg}
            seg_list.append(seg_row)

        point_gdf = gpd.GeoDataFrame(point_list, geometry="geometry", crs=source_crs)
        point_gdf = point_gdf.set_index("time")
        full_point_list.append(point_gdf)

        seg_gdf = gpd.GeoDataFrame(seg_list, geometry="geometry", crs=source_crs)
        seg_gdf = seg_gdf.set_index("time")
        full_segs_list.append(seg_gdf)

    full_point_gdf = pd.concat(full_point_list)
    full_segs_gdf = pd.concat(full_segs_list)

    if save:
        save_folder = f"{config.PROCESSED_DATA}/interp_gps/{year}"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        full_point_gdf.to_file(f"{save_folder}/{season}_point_{interp_freq}.geojson", driver="GeoJSON")
        full_segs_gdf.to_file(f"{save_folder}/{season}_segs_{interp_freq}.geojson", driver="GeoJSON")

    return full_point_gdf, full_segs_gdf


def get_year_season_df(full_gdf: object,
                       year: int,
                       season: str) -> object:
    """

    :param full_gdf:
    :param year:
    :param season:
    :return:
    """
    season_dict = {"spring": [1, 2, 3, 4, 5, 6], "autumn": [7, 8, 9, 10, 11, 12]}

    sub_gdf = full_gdf[full_gdf.Year == year]
    sub_gdf = sub_gdf[sub_gdf.index.month.isin(season_dict[season])]

    return sub_gdf


def get_traj_set(full_gdf: object,
                 year: int,
                 season: str = None,
                 plot: bool = False) -> object:
    """

    :param full_gdf:
    :param year:
    :param season:
    :param plot:
    :return:
    """
    season_dict = {"spring": [1, 2, 3, 4, 5, 6], "autumn": [7, 8, 9, 10, 11, 12]}

    sub_gdf = full_gdf[full_gdf.Year == year]

    if season:
        sub_gdf = sub_gdf[sub_gdf.index.month.isin(season_dict[season])]
    else:
        season = "both seasons"

    print(f"Selecting trajectories for {year} ({season})")
    traj_collection = mpd.TrajectoryCollection(sub_gdf, "FieldID", t="t", crs="epsg:4326")
    print(traj_collection)
    if plot:
        traj_collection.hvplot(geo=True, hover_cols=["FieldID", "t"], tiles="OSM",
                               line_width=2, frame_width=500, frame_height=400)

    return traj_collection



