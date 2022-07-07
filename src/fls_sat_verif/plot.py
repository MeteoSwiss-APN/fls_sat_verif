"""Plotting routines for FLS sat verification."""

# Standard library
import datetime as dt
import logging
import sys
from pathlib import Path
from re import I

# Third-party
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# from ipdb import set_trace


def plt_median_day_cycle(obs, fcst, plot_dir, max_lt, init_hours):
    """Plot median FLS fraction.

    Args:
        obs (dataframe): obs from satellite
        fcst (dataframe): tqc from model
        plot_dir (str): output_path
        max_lt (int): maximum leadtime - not implemented yet!
        init_hours (list): init hours of model simulations

    """
    # define colors
    color_obs = "mediumseagreen"
    color_fcst = "wheat"

    # valid hours: daytime cycle
    day_hours = np.arange(0, 24, 1)

    # calculate daily cycle median FLS fraction from OBS
    obs_median = pd.Series(index=day_hours)
    for day_hour in day_hours:
        obs_day_hour = obs[obs.index.hour == day_hour]
        obs_median[day_hour] = obs_day_hour.fls_frac.median()
        logging.info(f"day time {day_hour}: {len(obs_day_hour)} observations")

    # loop over init_hours
    for init_hour in init_hours:

        _, ax = plt.subplots(figsize=(9, 4))

        # calculate daily cycle median FLS fraction from FCST
        fcst_median = pd.Series(index=day_hours)

        for day_hour in day_hours:
            fcst_max_lt = fcst[fcst.columns[fcst.columns < (max_lt + 1)]]
            lt_hour = (day_hour + init_hour) % 24
            fcst_day_hour = fcst_max_lt[fcst_max_lt.index.hour == day_hour][lt_hour]
            fcst_median[day_hour] = fcst_day_hour.median()
            logging.info(f"day time {day_hour}: {len(fcst_day_hour)} forecasts")

            ax.bar(
                day_hour - 0.2,
                obs_median[day_hour],
                color=color_obs,
                width=0.4,
            )
            ax.bar(
                day_hour + 0.2,
                fcst_median[day_hour],
                color=color_fcst,
                width=0.4,
            )

        # x-axis
        ax.set_xlabel("Hour of day")
        ax.set_xticks([0, 6, 12, 18])

        # title
        ax.set_title(f"Median FLS fraction on Swiss Plateau")

        # legend
        # add customised legend
        legend_elements = [
            Patch(color=color_obs, label=f"OBS"),
            Patch(color=color_fcst, label=f"FCST, Init: {init_hour:02} UTC"),
        ]
        ax.legend(handles=legend_elements)

        # save figure
        file_name = f"median_day_cycle_init_{init_hour}"
        out_name = Path(plot_dir, f"{file_name}.png")
        plt.savefig(out_name, dpi=250)
        print(f"Saved as:")
        print(f"  {out_name}")


def plt_timeseries(obs, fcst, plot_dir):
    """Plot median FLS fraction. - not finished yet.

    Args:
        obs (dataframe): obs from satellite
        fcst (dataframe): tqc from model
        plot_dir (str): output_path

    """
    print("This routine is not finished yet.")
    sys.exit(1)
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
