# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 11:37:34 2023

@author: marrog
"""

import shutil
import imageio
import os
import argparse
import xarray as xr
import geopandas as gpd

import sys
sys.path.append("../../")
from src.data.load import read_csv_as_datetime_geometry, load_osisaf, load_icenet, load_amsr2
from src import config
from src.plotting.plotting_utils import single_day_xarray_and_tracks
from tqdm import tqdm_notebook as tqdm
import pandas as pd


def make_animation(year, raster_name, meta):
    # make save folder
    save_folder = f"{config.VIS_SAVE_FOLDER}/{year}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    print("Making animation...")

    # make animation
    images = []
    for file_name in sorted(os.listdir(config.TEMP_IMG_FOLDER)):
        if file_name.endswith('.png'):
            file_path = os.path.join(config.TEMP_IMG_FOLDER, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave(f'{save_folder}/{raster_name}_anim_{year}_{meta}.mp4', images, fps=20)
    print(f"Done! Saved as {save_folder}/{raster_name}_anim_{year}_{meta}.mp4")

    # delete temp folder before making new animation
    #shutil.rmtree(config.TEMP_IMG_FOLDER)
    return


if __name__ == "__main__":
    # Define commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str)
    parser.add_argument("--end", type=str)
    parser.add_argument("--data_source", type=str)
    parser.add_argument("--hemisphere", type = str)
    args = parser.parse_args()
    extra_info = "complete"
    
    # Need to change this to dates required
    #start_date = '2012-05-10-12-00'
    #end_date = '2012-05-15-12-00'
    
    start_date = args.start
    end_date = args.end
    
    dates = pd.date_range(start_date, end_date)
    #year_start = start_date.year
    for date in tqdm(dates): 
        extra_info = "complete"
        if args.data_source == "osisaf":
            #xarray_data = load_osisaf(config.PATH_TO_OSISAF, date)
            
            if args.hemisphere == "north":
                hemisphere_params = config.north_plot_config
                xarray_data = load_osisaf(hemisphere_params["PATH_TO_OSISAF"], date)
                subset_xarray = xarray_data[hemisphere_params["top"]:hemisphere_params["bottom"], hemisphere_params["left"]:hemisphere_params["right"]]
            if args.hemisphere == "south":
                hemisphere_params = config.south_plot_config
                xarray_data = load_osisaf(hemisphere_params["PATH_TO_OSISAF"], date)
                subset_xarray = xarray_data[55:370, 70:375]

            #subset_xarray = xarray_data
            plot_params = config.osisaf_plot_config
            single_day_xarray_and_tracks(date, subset_xarray, plot_params,hemisphere_params,
                                         save=True)
        else:
            print(f"Incorrect data source '{args.data_source}' entered!")
            print("Should be one of ['osisaf', 'icenet', 'modis', 'amsr2']")
    
    if os.path.exists(config.TEMP_IMG_FOLDER):
        make_animation(2012, args.data_source, extra_info)
    else:
        print("No temp_img_folder")