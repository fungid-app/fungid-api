import pandas as pd
import sqlite3
import math
from torch import Tensor, tensor
from .observation import Observation


class LocationModel():
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get_predictions(self, lat: float, long: float) -> pd.Series:
        location_stats = None
        with sqlite3.connect(self.connection_string) as con:
            total_obs, total_species, dist = 0, 0, 25

            while total_obs < 10000 and total_species < 200:
                location_stats = _get_locations(con, lat, long, dist=dist)
                total_obs = location_stats.sum()
                total_species = len(location_stats.index)
                dist += dist

        if location_stats is None:
            raise Exception("Error getting species stats")

        max_val = location_stats.max()
        return ((location_stats / max_val) + 1) / 2


def _get_locations(con,  lat: float, long: float, dist: int) -> pd.Series:
    p1, p2 = _get_bounding_box(lat, long, dist)

    return pd.read_sql_query("""SELECT t.species, COUNT(*) as local--,
                                    --MIN(ABS(decimallatitude - ?)) AS close_lat,
                                    --MIN(ABS(decimallongitude - ?)) AS close_long
                                FROM species t
                                JOIN observations v ON v.specieskey = t.specieskey
                                WHERE decimallatitude BETWEEN ? AND ?
                                AND decimallongitude BETWEEN ? AND ?
                                GROUP BY 1;""",
                             con, params=(p1[0], p2[0], p1[1], p2[1])).set_index('species').local


def _get_bounding_box(lat, lon, dist):
    latdiff = (180 / math.pi) * (dist / 6378)
    londiff = abs((180 / math.pi) * (dist / 6378) / math.cos(lat))
    return (lat - latdiff, lon - londiff), (lat + latdiff, lon + londiff)
