"""Configuration for pytest including fixtures."""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))
from hprocessing.ProcessEnviFile import (ProcessEnviFile, getEnviFile,
                                         getEnviHeader)
from hprocessing.ProcessFullDataset import ProcessFullDataset

MEASUREMENT = "20170815_meas1"
TESTPATH_LWIR = "data/testfiles/lwir/"
TESTFILE_HDR = "data/testfiles/hyp/Auto017.hdr"
TESTFILE_HDR_HIGHRES = "data/testfiles/hyp/Auto017_highres.hdr"
TESTFILE_TDR = "data/testfiles/hyd/TDR.csv"
POSITIONS = pd.DataFrame({
    "zone1_row_start": [10], "zone1_row_end": [15],
    "zone1_col_start": [5], "zone1_col_end": [8],
    "zone2_row_start": [25], "zone2_row_end": [28],
    "zone2_col_start": [15], "zone2_col_end": [18],
    "spec_row_start": [30], "spec_row_end": [35],
    "spec_col_start": [18], "spec_col_end": [25],
    "measurement": [MEASUREMENT]})
POSITIONS_LWIR = pd.DataFrame({
    "zone1_row_start": [120], "zone1_row_end": [130],
    "zone1_col_start": [315], "zone1_col_end": [355],
    "zone2_row_start": [120], "zone2_row_end": [130],
    "zone2_col_start": [260], "zone2_col_end": [300],
    "measurement": ["20170815"]})
MASKS = pd.read_csv("data/testfiles/masks/masks_test.csv", sep="\s+")


@pytest.fixture  # (scope="module")
def setupProcessor():
    proc = ProcessFullDataset(
        hyp_hdr_path=TESTFILE_HDR,
        meas_name=MEASUREMENT,
        positions_hyp=POSITIONS,
        positions_lwir=POSITIONS_LWIR,
        zone_list=["zone1"],
        lwir_path=TESTPATH_LWIR,
        soilmoisture_path=TESTFILE_TDR,
        masks=MASKS,
        verbose=1,
    )
    return proc


@pytest.fixture
def exampleEnviProcessing(exampleImage):
    """Set up an example ENVI processing."""
    img, wavelengths, bbl = exampleImage
    proc = ProcessEnviFile(
        image=img,
        wavelengths=wavelengths,
        bbl=bbl,
        zone_list=["zone1"],
        positions=POSITIONS,
        index_of_meas=0,
        grid=(1, 1)
    )
    return proc


@pytest.fixture
def exampleImage():
    """Set up an example image."""
    _, img = getEnviFile(filepath=TESTFILE_HDR)
    hdr_highres = getEnviHeader(TESTFILE_HDR_HIGHRES)
    wavelengths = hdr_highres["Wavelength"]
    bbl = hdr_highres["bbl"]
    return (img, wavelengths, bbl)
