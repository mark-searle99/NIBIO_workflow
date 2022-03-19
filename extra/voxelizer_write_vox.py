#!/bin/python3
# -*- coding:utf-8 -*-
"""This script voxelizes a point cloud.

It then writes the voxels to an ASCII voxel format with the extension ".vox", adapted from AMAPVox-software
(https://amap-dev.cirad.fr/projects/amapvox).
The first lines five of this format contain information on the minimum and maximum corners of the voxel grid, the split
and the voxel size.
The sixth line contains the column header, with the voxel indices and additional fields.
All other lines contain the indices of all voxels containing points. All other fields than the voxel indices are set to
zero.

"Usage: voxelizer.py input.las vox_size out_dir"

- The input format can be LAS/LAZ or ASCII ("Supported extensions: ['.las'., '.laz', '.txt', '.asc', '.xyt', '.csv']")
- Multiple input files can be given using wildcards, e.g. data/*.las
- vox_size is given in m
- The output voxel file will be written to out_dir with a suffix automatically generated from the voxel size

Optionally, the point cloud can be filtered, so that only voxels containing a minimum number of points are written using
the filter_by_point_count-function (see lines 200-201).

Dependencies:
- numpy
- pandas
- laspy (pip install laspy)
"""

import numpy as np

__author__: "Lukas Winiwarter and Hannah Weiser"
__email__: "h.weiser@stud.uni-heidelberg.de"
__date__: "09/2020"


class Voxelizer:
    def __init__(self, data, voxel_size=(1, 1, 1)):
        self.data = data
        if type(voxel_size) is not tuple:
            voxel_size = (voxel_size, voxel_size, voxel_size)
        self.voxel_size = voxel_size


    def voxelize(self, origin=None):
        """
        Function to voxelize point cloud data
        Adapted from Glira (https://github.com/pglira/Point_cloud_tools_for_Matlab/
        blob/master/classes/4pointCloud/uniformSampling.m)
        """
        # No.of points
        noPoi = self.data.shape[0]

        if origin is None:
            # Find voxel centers
            # Point with smallest coordinates
            minPoi = np.min(self.data, axis=0)
            maxPoi = np.max(self.data, axis=0)

            # Rounded local origin for voxel structure
            # (voxels of different pcs have coincident voxel centers if mod(100, voxelSize) == 0)
            # localOrigin = np.floor(minPoi / 100) * 100
            localOrigin = np.floor(minPoi / 1) * 1
            localMax = np.ceil(maxPoi / 1) * 1
        else:
            localOrigin = origin

        # Find 3 - dimensional indices of voxels in which points are lying
        idxVoxel = np.array([np.floor((self.data[:, 0] - localOrigin[0]) / self.voxel_size[0]),
                             np.floor((self.data[:, 1] - localOrigin[1]) / self.voxel_size[1]),
                             np.floor((self.data[:, 2] - localOrigin[2]) / self.voxel_size[2])]).T


        # Remove multiple voxels
        idxVoxelUnique, ic = np.unique(idxVoxel, axis=0,
                                       return_inverse=True)  # ic contains "voxel index" for each point


        # No.of voxel(equal to no.of selected points)
        noVoxel = idxVoxelUnique.shape[0]

        # Prepare list for every output voxel
        XVoxelContains = [[] for i in range(noVoxel)]

        # Select points nearest to voxel centers - --------------------------------------

        # Sort indices and points( in order to find points inside of voxels very fast in the next loop)
        idxSort = np.argsort(ic)
        ic = ic[idxSort]

        data_sorted = self.data[idxSort, :]
        idxJump, = np.nonzero(np.diff(ic))
        idxJump += 1

        # Example (3 voxel)
        # ic = [1 1 1 2 2 2 3]';
        # diff(ic) = [0 0 1 0 0 1]';
        # idxJump = [3     6]';
        #
        # idxInVoxel = [1 2 3]; for voxel 1
        # idxInVoxel = [4 5 6]; for voxel 2
        # idxInVoxel = [7];     for voxel 3

        for i in range(noVoxel):
            # Find indices of points inside of voxel(very, very fast this way)
            if i == 0:
                idxInVoxel = slice(0, idxJump[i])
            elif i == noVoxel - 1:
                idxInVoxel = slice(idxJump[i - 1], noPoi)
            else:
                idxInVoxel = slice(idxJump[i - 1], idxJump[i])

            # Fill voxel information
            XVoxelContains[i] = idxSort[idxInVoxel]

        return localOrigin, localMax, idxVoxelUnique, XVoxelContains


def filter_by_point_count(voxel_idx, pt_idxs_in_voxels, target_count):
    keep = [i for i in range(len(voxel_idx)) if len(pt_idxs_in_voxels[i]) >= target_count]
    pt_idxs_in_voxels = np.array(pt_idxs_in_voxels)
    filtered_idx = voxel_idx[keep]
    filtered_pt_idxs = pt_idxs_in_voxels[keep][:]
    n_voxels = voxel_idx.shape[0]
    n_voxels_filtered = len(filtered_idx)
    print("%i voxels contained less than %i points and were removed. %i voxels left." % (n_voxels-n_voxels_filtered, target_count, n_voxels_filtered))
    return np.array(filtered_idx), np.array(filtered_pt_idxs)


def save_vox(voxel_idx, origin, max, vox_size, fname):
    print("writing vox...")
    c = 1 / 2 * vox_size
    split = [np.max(voxel_idx[:, 0]), np.max(voxel_idx[:, 1]), np.max(voxel_idx[:, 2])]
    with open(fname, "w") as outfile:
        outfile.write("VOXEL SPACE\n")
        outfile.write("#min_corner: %f %f %f\n" % (origin[0]-c, origin[1]-c, origin[2]-c))
        outfile.write("#max_corner: %f %f %f\n" % (max[0], max[1], max[2]))
        outfile.write("#split: %i %i %i\n" % (split[0]+1, split[1]+1, split[2]+1))
        outfile.write("#res: %f\n" % vox_size)
        outfile.write("i j k PadBVTotal angleMean bsEntering bsIntercepted bsPotential ground_distance lMeanTotal lgTotal nbEchos nbSampling transmittance attenuation attenuationBiasCorrection\n")
        arr = np.zeros((voxel_idx.shape[0], 16))

        for idx, x in enumerate(voxel_idx):
            i, j, k = x
            arr[idx, :3] = [i, j, k]
        arr[:, 3] = 1

        np.savetxt(outfile, arr, delimiter=" ", fmt="%i")

if __name__ == '__main__':
    import time
    import pandas
    from laspy.file import File as LasFile
    import sys
    import os
    import glob
    if len(sys.argv) < 3:
        print("Usage: voxelizer.py input.las vox_size out_dir")
    print("Loading file...", end='')

    source_files = glob.glob(sys.argv[1])
    out_dir = sys.argv[3]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for source in source_files:
        t = time.time()

        source_basename = os.path.basename(source)
        source_fname, source_ext = os.path.splitext(source_basename)

        if source_ext == ".las" or source_ext == ".laz":
            inFile = LasFile(source, mode='r')
            data = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
        elif source_ext == ".txt" or source_ext == ".asc" or source_ext == ".xyz" or source_ext == "csv":
            data = pandas.read_csv(source, delimiter=' ', skipinitialspace=True, usecols=(0,1,2)).to_numpy(dtype=float)
        else:
            print("Please give a valid LAS or ASCII point cloud.\n"
                  "Supported extensions: ['.las'., '.laz', '.txt', '.asc', '.xyt', '.csv']")
            sys.exit()
        print(" [done (%.3f s)].\nVoxelizing..." % (time.time() - t), end='')

        t = time.time()
        vox_size_x = vox_size_y = vox_size_z = float(sys.argv[2])
        vox = Voxelizer(data, voxel_size=(vox_size_x, vox_size_y, vox_size_z))
        origin, max, voxel_idx, pt_idxs = vox.voxelize()
        print(" [done (%.3f s)]." % (time.time() - t))
        print("Voxelization of %s points with a voxel size of (%s|%s|%s) resulted in %d filled voxels" % (
            data.shape[0], vox_size_x, vox_size_y, vox_size_z, voxel_idx.shape[0]))

        #filtered_idx, filtered_pt_idxs = filter_by_point_count(voxel_idx, pt_idxs, 4)
        #save_vox(filtered_idx, origin, max, vox_size_x, os.path.join(out_dir, source_fname + "_" + str(int(vox_size_x*1000)) + ".vox"))
        save_vox(voxel_idx, origin, max, vox_size_x, os.path.join(out_dir, source_fname + "_" + str(int(vox_size_x*1000)) + ".vox"))
