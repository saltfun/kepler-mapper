from __future__ import division

import warnings
from itertools import product
import numpy as np

# TODO: Incorporate @pablodecm's cover API.


class Cover():
    """Helper class that defines the default covering scheme
    """

    def __init__(self,
                 n_cubes=10,
                 perc_overlap=0.2,
                 # Deprecated parameters:
                 nr_cubes=None,
                 overlap_perc=None):

        self.n_cubes = nr_cubes if nr_cubes else n_cubes
        self.perc_overlap = overlap_perc if overlap_perc else perc_overlap

        if overlap_perc is not None or nr_cubes is not None:
            warnings.warn(
                "Arguements `overlap_perc` and `nr_cubes` have been replaced with `perc_overlap` and `n_cubes`. Use `perc_overlap` and `n_cubes` instead. They will be removed in future releases.", DeprecationWarning)

    def define_bins(self, data):
        """Returns an iterable of all bins in the cover.

        Example
        -------
            If there are 4 cubes per dimension and 3 dimensions return the bottom left (origin) coordinates of 64 hypercubes, as a sorted list of Numpy arrays

        Warning: This function must assume that the first column of data are indices.
        """

        indexless_data = data[:, 1:]
        bounds = (np.min(indexless_data, axis=0),
                  np.max(indexless_data, axis=0))

        # We chop up the min-max column ranges into 'n_cubes' parts
        self.chunk_dist = (bounds[1] - bounds[0]) / self.n_cubes

        # We calculate the overlapping windows distance
        self.overlap_dist = self.perc_overlap * self.chunk_dist

        # We find our starting point
        self.d = bounds[0]

        # Use a dimension index array on the projected X
        # (For now this uses the entire dimensionality, but we keep for experimentation)
        self.di = np.array(range(1, data.shape[1]))
        self.nr_dimensions = len(self.di)

        if type(self.n_cubes) is not list:
            cubes = [self.n_cubes] * self.nr_dimensions
        else:
            assert len(self.n_cubes) == self.nr_dimensions, "There are {} ({}) dimensions specified but {} dimensions needing specification. If you supply specific number of cubes for each dimension, please supply the correct number.".format(
                len(self.n_cubes), self.n_cubes, self.nr_dimensions)
            cubes = self.n_cubes

        coordinates = map(np.asarray, product(
            *(range(i) for i in cubes)))

        return coordinates

    def find_entries(self, data, cube, verbose=0):
        """Find all entries in data that are in the given cube.

        Parameters
        ----------
        data: Numpy array
            Either projected data or original data.
        cube:
            an item from the list of cubes provided by `cover.define_bins` iterable.

        Returns
        -------
        hypercube: Numpy Array
            All entries in data that are in cube.

        """

        chunk = self.chunk_dist
        overlap = self.overlap_dist
        lower_bound = self.d + (cube * chunk)
        upper_bound = lower_bound + chunk + overlap

        # Slice the hypercube
        entries = (data[:, self.di] >= lower_bound) & \
                  (data[:, self.di] < upper_bound)

        hypercube = data[np.invert(np.any(entries == False, axis=1))]

        return hypercube


class CoverBounds(Cover):
    """
    Class that allows cover to be defined using upper and lower bounds for given dimensions.
    """

    def __init__(self,
                 n_cubes=10,
                 perc_overlap=0.2,
                 # Deprecated parameters:
                 nr_cubes=None,
                 overlap_perc=None,
                 # Bounds parameters
                 limits=None):
        """
        limits: Numpy Array (n_dim,2)
            (lower bound, upper bound) for every dimension
            If a value is set to np.float('inf'), the bound will be assumed to be the min/max value of the dimension
            Instead, if limits == None, this class works identically to the original Cover class.
        """
        Cover.__init__(self, n_cubes, perc_overlap, nr_cubes, overlap_perc)
        self.limits = limits

    def define_bins(self, data):
        """Returns an iterable of all bins in the cover.

        Example
        -------
            If there are 4 cubes per dimension and 3 dimensions return the bottom left (origin) coordinates of 64 hypercubes, as a sorted list of Numpy arrays

        Warning: This function must assume that the first column of data are indices.
        """

        indexless_data = data[:, 1:]
        try:  # Catch to see if self.limits has been set to None - then we just ape the behavior from Cover.
            if self.limits == None:
                bounds = (np.min(indexless_data, axis=0),
                          np.max(indexless_data, axis=0))
        except ValueError:  # self.limits is an array
            dump_arr = np.zeros(self.limits.shape)  # dump_arr is used so we can change the values of self.limits from None to the min/max
            dump_arr[:,0] = np.min(indexless_data, axis=0)
            dump_arr[:,1] = np.max(indexless_data, axis=0)
            dump_arr[self.limits != np.float('inf')] = 0
            self.limits[self.limits == np.float('inf')] = 0
            bounds_arr = self.limits + dump_arr
            """ bounds_arr[i,j] = self.limits[i,j] if self.limits[i,j] == inf
                bounds_arr[i,j] = max/min(indexless_data[i]) if self.limits == inf """
            bounds = (bounds_arr[:,0], bounds_arr[:,1])

        # Now bounds have been set, we just copy the behavior of Cover.define_bins

        # We chop up the min-max column ranges into 'n_cubes' parts
        self.chunk_dist = (bounds[1] - bounds[0]) / self.n_cubes

        # We calculate the overlapping windows distance
        self.overlap_dist = self.perc_overlap * self.chunk_dist

        # We find our starting point
        self.d = bounds[0]

        # Use a dimension index array on the projected X
        # (For now this uses the entire dimensionality, but we keep for experimentation)
        self.di = np.array(range(1, data.shape[1]))
        self.nr_dimensions = len(self.di)

        if type(self.n_cubes) is not list:
            cubes = [self.n_cubes] * self.nr_dimensions
        else:
            assert len(self.n_cubes) == self.nr_dimensions, "There are {} ({}) dimensions specified but {} dimensions needing specification. If you supply specific number of cubes for each dimension, please supply the correct number.".format(
                len(self.n_cubes), self.n_cubes, self.nr_dimensions)
            cubes = self.n_cubes

        coordinates = map(np.asarray, product(
            *(range(i) for i in cubes)))

        return coordinates
