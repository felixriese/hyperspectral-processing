"""Class to process full HydReSGeo dataset."""

import configparser
import glob
import itertools
import os

import numpy as np
import pandas as pd
from tqdm import tqdm

from .ProcessEnviFile import (ProcessEnviFile, getEnviFile, getEnviHeader,
                              readEnviHeader)

from .IRUtils import getIRDataFromMultipleZones


class ProcessFullDataset():
    """Class to process the full HydReSGeo dataset.

    Parameters
    ----------
    envi_hdr_filepath : str
        Path to envi header file (low resolution)
    meas_name : str
        Name of measurement
    positions_hyp : dict
        Dictionary with information of the positions config file for the
        hyperspectral camera
    positions_lwir : dict
        Dictionary with information of the positions config file for the
        lwir camera
    zone_list : list
        List of measurement zones in the image. That does not include the
        spectralon (white reference). If a zone needs to be ignored, it needs
        to be removed from this list.
    lwir_path : str
        Path to long-wave infrared (LWIR) data
    soilmoisture_filepath : str
        Path to soil moisture data
    masks : pd.DataFrame or None
        Masks for hyperspectral images
    soilmode : str
        Mode of the soil measurements (e.g. KW33, Lysimeter)
    imageshape : tuple, optional (default= (50, 50))
        Height and width of the image
    time_window_width : int, optional (default=6)
        Time window width to match the hyperspectral image to the soil moisture
        data. The unit of the time window width is minutes.
    verbose : int, optional (default=0)
        Controls the verbosity.

    Todo
    -----
    - Add attributes to class docstring.
    - Remove self.date and self.time, only use self.datetime. Remove all
      unnecessary functions of self.date and self.time.

    """

    def __init__(self,
                 hyp_hdr_path: str,
                 meas_name: str,
                 positions_hyp: dict,
                 positions_lwir: dict,
                 zone_list: list,
                 lwir_path: str,
                 soilmoisture_path: str,
                 masks: pd.DataFrame,
                 grid: tuple = (1, 1),
                 imageshape: tuple = (50, 50),
                 time_window_width: int = 6,
                 verbose=0):
        """Initialize ProcessDataset instance."""
        self.hyp_hdr_path = hyp_hdr_path
        self.meas_name = meas_name
        self.positions_hyp = positions_hyp
        self.positions_lwir = positions_lwir
        self.zone_list = zone_list
        self.lwir_path = lwir_path
        self.soilmoisture_path = soilmoisture_path
        self.masks = masks
        self.grid = grid
        self.imageshape = imageshape
        self.time_window_width = time_window_width
        self.verbose = verbose

        # get Envi files
        self.envi_hdr_highres_path = self.hyp_hdr_path[:-4] + "_highres.hdr"
        self.hdr, self.envi_img = getEnviFile(self.hyp_hdr_path)
        self.hdr_highres = getEnviHeader(self.envi_hdr_highres_path)
        self.date, self.time = readEnviHeader(self.hdr_highres)

        # set datetime TODO: remove hard-coded timezone
        self.datetime = pd.to_datetime(self.date+" "+self.time+"+02:00",
                                       utc=True)

        # read out header file
        self.wavelengths = self.hdr_highres["Wavelength"]
        self.bbl = self.hdr_highres["bbl"]

        # get measurement index
        self.index_of_meas = int(np.argwhere(
            positions_hyp["measurement"].values == meas_name))

        self.mask = None

        # improvised solution to translate between zone1-8 to A1-D2
        self.zone_dict = {
            "A1": "zone1", "A2": "zone2", "B1": "zone3", "B2": "zone4",
            "C1": "zone5", "C2": "zone6", "D1": "zone7", "D2": "zone8"}
        # "zone1": "A1", "zone2": "A2", "zone3": "B1", "zone4": "B2",
        # "zone5": "C1", "zone6": "C2", "zone7": "D1", "zone8": "D2"}

    def process(self) -> pd.DataFrame:
        """Process a full dataset.

        Returns
        -------
        pd.DataFrame
            Dataframe with hyperspectral, LWIR, and soil moisture data for
            one image.

        """
        # set mask
        if self.masks is not None:
            mask_index = self.masks.index[
                self.masks["measurement"] == self.meas_name].tolist()[0]
            if self.index_of_meas != mask_index:
                raise IOError(("positions.csv and mask.csv don't have the"
                               "same sequence of dates."))

            self.mask = getMask(
                masks=self.masks,
                index_of_meas=self.index_of_meas,
                imageshape=self.imageshape)

        # random check if hyperspectral image is empty
        if np.sum(self.envi_img[:, :, 5]) == 0:
            if self.verbose:
                print("Error: The hyperspectral image is empty.")
            return None

        # process
        envi_processor = ProcessEnviFile(
            image=self.envi_img,
            wavelengths=self.wavelengths,
            bbl=self.bbl,
            zone_list=self.zone_list,
            positions=self.positions_hyp,
            index_of_meas=self.index_of_meas,
            mask=self.mask,
            grid=self.grid)
        df_hyp = envi_processor.getMultipleSpectra()

        # add datetime as column
        df_hyp["datetime"] = self.datetime

        # add soil moisture data
        df_hyd = self.getSoilMoistureData()
        df_hyd = df_hyd.drop(labels=["zone"], axis=1)

        # add IR data
        df_lwir = self.getLwirData()
        df_lwir = df_lwir.drop(labels=["zone"], axis=1)

        return pd.concat([df_hyp, df_hyd, df_lwir], axis=1)

    def getSoilMoistureData(self):
        """Get soil moisture data.

        To match the dates of the soil moisture measurements and the
        hyperspectral image, the timezones are converted to UTC.

        Returns
        --------
        pd.Dataframe
            Dataframe of soil moisture measurements which correspond to the
            hyperspectral image of this instance.

        Todo
        -----
        - Move the CSV file read out into process-function outside this file
        - Add an optional time shift correction between soil moisture data and
          the hyperspectral data.

        """
        soilmoisture_sensors = getUppermostSoilMoistureSensors()

        # read out soil moisture data
        df_sm = pd.read_csv(self.soilmoisture_path)
        df_sm["timestamp"] = pd.to_datetime(df_sm["timestamp"], utc=True)

        sm_dict = {"zone": [], "volSM_vol%": [], "T_C": []}
        for i, sensor in enumerate(soilmoisture_sensors["number"]):

            # only consider sensors in zone_list
            zone = soilmoisture_sensors["zone"].iloc[i]
            if self.zone_dict[zone] not in self.zone_list:
                continue

            # find nearest date
            nearest_date, time_delta = findNearestDate(
                df_sm[df_sm["sensorID"] == "T"+str(sensor)].timestamp,
                self.datetime)

            if time_delta > self.time_window_width / 2:
                if self.verbose:
                    print("Warning: Could not find a soil moisture measurement"
                          "for sensor {0}".format(sensor))
                continue

            nearest_row = df_sm[(df_sm["sensorID"] == "T"+str(sensor)) &
                                (df_sm["timestamp"] == nearest_date)]

            sm_dict["zone"].append(self.zone_dict[zone])
            sm_dict["volSM_vol%"].append(nearest_row["volSM_vol%"].values[0])
            sm_dict["T_C"].append(nearest_row["T_C"].values[0])

        return pd.DataFrame(sm_dict)

    def getLwirData(self):
        """Get LWIR data from one of the CSV export files.

        This function is based on code from another repository by the authors:
        https://github.com/felixriese/thermal-image-processing

        Parameters
        ----------
        date : str
            Date formatted as yyyymmdd, e.g. 20170816
        time : str
            Time formatted as hh-mm-ss, e.g. 13-31-40.

        Returns
        -------
        pd.DataFrame
            IR data of the current datapoint (matched to date and time)

        Todo
        -----
        - Implement grid-wise LWIR data extraction. (For now, only zone-wise
          data extraction is implemented.)

        """
        # find LWIR file within the correct time window
        lwir_datetime_list = []
        for csvfile in glob.glob(self.lwir_path+"/ir_export_*.csv"):
            csvfile_list = csvfile.split("/")[-1].split("_")
            lwir_datetime = pd.to_datetime(
                csvfile_list[2]+" "+csvfile_list[5][:-4].replace("-", ":") +
                "+02:00", utc=True)
            lwir_datetime_list.append(lwir_datetime)
        nearest_date, time_delta = findNearestDate(
            lwir_datetime_list, self.datetime)

        # check if the nearest datetime is close enough
        if time_delta > self.time_window_width / 2:
            if self.verbose:
                print("Warning: Did not find LWIR data.")
            return pd.DataFrame({"zone": [np.nan], "mean": [np.nan],
                                 "med": [np.nan], "std": [np.nan]})

        # load LWIR CSV file
        csvfile = glob.glob(self.lwir_path+"ir_export_" +
                            nearest_date.strftime("%Y%m%d")+"_*" +
                            nearest_date.tz_convert("Europe/Berlin").strftime(
                                "%H-%M-%S")+".csv")[0]

        # get data from different zones
        df_lwir_original = getIRDataFromMultipleZones(
            csvpath=csvfile,
            positions=self.positions_lwir.to_dict('list'),
            zone_list=self.zone_list)

        # The `df_lwir_original` results in one row and column names such as
        # "ir_zone1_med". In the next step, one row per zone needs to be
        # generated.
        lwir_dict = {"zone": [], "mean": [], "med": [], "std": []}
        for zone in self.zone_list:
            lwir_dict["zone"].append(zone)
            lwir_dict["mean"].append(
                df_lwir_original["ir_"+str(zone)+"_mean"].values[0])
            lwir_dict["med"].append(
                df_lwir_original["ir_"+str(zone)+"_med"].values[0])
            lwir_dict["std"].append(
                df_lwir_original["ir_"+str(zone)+"_std"].values[0])

        return pd.DataFrame(lwir_dict)


def getMask(masks, index_of_meas, imageshape=(50, 50)):
    """Mask image with masks from mask.csv file.

    Parameters
    ----------
    masks : pd.DataFrame or None
        Masks for hyperspectral images
    index_of_meas : int
        Index of the measurement in the file
    imageshape : tuple, optional (default= (50, 50))
        Height and width of the image

    Returns
    -------
    mask : 2D numpy array
        Mask in imageshape with 1 (= true value) and 0 (= mask)

    """
    mask = np.ones(imageshape, dtype=int)

    # define borders
    start_row = int(masks["start_row"][index_of_meas])
    end_row = int(masks["end_row"][index_of_meas])
    start_col = int(masks["start_col"][index_of_meas])
    end_col = int(masks["end_col"][index_of_meas])

    # mask around borders
    mask[:start_row] = 0
    mask[end_row:] = 0
    mask[:, :start_col] = 0
    mask[:, end_col:] = 0

    # bar masks
    for i in range(1, 5):
        wooden_bar = getWoodenBarMask(
            [masks["bar"+str(i)+"_p1_x"][index_of_meas],
             masks["bar"+str(i)+"_p1_y"][index_of_meas]],
            [masks["bar"+str(i)+"_p2_x"][index_of_meas],
             masks["bar"+str(i)+"_p2_y"][index_of_meas]],
            height=masks["bar"+str(i)+"_height"][index_of_meas],
            imageshape=imageshape)
        mask[[x[0] for x in wooden_bar], [x[1] for x in wooden_bar]] = 0

    return mask


def getWoodenBarMask(point1, point2, height, imageshape=(50, 50)):
    """Get mask for wooden bar.

    Parameters
    ----------
    point1, point2 : list of int
        Coordinates of the two points
    height : int
        Height/width of the bar in y (row) direction
    imageshape : tuple, optional (default= (50, 50))
        Height and width of the image

    Returns
    -------
    wooden_bar : list of tuple (int, int)
        List of pixels to be masked

    """
    m1, c1 = getLineFromPoints(point1, point2)
    m2, c2 = getLineFromPoints((point1[0] + height, point1[1]),
                               (point2[0] + height, point2[1]))

    def woodenBarUpper(x):
        return m1*x + c1

    def woodenBarLower(x):
        return m2*x + c2

    wooden_bar = [(x, y) for (x, y) in itertools.product(
        range(imageshape[0]), range(imageshape[1]))
                  if woodenBarLower(x) < y < woodenBarUpper(x)]

    return wooden_bar


def getAllSoilMoistureSensors():
    """Get information about the soil moisture sensors.

    Returns
    -------
    sensors : dict
        Sensor information consisting of number, field, depth, and name.

    """
    sensors = {
        "number": [36554, 36555, 36556, 36547, 36557, 36558,
                   36559, 36553, 36549, 36550, 36551, 36552,
                   36560, 36562, 36563, 36564, 36565, 36561],
        "zone": ["A1", "A1", "A1", "A2", "B1", "B1", "B1", "B2", "C1",
                 "C1", "C1", "C1", "C2", "D1", "D1", "D1", "D1", "D2"],
        "depth": [2.5, 5.0, 10.0, 5.0, 2.5, 5.0, 10.0, 5.0, 2.5,
                  5.0, 10.0, 20.0, 5.0, 2.5, 5.0, 10.0, 20.0, 5.0]}
    sensors["name"] = ["SM_" + str(sensors["number"][i]) + "_" +
                       str(sensors["zone"][i]) + "_" + str(sensors["depth"][i])
                       for i in range(len(sensors["number"]))]

    return sensors


def getUppermostSoilMoistureSensors():
    """Get information about the soil moisture sensors.

    Returns
    -------
    sensors : dict
        Sensor information consisting of number, field, depth, and name.

    """
    sensors = pd.DataFrame(getAllSoilMoistureSensors())
    df_temp_list = []

    for zone in np.unique(sensors["zone"].values):
        min_index = sensors[sensors["zone"] == zone]["depth"].values.argmin()
        df_temp_list.append(sensors[sensors["zone"] == zone].iloc[min_index])

    return pd.concat(df_temp_list, axis=1).T


def findNearestDate(date_list, date):
    """Find closest datapoint of each uppermost sensor in time window.

    Adapted from https://stackoverflow.com/a/32237949/3816498 .

    Parameters
    ----------
    date_list : array-like
        List of dates
    date : datetime
        The date, to which the nearest date in `items` should be found.

    Returns
    -------
    nearest_date : datetime
        Nearest date to `date` in `date_list`
    time_delta : int
        Time difference in minutes

    """
    nearest_date = min(date_list, key=lambda x: abs(x - date))
    time_delta = (nearest_date - date).total_seconds() / 60.
    return nearest_date, time_delta


def readConfig(config_path: str,
               data_directory: str,
               verbose=0) -> dict:
    """Read config file to process a dataset.

    Parameters
    ----------
    config_path : str
        Path to config file
    data_directory : str
        Directory of the dataset folder.
    verbose : int, optional (default=0)
        Controls the verbosity.

    Returns
    -------
    config_dict : dict
        Configuration of the processing

    """
    # open config file
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_path)
    if verbose:
        print("Config file is valid.")
        if verbose > 1:
            print("Config file sections: {0}.".format(config.sections()))
    config_dict = {}

    # read out data paths
    for var in ["data_hyp", "data_lwir", "data_sm"]:
        config_dict[var] = (data_directory + config["Paths"][var])
    config_dict["data_output"] = config["Paths"]["data_output"]

    # read out positions, ignore-csv-files, and masks
    for var in ["positions_hyp", "positions_lwir",
                "ignore_hyp_measurements", "ignore_hyp_fields",
                "ignore_hyp_datapoints", "masks_hyp"]:
        config_dict[var] = pd.read_csv(data_directory + config["Paths"][var],
                                       sep="\s+")
        if "measurement" in config_dict[var].columns:
            config_dict[var]["measurement"] = config_dict[var][
                "measurement"].astype("str")

    # read out grid size
    config_dict["grid"] = (1, 1)
    if (config["Process"]["grid_rows"].isdigit() and
            config["Process"]["grid_columns"].isdigit()):
        config_dict["grid"] = (int(config["Process"]["grid_rows"]),
                               int(config["Process"]["grid_columns"]))

    # read out image shape
    config_dict["imageshape"] = (50, 50)
    if (config["Process"]["hyp_image_rows"].isdigit() and
            config["Process"]["hyp_image_columns"].isdigit()):
        config_dict["imageshape"] = (
            int(config["Process"]["hyp_image_rows"]),
            int(config["Process"]["hyp_image_columns"]))

    # read out booleans
    config_dict["overwrite_csv_file"] = config["Process"].getboolean(
        "overwrite_csv_file")

    # read out time window width
    config_dict["time_window_width"] = int(
        config["Process"]["time_window_width"])

    return config_dict


def getLineFromPoints(point1, point2):
    """Get line parameter (y = mx +c) from two points.

    Parameters
    ----------
    point1, point2 : list of int
        Coordinates of the two points

    Returns
    -------
    m, c : float
        Line parameters for y = mx +c

    """
    # m = (y2 - y1)/(x1 - x2)
    m = (point2[1] - point1[1]) / (point2[0] - point1[0])

    # c = y2 - m*x2
    c = point2[1] - m * point2[0]

    return m, c


def processHydReSGeoDataset(config_path: str,
                            data_directory: str,
                            verbose=0) -> pd.DataFrame:
    """Process the full HydReSGeo dataset.

    Parameters
    ----------
    config_path : str
        Path to config file
    data_directory : str
        Directory of the dataset folder.
    verbose : int, optional (default=0)
        Controls the verbosity.

    Returns
    -------
    pd.DataFrame
        Output data of the processing

    """
    # path to the output folder
    config = readConfig(config_path=config_path, data_directory=data_directory)
    params = {
        "positions_hyp": config["positions_hyp"],
        "positions_lwir": config["positions_lwir"],
        "lwir_path": config["data_lwir"],
        "soilmoisture_path": config["data_sm"],
        "masks": config["masks_hyp"],
        "grid": config["grid"],
        "imageshape": config["imageshape"],
        "time_window_width": config["time_window_width"],
        "verbose": verbose
    }

    output_list = []

    if (not config["overwrite_csv_file"] and
            os.path.isfile(config["data_output"])):
        print("Processing not executed, file already exists.")
        print("To overwrite the existing file, change the config.")

    # loop through hyperspectral images
    for _, hyp_header in enumerate(
            tqdm(glob.glob(config["data_hyp"]+"*/*[0-9].hdr"))):

        meas_name = hyp_header.split("/")[-2].replace("_hyp", "")
        file_number = int(hyp_header.split("/")[-1][4:7])
        zone_list = ["zone"+str(i) for i in range(1, 9)]

        # ignore measurements
        if verbose:
            print("-"*50)
            print("Processing {0} - file {1}...".format(
                meas_name, file_number))
        if meas_name in config["ignore_hyp_measurements"].values:
            if verbose:
                print("Ignoring measurement.")
            continue

        # ignore datapoint
        if meas_name in config["ignore_hyp_datapoints"]["measurement"].values:
            if file_number in config["ignore_hyp_datapoints"][
                    config["ignore_hyp_datapoints"]["measurement"] ==
                    meas_name]["filenumber"].values:
                if verbose:
                    print("Ignoring file.")
                continue

        # ignore field
        if meas_name in config["ignore_hyp_fields"]["measurement"].values:
            if file_number in config["ignore_hyp_fields"][
                    config["ignore_hyp_fields"]["measurement"] ==
                    meas_name]["filenumber"].values:
                zones_to_drop = config["ignore_hyp_fields"][
                    (config["ignore_hyp_fields"]["measurement"] == meas_name) &
                    (config["ignore_hyp_fields"]["filenumber"] == file_number)
                    ]["zone"].values
                for zone_to_drop in zones_to_drop:
                    zone_list.remove("zone"+str(zone_to_drop))
                if verbose:
                    print("Removed {0} zone(s).".format(len(zones_to_drop)))

        proc = ProcessFullDataset(
            hyp_hdr_path=hyp_header,
            meas_name=meas_name,
            zone_list=zone_list,
            **params)
        datapoint = proc.process()
        if datapoint is not None:
            output_list.append(datapoint)
    output_df = pd.concat(output_list, axis=0, ignore_index=True)
    output_df.to_csv(config["data_output"])
    if verbose:
        print("Successfully executed!")

    return output_df
