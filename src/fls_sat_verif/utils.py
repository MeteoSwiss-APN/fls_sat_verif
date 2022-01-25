"""Utils for the command line tool."""
# Standard library
import logging
import os
import pickle
import sys
from bdb import set_trace
from pathlib import Path

# Third-party
import pandas as pd
from click import option


def count_to_log_level(count: int) -> int:
    """Map occurrence of the command line option verbose to the log level."""
    if count == 0:
        return logging.ERROR
    elif count == 1:
        return logging.WARNING
    elif count == 2:
        return logging.INFO
    else:
        return logging.DEBUG


def extract_tqc(grib_file, out_dir, date_str, lt):
    """Extract tqc from model file using fieldextra.

    Args:
        grib_file (str): Grib file
        out_dir (str): Output directory
        date_str (str): date
        lt (int): leadtime

    """
    logging.debug(f"Apply fxfilter to: {grib_file}.")

    # new filename
    new_name = Path(out_dir, f"tqc_{date_str}_{lt:03}.grb2")
    logging.info(f"Creating: {str(new_name)}.")

    # check whether filtered file already exists
    if new_name.is_file():
        logging.info(f"  ...exists already!")
        return

    # apply fxfilter
    cmd = f"fxfilter -o {new_name} -s TQC {grib_file}"
    logging.debug(f"Will run: {cmd}")
    os.system(cmd)

    return


def retrieve_cosmo_files(start, end, interval, out_dir, max_lt):
    """Retrieve COSMO files.

    Args:
        start (datetime):   start
        end (datetime):     end
        interval (int):     interval between simulations
        out_dir (str):      output directory for tqc-files
        max_lt (int):       maximum leadtime

    """
    cosmo_dir = f"/store/s83/osm/COSMO-1E/"  # FCST{start.strftime('%y')}"
    logging.info(f"Retrieving COSMO-files from {cosmo_dir}")

    # create output directory
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # list of ini-dates of simulations
    dates = pd.date_range(start, end, freq=f"{interval}H")

    # loop over simulations
    for date in dates:

        # string of date for directories
        date_str = date.strftime("%y%m%d%H")

        # collect grib files
        for lt in range(0, max_lt + 1, 1):
            model_file = list(
                Path(cosmo_dir, f"FCST{date.strftime('%y')}").glob(
                    f"{date_str}_???/grib/c1effsurf{lt:03}_000"
                )
            )
            if len(model_file) == 0:
                logging.warning(f"No file found for {date_str}: +{lt}h.")
            elif len(model_file) > 1:
                print(f"Model file description ambiguous.")
                sys.exit(1)
            else:
                # apply fxfilter
                extract_tqc(model_file[0], out_dir, date_str, lt)


def get_fls_fractions(in_dir):
    """Retrieve dataframe containing FLS fractions.

    Args:
        in_dir (str): input directory

    """
    pass


def calc_fls_fractions(start, end, in_dir_obs, in_dir_model, out_dir_fls):
    """Calculate FLS fractions in Swiss Plateau for OBS and FCST.

    Args:
        start (datetime):       start
        end (datetime):         end
        in_dir_obs (str):       dir with sat data
        in_dir_model (str):     dir with model data
        out_dir_fls (str):      dir with fls fractions

    """
    pass
