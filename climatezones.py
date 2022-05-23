from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import logging


def get_logger(name):
    zone_file = "dbs/{}.csv".format(name)

    logger = logging.getLogger('log')
    logger.setLevel(logging.INFO)
    ch = logging.FileHandler(zone_file)
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)
    return logger


def prepare_shapefile(filename):
    gdf = gpd.read_file(filename)
    gdf['shapeid'] = np.arange(len(gdf))
    return gdf.set_index('shapeid')


def get_points():
    points = pd.read_csv('tmp/points.csv')
    points = gpd.GeoDataFrame(
        points, geometry=gpd.points_from_xy(points.lat, points.long))
    points['pointid'] = np.arange(len(points))
    points = points.set_index('pointid')
    return points


def spatialjoin(shapes, points):
    return pd.DataFrame(points.sindex.query_bulk(shapes.geometry)) \
        .transpose() \
        .rename(columns={0: 'shapeid', 1: 'pointid'}) \
        .join(shapes, on='shapeid') \
        .join(points, on="pointid", rsuffix="_pt")


def print_results(df, column, logger):
    for gbifid, code in df[["gbifid", column]].to_numpy():
        logger.info("{},{}".format(gbifid, code))


def get_zones(points, filename, column, output):
    logger = get_logger(output)
    base_model = prepare_shapefile(filename)
    spatial = spatialjoin(base_model, points)
    pointgroup = spatial.groupby(by="pointid")
    print('printing singles')

    singles = pointgroup.max()[pointgroup.count()[column] == 1]
    print_results(singles, column, logger)

    dupepoints = pointgroup.max()[pointgroup.count()[column] > 1]
    duperows = spatial[spatial.pointid.isin(dupepoints.index)]
    duperowsg = gpd.GeoDataFrame(duperows, geometry=duperows.geometry)
    print('starting doubles')
    fixed = duperowsg[duperowsg.geometry.contains(duperowsg.geometry_pt)]
    fixed.to_file('fixed.df')
    print('finsihed doubles')
    print_results(fixed, column, logger)


def main():
    points = get_points()
    get_zones(points, 'gaez18/gaez18.shp', 'GRIDCODE', 'gz')
    # get_zones(
    #     points, 'koppen-geiger/Shapefiles/world_climates_completed_koppen_geiger.shp', 'dn', 'kg')


if __name__ == '__main__':
    main()
