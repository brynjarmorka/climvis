"""
Graphics for the uibkvis.

Author: Brynjar
"""
from matplotlib import pyplot as plt
from matplotlib import cm
from windrose import WindroseAxes


def plot_wind_dir(df, station, interval, filepath=None):
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
    plt.plot(df["time"], df["dd"], ".", color="#6299C6")
    plt.ylabel("Wind direction (°)")
    plt.xlabel("Time [MM-DD HH]")
    plt.title(f"Wind direction the past {interval} day(s) at {station[0].upper() + station[1:]}")

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()

    return f


def plot_windrose(df, station, interval, filepath=None):
    """
    Plotting a windrose from the wind dir and wind speed.

    Author: Brynjar

    Parameters
    ----------
    df dataframe
        dd is wind dir, ff is wind speed
    station str
    days str
    filepath path

    Returns
    -------
    f plot
    """
    ax = WindroseAxes.from_ax()
    ax.bar(df.dd, df.ff, normed=True, opening=0.8, edgecolor='white', cmap=cm.get_cmap('Pastel1'))
    ax.set_legend()
    plt.legend(title="Wind speed [m/s]")
    plt.xlabel(f"Data from {df.time.iloc[0]} to {df.time.iloc[-1]}")
    plt.title(f"Windrose for the past {interval} day(s) at {station[0].upper() + station[1:]}")

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
    return ax
