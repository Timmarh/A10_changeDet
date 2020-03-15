# -*- coding: utf-8 -*-
"""

@author: Chris Lucas
"""

import os
import numpy as np
from numpy.lib import recfunctions
from scipy.spatial import cKDTree
import pdal


READ_PIPELINE = """
{{
    "pipeline": [
        {{
            "type": "readers.las",
            "filename": "{path}"
        }}
    ]
}}
"""

WRITE_PIPELINE = """
{{
    "pipeline": [
        {{
            "type": "writers.las",
            "filename": "{path}",
            "extra_dims": "all"
        }}
    ]
}}
"""


def read(path):
    pipeline = pdal.Pipeline(
        READ_PIPELINE.format(path=path)
    )
    pipeline.validate()
    pipeline.execute()
    point_cloud = pipeline.arrays[0]

    return point_cloud


def write(point_cloud, path):
    pipeline = pdal.Pipeline(
        WRITE_PIPELINE.format(path=path),
        arrays=[point_cloud]
    )
    pipeline.validate()
    pipeline.execute()


def hausdorff_distance(reference_cloud, compared_cloud):
    tree = cKDTree(reference_cloud)
    distances, _ = tree.query(compared_cloud, k=1)
    return distances


def main():
    output_folder = "/var/data/rws/data/2019/change/"
    laz_folder_2018 = "/var/data/rws/data/2018/las_processor_bundled_out/"
    laz_folder_2019 = "/var/data/rws/data/2019/amsterdam/"

    laz_files_2018 = os.listdir(laz_folder_2018)
    laz_files_2019 = os.listdir(laz_folder_2019)

    for laz_2019 in laz_files_2019:
        if not os.path.isfile(output_folder + laz_2019):
            print(f'Processing: {laz_2019} ..')
            if laz_2019 in laz_files_2018:
                print('Found matching 2018 file, computing distances..')
                point_cloud_2019 = read(laz_folder_2019 + laz_2019)
                points_2019 = point_cloud_2019[['X', 'Y', 'Z']]
                points_2019 = np.array(points_2019[['X', 'Y', 'Z']].tolist())
                point_cloud_2018 = read(laz_folder_2018 + laz_2019)
                points_2018 = point_cloud_2018[['X', 'Y', 'Z']]
                points_2018 = np.array(points_2018[['X', 'Y', 'Z']].tolist())

                if len(points_2018) > 0 and len(points_2019) > 0:
                    distances = hausdorff_distance(points_2018, points_2019)

                    print(f'Done, saving to: {output_folder + laz_2019} ..')

                    point_cloud_2019 = recfunctions.append_fields(
                        point_cloud_2019, 'HausdorffDist2018', distances, 'f8'
                    )
                    write(point_cloud_2019, output_folder + laz_2019)
                else:
                    print('No points found in one of the '
                          'point clouds, skipping..')
            else:
                print('No matching 2018 file found, skipping..')
        else:
            print('Already done, skipping..')


if __name__ == '__main__':
    main()
