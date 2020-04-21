"""Test ProcessFullDataset class."""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))
from hprocessing.ProcessFullDataset import *


MASKS = pd.read_csv("data/testfiles/masks/masks_test.csv", sep="\s+")


def testGetWoodenBarMask(setupProcessor):
    wooden_bar = getWoodenBarMask(
        point1=(5, 5), point2=(10, 6.), height=2.)
    assert(wooden_bar == [(1, 4), (2, 4), (6, 5), (11, 6), (16, 7), (21, 8),
                          (26, 9), (31, 10), (36, 11), (41, 12), (46, 13)])


def testGetMask(setupProcessor):
    mask = getMask(setupProcessor.masks, setupProcessor.index_of_meas,
                   setupProcessor.imageshape)
    assert(mask.shape == (50, 50))


@pytest.mark.parametrize("zone_list,expected", [
    (["zone1"], (1, 3)),
    (["zone1", "zone2"], (2, 3)),
])
def testGetSoilMoistureData(setupProcessor, zone_list, expected):
    proc = setupProcessor
    proc.zone_list = zone_list
    sm_list = proc.getSoilMoistureData()
    assert(isinstance(sm_list, pd.DataFrame))
    print(sm_list)
    assert(sm_list.shape == expected)


def testGetLwirData(setupProcessor):
    proc = setupProcessor
    proc.datetime = pd.to_datetime("2017-08-16 10:30:00+02:00", utc=True)
    lwir_data = proc.getLwirData()
    assert(isinstance(lwir_data, pd.DataFrame))
    assert(lwir_data.shape == (1, 4))


@pytest.mark.parametrize("masks", [
    (None), (MASKS),
])
def testProcess(setupProcessor, masks):
    setupProcessor.masks = masks
    df = setupProcessor.process()
    df_hyp_n = 125 + 3 + 1
    df_sm_n = 2
    df_lwir_n = 3
    assert(df.shape == (1, df_hyp_n + df_sm_n + df_lwir_n))

def testGetLineFromPoints():
    m, c = getLineFromPoints(point1=(5, 5), point2=(7.5, 7.5))
    assert(m == 1)
    assert(c == 0)


def testGetAllSoilMoistureSensors():
    sensors = getAllSoilMoistureSensors()
    assert(isinstance(sensors, dict))
    assert(len(sensors["number"]) == 18)


def testGetUppermostSoilMoistureSensors():
    uppermost_sensors = getUppermostSoilMoistureSensors()
    assert(uppermost_sensors.shape[0] == 8)


def testFindNearestDate():
    # data
    date = "2020-01-01 14:25:00+02:00"
    date_df = pd.DataFrame({"dates": ["2020-01-01 14:00:00+02:00",
                                      "2020-01-01 14:30:00+02:00",
                                      "2020-01-01 16:15:00+00:00",
                                      "2020-01-01 14:32:00+02:00"]})
    # convert to datetime
    date_df.dates = pd.to_datetime(date_df["dates"], utc=True)
    date = pd.to_datetime(date, utc=True)

    nearest_date, time_delta = findNearestDate(date_df.dates, date)
    assert(nearest_date == pd.to_datetime("2020-01-01 14:30:00+02:00", utc=True))
    assert(time_delta == 5)


# def testReadConfig():
#     """Test can only be run locally."""
#     config = readConfig("config/HydReSGeo.ini",
#                         data_directory="/Volumes/Trust_One/HydReSGeo/")

#     for var in ["data_hyp", "data_lwir", "data_sm", "data_output"]:
#         assert(isinstance(config[var], str))

#     for var in ["positions_hyp", "positions_lwir", "positions_lwir",
#                 "ignore_hyp_measurements", "ignore_hyp_fields",
#                 "ignore_hyp_datapoints", "masks_hyp"]:
#         print(var)
#         assert(isinstance(config[var], pd.DataFrame))
#         if var in ["positions_hyp", "positions_lwir", "positions_lwir",
#                    "ignore_hyp_fields", "masks_hyp"]:
#             assert(config[var].shape[1] > 2)
