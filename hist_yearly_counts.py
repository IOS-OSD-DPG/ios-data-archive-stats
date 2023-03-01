"""
Author: Hana Hourston
Date: Mar. 1, 2023
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import glob


def get_year_from_filename(infile, dtype):
    """
    dtype: "ADCP", "BOT", "CTD", or "CUR"
    """

    if dtype in ['ADCP', 'CUR']:
        dfin = pd.read_csv(infile, header=0, names=['File path'])
        dfout = dfin
        func = lambda x: int(os.path.basename(x).split('_')[1][:4])
        dfout['Year'] = list(map(func, dfout.iloc[:, 0]))
    elif dtype in ['BOT', 'CTD', 'CHE']:
        # func = lambda x: int(os.path.basename(x)[:4])
        dfin = pd.read_csv(infile)
        dfout = dfin.loc[:, ['FILE_URL']]
        dfout.rename(columns={'FILE_URL': 'File path'}, inplace=True)
        dfout['Year'] = pd.to_datetime(dfin.loc[:, 'START TIME(UTC)']).dt.year
    else:
        print('Unsupported dtype', dtype)
        return

    outfile = infile.replace('.csv', '_hasyear.csv')
    dfout.to_csv(outfile, index=False)
    return


def hist_annual_instrument_count(infile, png_name: str, dtype: str):
    # Get data in right format
    dfin = pd.read_csv(infile)

    num_profs = len(dfin)
    num_bins = dfin.Year.max() - dfin.Year.min() + 1

    # Manually assign y axis ticks to have only whole number ticks
    # num_yticks = dfin.Year.max

    # if num_yticks < 10:
    #     yticks = np.arange(num_yticks + 1)

    plt.clf()  # Clear any active plots
    fig, ax = plt.subplots()  # Create a new figure and axis instance

    ax.hist(dfin.Year.values, bins=num_bins, align='left',
            label='Number of files: {}'.format(num_profs))
    # if num_yticks < 10:
    #     ax.set_yticks(yticks)
    ax.minorticks_on()
    ax.set_ylabel('Number of Profiles')
    plt.legend()

    plt.title('Number of {} files per year'.format(dtype))
    plt.tight_layout()
    plt.savefig(png_name)
    plt.close(fig)
    return


def scatter_year_counts(fdict, png_name):
    plt.clf()  # Clear any active plots
    fig, ax = plt.subplots()  # Create a new figure and axis instance

    # plot the data
    colours = ['r', 'g', 'b', 'grey']
    symbols = ['o', 'v', '.', 'P']
    for key, col, sym in zip(fdict.keys(), colours, symbols):
        # Load the csv data
        df = pd.read_csv(fdict[key])
        num_files = str(len(df))
        num_bins = df.Year.max() - df.Year.min() + 1
        # Use hist function to count number of occurrences,
        # or use numpy.unique
        hist, bin_edges = np.histogram(df.Year.values, num_bins)
        # scatter plot
        ax.plot(bin_edges[:-1], hist, color=col, marker=sym,
                label=f'{key}: {num_files}')

    ax.minorticks_on()
    ax.set_ylabel('Number of files')
    plt.legend(title='Total file counts')

    plt.tight_layout()
    plt.savefig(png_name)
    plt.close(fig)
    return


input_dir = 'C:\\Users\\HourstonH\\Documents\\sopo2023\\lu_poster\\'

# file_lists = glob.glob(input_dir + '*.csv')
# file_lists.sort()
#
# for f in file_lists:
#     print(os.path.basename(f))
#     # hist_annual_instrument_count()
#     dtype = os.path.basename(f).split('_')[-1].split('.')[0]
#     print(dtype)
#     get_year_from_filename(f, dtype)

file_lists = glob.glob(input_dir + '*hasyear.csv')
file_lists.sort()

file_dict = {}
for f in file_lists:
    print(os.path.basename(f))
    if 'CTD' in os.path.basename(f):
        file_dict['CTD'] = f
    elif 'CUR' in os.path.basename(f):
        file_dict['CUR'] = f
    elif 'ADCP' in os.path.basename(f):
        file_dict['ADCP'] = f
    elif 'BOT' in os.path.basename(f):
        file_dict['BOTTLE'] = f

    plot_name = input_dir + 'IOS file counts per year.png'
    # hist_annual_instrument_count(f, plot_name, dtype)
    scatter_year_counts(file_dict, plot_name)
