import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature, NaturalEarthFeature
from matplotlib import pyplot as plt
import os
import pandas as pd
import rasterio

import sys
sys.path.append("../../")
from src import config
# from scalebar import scale_bar

import warnings
warnings.filterwarnings("ignore")


def single_day_xarray_and_tracks(date: str,
                                 rstr_xarray: object,
                                 PLOT_CONFIG: dict,
                                 HEMISPHERE_CONFIG : dict, 
                                 save: bool = True):
    """

    :param date:
    :param point_gdf:
    :param seg_gdf:
    :param rstr_xarray:
    :param PLOT_CONFIG:
    :param save:
    :return:
    """

    date_str = date.strftime('%Y-%m-%d-%H-%M-%S')
    date_str_display = date.strftime("%d %b %Y")
    # get points and line segments for specified date
    #day_point = point_gdf.loc[date]
    #day_seg = seg_gdf.loc[date]

    #transform = ccrs.LambertAzimuthalEqualArea(0, 90)
    #north
    #projection = ccrs.LambertAzimuthalEqualArea(PLOT_CONFIG["central_lon"], 90)
    
    #south
    projection = ccrs.LambertAzimuthalEqualArea(PLOT_CONFIG["central_lon"], HEMISPHERE_CONFIG["plotting_latitude"])
    
    fig, ax = plt.subplots( subplot_kw={'projection': projection})
    #extent = 4e6
    #add polygonised land mask built into rasterio
    #for north hemisphere
    land = NaturalEarthFeature('physical', 'land', edgecolor='grey', scale='50m')
    ax.add_feature(land, facecolor='grey', linewidth=0.2)
    
    #fig = plt.figure()
    #ax = plt.axes()

    # add background map if specified
    
    if PLOT_CONFIG["bg_map"]:
        ax.add_image(PLOT_CONFIG["bg_map"], 8, zorder=0)
    if PLOT_CONFIG["c_map"]:
        cmap = PLOT_CONFIG["c_map"]

    if PLOT_CONFIG["save_name"] == "icenet":
        start_time = pd.to_datetime(str(rstr_xarray.time.values))
        plot_title = f"{PLOT_CONFIG['full_name']} - Leadtime: {rstr_xarray.leadtime.values}   " \
                     f"(Init: {start_time.strftime('%d-%m-%Y')})"
    elif PLOT_CONFIG["save_name"] == "osisaf":
        plot_title = f"{PLOT_CONFIG['full_name']} - Time: {date.strftime('%d-%m-%Y %H:%M:%S')}"
    else:
        plot_title = f"{PLOT_CONFIG['full_name']} - Time: {date.strftime('%d-%m-%Y %H:%M:%S')}"
    cmap.set_bad('grey',1.)
    rstr_xarray.plot(
        ax=ax,
        cmap=cmap,
        vmin=PLOT_CONFIG["vmin"],
        vmax=PLOT_CONFIG["vmax"],
        zorder=1,
        cbar_kwargs={"label": "Sea Ice Concentration (%)"}
        #levels=PLOT_CONFIG["levels"],
        #cbar_kwargs={"ticks": PLOT_CONFIG["levels"], "spacing": "proportional"}
    )
    
    ax.set_title(f"Date: {date_str_display}")
    #Change to Arctic/ Antarctic?
    plt.suptitle(str(HEMISPHERE_CONFIG["plot_title"]), fontsize=16)
    ax.axes.get_yaxis().set_visible(False)
    ax.axes.get_xaxis().set_visible(False)
    #ax.coastlines('110m')
    plt.tight_layout()

    if save:
        if not os.path.exists(config.TEMP_IMG_FOLDER):
            os.makedirs(config.TEMP_IMG_FOLDER)

        plt.savefig(f"{config.TEMP_IMG_FOLDER}/{PLOT_CONFIG['save_name']}_{date_str}.png",
                    dpi=300, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
