"""Functions to plot ENVI files."""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

from .ProcessEnviFile import convertWavelength, getEdgesForGrid


def plotEnviImageWithMask(image,
                          wavelengths: list,
                          rectangles: list,
                          mask=None,
                          grid: tuple = (1, 1),
                          channel: int = 3,
                          title: str = "",
                          imageshape: tuple = (50, 50),
                          save_to_file: bool = False):
    """
    Plot Envi image with mask.

    Parameters
    ----------
    image : bsq-file
        Envi Image
    wavelengths : list of int
        List of measured wavelength bands
    rectangles : list of int
        Rectangle geometry data.
    mask : list of lists
        Mask to be plotted
    grid : tuple (int, int), optional (default=(1, 1))
        Size of the grid (rows, columns). If row/column zero, every pixel
        is one row/column.
    channel : int
        Band/channel of the sensor
    title : str
        Plot title
    imageshape : tuple of (int, int), optional
        Image shape
    save_to_file : bool, optional
        Should plot be saved to file?

    """
    bwmap = np.array([[image[i, j, channel] for j in range(imageshape[0])]
                      for i in range(imageshape[1])])
    if mask is not None:
        bwmap_masked = np.multiply(bwmap, mask)
    plt.clf()
    plt.imshow(bwmap, cmap="viridis")
    if mask is not None:
        plt.imshow(bwmap_masked, cmap="viridis", alpha=0.5)
    plt.xlabel("Sensor columns")
    plt.ylabel("Sensor rows")
    # plt.title("Image at wavelength = "+str(wavelengths[channel])+"nm")
    print("Image at wavelength = "+str(wavelengths[channel])+"nm")

    # plot rectangles
    currentAxis = plt.gca()
    for i, r in enumerate(rectangles):
        # IMPORTANT: (x,y) != (row, column)
        upperleft = (r[2], r[0])  # lowerleft = envi upperleft
        width = r[3] - r[2]
        height = r[1] - r[0]
        currentAxis.add_patch(Rectangle(xy=upperleft, width=width,
                                        height=height, facecolor="white",
                                        alpha=0.5))

        if i == 0:
            continue    # spectralon

        # plot fields (grid)
        new_edges_list = getEdgesForGrid(r, grid)
        for new_r in new_edges_list:
            # IMPORTANT: (x,y) != (row, column)
            upperleft = (new_r[2], new_r[0])  # lowerleft = envi upperleft
            width = new_r[3] - new_r[2]
            height = new_r[1] - new_r[0]
            # colorSet1
            currentAxis.add_patch(Rectangle(xy=upperleft, width=width,
                                            height=height, facecolor="none",
                                            edgecolor="white", alpha=0.5))

    if save_to_file:
        plt.savefig("plots/plot_envi_withrectangles_"+title+".pdf",
                    bbox_inches='tight')
    else:
        plt.show()


def plotEnviImageWithRectangles(image,
                                wavelengths: list,
                                rectangles: list,
                                channel: int = 137,
                                title: str = "",
                                imageshape: tuple = (50, 50),
                                includeColorbar: bool = True,
                                fontsize: int = 10,
                                save_to_file: bool = False):
    """
    Plot Envi image with (multiple) rectangle(s).

    All functions for bsq-files can be found here:
    https://github.com/spectralpython/spectral/blob/master/spectral/io/
    bsqfile.py

    Parameters
    ----------
    image : bsq-file
        Envi Image
    wavelengths : list of int
        List of measured wavelength bands
    rectangles : list of lists
        Corner points of the rectangles to be plotted
    channel : int
        Band/channel of the sensor
    title : str
        Plot title
    imageshape : tuple of (int, int), optional
        Image shape
    includeColorbar : boolean, optional
        If true, the colorbar is included into the plot
    fontsize : int, optional
        Fontsize of labels in the plot
    save_to_file : bool, optional
        Should plot be saved to file?

    """
    bwmap = [[image[i, j, channel] for j in range(imageshape[0])]
             for i in range(imageshape[1])]
    plt.clf()

    # fig, ax = plt.subplots(figsize=(6,5),dpi=200)
    plt.imshow(bwmap, cmap="viridis")
    if includeColorbar:
        cbar = plt.colorbar()
        cbar.ax.set_ylabel('Sensor counts', fontsize=fontsize)
        cbar.ax.tick_params(labelsize=fontsize)

        # hide every second label:
        for label in cbar.ax.yaxis.get_ticklabels()[::2]:
            label.set_visible(False)

    plt.xlabel("Sensor columns", fontsize=fontsize)
    plt.ylabel("Sensor rows", fontsize=fontsize)
    plt.xlim(xmin=0)
    plt.ylim(ymax=0)    # "max" because rows not equals y
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    # plt.title("Image at wavelength = "+str(wavelengths[channel])+"nm")
    print("Image at wavelength = {0} nm"
          .format(convertWavelength(wavelengths[channel])))
    currentAxis = plt.gca()
    for r in rectangles:
        # IMPORTANT: (x,y) != (row, column)
        upperleft = (r[2], r[0])  # lowerleft = envi upperleft
        width = r[3] - r[2]
        height = r[1] - r[0]
        currentAxis.add_patch(Rectangle(xy=upperleft, width=width,
                                        height=height, facecolor="white",
                                        alpha=0.5))
    if save_to_file:
        plt.savefig("plots/plot_envi_withrectangles_"+title+".pdf",
                    bbox_inches='tight')
    else:
        plt.show()
