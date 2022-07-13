from typing import Tuple, Optional
import pandas as pd
import numpy as np
import rasterio
from rasterio.windows import Window
import math
import sqlite3


class GeoRaster:
    def __init__(self, raster_path: str):
        self.raster_path = raster_path
        self.raster_data = self.read_raster()
        self.transformer = self.get_transformer()

    def find_val(self, x: int, y: int, depth: int) -> int:
        """
        Find the closest value at a given x, y coordinate, given a depth
        """
        window = Window(y-depth, x-depth, 2*depth + 1, 2*depth + 1)
        data = self.raster_data.read(1, window=window)
        return get_common_val(data)

    def find_closest_value(self, x: int, y: int) -> int:
        """
        Find the closest value at a given x, y coordinate
        """
        val: int = self.find_val(x, y, 0)

        depth: int = 1

        while val == 0:
            val = self.find_val(x, y, depth)
            depth = math.ceil(depth * 1.25)

        return val

    def get_value(self, lat: float, long: float):
        (x, y) = self.transformer.rowcol(long, lat)
        return int(self.find_closest_value(x, y))

    def read_raster(self):
        """
        Read raster data from file
        """
        return rasterio.open(self.raster_path)

    def get_transformer(self):
        """
        Get the transformer object for the raster
        """
        return rasterio.transform.AffineTransformer(self.raster_data.transform)


def get_common_val(window) -> int:
    bins = np.bincount(window.flatten())

    if(len(bins) > 0):
        bins[0] = 0
        return bins.argmax()
    else:
        return 0


class KGRaster:
    def __init__(self, filename: str):
        self.raster_path = filename
        self.raster = GeoRaster(self.raster_path)

    def get_value(self, lat: float, long: float):
        return self.raster.get_value(lat, long)


class EluRaster:
    def __init__(self, filename: str, db_path: str):
        self.raster_path = filename
        self.raster = GeoRaster(self.raster_path)
        self.db_path = db_path

    def get_classes(self, lat: float, long: float) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        eluid = self.raster.get_value(lat, long)

        with sqlite3.connect(self.db_path) as con:
            classes: Tuple[str, str, str] = con.execute(
                "SELECT class1, class2, class3 FROM classifier_elu_values WHERE eluid = ?;", (eluid, )).fetchone()
            return classes

        return None, None, None
