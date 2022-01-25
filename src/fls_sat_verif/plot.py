"""Plotting routines for FLS sat verification."""

# Standard library
import datetime as dt
import logging
from pathlib import Path

# Third-party
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# from ipdb import set_trace


def plt_median(obs, fcst, plot_dir):
    """Plot median FLS fraction.

    Args:
        obs (dataframe): obs from satellite
        fcst (dataframe): tqc from model
        plot_dir (str): output_path

    """
    pass


def plt_timeseries(obs, fcst, plot_dir):
    """Plot median FLS fraction.

    Args:
        obs (dataframe): obs from satellite
        fcst (dataframe): tqc from model
        plot_dir (str): output_path

    """
    _, ax = plt.subplots(figsize=(7, 4))
    timestamps = [pd.to_datetime(i) for i in obs.index.values]
    ax.plot(timestamps, obs.fls_frac.values)
    ax.set_title("Observed FLS fraction")

    # timestamps on x-axis
    locator = mdates.AutoDateLocator(minticks=4, maxticks=12)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    file_name = "timeseries_obs"
    out_name = Path(plot_dir, f"{file_name}.png")
    plt.savefig(out_name)
    logging.info(f"Saved as:")
    logging.info(f"  {out_name}")
