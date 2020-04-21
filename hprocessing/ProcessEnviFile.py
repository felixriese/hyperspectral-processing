"""Class and functions to process envi file.

The package `spectral` is used in this repository with permission by the
authors (see `spectralpython/spectral/issues/103
<https://github.com/spectralpython/spectral/issues/103>`_).

"""

import itertools

import numpy as np
import pandas as pd
import spectral as spy


class ProcessEnviFile():
    """Class to process ENVI files.

    Parameters
    ----------
    image : spectral image
        Image file of the hyperspectral image
    wavelengths : list of int
        List of measured wavelength bands
    bbl : list of str/int/bool
        List of bbl values that say which wavelengths are measured in good
        quality (1) and which are not (0)
    zone_list : list
        List of measurement zones in the image. That does not include the
        spectralon (white reference). If a zone needs to be ignored, it needs
        to be removed from this list.
    positions : dict
        Dictionary with information of the positions config file
    index_of_meas : int
        Index of dataset in positions CSV file
    mask : numpy array, optional (default=None)
        Zero = pixel to be masked, One = good pixel
    grid : tuple (int, int), optional (default=(1, 1))
        Size of the grid (rows, columns). If row/column zero, every pixel
        is one row/column.

    """

    def __init__(self,
                 image,
                 wavelengths: list,
                 bbl: list,
                 zone_list: list,
                 positions: dict,
                 index_of_meas: int,
                 mask=None,
                 grid: tuple = (1, 1)):
        """Initialize ProcessEnviFile object."""
        self.image = image
        self.wavelengths_original = wavelengths
        self.bbl_original = bbl
        self.zone_list = zone_list
        self.positions = positions
        self.mask = mask
        self.grid = grid
        self.index_of_meas = index_of_meas

        self.wavelengths_original, self.bbl_original = validateWavelengths(
            wavelengths=self.wavelengths_original, bbl=self.bbl_original)
        self.wavelengths, _ = removeBadBands(
            self.wavelengths_original, self.wavelengths_original,
            self.bbl_original)

        self.grid_elements = None

    def getMultipleSpectra(self):
        """Get soil spectrum for measurements with multiple soil spectra.

        In these measurements, there are multiple spectra measured: the one of
        the spectralon and the multiple soil spectra. The soil spectra are
        combined with the spectralon spectrum to get the reflectance spectra of
        the soil measurements.

        Returns
        -------
        zones_fields_df : DataFrame
            DataFrame containing the reflectance spectra of the soil
            measurements

        Todo
        -----
        - Replace pandas by numpy

        """
        # get spectrum of the spectralon (= white reference)
        spec_edges = self.getEdgesFromPrefix(prefix="spec")
        df_spectralon = self.getMeanSpectrumFromRectangle(
            edges=spec_edges, mode="max10")

        # loop over all zones and get spectra
        zone_spectra_cali = []
        for _, zone in enumerate(self.zone_list):
            zone_edges = self.getEdgesFromPrefix(prefix=zone)

            df_zone = self.getMeanSpectraFromSquareGrid(
                edges=zone_edges, mode="median")
            df_zone["zone"] = zone
            zone_spectra_cali.append(self.getCalibratedSpectra(
                spectra=df_zone, spectralon=df_spectralon,
                spectralon_factor=0.95))

        zones_fields_df = pd.concat(zone_spectra_cali,
                                    axis=0, ignore_index=True)

        return zones_fields_df

    def getEdgesFromPrefix(self, prefix: str):
        """Get start and end values of edges in rows and columns.

        These four values describe a rectangle on the hyperspectral image.

        Parameters
        ----------
        prefix : str
            Name of the rectangle which corresponds to the resulting edges

        Returns
        -------
        edges : list of [int, int, int, int]
            Edges of the resulting rectangle

        """
        edges = [self.positions[prefix+"_row_start"][self.index_of_meas],
                 self.positions[prefix+"_row_end"][self.index_of_meas],
                 self.positions[prefix+"_col_start"][self.index_of_meas],
                 self.positions[prefix+"_col_end"][self.index_of_meas]]
        return edges

    def getMeanSpectrumFromRectangle(self,
                                     edges: list,
                                     mode: str = "median") -> pd.DataFrame:
        """Get mean spectrum from rectangle area (region of interest, ROI).

        Parameters
        ----------
        edges : list of 4 int
            Edges of the square (row_start, row_end, col_start, col_end)
        mode : str
            Mode for calculating the "mean spectrum". Possible values: median,
            mean, max, max10 (= maximum of the top 10 pixels).

        Returns
        -------
        df_spectrum : pd.DataFrame
            Dataframe with the spectrum as row, wavelengths as columns

        Todo
        -----
        - implement statsmodels.robust.scale.Huber as robust mean

        """
        spectrum_mean = []
        for i in range(len(self.wavelengths_original)):
            roi = []
            for row in range(edges[0], edges[1]):
                for col in range(edges[2], edges[3]):
                    if self.mask is not None:
                        if self.mask[row, col] == 1:
                            continue
                    roi.append(self.image[row, col, i])

            if mode == "median":
                spectrum_mean.append(np.median(roi))
            elif mode == "mean":
                spectrum_mean.append(np.mean(roi))
            elif mode == "max":
                spectrum_mean.append(np.max(roi))
            elif mode == "max10":
                spectrum_mean.append(np.mean(np.sort(roi)[-10:]))

        wavelengths, spectrum_mean = removeBadBands(
            spectrum=spectrum_mean, wavelengths=self.wavelengths_original,
            bbl=self.bbl_original)

        df_spectrum = pd.DataFrame(data=[spectrum_mean], columns=wavelengths)

        return df_spectrum

    def getRealGridSize(self, edges: list):
        """Calculate grid size.

        Parameters
        ----------
        edges : list of 4 int
            Edges of the square (row_start, row_end, col_start, col_end)

        Returns
        -------
        (int, int)
            Number of grid rows and columns

        """
        if not self.grid:
            grid_n_rows = (edges[1] - edges[0])
            grid_n_columns = (edges[3] - edges[2])

        else:
            if self.grid[0] == 0:
                grid_n_rows = (edges[1] - edges[0])
            else:
                grid_n_rows = self.grid[0]

            if self.grid[1] == 0:
                grid_n_columns = (edges[3] - edges[2])
            else:
                grid_n_columns = self.grid[1]

        return (grid_n_rows, grid_n_columns)

    def getMeanSpectraFromSquareGrid(self, edges, mode: str = "median"):
        """Get mean spectra from squared grid area (region of interest, ROI).

        Parameters
        ----------
        edges : list of 4 int
            Edges of the square (row_start, row_end, col_start, col_end)
        mode : str
            Mode for calculating the "mean spectrum". Possible values:  median,
            mean, max, max10 (= maximum of the top 10 pixels).

        Returns
        -------
        df : pd.DataFrame
            DataFrame with all spectra as rows.

        """
        grid_real = self.getRealGridSize(edges)
        self.grid_elements = getGridElements(grid_real)
        new_edges_list = getEdgesForGrid(edges, grid_real=grid_real)

        spectra_list = []
        for new_edges in new_edges_list:
            spectra_list.append(self.getMeanSpectrumFromRectangle(
                edges=new_edges, mode=mode))
        df = pd.concat(spectra_list, ignore_index=True)
        df["GridElement_Row"] = [el[0] for el in self.grid_elements]
        df["GridElement_Column"] = [el[1] for el in self.grid_elements]

        return df

    def getCalibratedSpectra(self,
                             spectra: pd.DataFrame,
                             spectralon: pd.DataFrame,
                             spectralon_factor: float = 0.95) -> pd.DataFrame:
        """Get calibrated spectra.

        Parameters
        ----------
        spectra : pd.DataFrame
            Not-calibrated spectra
        spectralon : pd.DataFrame
            Spectrum of the spectralon (white reference)
        spectralon_factor : float, optional (default=0.95)
            Factor of how much solar radiation the spectralon reflects.

        Returns
        -------
        pd.DataFrame
            Calibrated spectra

        """
        new_spectra = spectra.copy(deep=True)

        def getCalibratedSpectrumSimple(x):
            return getCalibratedSpectrum(
                soil=x,
                spectralon=spectralon[self.wavelengths],
                spectralon_factor=spectralon_factor)

        new_spectra[self.wavelengths] = spectra[self.wavelengths].apply(
            getCalibratedSpectrumSimple, axis=1, raw=True)
        return new_spectra


def getEdgesForGrid(edges: list, grid_real):
    """Calculate the grid geometry (edges).

    Parameters
    ----------
    edges : list of 4 int
        Edges of the square (row_start, row_end, col_start, col_end)

    Returns
    -------
    new_edges : list of int
        New edges of the grid inside the rectangle.

    """
    # calculating the height
    height = int((edges[1] - edges[0]) / grid_real[0])

    # calculating the width
    width = int((edges[3] - edges[2]) / grid_real[1])

    # calculating starting points of the new rows and columns
    new_row_starts = [int(edges[0] + height*i)
                      for i in range(int((edges[1] - edges[0]) / height))]
    new_col_starts = [int(edges[2] + width*i)
                      for i in range(int((edges[3] - edges[2]) / width))]

    # calculating all edges of the grid
    new_edges = []
    for row_s in new_row_starts:
        for col_s in new_col_starts:
            new_edges.append([row_s, row_s+height, col_s, col_s+width])

    return new_edges


def getEnviFile(filepath):
    """Read from envi file.

    The envi files consist of one header file (.hdr) and one image file (.cue).
    The documentation for the ENVI functions can be found here:
    https://github.com/spectralpython/spectral/blob/master/spectral/io/envi.py
    The documentation for the ENVI header files can be found here:
    https://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html

    Parameters
    ----------
    filepath : str
        Path to header file

    Returns
    -------
    header : spectral header
        Contains description, samples, lines, bands, header offset, file type,
        data type, interleave, sensor type, z plot average, z plot range,
        default stretch,  plot titles, reflectance, byte order, bbl,
        wavelength, wavelength units.
    image : spectral image
        Image file of the hyperspectral image. Order of the indices:
        image[row, column], image[row, column, band]
        See here: http://www.spectralpython.net/fileio.html

    """
    spy.settings.envi_support_nonlowercase_params = True

    header = getEnviHeader(filepath)
    image = spy.io.envi.open(filepath, filepath[:-3]+"cue")

    return header, image


def getEnviHeader(filepath):
    """Read envi header file.

    Parameters
    ----------
    filepath : str
        Path to header file

    Returns
    -------
    header : spectral header
        Contains description, samples, lines, bands, header offset, file type,
        data type, interleave, sensor type, z plot average, z plot range,
        default stretch,  plot titles, reflectance, byte order, bbl,
        wavelength, wavelength units.

    """
    header = spy.io.envi.read_envi_header(filepath)
    return header


def readEnviHeader(header):
    """Read out the header of the ENVI file.

    The documentation of the ENVI Header Files can be found here:
    https://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html

    Parameters
    ----------
    header : envi header format
        Header of the ENVI file

    Returns
    -------
    date_formatted : str
        Date formatted as yyyymmdd
    time_formatted : str
        Time formatted as hh:mm:ss

    """
    description = header["description"].split("\n")

    datestring = description[0]  # datestring format: "Date: 05/17/2017,"
    timestring = description[1]  # timestring format: "Time: 6:02:24.34 P,"

    date = datestring[6:-1]  # date format: "05/17/2017"
    time = timestring[6:-6]  # time format: "6:02:24"
    ampm = timestring[-2]  # ampm: A or P

    date_formatted = date[6:] + date[0:2] + date[3:5]   # format: "20170517"
    time_formatted = formatTime(time, ampm)  # format: "18:02:24"

    return date_formatted, time_formatted


def formatTime(time, ampm):
    """Format time from 6:02PM to 18:02 (or 10:02PM to 22:02).

    Parameters
    ----------
    time : str
        Time formated as "6:02:24" (or 10:02:24)
    ampm : str
        Formatted as "A" or "P" for AM or PM

    Returns
    -------
    newtime : str
        Time formatted as "18:02:24" (or 22:02:24)

    """
    hour, minute, second = time.split(":")
    if ampm[0] == "P" and int(hour) < 12:
        newtime = str((int(hour) + 12) % 24) + ":" + minute + ":" + second
    else:
        newtime = time
    return newtime


def getCalibratedSpectrum(soil, spectralon, spectralon_factor: float = 0.95):
    """Calibrate hyperspectral spectrum from soil via spectralon.

    Calibrate each bin of the soil spectrum on the respective bin in the
    spectralon (= white reference) spectrum.

    Parameters
    ----------
    soil : list of float
        Spectrum of the soil.
    spectralon : list of float
        Spectrum of the spectralon.
    spectralon_factor : float
        Factor of how much solar radiation the spectralon reflects.

    Returns
    -------
    np.array of floats
        List of reflectance values for each band of the soil image.

    """
    return np.divide(np.squeeze(soil).astype(float),
                     np.squeeze(spectralon).astype(float)) * spectralon_factor


def validateWavelengths(wavelengths: list, bbl: list):
    """Validate wavelengths and bbl.

    Parameters
    ----------
    wavelengths : list of int
        List of measured wavelength bands
    bbl : list of str/int/bool
        List of bbl values that say which wavelengths are measured in
        good quality (1) and which are not (0)

    Returns
    --------
    list of int
        Validated `wavelengths` list
    list of int
        Validated `bbl` list

    Raises
    ------
    ValueError:
        Raised if `wavelengths` and `bbl` are of a different length.

    """
    # check for inconsistencies
    if len(wavelengths) != len(bbl):
        raise ValueError(
            "Length of wavelengths ({0}) and bbl ({1}) is not equal.".format(
                len(wavelengths), len(bbl)))

    # remove zero-wavelength at the beginning
    if len(wavelengths) == 139:
        return wavelengths[1:], bbl[1:]

    return wavelengths, bbl


def removeBadBands(spectrum, wavelengths, bbl):
    """Remove bands that are marked as bad in bbl list.

    Parameters
    ----------
    spectrum : list of int
        Spectrum as a list.
    wavelengths : list of int
        List of measured wavelength bands
    bbl : list of str/int/bool
        List of bbl values that say which wavelengths are measured in
        good quality (1) and which are not (0)

    Returns
    -------
    newwavelengths : list of int
        List of "good" wavelength bands
    newspectrum : list of int
        Spectrum of all "good" bands as a list

    """
    newwavelengths = []
    newspectrum = []
    for i, refl in enumerate(spectrum):
        if int(bbl[i]) == 1:
            newwavelengths.append(wavelengths[i])
            newspectrum.append(refl)
    return newwavelengths, newspectrum


def convertWavelength(wavelength) -> str:
    """Convert wavelength into string in nano meter.

    Parameters
    -----------
    wavelength : str, int, float
        Wavelength in nano meters or micro meters

    Returns
    --------
    str
        Wavelength as string

    Raises
    -------
    ValueError
        If wavelegnth between 5 and 200

    """
    # micro meter
    if float(wavelength) < 5.0:
        return str(int(float(wavelength)*1000))

    # nano meter
    if int(wavelength) > 200:
        return str(int(wavelength))

    # invalid wavelength
    raise ValueError("Warning: Could not convert wavelength.")


def getGridElements(grid: tuple) -> list:
    """Get elements of a 2-dimensional grid.

    Parameters
    ----------
    grid : tuple (int, int), optional (default=(1, 1))
        Size of the grid (rows, columns). If row/column zero, every pixel
        is one row/column.

    Returns
    -------
    list of tuples (int, int)
        List of grid elements

    """
    if grid is None or grid == (0, 0):
        return [(0, 0)]
    return list(itertools.product(range(grid[0]), range(grid[1])))
