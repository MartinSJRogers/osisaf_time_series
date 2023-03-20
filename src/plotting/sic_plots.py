import cartopy.crs as ccrs
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import os
from shapely import wkt
import geopandas as gpd

import sys
sys.path.append("../../")
from src.data.load import load_osisaf
from src import config


def per_sample_sic_and_location(sic_df: object,
                                save_plot: bool = False) -> None:
    """

    :param sic_df:
    :param save_plot:
    :return:
    """
    # convert to geopandas
    sic_df["geometry"] = sic_df.geometry.apply(wkt.loads)
    sic_gdf = gpd.GeoDataFrame(sic_df, geometry="geometry", crs=4326)
    sic_gdf["ice_conc"] = sic_gdf.ice_conc * 100
    sample_point = sic_gdf[sic_gdf.day_index == 0]
    sample_date = sample_point.index[0]

    f = plt.figure(figsize=(12, 4))

    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], projection=config.PROJECTION)

    sic_gdf.ice_conc.plot(ax=ax1)
    ax1.vlines(x=sample_date, ymin=0, ymax=100, color="red", linestyle=":")
    ax1.set_title("SIC at crossing point = {:.1f}%".format(sample_point.ice_conc[0]))
    ax1.grid("on")

    osisaf = load_osisaf(config.PATH_TO_OSISAF, sample_date)

    osisaf.sel(
        xc=slice(*config.x),
        yc=slice(*config.y)).plot(
        transform=config.TRANSFORM,
        vmin=0,
        vmax=100,
        ax=ax2
    )

    sample_point.to_crs(config.PROJECTION, inplace=True)
    sample_point.plot(ax=ax2, c="red", marker="x")

    ax2.set_extent(config.PLOT_EXTENT, crs=ccrs.PlateCarree())
    ax2.coastlines("10m")

    plt.tight_layout()
    if save_plot:

        save_folder = config.SIC_PLOTS_FOLDER + "/sample_points"
        print(f"Saving {sample_point.index.year[0]} - {sample_point.FieldID[0]} to {save_folder}...")

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        plt.savefig(f"{save_folder}/{sample_point.index.year[0]}_{sample_point.FieldID[0]}.png",
                    bbox_inches="tight",
                    facecolor="white")
        plt.close()

    else:
        plt.show()
    return
