# import numpy as np
# import pandas as pd
import shapely.wkt
from numpy.lib import recfunctions as rfn
import os 
from pathlib import Path
import yaml

from db_class import Database
from functions import (filter_distance, find_distances_centroid,
                       find_distances_pcs, get_points, get_relevant_cids,
                       recursive_planes, write_to_laz, prepare_sql_string,
                       write_to_laz)



def filter_entire_pc(wkt_id, wkt):
    '''
    Function that calculates the difference in height between the top and bottom
    of a bridge over a road between two years. 

    in:
        wkt_id [integer]:
            Integer value corresponding to the id of the polygon in the database.

        wkt [string]: 
            Text representation of a polygon. The polygon lies on the A10 and 
            there are points in this polygon in the paths.
        
        laz_dir [string or None]: 
            If it's a string it has to be a Path to a output directory for the laz files.
            If it's None, no output laz file is generated.
    '''

    paths = {
        '2018': config['path_2019'],
        '2019': config['path_2018']
    }

    if shapely.wkt.loads(wkt).geom_type == 'Polygon':
        xmin, ymin, xmax, ymax = shapely.wkt.loads(wkt).bounds
        bounds = f'([{xmin}, {xmax}], [{ymin}, {ymax}])'

    elif shapely.wkt.loads(wkt).geom_type == 'Point':
        polygon = shapely.wkt.loads(wkt).buffer(0.7)
        wkt = polygon.wkt

        xmin, ymin, xmax, ymax = shapely.wkt.loads(wkt).bounds
        bounds = f'([{xmin}, {xmax}], [{ymin}, {ymax}])'

    pc18 = get_points(paths['2018'], bounds, wkt)
    print(f'loaded pc 2018')
    pc19 = get_points(paths['2019'], bounds, wkt)
    print(f'loaded pc 2019')

    # pre processing (filtering of everything that moved more than  5 cm)
    filtered_2018 = filter_distance(pc18, pc19, 0.05)
    laz_path = os.path.join(config['output_path'], f'2018/{wkt_id}.laz')
    write_to_laz(filtered_2018, laz_path)
    print(f'wrote to {laz_path}')
    del filtered_2018


    filtered_2019 = filter_distance(pc19, pc18, 0.05)
    laz_path = os.path.join(config['output_path'], f'2019/{wkt_id}.laz')
    write_to_laz(filtered_2019, laz_path)
    print(f'wrote to {laz_path}')
    del filtered_2019


if __name__ == '__main__':
    
    with open('config.yaml', 'rt') as f:
        config = yaml.safe_load(f)
    
    schema = config['schema']
    table = 'vakken'
    out_table = config['out_table']
    out_path = config['output_path']

    # database connection and query
    database = Database(
            'VU', 
            host=config['host'], 
            dbname=config['dbname'], 
            user=config['user'], 
            password=config['password'], 
            port=config['port']
        )

    query = f'SELECT id, ST_AsText(geom) wkt FROM {schema}.{table}'
    result = database.execute_query(query)[0]

    for dictionary in result:
        wkt_id = dictionary['id']
        wkt = dictionary['wkt']
        try:
            filter_entire_pc(wkt_id, wkt)
            print(f'wrote {wkt_id} to {os.path.join(out_path)}')
            
        except Exception as e:
            print(f'{wkt_id} failed because of {e.message}')
        
        

    # filter_entire_pc