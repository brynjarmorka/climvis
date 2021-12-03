"""
Graphics for the uibkvis.

Author: Brynjar
"""
from matplotlib import pyplot as plt


def plot_wind_dir(df, station, filepath=None):
    """
    Plotting first lvl wind directions from ACINN data

    Author: Brynjar

    Parameters
    ----------
    df dataframe
        The dataframe with the ACINN data
    station str
    filepath path

    Returns
    -------
    f figure
        the plot
    """
    f, ax = plt.subplots(figsize=(12, 4))
    station = station[0].upper() + station[1:]  # gives capital first letter
    plt.plot(df['time'], df['dd'], '.')
    plt.ylabel('Wind direction (°)')
    plt.title(f'Wind direction at {station}')

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()

    return f
