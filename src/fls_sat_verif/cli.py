"""Command line interface of fls_sat_verif."""
# Standard library
import logging
import sys
from email.policy import default

# Third-party
import click
import pandas as pd

# Local
from . import __version__
from .plot import plt_median_day_cycle
from .plot import plt_timeseries
from .utils import calc_fls_fractions
from .utils import count_to_log_level
from .utils import create_working_dirs
from .utils import load_obs_fcst
from .utils import retrieve_cosmo_files

# from ipdb import set_trace


@click.command()
@click.version_option(__version__, "--version", "-V", message="%(version)s")
@click.option(
    "--dry-run",
    "-n",
    flag_value="dry_run",
    default=False,
    help="Perform a trial run with no changes made",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    default=1,
    help="Increase verbosity (specify multiple times for more)",
)
@click.option("--wd", type=str, help="Working directory.")
@click.option("--exp", type=str, help="Name of experiment.")
@click.option(
    "--retrieve_cosmo",
    is_flag=True,
    help="Retrieve cosmo forecast files from store from <start> to <end>.",
)
@click.option(
    "--calc_fractions", is_flag=True, help="Calculate FLS fractions from OBS and FCST."
)
@click.option("--plot_median_day_cycle", is_flag=True, help="Plot median.")
@click.option("--plot_timeseries", is_flag=True, help="Plot timeseries.")
@click.option(
    "--start",
    type=click.DateTime(formats=["%y%m%d%H"]),
    help="Start date: YYMMDDHH.",
)
@click.option(
    "--end",
    type=click.DateTime(formats=["%y%m%d%H"]),
    help="End date: YYMMDDHH.",
)
@click.option("--init", type=int, multiple=True, help="Init time, e.g. 00 UTC, 12 UTC.")
@click.option(
    "--interval", type=int, default=12, help="Time between init of simulations."
)
@click.option(
    "--max_lt", type=int, default=24, help="Maximal leadtime in hours. Default: 33"
)
@click.option(
    "--exp_model_dir",
    type=str,
    default="/store/s83/osm/COSMO-1E/",
    help="Path to model output. EXPECTS SUBOLDERS FOR YEARS! -> FCST21, FCST22, ... ",
)
@click.option(
    "--extend_previous",
    is_flag=True,
    default=False,
    help="Extend existing obs and fcst dataframes if available.",
)
@click.option(
    "--load_previous",
    is_flag=True,
    default=False,
    help="Load existing obs and fcst dataframes if available.",
)
@click.option(
    "--lscl_threshold",
    type=float,
    default=0.7,
    help="Low stratus confidence threshold. Default: 0.7",
)
@click.option(
    "--high_cloud_threshold",
    type=float,
    default=0.05,
    help="Threshold for excluding days due to high clouds.",
)
def main(
    *,
    dry_run: bool,
    verbose: int,
    wd: str,
    exp: str,
    exp_model_dir: str,
    retrieve_cosmo: bool,
    calc_fractions: bool,
    plot_median_day_cycle: bool,
    plot_timeseries: bool,
    start: str,
    end: str,
    init: int,  # used for plotting specific or all leadtimes
    interval: int,  # used for extracting tqc
    max_lt: int,
    extend_previous: bool,
    load_previous: bool,
    lscl_threshold: float,
    high_cloud_threshold,
) -> None:

    logging.basicConfig(level=count_to_log_level(verbose))

    # logging.warning("This is a warning.")
    # logging.info("This is an info message.")
    # logging.debug("This is a debug message.")

    # check mandatory inputs:
    # - working directory
    # - experiment identifier
    # - start
    # - end

    if not wd:
        print(f"Please give a sensible input for the working directory: --wd.")
        sys.exit(1)
    else:
        print(f"\n-------------------------------")
        print(f"Working directory: {wd}")
        print(f"-------------------------------\n")

    if not exp:
        print(f"Please give a sensible input for the experiment identifier: --exp.")
        sys.exit(1)

    if not start:
        print("Please indicate --start: YYMMDDHH.")
        sys.exit(1)

    if not end:
        print("Please indicate --end: YYMMDDHH.")
        sys.exit(1)

    sat_dir, tqc_dir, fls_dir, plot_dir = create_working_dirs(wd)

    if dry_run:
        click.echo("This is a dry run. Globi wishes you a good day.")
        return

    if load_previous:
        obs, fcst = load_obs_fcst(fls_dir)
        crit = obs.high_clouds < high_cloud_threshold
        # set_trace()

    if retrieve_cosmo:

        retrieve_cosmo_files(
            start=start,
            end=end,
            interval=interval,
            max_lt=max_lt,
            tqc_dir=tqc_dir,
            exp_model_dir=exp_model_dir,
            exp=exp,
        )

    if calc_fractions:
        obs, fcst = calc_fls_fractions(
            start,
            end,
            interval=interval,
            in_dir_obs=sat_dir,
            in_dir_model=tqc_dir,
            out_dir_fls=fls_dir,
            exp=exp,
            max_lt=max_lt,
            extend_previous=extend_previous,
            threshold=lscl_threshold,
        )

    if plot_median_day_cycle:
        plt_median_day_cycle(
            obs[crit].loc[start:end],
            fcst[crit].loc[start:end],
            plot_dir,
            max_lt,
            init_hours=init,
        )

    if plot_timeseries:
        plt_timeseries(obs[crit], fcst[crit], plot_dir)
