"""
Author: Hana Hourston @hhourston
Date: Mar. 1, 2023

Plot IOS files on a map:
Bottle (BOT and CHE)
CTD
Current meter (CUR)
Acoustic Doppler current profiler (ADCP)
Thermosalinograph (TOB)
Weather station (ANE)
"""

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

DTYPES = ['BOT_CHE', 'CTD', 'ADCP', 'CUR', 'TOB', 'ANE']

ARCTIC_PAC_LAT_CUTOFF = 68


def map_all(wdir, left_lon, bot_lat, right_lon, top_lat):
    colours = ['r', 'g', 'b', 'chartreuse', 'm', 'c']
    symbols = ['o', 'v', '.', 'P', '^', 's']
    # Make the map
    # area_thresh=1000 means don't plot coastline features less
    # than 1000 km^2 in area.
    # m = Basemap(llcrnrlon=left_lon, llcrnrlat=bot_lat,
    #             urcrnrlon=right_lon, urcrnrlat=top_lat,
    #             projection='lcc', area_thresh=1000.,
    #             resolution='c', lat_0=0.5 * (bot_lat + top_lat),
    #             lon_0=0.5 * (left_lon + right_lon))  # lat_0=53.4, lon_0=-129.0)

    # Azimuthal equidistant projection
    # width = 28000000; lon_0 = -105; lat_0 = 40
    width = 23000000; lon_0 = -140; lat_0 = 20
    m = Basemap(width=width,height=width,projection='aeqd',
                lat_0=lat_0,lon_0=lon_0)

    fig = plt.figure(num=None, figsize=(8, 6), dpi=100)
    m.drawcoastlines(linewidth=0.2)
    m.drawmapboundary(fill_color='white')
    m.fillcontinents(color='0.8')
    # m.drawrivers()

    # 20 degree graticule.
    m.drawparallels(np.arange(-80,81,20))
    m.drawmeridians(np.arange(-180,181,20))

    # parallels = np.arange(bot_lat, top_lat, 0.5)  # parallels = np.arange(48., 54, 0.2), parallels = np.linspace(bot_lat, top_lat, 10)
    # m.drawparallels(parallels, labels=[True, False, True, False])  # draw parallel lat lines
    # meridians = np.arange(left_lon, right_lon, 0.5)
    # m.drawmeridians(meridians, labels=[False, False, False, True])

    # Iterate through the dtypes
    for dtype, col, sym in zip(DTYPES, colours, symbols):
    # for dtype, col, sym in zip(['ADCP'], ['g'], ['.']):
        print(dtype)
        infile = os.path.join(wdir, f'csv_file_download_list_{dtype}.csv')
        dfin = pd.read_csv(infile)
        x, y = m(dfin.LON.values, dfin.LAT.values)
        if dtype == 'BOT_CHE':
            dtype = 'BOTTLE'
        # elif dtype == 'TOB':
        #     dtype = 'TSG'
        m.scatter(x, y, marker=sym, color=col, s=5, label=dtype)

    plt.legend(loc='lower right')
    plt.tight_layout()
    # Save the fig and close
    plt.savefig(os.path.join(wdir, 'ios-wp-file-map.png'))
    plt.close(fig)
    return


def pacific_map_bounds():
    # left_lon, bot_lat, right_lon, top_lat
    return [-180, 20, -115, 70]


def map_pacific():
    """
    file_list: contains the input file names, may only be one
    """
    left_lon, bot_lat, right_lon, top_lat = pacific_map_bounds()
    # Make the map
    # area_thresh=1000 means don't plot coastline features less
    # than 1000 km^2 in area.
    # Use Equidistant Cylindrical Projection
    # The simplest projection, just displays the world in
    # latitude/longitude coordinates.
    m = Basemap(llcrnrlon=left_lon, llcrnrlat=bot_lat,
                urcrnrlon=right_lon, urcrnrlat=top_lat,
                projection='cyl',  # area_thresh=1000.,
                resolution='h')

    m.drawcoastlines(linewidth=0.2)
    m.drawmapboundary(fill_color='white')
    m.fillcontinents(color='0.8')

    # Graticule.
    # labels = [left,right,top,bottom]
    m.drawparallels(np.arange(20,71,10), labels=[True,False,False,False])
    m.drawmeridians(np.arange(-180,-114,15), labels=[True,False,False,True])

    return m


def subset_pacific_data(df):
    left_lon, bot_lat, right_lon, top_lat = pacific_map_bounds()
    # Restrict the upper lat more to not include arctic
    return ((df.LON.values >= left_lon) &
            (df.LON.values <= right_lon) &
            (df.LAT.values >= bot_lat) &
            (df.LAT.values <= ARCTIC_PAC_LAT_CUTOFF))


def subset_arctic_data(df):
    return df.LAT.values >= ARCTIC_PAC_LAT_CUTOFF


def map_arctic():
    """
    file_list: contains the input file names, may only be one
    """
    # Find a good map projection to use
    # nplaea: North Polar Lambert Azimuthal Projection
    m = Basemap(projection='nplaea', boundinglat=65,
                lon_0=230, resolution='h')  # , area_thresh=1000.)

    m.drawcoastlines(linewidth=0.2)
    m.drawmapboundary(fill_color='white')
    m.fillcontinents(color='0.8')

    # Graticule.
    # labels = [left,right,top,bottom]
    m.drawparallels(np.arange(60,81,10), labels=[True,False,False,False])
    m.drawmeridians(np.arange(-180,181,30), labels=[False,True,False,True])

    return m


def do_map(file_list: list, region: str, dtype: str, output_dir: str):
    # Initialize figure
    plt.clf()  # Clear any active plots
    fig = plt.figure(num=None, figsize=(8, 6), dpi=100)

    # Load the data
    dfall = pd.DataFrame()
    for f in file_list:
        dfin = pd.read_csv(f)
        dfall = pd.concat((dfall, dfin))

    if region.lower() == 'pacific':
        # Make map instance
        m = map_pacific()
        # Subset the data to the region
        subsetter = subset_pacific_data(dfall)
    elif region.lower() == 'arctic':
        # Make map instance
        m = map_arctic()
        # Subset the data to the region
        subsetter = subset_arctic_data(dfall)

    # Scatter the points
    start_year = min(pd.to_datetime(
        dfall.loc[subsetter, 'START TIME(UTC)']).dt.year)
    end_year = max(pd.to_datetime(
        dfall.loc[subsetter, 'END TIME(UTC)']).dt.year)

    num_files = sum(subsetter)

    x, y = m(dfall.LON.values[subsetter], dfall.LAT.values[subsetter])
    # alpha defines the opacity
    m.scatter(x, y, marker='o', color='r', alpha=0.25)

    plt.title(
        f'{start_year} - {end_year} {dtype} {region.capitalize()} Files {num_files}')
    plt.tight_layout()
    # Save the fig and close
    plt.savefig(os.path.join(
        output_dir, f'all_{region.lower()}_{dtype}_map_hires.png'))
    plt.close(fig)
    return


def map_regions(wdir):
    """
    dtype: 'BOT and CHE' or 'CTD' or 'ADCP and CUR'
    region: 'pacific' or 'arctic'
    """

    for dtype in ['BOT_CHE', 'CTD', 'ADCP']:
        if dtype == 'ADCP':
            # Combine with current meter
            file_list = [
                os.path.join(wdir, f'csv_file_download_list_{dtype}.csv'),
                os.path.join(wdir, f'csv_file_download_list_CUR.csv')
            ]
            dtype = 'ADCP + Current Meter'
        else:
            file_list = [
                os.path.join(wdir, f'csv_file_download_list_{dtype}.csv')
            ]
            if dtype == 'BOT_CHE':
                dtype = 'Bottle'

        print(dtype)
        do_map(file_list, 'pacific', dtype, wdir)
        do_map(file_list, 'arctic', dtype, wdir)

    return


input_dir = 'C:\\Users\\HourstonH\\Documents\\sopo2023\\lu_poster\\'

# left_lon, bot_lat, right_lon, top_lat = [-180, -80, 180, 90]
# map_all(input_dir, left_lon, bot_lat, right_lon, top_lat)

map_regions(input_dir)
