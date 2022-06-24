import pandas as pd
import sqlite3
import math
from torch import Tensor, tensor
from .observation import Observation


class LocationModel():
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get_predictions(self, lat: float, long: float) -> pd.DataFrame:
        species_stats = None
        with sqlite3.connect(self.connection_string) as con:
            species_stats = _get_db_species(con, lat, long, dist=10000)

        if species_stats is None:
            raise Exception("Error getting species stats")

        return species_stats


def _get_db_species(con,  lat: float, long: float, dist: int) -> pd.DataFrame:
    p1, p2 = _get_bounding_box(lat, long, dist)
    print(p1, p2)
    return pd.read_sql_query("""
    SELECT species, COUNT(*)
    FROM validobservations v
    JOIN trainingspecies t ON v.specieskey = t.specieskey
    WHERE decimallatitude BETWEEN ? AND ?
    AND decimallongitude BETWEEN ? AND ?
    GROUP BY 1 ORDER BY 2;""",
                             con, params=(p1[0], p2[0], p1[1], p2[1])).set_index('species')


def _get_bounding_box(lat, lon, dist):
    latdiff = (180 / math.pi) * (dist / 6378137)
    londiff = (180 / math.pi) * (dist / 6378137) / math.cos(lat)
    return (lat - latdiff, lon - londiff), (lat + latdiff, lon + londiff)


def get_species_stats(connection_string: str) -> pd.DataFrame:
    species_stats = None

    with sqlite3.connect(connection_string) as con:
        species_stats = pd.read_sql_query(
            "SELECT s.species, s.stat, s.value, s.likelihood FROM speciesstats s;", con)

        species_stats = species_stats.set_index(
            ['stat', 'value', 'species'])

        species_stats = species_stats.sort_index(
            level=species_stats.index.names)

    if species_stats is None:
        raise Exception("Error getting species stats")

    return species_stats
