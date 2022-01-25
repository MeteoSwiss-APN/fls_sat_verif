"""Command line interface of fls_sat_verif."""
# Standard library
import logging
from email.policy import default

# Third-party
import click

# Local
from . import __version__
from .utils import calc_fls_fractions
from .utils import count_to_log_level
from .utils import retrieve_cosmo_files


@click.command()
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
    help="Increase verbosity (specify multiple times for more)",
)
@click.option(
    "--version",
    "-V",
    is_flag=True,
    help="Print version",
)
@click.option(
    "--retrieve_cosmo",
    is_flag=True,
    help="Retrieve cosmo forecast files from store from <start> to <end>.",
)
@click.option(
    "--calc_fractions", is_flag=True, help="Calculate FLS fractions from OBS and FCST."
)
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
@click.option("--interval", type=int, help="Time between init of simulations.")
@click.option(
    "--max_lt", type=int, default=33, help="Maximal leadtime in hours. Default: 33"
)
@click.option(
    "--model_dir",
    type=str,
    help="Directory with TQC from model output.",
    default="/scratch/swester/input_sat_verif/tqc",
)
@click.option(
    "--obs_dir",
    type=str,
    help="Directory with raw low cloud confidence level files.",
    default="/scratch/swester/input_sat_verif/sat",
)
@click.option(
    "--fls_dir",
    type=str,
    help="Directory where pickled dataframes containing FLS fractions are stored.",
    default="/scratch/swester/input_sat_verif/fls",
)
def main(
    *,
    dry_run: bool,
    verbose: int,
    version: bool,
    retrieve_cosmo: bool,
    calc_fractions: bool,
    start: str,
    end: str,
    init: int,
    interval: int,
    max_lt: int,
    model_dir: str,
    obs_dir: str,
    fls_dir: str,
) -> None:

    logging.basicConfig(level=count_to_log_level(verbose))

    # logging.warning("This is a warning.")
    # logging.info("This is an info message.")
    # logging.debug("This is a debug message.")

    if version:
        click.echo(__version__)
        return

    if dry_run:
        click.echo("Is dry run")
        return

    if retrieve_cosmo:
        retrieve_cosmo_files(
            start=start, end=end, interval=interval, out_dir=model_dir, max_lt=max_lt
        )

    if calc_fractions:
        calc_fls_fractions(
            start, end, in_dir_obs=obs_dir, in_dir_model=model_dir, out_dir_fls=fls_dir
        )
