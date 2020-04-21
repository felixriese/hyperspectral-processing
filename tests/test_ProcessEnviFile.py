"""Test ProcessEnviFile class."""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))
from hprocessing.ProcessEnviFile import *
from hprocessing.ProcessFullDataset import getMask

TESTFILE_HDR = "data/testfiles/hyp/Auto017.hdr"
TESTFILE_HDR_HIGHRES = "data/testfiles/hyp/Auto017_highres.hdr"

EDGES = [10, 15, 5, 8]
SPEC_EDGES = [30, 35, 18, 25]
MASKS = pd.read_csv("data/testfiles/masks/masks_test.csv", sep="\s+")


@pytest.mark.parametrize("grid,expected_shape", [
    ((1, 1), (1, 125+2)),
    ((2, 3), (6, 125+2)),
    ((0, 0), (15, 125+2)),
    (None, (15, 125+2))
])
def testGetMeanSpectraFromSquareGrid(exampleEnviProcessing, grid,
                                     expected_shape):
    proc = exampleEnviProcessing
    proc.grid = grid
    spectra = proc.getMeanSpectraFromSquareGrid(edges=EDGES)
    assert(spectra.shape == expected_shape)


@pytest.mark.parametrize("grid,with_mask,zone_list,expected_shape", [
    ((1, 1), False, ["zone1"], (1, 125+3)),
    ((1, 1), True, ["zone1"], (1, 125+3)),
    ((1, 1), False, ["zone1", "zone2"], (2, 125+3)),
    ((2, 3), False, ["zone1"], (6, 125+3)),
    ((0, 0), False, ["zone1"], (15, 125+3)),
    (None, False, ["zone1"], (15, 125+3))
])
def testGetMultipleSpectra(exampleEnviProcessing, setupProcessor, with_mask,
                           zone_list, grid, expected_shape):
    proc = exampleEnviProcessing
    proc.grid = grid
    proc.zone_list = zone_list
    if with_mask:
        proc.mask = getMask(setupProcessor.masks, setupProcessor.index_of_meas,
                            setupProcessor.imageshape)
    df = proc.getMultipleSpectra()
    assert(df.shape == expected_shape)


@pytest.mark.parametrize("grid,expected_rows,expected_columns", [
    ((1, 1), 1, 1),
    ((2, 3), 2, 3),
    ((0, 0), 5, 3),
    (None, 5, 3)
])
def testGetRealGridSize(exampleEnviProcessing, grid, expected_rows,
                        expected_columns):
    proc = exampleEnviProcessing
    proc.grid = grid
    n_rows, n_columns = proc.getRealGridSize(edges=EDGES)
    print(n_rows, n_columns)
    assert(n_rows == expected_rows)
    assert(n_columns == expected_columns)


@pytest.mark.parametrize("grid,expected_edges", [
    ((1, 1), [[10, 15, 5, 8]]),
    ((2, 2), [[10, 12, 5, 6], [10, 12, 6, 7], [10, 12, 7, 8],
              [12, 14, 5, 6], [12, 14, 6, 7], [12, 14, 7, 8]]),
])
def testGetEdgesForGrid(exampleEnviProcessing, grid, expected_edges):
    proc = exampleEnviProcessing
    proc.grid = grid
    grid_real = proc.getRealGridSize(EDGES)
    new_edges = getEdgesForGrid(edges=EDGES, grid_real=grid_real)
    assert(new_edges == expected_edges)


@pytest.mark.parametrize("mode", [
    ("median"), ("mean"), ("max"), ("max10"),
])
def testGetMeanSpectrumFromRectangle(exampleEnviProcessing, mode):
    proc = exampleEnviProcessing
    df_spectrum = proc.getMeanSpectrumFromRectangle(
        edges=EDGES, mode=mode)
    # assert(len(wavelengths) == 125 and len(spectrum_mean) == 125)
    print(df_spectrum)
    assert(df_spectrum.shape == (1, 125))


def testGetEdgesFromPrefix(exampleEnviProcessing):
    proc = exampleEnviProcessing
    edges = proc.getEdgesFromPrefix(prefix="zone1")

    assert(len(edges) == 4)
    assert(isinstance(edges, list))
    assert(edges == EDGES)



def testGetEnviFile():
    hdr, img = getEnviFile(filepath=TESTFILE_HDR)

    assert(isinstance(hdr, dict))
    assert(img.shape == (50, 50, 138))


def testGetEnviHeader():
    hdr = getEnviHeader(TESTFILE_HDR_HIGHRES)
    assert(isinstance(hdr, dict))


def testConvertWavelength():
    assert(convertWavelength("300") == str(300))
    assert(convertWavelength(float(300)) == str(300))
    assert(convertWavelength(int(300)) == str(300))

    assert(convertWavelength("2.5") == str(2500))
    assert(convertWavelength(float(2.5)) == str(2500))
    assert(convertWavelength(int(2)) == str(2000))

    with pytest.raises(ValueError):
        convertWavelength("10")


def testRemoveBadBands(exampleImage):
    img, wavelengths, bbl = exampleImage
    wavelengths, spectrum = removeBadBands(
        spectrum=img[5, 5],
        wavelengths=wavelengths,
        bbl=bbl)
    assert(len(wavelengths) == 125)
    assert(float(wavelengths[5]) < 1000)
    assert(len(spectrum) == 125)


def testValidateWavelengths(exampleImage):
    _, wavelengths, bbl = exampleImage

    # check 139 -> 138 bands
    new_wavelengths, new_bbl = validateWavelengths(wavelengths, bbl)
    assert(wavelengths[1:] == new_wavelengths)
    assert(bbl[1:] == new_bbl)

    # check 138 -> 138 bands
    new_wavelengths, new_bbl = validateWavelengths(
        wavelengths[1:], bbl[1:])
    assert(wavelengths[1:] == new_wavelengths)
    assert(bbl[1:] == new_bbl)

    # check raises
    with pytest.raises(ValueError):
        validateWavelengths(wavelengths[1:], bbl)


def testGetCalibratedSpectrum(exampleImage):
    img, _, _ = exampleImage

    getCalibratedSpectrum(
        soil=list(img[5, 8, :]), spectralon=list(img[30, 25, :]))


def testReadEnviHeader():
    hdr_highres = getEnviHeader(TESTFILE_HDR_HIGHRES)
    date, time = readEnviHeader(hdr_highres)
    assert(date == "20170815")
    assert(time == "17:57:02")


@pytest.mark.parametrize("time,ampm,expected", [
    ("6:02:24", "A", "6:02:24"),
    ("6:02:24", "P", "18:02:24"),
    ("6:02:24", "PM", "18:02:24"),
])
def testFormatTime(time, ampm, expected):
    newtime = formatTime(time, ampm)
    assert(newtime == expected)


@pytest.mark.parametrize("grid,expected", [
    ((1, 1), [(0, 0)]),
    ((2, 1), [(0, 0), (1, 0)]),
    ((0, 0), [(0, 0)]),
    (None, [(0, 0)]),
])
def testGetGridElements(grid, expected):
    grid_elements = getGridElements(grid)
    assert(grid_elements == expected)
