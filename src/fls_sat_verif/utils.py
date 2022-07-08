"""Utils for the command line tool."""
# Standard library
import datetime as dt
import logging
import os
import pickle
import sys
from pathlib import Path

# Third-party
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

# from ipdb import set_trace


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


def create_working_dirs(wd):
    """Create working directory and required subfolders.

    Args:
        wd (str): Path to working directory.

    Returns:
        sat_dir: Directory for satellite data (LSCL).
        tqc_dir: Directory for model data (TQC netcdf files.)
        fls_dir: Directory for pandas dataframes for FLS fractions.
        plot_dir: Directory for final plots.

    """
    sat_dir = Path(wd, "sat")
    tqc_dir = Path(wd, "tqc")
    fls_dir = Path(wd, "fls")
    plot_dir = Path(wd, "plots")

    logging.info("Your working directories:")

    for dir in [sat_dir, tqc_dir, fls_dir, plot_dir]:
        Path(dir).mkdir(parents=True, exist_ok=True)
        logging.info(f"   {dir}")

    return sat_dir, tqc_dir, fls_dir, plot_dir


def extract_tqc(grib_file, out_dir, date_str, lt):
    """Extract tqc from model file using fieldextra.

    Args:
        grib_file (str): Grib file
        out_dir (str): Output directory
        date_str (str): date YYMMDDHH
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


def retrieve_cosmo_files(start, end, interval, max_lt, tqc_dir, exp_model_dir, exp):
    """Retrieve COSMO files.

    Args:
        start (datetime):   start
        end (datetime):     end
        interval (int):     interval between simulations
        max_lt (int):       maximum leadtime
        tqc_dir (str):      tqc-folder in working directory
        exp_model_dir (str): path to model (cosmo) output
        exp (str):          experiment identifier

    """
    logging.info(f"Retrieving COSMO-files from {exp_model_dir}")
    logging.info(f"   from +0h to +{max_lt}h leadtime")

    # list of ini-dates of simulations
    dates = pd.date_range(start, end, freq=f"{interval}H")
    first_date = dates[0].strftime("%b %d, %Y, %H UTC")
    last_date = dates[-1].strftime("%b %d, %Y, %H UTC")
    logging.info(f"   for {first_date} to {last_date}.")

    # output dir (experiment-specific)
    out_dir = Path(tqc_dir, exp)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    logging.info(f"   and put tqc here:")
    logging.info(f"   {out_dir}")

    # loop over simulations
    for date in dates:

        # string of date for directories
        date_str = date.strftime("%y%m%d%H")

        # collect grib files
        for lt in range(0, max_lt + 1, 1):
            model_file = list(
                Path(exp_model_dir, f"FCST{date.strftime('%y')}").glob(
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


def get_ml_mask(lats, lons):
    """Retrieve mask of Swiss Plateau (Mittelland).

    Args:
        lats (array): latitudes
        lons (array): longitudes

    Returns:
    mask (array with True and False)

    """
    # polygon points
    ll_corner = (46.12, 5.89)
    p1 = (46.06, 6.10)
    p2 = (46.33, 6.78)
    p3 = (46.55, 7.01)
    p4 = (46.64, 7.31)
    p5 = (46.65, 7.65)
    p6 = (46.62, 7.79)
    p7 = (46.81, 8.33)
    p8 = (47.09, 9.78)
    p9 = (47.82, 10.02)
    p10 = (47.81, 8.34)
    p11 = (47.38, 7.87)
    p12 = (47.29, 7.68)
    p13 = (47.25, 7.45)
    p14 = (47.13, 7.06)
    p15 = (47.07, 6.87)
    p16 = (46.73, 6.36)
    p17 = (46.59, 6.30)
    p18 = (46.18, 5.86)

    # create polygon
    Path = mpath.Path
    path_data = [
        (Path.MOVETO, ll_corner),
        (Path.LINETO, p1),
        (Path.LINETO, p2),
        (Path.LINETO, p3),
        (Path.LINETO, p4),
        (Path.LINETO, p5),
        (Path.LINETO, p6),
        (Path.LINETO, p7),
        (Path.LINETO, p8),
        (Path.LINETO, p9),
        (Path.LINETO, p10),
        (Path.LINETO, p11),
        (Path.LINETO, p12),
        (Path.LINETO, p13),
        (Path.LINETO, p14),
        (Path.LINETO, p15),
        (Path.LINETO, p16),
        (Path.LINETO, p17),
        (Path.LINETO, p18),
        (Path.CLOSEPOLY, ll_corner),
    ]
    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)

    # store original shape
    shape = lats.shape

    # path.contains_points checks whether points are within polygon
    # however, this function can only handle vectors
    # -> ravel and unravel
    latlon = [[lat, lon] for lat, lon in zip(lats.ravel(), lons.ravel())]
    mask = np.reshape(path.contains_points(latlon), shape)

    return mask


def save_as_pickle(obj, path):
    """Save object as pickled object.

    Args:
        obj (python object): usually dataframe
        path (str): full path

    """
    # create parent if not existing yet
    path.parents[0].mkdir(parents=True, exist_ok=True)

    # dump object
    pickle.dump(obj, open(path, "wb"))
    logging.info(f"Saved {path}")

    return


def calc_fls_fractions(
    start,
    end,
    interval,
    in_dir_obs,
    in_dir_model,
    out_dir_fls,
    exp,
    max_lt,
    extend_previous,
    threshold,
):
    """Calculate FLS fractions in Swiss Plateau for OBS and FCST.

    Args:
        start (datetime):       start
        end (datetime):         end
        interval (int):         interval between simulations in hours
        in_dir_obs (str):       dir with sat data
        in_dir_model (str):     dir with model data
        out_dir_fls (str):      dir with fls fractions
        exp (str):              experiment identifier
        max_lt (int):           maximum leadtime
        extend_previous (bool): load previous obs and fcst dataframes
        threshold (float):      threshold for low stratus confidence level

    Returns:
        obs (dataframe)
        fcst (dataframe)

    """
    # determine init and valid timestamps
    ini_times = pd.date_range(start=start, end=end, freq=f"{interval}H")
    valid_times = pd.date_range(
        start=start, end=end + dt.timedelta(hours=max_lt), freq="1H"
    )
    first_date = valid_times[0].strftime("%b %d, %Y, %H UTC")
    last_date = valid_times[-1].strftime("%b %d, %Y, %H UTC")
    logging.info("Calculating FLS fractions ")
    logging.info(f"   for {first_date} to {last_date}.")

    # retrieve OBS dataframe
    obs_path = Path(out_dir_fls, "obs.p")
    if obs_path.is_file() and extend_previous:
        obs = pickle.load(open(obs_path, "rb"))
        logging.warning(f"Loaded obs from pickled object:")
        logging.warning(f"  {obs_path}")
    else:
        # create dataframe
        obs = pd.DataFrame(columns=["fls_frac", "high_clouds"], index=valid_times)
        logging.warning("Created new obs dataframe:")
        logging.warning(f"  {obs_path}")

    # retrieve FCST dataframe
    fcst_path = Path(out_dir_fls, f"fcst_{exp}.p")
    if fcst_path.is_file() and extend_previous:
        fcst = pickle.load(open(fcst_path, "rb"))
        logging.warning("Loaded fcst from pickled object:")
        logging.warning(f"  {fcst_path}")
    else:
        # create dataframe
        fcst = pd.DataFrame(columns=np.arange(max_lt + 1), index=valid_times)
        logging.warning("Created new fcst dataframe:")
        logging.warning(f"  {fcst_path}")

    # initiate variables
    ml_mask = None
    ml_size = None

    for valid_time in valid_times:

        valid_time_str = valid_time.strftime("%y%m%d%H")

        # A) extract FLS fraction from OBS
        ##################################

        # timestamp from sat images: -15min
        obs_timestamp = (valid_time - dt.timedelta(minutes=15)).strftime("%y%m%d%H%M")
        logging.debug(f"SAT timestamp: {obs_timestamp}")

        # obs filename
        obs_file = Path(in_dir_obs, f"MSG_lscl-cosmo1eqc3km_{obs_timestamp}_c1e.nc")
        logging.warning(f"SAT file: {obs_file}")

        # load obs file
        try:
            ds = xr.open_dataset(obs_file).squeeze()
        except FileNotFoundError:
            logging.warning(f"No sat file for {obs_timestamp}.")
            logging.debug(f" -> {obs_file}")
            continue

        if ml_mask is None:
            ml_mask = get_ml_mask(ds.lat_1.values, ds.lon_1.values)
            ml_size = np.sum(ml_mask)
            logging.debug(f"{ml_size} grid points in ML.")

        # lscl = low stratus confidence level (diagnosed)
        lscl = ds.LSCL.values
        lscl_ml = lscl[ml_mask]

        # count nan-values (=high clouds)
        n_high_clouds = np.sum(np.isnan(lscl_ml))

        # count values larger than threshold (=FLS)
        n_fls = np.sum(lscl_ml > threshold)

        # fill into dataframe
        obs.loc[valid_time]["fls_frac"] = n_fls / ml_size
        obs.loc[valid_time]["high_clouds"] = n_high_clouds / ml_size

        # B) extract FLS fraction from FCST
        ###################################

        for lt in range(max_lt + 1):
            ini_time = valid_time - dt.timedelta(hours=lt)
            ini_time_str = ini_time.strftime("%y%m%d%H")
            fcst_file = Path(in_dir_model, exp, f"tqc_{ini_time_str}_{lt:03}.grb2")

            if fcst_file.is_file():
                logging.warning(f"Loading {fcst_file}")
                ds2 = xr.open_dataset(fcst_file, engine="cfgrib").squeeze()

            else:
                # logging.debug(f"  but no {fcst_file}")
                continue

            tqc = ds2.unknown.values

            # overwrite grid points covered by high clouds with nan
            tqc[np.isnan(lscl)] = np.nan

            # mask swiss plateau
            tqc_ml = tqc[ml_mask]

            # count grid points with liquid water path > 0.1 g/m2
            n_fls = np.sum(tqc_ml > 0.0001)

            # fill into dataframe
            fcst.loc[valid_time][lt] = n_fls / ml_size

    save_as_pickle(obs, obs_path)
    save_as_pickle(fcst, fcst_path)

    return obs, fcst

    # plot mask
    # plt.pcolormesh(ml_mask)
    # plt.savefig("/scratch/swester/tmp/ml_mask.png")


def load_obs_fcst(wd, exp):  # TODO: WIP
    """Load obs and fcst from existing pickled dataframes.

    Args:
        wd (PATH): obs
        exp (str): experiment identifier

    Returns:
        2 dataframes: obs, fcst

    """
    obs = pickle.load(open(Path(wd, "", "obs.p"), "rb"))
    fcst = pickle.load(open(Path(fls_path, f"fcst_{exp}.p"), "rb"))
    return obs, fcst
